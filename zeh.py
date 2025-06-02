import customtkinter as ctk
from googletrans import Translator
import language_tool_python
from threading import Thread

class TranslationApp:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        self.root = ctk.CTk()
        self.root.title("Traducteur Français-Anglais")
        self.root.geometry("1000x800")
        
        self.translator = Translator()
        self.tool = language_tool_python.LanguageTool('fr')
        self.setup_ui()
        
    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        rows_config = [
            (0, 0), (1, 1), 
            (2, 0),          
            (3, 0), (4, 1),  
            (5, 0), (6, 1)   
        ]
        for row, weight in rows_config:
            main_frame.grid_rowconfigure(row, weight=weight)
        
        ctk.CTkLabel(main_frame, text="Texte en Français:", font=("Helvetica", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5))
        
        self.text_french = ctk.CTkTextbox(
            main_frame, 
            wrap="word",
            font=("Helvetica", 13),
            height=200,
            corner_radius=10
        )
        self.text_french.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.btn_translate = ctk.CTkButton(
            btn_frame, 
            text="Traduire en Anglais", 
            command=self.start_translation_thread,
            font=("Helvetica", 14),
            height=40,
            corner_radius=10
        )
        self.btn_translate.pack(side="left", padx=5)
        
        ctk.CTkLabel(main_frame, text="Traduction Anglaise:", font=("Helvetica", 14, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 5))
        
        self.text_english = ctk.CTkTextbox(
            main_frame, 
            wrap="word",
            font=("Helvetica", 13),
            height=200,
            corner_radius=10,
        )
        self.text_english.grid(row=4, column=0, sticky="nsew")
        
    def start_translation_thread(self):
        self.btn_translate.configure(state="disabled", text="Traduction en cours...")
        Thread(target=self.translate_text, daemon=True).start()
        
    def translate_text(self):
        text = self.text_french.get("1.0", "end").strip()
        
        self.text_english.delete("1.0", "end")
        self.text_english.insert("1.0", "Traduction en cours...")
        
        try:
            translated = self.translator.translate(text, src='fr', dest='en').text
            self.root.after(0, self.update_translation, translated)
        except Exception as e:
            self.root.after(0, self.update_translation, f"Erreur: {str(e)}")
                  
    def update_translation(self, translated_text):
        self.text_english.delete("1.0", "end")
        self.text_english.insert("1.0", translated_text)
        self.btn_translate.configure(state="normal", text="Traduire en Anglais")
        

if __name__ == "__main__":
    app = TranslationApp()
    app.root.mainloop()