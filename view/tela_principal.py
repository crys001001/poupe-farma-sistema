import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser
import os
import sys


BRAND_GREEN = "#7AC142"
BRAND_GREEN_HOVER = "#629B35"
BRAND_RED = "#E31E24"
BRAND_RED_HOVER = "#B9181D"

BG_COLOR = "#121212"          
CARD_COLOR = "#1E1E1E"        
INPUT_BG = "#2A2A2A"          

ctk.set_appearance_mode("dark")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

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
        except Exception as erro:
            ctk.CTkLabel(self.janela, text=f"[ IMAGEM NÃO ENCONTRADA ]\nCaminho:\n{caminho_imagem}", text_color="yellow").pack(pady=20)
        
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
        
        self.geometry("900x780")
        self.title("Poupe Farma - Sistema Integrado")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR) 
        
        # Variáveis de controle para a animação não bugar se clicar muito rápido
        self._clientes_draw_id = 0
        self._fila_draw_id = 0
        self._historico_draw_id = 0
        
        try:
            caminho_icone = resource_path("icone.ico")
            self.iconbitmap(caminho_icone)
        except: pass

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkButton(header, text="⚙️ Sobre o Dev", width=120, height=35, fg_color="#333333", hover_color="#444444", font=("Arial", 12, "bold"), corner_radius=8, command=self.abrir_sobre).pack(side="right")

        self.tabview = ctk.CTkTabview(self, width=860, height=690,
                                      fg_color="transparent", 
                                      segmented_button_fg_color=CARD_COLOR,
                                      segmented_button_selected_color=BRAND_GREEN,
                                      segmented_button_selected_hover_color=BRAND_GREEN_HOVER,
                                      segmented_button_unselected_color=CARD_COLOR,
                                      text_color="white")
        self.tabview.pack(padx=20, pady=5)
        self.tabview._segmented_button.configure(font=("Arial", 20, "bold"))

        self.tabview.add("Cadastro")
        self.tabview.add("Clientes")
        self.tabview.add("Entregas")
        self.tabview.add("Histórico")

        
        self.barra_carregamento = ctk.CTkProgressBar(self, mode="indeterminate", fg_color=CARD_COLOR, progress_color=BRAND_GREEN, height=8)
        self.barra_carregamento.pack(fill="x", side="bottom", padx=20, pady=(0, 15))
        self.barra_carregamento.set(0)
        self.barra_carregamento.pack_forget() 

        self.montar_aba_cadastro()
        self.montar_aba_clientes()
        self.montar_aba_entregas()
        self.montar_aba_historico()

    def iniciar_carregamento(self):
        self.barra_carregamento.pack(fill="x", side="bottom", padx=20, pady=(0, 15))
        self.barra_carregamento.start()

    def parar_carregamento(self):
        self.barra_carregamento.stop()
        self.barra_carregamento.pack_forget()

    def abrir_sobre(self): JanelaSobre(self)

    def abrir_whatsapp(self, telefone):
        num = ''.join(filter(str.isdigit, telefone))
        if num:
            if not num.startswith("55"): num = "55" + num
            webbrowser.open(f"https://wa.me/{num}")

    def criar_input(self, master, placeholder, width):
        return ctk.CTkEntry(master, placeholder_text=placeholder, width=width, height=50, font=("Arial", 16), fg_color=INPUT_BG, border_width=0, corner_radius=8)

    def mudar_aba(self, nome_aba): self.tabview.set(nome_aba)

    def aplicar_mascara_fixa(self, event):
        entry = event.widget
        texto = entry.get()
        numeros = ''.join(filter(str.isdigit, texto))
        if len(numeros) > 11: numeros = numeros[:11]
        formatado = numeros
        if len(numeros) > 2: formatado = f"({numeros[:2]}) {numeros[2:]}"
        if len(numeros) > 7: formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        cursor_pos = entry.index(ctk.INSERT)
        entry.delete(0, 'end')
        entry.insert(0, formatado)
        entry.icursor(cursor_pos + (len(formatado) - len(texto)))

    def abrir_detalhes_pedido(self, pedido):
        janela = ctk.CTkToplevel(self)
        janela.title("Ficha da Entrega")
        janela.geometry("450x380")
        janela.configure(fg_color=BG_COLOR)
        janela.attributes("-topmost", True) 
        frame = ctk.CTkFrame(janela, fg_color=CARD_COLOR, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame, text="DETALHES DO PEDIDO", font=("Arial", 14, "bold"), text_color=BRAND_GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(frame, text=f"👤 {pedido['nome_cliente']}", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=5)
        
        frame_tel = ctk.CTkFrame(frame, fg_color="transparent")
        frame_tel.pack(anchor="w", padx=20, pady=0, fill="x")
        ctk.CTkLabel(frame_tel, text=f"📱 {pedido['telefone']}", font=("Arial", 14), text_color="#aaaaaa").pack(side="left")
        ctk.CTkButton(frame_tel, text="WhatsApp", width=70, height=24, font=("Arial", 11, "bold"), fg_color="#25D366", hover_color="#128C7E", corner_radius=6, command=lambda t=pedido['telefone']: self.abrir_whatsapp(t)).pack(side="left", padx=15)
        
        ctk.CTkLabel(frame, text=f"📍 {pedido['endereco']}", font=("Arial", 15), wraplength=350, justify="left").pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(frame, text=f"📦 {pedido['conteudo']}", font=("Arial", 18, "bold"), text_color="#ffcc00", wraplength=350, justify="left").pack(anchor="w", padx=20, pady=10)
        ctk.CTkButton(frame, text="Fechar", command=janela.destroy, fg_color="#444444", hover_color="#333333", corner_radius=8).pack(pady=20)

    def abrir_edicao_entrega(self, pedido):
        janela = ctk.CTkToplevel(self)
        janela.title(f"Editar Pedido #{pedido['id']}")
        janela.geometry("400x220")
        janela.configure(fg_color=BG_COLOR)
        janela.attributes("-topmost", True)
        janela.transient(self)
        janela.grab_set()

        ctk.CTkLabel(janela, text="Editar Conteúdo da Entrega:", font=("Arial", 16, "bold"), text_color=BRAND_GREEN).pack(pady=(20, 10))
        entry_edit = self.criar_input(janela, "Conteúdo", 340)
        entry_edit.pack(pady=10)
        entry_edit.insert(0, pedido['conteudo'])

        def salvar():
            if entry_edit.get():
                self.controller.editar_conteudo_entrega(pedido['id'], entry_edit.get())
                janela.destroy()
        ctk.CTkButton(janela, text="Salvar Alteração", font=("Arial", 14, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, command=salvar).pack(pady=15)

    
    # ABA 1: CADASTRO
    
    def montar_aba_cadastro(self):
        aba = self.tabview.tab("Cadastro")
        container = ctk.CTkFrame(aba, fg_color="transparent")
        container.pack(pady=40)
        ctk.CTkLabel(container, text="Ficha do Cliente", font=("Arial", 28, "bold"), text_color="white").pack(pady=(0, 20))
        
        frame_busca = ctk.CTkFrame(container, fg_color="transparent")
        frame_busca.pack(pady=5)
        self.entry_telefone = self.criar_input(frame_busca, "Celular (Ex: 81999999999)", 380)
        self.entry_telefone.pack(side="left", padx=(0, 10))
        self.entry_telefone.bind("<KeyRelease>", self.aplicar_mascara_fixa)
        ctk.CTkButton(frame_busca, text="Buscar", command=self.controller.buscar_cliente, width=150, height=50, font=("Arial", 16, "bold"), fg_color="#444444", hover_color="#333333", corner_radius=8).pack(side="left")

        self.entry_nome = self.criar_input(container, "Nome Completo", 540)
        self.entry_nome.pack(pady=10)
        self.entry_endereco = self.criar_input(container, "Endereço (Rua/Avenida/Bairro)", 540)
        self.entry_endereco.pack(pady=10)

        frame_detalhes = ctk.CTkFrame(container, fg_color="transparent")
        frame_detalhes.pack(pady=10)
        self.entry_numero = self.criar_input(frame_detalhes, "Número", 265)
        self.entry_numero.pack(side="left", padx=(0, 10))
        self.entry_complemento = self.criar_input(frame_detalhes, "Complemento", 265)
        self.entry_complemento.pack(side="left")

        ctk.CTkButton(container, text="Salvar Cadastro", command=self.controller.salvar_cliente, width=540, height=55, font=("Arial", 18, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, corner_radius=8).pack(pady=30)
        self.lbl_status_cadastro = ctk.CTkLabel(container, text="", font=("Arial", 16))
        self.lbl_status_cadastro.pack()

    def get_dados_cadastro(self): return {"telefone": ''.join(filter(str.isdigit, self.entry_telefone.get())), "nome": self.entry_nome.get().title(), "endereco": self.entry_endereco.get(), "numero": self.entry_numero.get(), "complemento": self.entry_complemento.get()}
    def set_telefone_cadastro(self, telefone): self.entry_telefone.delete(0, 'end'); self.entry_telefone.insert(0, telefone); self.aplicar_mascara_fixa(type('Event', (), {'widget': self.entry_telefone})())
    def preencher_cadastro(self, dados): self.entry_nome.delete(0, 'end'); self.entry_nome.insert(0, dados['nome']); self.entry_endereco.delete(0, 'end'); self.entry_endereco.insert(0, dados['endereco']); self.entry_numero.delete(0, 'end'); self.entry_numero.insert(0, dados['numero']); self.entry_complemento.delete(0, 'end'); self.entry_complemento.insert(0, dados['complemento'])
    def limpar_cadastro(self): self.entry_nome.delete(0, 'end'); self.entry_endereco.delete(0, 'end'); self.entry_numero.delete(0, 'end'); self.entry_complemento.delete(0, 'end')
    def mostrar_status_cadastro(self, msg, cor): self.lbl_status_cadastro.configure(text=msg, text_color=cor)

    
    # ABA 2: CLIENTES (COM ANIMAÇÃO)
    
    def montar_aba_clientes(self):
        aba = self.tabview.tab("Clientes")
        top_bar = ctk.CTkFrame(aba, fg_color="transparent")
        top_bar.pack(pady=(20, 10), fill="x", padx=40)
        self.entry_pesquisa = self.criar_input(top_bar, "🔍 Buscar cliente...", 550)
        self.entry_pesquisa.pack(side="left", padx=(0, 10))
        self.entry_pesquisa.bind("<KeyRelease>", self.controller.filtrar_clientes)
        ctk.CTkButton(top_bar, text="Atualizar", command=self.controller.carregar_clientes, width=120, height=50, font=("Arial", 14, "bold"), fg_color="#444444", hover_color="#333333", corner_radius=8).pack(side="right")
        self.scroll_clientes = ctk.CTkScrollableFrame(aba, width=750, height=520, fg_color="transparent")
        self.scroll_clientes.pack(pady=10)

    def get_texto_pesquisa(self): return self.entry_pesquisa.get().lower()

    def desenhar_lista_clientes(self, lista):
        self._clientes_draw_id += 1
        current_id = self._clientes_draw_id
        for widget in self.scroll_clientes.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._clientes_draw_id or index >= len(lista): return
            c = lista[index]
            card = ctk.CTkFrame(self.scroll_clientes, fg_color=CARD_COLOR, corner_radius=12)
            card.pack(fill="x", pady=6, padx=10)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=20, pady=15)
            ctk.CTkLabel(info, text=c['nome'], font=("Arial", 18, "bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"📱 {c['telefone']}   |   📍 {c['endereco']}, {c['numero']} {c['complemento']}", font=("Arial", 14), text_color="#aaaaaa").pack(anchor="w", pady=(5,0))
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)
            ctk.CTkButton(botoes, text="WhatsApp", width=80, height=30, font=("Arial", 11, "bold"), fg_color="#25D366", hover_color="#128C7E", corner_radius=6, command=lambda tel=c['telefone']: self.abrir_whatsapp(tel)).pack(pady=2)
            ctk.CTkButton(botoes, text="Editar", width=80, height=30, fg_color="#3a3a3a", hover_color="#555555", corner_radius=6, command=lambda cli=c: self.controller.preparar_edicao(cli)).pack(pady=2)
            ctk.CTkButton(botoes, text="Excluir", width=80, height=30, fg_color="transparent", border_width=1, border_color=BRAND_RED, text_color=BRAND_RED, hover_color="#3a1114", corner_radius=6, command=lambda tel=c['telefone']: self.controller.excluir_cliente(tel)).pack(pady=2)
            
            self.after(15, lambda: animar(index + 1)) # Efeito Cascata de 15ms

        animar(0)

    
    # ABA 3: ENTREGAS (COM ANIMAÇÃO)
    
    def montar_aba_entregas(self):
        aba = self.tabview.tab("Entregas")
        panel = ctk.CTkFrame(aba, fg_color=CARD_COLOR, corner_radius=15)
        panel.pack(pady=(20, 10), fill="x", padx=30)
        ctk.CTkLabel(panel, text="NOVA ENTREGA", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", padx=20, pady=(15, 0))
        f_input = ctk.CTkFrame(panel, fg_color="transparent")
        f_input.pack(pady=(10, 15), padx=20, fill="x")
        self.entry_busca_entrega = self.criar_input(f_input, "Nome ou Telefone...", 240)
        self.entry_busca_entrega.pack(side="left", padx=(0, 10))
        self.entry_conteudo = self.criar_input(f_input, "Conteúdo (Ex: Dipirona)", 350)
        self.entry_conteudo.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.entry_conteudo.bind("<Return>", lambda e: self.controller.lancar_entrega())
        ctk.CTkButton(f_input, text="Lançar", command=self.controller.lancar_entrega, width=120, height=50, font=("Arial", 16, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, corner_radius=8).pack(side="right")
        self.lbl_status_lancar = ctk.CTkLabel(aba, text="", font=("Arial", 14))
        self.lbl_status_lancar.pack()

        top_fila = ctk.CTkFrame(aba, fg_color="transparent")
        top_fila.pack(fill="x", padx=40)
        ctk.CTkLabel(top_fila, text="Pedidos Pendentes", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(top_fila, text="Atualizar", command=self.controller.carregar_fila, width=100, height=30, fg_color="#444444", hover_color="#333333", corner_radius=6).pack(side="right")
        self.scroll_fila = ctk.CTkScrollableFrame(aba, width=780, height=380, fg_color="transparent")
        self.scroll_fila.pack(pady=5)

    def get_dados_lancamento(self): return self.entry_busca_entrega.get(), self.entry_conteudo.get()
    def limpar_lancamento(self): self.entry_busca_entrega.delete(0, 'end'); self.entry_conteudo.delete(0, 'end')
    def mostrar_status_lancamento(self, msg, cor): self.lbl_status_lancar.configure(text=msg, text_color=cor)

    def desenhar_fila(self, entregas):
        self._fila_draw_id += 1
        current_id = self._fila_draw_id
        for widget in self.scroll_fila.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._fila_draw_id or index >= len(entregas): return
            e = entregas[index]
            card = ctk.CTkFrame(self.scroll_fila, fg_color=CARD_COLOR, corner_radius=10)
            card.pack(fill="x", pady=6, padx=10)
            ctk.CTkFrame(card, width=6, fg_color=BRAND_GREEN, corner_radius=10).pack(side="left", fill="y")
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            ctk.CTkLabel(info, text=f"#{e['id']} - {e['nome_cliente']}  |  📱 {e['telefone']}", font=("Arial", 16, "bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"📦 {e['conteudo']}", font=("Arial", 15), text_color="#aaaaaa", anchor="w").pack(fill="x", pady=(5,0))
            
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)
            ctk.CTkButton(botoes, text="WhatsApp", width=90, height=35, font=("Arial", 12, "bold"), fg_color="#25D366", hover_color="#128C7E", corner_radius=6, command=lambda tel=e['telefone']: self.abrir_whatsapp(tel)).pack(side="left", padx=4)
            ctk.CTkButton(botoes, text="Ver Dados", width=90, height=35, font=("Arial", 12, "bold"), fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda ped=e: self.abrir_detalhes_pedido(ped)).pack(side="left", padx=4)
            ctk.CTkButton(botoes, text="Editar", width=80, height=35, font=("Arial", 12, "bold"), fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda ped=e: self.abrir_edicao_entrega(ped)).pack(side="left", padx=4)
            ctk.CTkButton(botoes, text="Entregue", width=100, height=35, font=("Arial", 12, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, corner_radius=6, command=lambda id=e['id']: self.controller.alterar_status(id, "entregue")).pack(side="left", padx=(15, 4))
            ctk.CTkButton(botoes, text="X", width=40, height=35, font=("Arial", 14, "bold"), fg_color="transparent", border_width=1, border_color=BRAND_RED, text_color=BRAND_RED, hover_color="#3a1114", corner_radius=6, command=lambda id=e['id']: self.controller.alterar_status(id, "cancelar")).pack(side="left", padx=4)
            
            self.after(15, lambda: animar(index + 1)) # Efeito Cascata de 15ms
            
        animar(0)

    
    # ABA 4: HISTÓRICO (COM ANIMAÇÃO)
    
    def montar_aba_historico(self):
        aba = self.tabview.tab("Histórico")
        top_hist = ctk.CTkFrame(aba, fg_color="transparent")
        top_hist.pack(fill="x", padx=40, pady=(20,10))
        ctk.CTkLabel(top_hist, text="Histórico", font=("Arial", 22, "bold")).pack(side="left")
        self.combo_filtro = ctk.CTkComboBox(top_hist, values=["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Tudo"], command=self.controller.mudar_filtro_historico, state="readonly", fg_color=INPUT_BG, border_width=0)
        self.combo_filtro.set("Hoje") 
        self.combo_filtro.pack(side="left", padx=20)
        ctk.CTkButton(top_hist, text="📥 Fechamento Excel", width=140, height=35, font=("Arial", 12, "bold"), fg_color="#1E6E43", hover_color="#154d2f", corner_radius=8, command=self.controller.exportar_excel).pack(side="right")
        self.scroll_hist = ctk.CTkScrollableFrame(aba, width=780, height=550, fg_color="transparent")
        self.scroll_hist.pack(pady=5)

    def desenhar_historico(self, historico):
        self._historico_draw_id += 1
        current_id = self._historico_draw_id
        for widget in self.scroll_hist.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._historico_draw_id or index >= len(historico): return
            h = historico[index]
            card = ctk.CTkFrame(self.scroll_hist, fg_color=CARD_COLOR, corner_radius=10)
            card.pack(fill="x", pady=5, padx=10)
            cor = BRAND_GREEN if h['status'] == "Entregue" else BRAND_RED
            ctk.CTkFrame(card, width=6, fg_color=cor, corner_radius=10).pack(side="left", fill="y")
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            ctk.CTkLabel(info, text=f"Pedido #{h['id']} - {h['nome_cliente']}  |  📅 {h.get('data_formatada', 'N/A')}", font=("Arial", 16, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"Status: {h['status'].upper()}  |  Conteúdo: {h['conteudo']}", font=("Arial", 14), text_color="#aaaaaa", anchor="w").pack(fill="x", pady=(3,0))
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)
            ctk.CTkButton(botoes, text="Detalhes", width=80, height=35, fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda ped=h: self.abrir_detalhes_pedido(ped)).pack(side="left")
            
            self.after(15, lambda: animar(index + 1)) # Efeito Cascata de 15ms
            
        animar(0)