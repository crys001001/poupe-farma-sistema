import customtkinter as ctk
from view.config import BRAND_GREEN, BRAND_GREEN_HOVER, criar_input, aplicar_mascara_fixa

class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.montar_ui()

    def montar_ui(self):
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, pady=40)
        
        ctk.CTkLabel(center_frame, text="Ficha do Cliente", font=("Arial", 28, "bold"), text_color="white").pack(pady=(0, 20))
        
        frame_linha1 = ctk.CTkFrame(center_frame, fg_color="transparent")
        frame_linha1.pack(pady=5, fill="x")
        self.entry_telefone = criar_input(frame_linha1, "Celular (Ex: 81999999999)", 410)
        self.entry_telefone.pack(side="left", padx=(0, 10))
        self.entry_telefone.bind("<KeyRelease>", aplicar_mascara_fixa)
        ctk.CTkButton(frame_linha1, text="Buscar", command=self.controller.buscar_cliente, width=120, height=50, font=("Arial", 16, "bold"), fg_color="#444444", hover_color="#333333", corner_radius=8).pack(side="left")

        self.entry_nome = criar_input(center_frame, "Nome Completo", 540)
        self.entry_nome.pack(pady=8)
        self.entry_endereco = criar_input(center_frame, "Endereço (Rua/Avenida)", 540)
        self.entry_endereco.pack(pady=8)

        frame_linha4 = ctk.CTkFrame(center_frame, fg_color="transparent")
        frame_linha4.pack(pady=8, fill="x")
        self.entry_numero = criar_input(frame_linha4, "Nº", 100)
        self.entry_numero.pack(side="left", padx=(0, 10))
        self.entry_bairro = criar_input(frame_linha4, "Bairro", 180)
        self.entry_bairro.pack(side="left", padx=(0, 10))
        self.entry_complemento = criar_input(frame_linha4, "Complemento", 240)
        self.entry_complemento.pack(side="left")

        self.entry_desejo = criar_input(center_frame, "Desejo / Faltou na loja (Opcional)", 540)
        self.entry_desejo.pack(pady=8)

        ctk.CTkButton(center_frame, text="Salvar Cadastro", command=self.controller.salvar_cliente, width=540, height=55, font=("Arial", 18, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, corner_radius=8).pack(pady=25)
        self.lbl_status = ctk.CTkLabel(center_frame, text="", font=("Arial", 16))
        self.lbl_status.pack()

    def get_dados(self): 
        return {
            "telefone": ''.join(filter(str.isdigit, self.entry_telefone.get())), 
            "nome": self.entry_nome.get().title(), 
            "endereco": self.entry_endereco.get(), 
            "numero": self.entry_numero.get(), 
            "bairro": self.entry_bairro.get(),
            "complemento": self.entry_complemento.get(),
            "produto_desejo": self.entry_desejo.get()
        }
        
    def preencher(self, dados): 
        self.limpar()
        self.entry_nome.insert(0, dados.get('nome') or "")
        self.entry_endereco.insert(0, dados.get('endereco') or "")
        self.entry_numero.insert(0, dados.get('numero') or "")
        self.entry_bairro.insert(0, dados.get('bairro') or "")
        self.entry_complemento.insert(0, dados.get('complemento') or "")
        self.entry_desejo.insert(0, dados.get('produto_desejo') or "")
        
    def limpar(self): 
        self.entry_nome.delete(0, 'end')
        self.entry_endereco.delete(0, 'end')
        self.entry_numero.delete(0, 'end')
        self.entry_bairro.delete(0, 'end')
        self.entry_complemento.delete(0, 'end')
        self.entry_desejo.delete(0, 'end')
        
    def mostrar_status(self, msg, cor): 
        self.lbl_status.configure(text=msg, text_color=cor)