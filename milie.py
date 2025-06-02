import customtkinter as ctk
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from threading import Thread

class ChatbotApp:
    def __init__(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Chatbot Nilie Bot")
        self.root.geometry("700x600")
        
        self.setup_model()
        
        self.setup_ui()
        
    def setup_model(self):
        """Charge le modèle et le tokenizer avec configuration correcte"""
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.chat_history_ids = None
        self.max_new_tokens = 500  # Limite de nouveaux tokens à générer
        self.max_length = 1024     # Longueur maximale totale
        
    def setup_ui(self):
        """Configure l'interface graphique"""
        # Cadre principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Zone de chat
        self.chat_display = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            width=650,
            height=400,
            font=("Arial", 12),
            state="disabled"
        )
        self.chat_display.pack(pady=(0, 10))
        
        # Zone de saisie
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.pack(fill="x")
        
        self.user_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Tapez votre message ici...",
            width=500,
            font=("Arial", 12)
        )
        self.user_input.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        # Bouton d'envoi
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Envoyer",
            command=self.send_message,
            width=100,
            font=("Arial", 12, "bold")
        )
        self.send_button.pack(side="right")
        
        # Message de bienvenue
        self.display_message("Bot", "Bonjour ! Je suis votre assistant DialoGPT. Posez-moi vos questions (tapez 'quit' pour quitter).")
        
    def display_message(self, sender, message):
        """Affiche un message dans la zone de chat"""
        self.chat_display.configure(state="normal")
        
        # Configuration des tags pour le style
        if sender == "Bot":
            tag = "bot"
            prefix = "Assistant: "
            color = "#2E86C1"  # Bleu
        else:
            tag = "user"
            prefix = "Vous: "
            color = "#27AE60"  # Vert
        
        self.chat_display.tag_config(tag, foreground=color)
        
        self.chat_display.insert("end", prefix + message + "\n\n", tag)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        
    def send_message(self):
        """Envoie le message de l'utilisateur et obtient une réponse"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return
            
        # Commande pour quitter
        if user_text.lower() == 'quit':
            self.root.destroy()
            return
            
        # Afficher le message de l'utilisateur
        self.display_message("User", user_text)
        self.user_input.delete(0, "end")
        
        # Désactiver l'entrée pendant le traitement
        self.user_input.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        # Afficher un indicateur de traitement
        self.chat_display.configure(state="normal")
        self.typing_indicator = self.chat_display.index("end-1c")
        self.chat_display.insert("end", "Assistant est en train de réfléchir...\n")
        self.chat_display.configure(state="disabled")
        
        # Lancer la génération de réponse dans un thread séparé
        Thread(target=self.generate_response, args=(user_text,), daemon=True).start()
        
    def generate_response(self, user_input):
        """Génère une réponse à partir de l'entrée utilisateur"""
        try:
            # Encodage du nouvel input
            inputs = self.tokenizer(
                user_input + self.tokenizer.eos_token, 
                return_tensors='pt',
                truncation=True,
                max_length=self.max_length - self.max_new_tokens  # Réserve de place pour la réponse
            )
            
            # Concaténation avec l'historique de chat si existant
            if self.chat_history_ids is not None:
                inputs['input_ids'] = torch.cat([self.chat_history_ids, inputs['input_ids']], dim=-1)
                # Création du masque d'attention
                inputs['attention_mask'] = torch.ones_like(inputs['input_ids'])
            
            # Vérification de la longueur totale
            if inputs['input_ids'].shape[-1] > self.max_length - self.max_new_tokens:
                inputs['input_ids'] = inputs['input_ids'][:, -self.max_length + self.max_new_tokens:]
                inputs['attention_mask'] = inputs['attention_mask'][:, -self.max_length + self.max_new_tokens:]
            
            # Génération de la réponse avec paramètres optimisés
            self.chat_history_ids = self.model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=self.max_new_tokens,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                early_stopping=True
            )
            
            # Décodage de la réponse
            response = self.tokenizer.decode(
                self.chat_history_ids[:, inputs['input_ids'].shape[-1]:][0],
                skip_special_tokens=True
            )
            
            # Affichage de la réponse dans l'interface
            self.root.after(0, self.finish_response, response)
            
        except Exception as e:
            error_msg = f"Désolé, une erreur est survenue: {str(e)}"
            self.root.after(0, self.finish_response, error_msg)
            
    def finish_response(self, response):
        """Finalise l'affichage de la réponse"""
        self.chat_display.configure(state="normal")
        
        # Supprimer l'indicateur de traitement
        if hasattr(self, 'typing_indicator'):
            self.chat_display.delete(self.typing_indicator, "end")
        
        # Afficher la réponse
        self.display_message("Bot", response)
        
        # Réactiver l'entrée utilisateur
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")
        self.user_input.focus()

if __name__ == "__main__":
    app = ChatbotApp()
    app.root.mainloop()
