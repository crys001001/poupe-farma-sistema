import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser
import os
from view.config import BG_COLOR, CARD_COLOR, BRAND_GREEN, BRAND_GREEN_HOVER, resource_path
from view.aba_cadastro import AbaCadastro
from view.aba_clientes import AbaClientes
from view.aba_entregas import AbaEntregas
from view.aba_historico import AbaHistorico

ctk.set_appearance_mode("dark")

class JanelaSobre:
    def __init__(self, janela_principal):
        self.janela = ctk.CTkToplevel(janela_principal)
        self.janela.title("Sobre o Desenvolvedor")
        self.janela.geometry("500x680")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=BG_COLOR)
        self.janela.transient(janela_principal)
        self.janela.grab_set() 
        
        caminho_imagem = resource_path(os.path.join("assets", "final_image.png"))
        try:
            img_pil = Image.open(caminho_imagem)
            img_icone = ImageTk.PhotoImage(img_pil)
            self.janela.after(10, lambda: self.janela.iconphoto(False, img_icone))
            img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(240, 250))
            ctk.CTkLabel(self.janela, text="", image=img_ctk).pack(pady=(20, 10))
        except Exception:
            ctk.CTkLabel(self.janela, text=f"[ IMAGEM NÃO ENCONTRADA ]", text_color="yellow").pack(pady=20)
        
        cor_militar = "#E5B800" 
        ctk.CTkLabel(self.janela, text="METAL GEAR OS", font=("Impact", 32), text_color=cor_militar).pack(pady=(10, 0))
        ctk.CTkLabel(self.janela, text="SISTEMA INTEGRADO DE ENTREGAS E LOGÍSTICA [v1.0]", font=("Consolas", 11, "bold"), text_color="#A0A0A0").pack(pady=(0, 15))
        
        frame_dev = ctk.CTkFrame(self.janela, fg_color=CARD_COLOR, corner_radius=8, border_width=2, border_color=cor_militar)
        frame_dev.pack(pady=10, padx=30, fill="x")
        ctk.CTkLabel(frame_dev, text="> DESENVOLVEDOR LÍDER:", font=("Consolas", 11, "bold"), text_color=cor_militar).pack(pady=(15, 2))
        ctk.CTkLabel(frame_dev, text="Crystyan Vicente Gomes de Arruda", font=("Arial", 18, "bold"), text_color="#00FF00").pack(pady=2)
        ctk.CTkLabel(frame_dev, text="Análise e Desenvolvimento de Sistemas (ADS)", font=("Consolas", 11, "italic"), text_color="#CCCCCC").pack(pady=(0, 15))
        
        frame_links = ctk.CTkFrame(self.janela, fg_color="transparent")
        frame_links.pack(pady=15)
        
        meu_linkedin = "https://www.linkedin.com/in/crystyan-vicente-92723a26b/" 
        meu_github = "https://github.com/crys001001"          
        meu_youtube = "https://www.youtube.com/@crystyanvicente7681"
        
        ctk.CTkButton(frame_links, text="🔗 LinkedIn", font=("Arial", 13, "bold"), fg_color="#0077B5", hover_color="#005582", width=120, command=lambda: webbrowser.open(meu_linkedin)).grid(row=0, column=0, padx=5)
        ctk.CTkButton(frame_links, text="💻 GitHub", font=("Arial", 13, "bold"), fg_color="#333333", hover_color="#111111", width=120, command=lambda: webbrowser.open(meu_github)).grid(row=0, column=1, padx=5)
        ctk.CTkButton(frame_links, text="▶️ YouTube", font=("Arial", 13, "bold"), fg_color="#FF0000", hover_color="#CC0000", width=120, command=lambda: webbrowser.open(meu_youtube)).grid(row=0, column=2, padx=5)
        
        frase_venom = '"This is our new home. This is our heaven, and our hell.\nThis is Diamond Dogs."'
        ctk.CTkLabel(self.janela, text=f"{frase_venom}\n- Venom Snake", font=("Consolas", 12, "italic"), text_color="gray").pack(side="bottom", pady=20)


class TelaFarmacia(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller 
        
        self.geometry("1024x768")
        self.title("Poupe Farma - Sistema Integrado")
        self.resizable(True, True)
        self.configure(fg_color=BG_COLOR) 
        
        try: self.state("zoomed") 
        except: pass
        
        try:
            import ctypes
            myappid = 'crystyan.poupefarma.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

        try:
            caminho_imagem = resource_path(os.path.join("assets", "final_image.png"))
            img_icon = ImageTk.PhotoImage(Image.open(caminho_imagem))
            self.iconphoto(False, img_icon)
        except: pass
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 0))
        
        ctk.CTkLabel(header, text="Poupe Farma", font=("Arial", 26, "bold")).pack(side="left")
        ctk.CTkButton(header, text="Sobre", width=120, height=35, fg_color="#333333", hover_color="#444444", font=("Arial", 12, "bold"), corner_radius=8, command=lambda: JanelaSobre(self)).pack(side="right")

        self.tabview = ctk.CTkTabview(
            self,
            fg_color="transparent", 
            segmented_button_fg_color=CARD_COLOR,
            segmented_button_selected_color=BRAND_GREEN,
            segmented_button_selected_hover_color=BRAND_GREEN_HOVER,
            segmented_button_unselected_color=CARD_COLOR,
            text_color="white"
        )
        self.tabview.pack(padx=20, pady=5, expand=True, fill="both")
        self.tabview._segmented_button.configure(font=("Arial", 20, "bold"))

        self.tabview.add("Cadastro")
        self.tabview.add("Clientes")
        self.tabview.add("Entregas")
        self.tabview.add("Histórico")

        self.barra_carregamento = ctk.CTkProgressBar(self, mode="indeterminate", fg_color=CARD_COLOR, progress_color=BRAND_GREEN, height=8)
        self.barra_carregamento.set(0)

        # Instanciar as Abas componentizadas
        self.aba_cadastro = AbaCadastro(self.tabview.tab("Cadastro"), controller)
        self.aba_cadastro.pack(fill="both", expand=True)

        self.aba_clientes = AbaClientes(self.tabview.tab("Clientes"), controller)
        self.aba_clientes.pack(fill="both", expand=True)

        self.aba_entregas = AbaEntregas(self.tabview.tab("Entregas"), controller)
        self.aba_entregas.pack(fill="both", expand=True)

        self.aba_historico = AbaHistorico(self.tabview.tab("Histórico"), controller)
        self.aba_historico.pack(fill="both", expand=True)

    def iniciar_carregamento(self):
        self.barra_carregamento.pack(fill="x", side="bottom", padx=20, pady=(0, 15))
        self.barra_carregamento.start()

    def parar_carregamento(self):
        self.barra_carregamento.stop()
        self.barra_carregamento.pack_forget()