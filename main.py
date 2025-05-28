import customtkinter as ctk
import language_tool_python
from threading import Thread

class CorrecteurApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Grammatical")
        self.root.geometry("1000x800")
        
        self.tool = language_tool_python.LanguageTool('fr')
        self.setup_ui()
        
    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        main_frame.grid_rowconfigure(0, weight=0)  # Label
        main_frame.grid_rowconfigure(1, weight=1)  # Zone texte original
        main_frame.grid_rowconfigure(2, weight=0)  # Bouton
        main_frame.grid_rowconfigure(3, weight=1)  # Zone texte corrigé
        main_frame.grid_rowconfigure(4, weight=0)  # Label
        main_frame.grid_rowconfigure(5, weight=1)  # Zone explications
        
        ctk.CTkLabel(main_frame, text="Entrez votre texte à corriger:", font=("Montserrat", 18, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5))
        
        self.text_original = ctk.CTkTextbox(
            main_frame, 
            wrap="word",
            font=("Montserrat", 14),
            height=200,
            corner_radius=10
        )
        self.text_original.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        self.btn_correct = ctk.CTkButton(
            main_frame, 
            text="Corriger le texte", 
            command=self.start_correction_thread,
            font=("Montserrat", 18),
            height=40,
            corner_radius=10
        )
        self.btn_correct.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Texte corrigé:", font=("Montserrat", 18, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 5))
        
        self.text_corrige = ctk.CTkTextbox(
            main_frame, 
            wrap="word",
            font=("Montserrat", 14),
            height=200,
            corner_radius=10,
        )
        self.text_corrige.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Détail des erreurs:", font=("Montserrat", 18, "bold")).grid(
            row=5, column=0, sticky="w", pady=(0, 5))
        
        self.text_explications = ctk.CTkTextbox(
            main_frame, 
            wrap="word",
            font=("Montserrat", 14),
            height=200,
            corner_radius=10,
        )
        self.text_explications.grid(row=6, column=0, sticky="nsew")
        
    def start_correction_thread(self):
        self.btn_correct.configure(state="disabled", text="Traitement en cours...")
        
        Thread(target=self.corriger_texte, daemon=True).start()
        
    def corriger_texte(self):
        texte = self.text_original.get("1.0", "end")
        
        self.text_corrige.delete("1.0", "end")
        self.text_corrige.insert("1.0", "Traitement...")
        self.text_explications.delete("1.0", "end")
        self.text_explications.insert("1.0", "Analyse en cours...")
        
        corrected_text = self.tool.correct(texte)
        

        matches = self.tool.check(texte)
        explications = []
        
        for match in matches:
            if match.ruleId == "FR_AGREEMENT":
                error_msg = f"Erreur d'accord: {match.message}"
            elif match.ruleId.startswith("CONFUSIONS_"):
                error_msg = f"Confusion possible: {match.message}"
            else:
                error_msg = match.message
                
            explication = (
                f"● {error_msg}\n"
                f"   → Correction suggérée: {match.replacements[0] if match.replacements else 'Aucune suggestion'}\n"
                f"   (Type: {match.ruleId})\n\n"
            )
            explications.append(explication)
        
        self.root.after(0, self.update_results, corrected_text, explications)
        
    def update_results(self, corrected_text, explications):
        self.text_corrige.delete("1.0", "end")
        self.text_corrige.insert("1.0", corrected_text)
        
        self.text_explications.delete("1.0", "end")
        if not explications:
            self.text_explications.insert("1.0", "✅ Aucune erreur détectée!")
        else:
            self.text_explications.insert("1.0", "".join(explications))
        
        self.btn_correct.configure(state="normal", text="Corriger le texte")

if __name__ == "__main__":
    app = CorrecteurApp()
    app.root.mainloop()