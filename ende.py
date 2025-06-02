import customtkinter as ctk
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from threading import Thread

class DialoGPTChatbot:
    def __init__(self):
        # Configuration de l'interface
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.root = ctk.CTk()
        self.root.title("Chatbot Mistral")
        self.root.geometry("900x700")
        
        # Chargement du modèle DialoGPT
        self.load_model()
        self.setup_ui()
        
    def load_model(self):
        """Charge le modèle DialoGPT optimisé"""
        model_name = "microsoft/DialoGPT-medium"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Configuration pour éviter les erreurs
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Paramètres de génération
        self.generation_config = {
            "max_new_tokens": 300,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id
        }
        
    def setup_ui(self):
        """Interface moderne avec CustomTkinter"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header,
            text="Mistral Assistant",
            font=("Arial", 20, "bold")
        ).pack(side="left")
        
        # Zone de conversation
        self.conversation = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=("Arial", 14),
            height=500,
            state="disabled"
        )
        self.conversation.pack(fill="both", expand=True)
        
        # Input area
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(10, 0))
        
        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Écrivez votre message...",
            font=("Arial", 14),
            height=50
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        send_btn = ctk.CTkButton(
            input_frame,
            text="Envoyer",
            command=self.send_message,
            font=("Arial", 14, "bold"),
            height=50,
            width=100
        )
        send_btn.pack(side="right")
        
        # Style des messages
        self.conversation.tag_config("user", foreground="#4CAF50")
        self.conversation.tag_config("assistant", foreground="#2196F3")
        self.conversation.tag_config("system", foreground="#9E9E9E")
        
        self.add_message("system", "Prêt à discuter! Posez-moi vos questions.")
    
    def add_message(self, role, content):
        """Ajoute un message à la conversation"""
        self.conversation.configure(state="normal")
        self.conversation.insert("end", f"{role.capitalize()}: {content}\n\n", role)
        self.conversation.configure(state="disabled")
        self.conversation.see("end")
    
    def send_message(self):
        """Envoie le message et génère une réponse"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return
            
        if user_text.lower() in ("quit", "exit"):
            self.root.destroy()
            return
            
        self.user_input.delete(0, "end")
        self.user_input.configure(state="disabled")
        
        self.add_message("user", user_text)
        self.add_message("assistant", "Je réfléchis...")
        
        # Génération dans un thread séparé
        Thread(target=self.generate_response, args=(user_text,), daemon=True).start()
    
    def generate_response(self, prompt):
        """Génère la réponse avec DialoGPT"""
        try:
            # Formatage du prompt pour DialoGPT
            inputs = self.tokenizer(
                prompt + self.tokenizer.eos_token,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )
            
            # Génération de la réponse
            outputs = self.model.generate(
                inputs.input_ids,
                **self.generation_config
            )
            
            # Décodage de la réponse
            response = self.tokenizer.decode(
                outputs[:, inputs.input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )
            
            # Affichage de la réponse
            self.root.after(0, lambda: self.finish_response(response))
            
        except Exception as e:
            self.root.after(0, lambda: self.finish_response(f"Erreur: {str(e)}"))
    
    def finish_response(self, response):
        """Affiche la réponse finale"""
        self.conversation.configure(state="normal")
        self.conversation.delete("end-2l linestart", "end")
        self.conversation.insert("end", response + "\n\n", "assistant")
        self.conversation.configure(state="disabled")
        
        self.user_input.configure(state="normal")
        self.user_input.focus()

if __name__ == "__main__":
    app = DialoGPTChatbot()
    app.root.mainloop()
