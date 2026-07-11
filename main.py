import threading
import csv
from fpdf import FPDF
from tkinter import filedialog
from models.api_model import FarmaciaAPI
from view.tela_principal import TelaFarmacia

class FarmaciaController:
    def __init__(self):
        self.api = FarmaciaAPI()
        self.view = TelaFarmacia(controller=self)
        self.clientes_cache = []
        
        # O .after(100) garante que a interface termine de desenhar ANTES de puxar do banco
        # Isso mata qualquer chance daquele erro TclError ou AttributeError no arranque
        self.view.after(100, self.carregar_clientes)
        self.view.after(100, self.carregar_fila)
        self.view.after(100, self.carregar_historico)

    def iniciar(self): 
        self.view.mainloop()

    # --- CLIENTES ---
    def buscar_cliente(self):
        telefone = self.view.aba_cadastro.get_dados()['telefone']
        if not telefone: return
        self.view.iniciar_carregamento()
        def task():
            try:
                res = self.api.buscar_cliente(telefone)
                if res and res.get("encontrado"):
                    self.view.after(0, lambda: self.view.aba_cadastro.preencher(res['dados']))
                else:
                    self.view.after(0, lambda: self.view.aba_cadastro.mostrar_status("Novo cliente. Pode preencher.", "#E5B800"))
            except: pass
            finally: self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def salvar_cliente(self):
        dados = self.view.aba_cadastro.get_dados()
        if not dados["telefone"] or not dados["nome"]: return
        self.view.iniciar_carregamento()
        def task():
            try:
                if self.api.salvar_cliente(dados):
                    self.view.after(0, lambda: self.view.aba_cadastro.mostrar_status("Salvo com sucesso!", "#7AC142"))
                    self.carregar_clientes()
            except: pass
            finally: self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def carregar_clientes(self):
        def task():
            try:
                self.clientes_cache = self.api.listar_clientes()
                self.view.after(0, lambda: self.view.aba_clientes.desenhar_lista(self.clientes_cache))
            except: pass
        threading.Thread(target=task).start()

    def filtrar_clientes(self, event=None):
        t = self.view.aba_clientes.get_pesquisa()
        filtrados = [c for c in self.clientes_cache if t in c['nome'].lower() or t in c['telefone']]
        self.view.aba_clientes.desenhar_lista(filtrados)

    def excluir_cliente(self, telefone):
        self.view.iniciar_carregamento()
        def task():
            try:
                self.api.excluir_cliente(telefone)
                self.carregar_clientes()
            except: pass
            finally: self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    # --- ENTREGAS ---
    def lancar_entrega(self):
        busca, conteudo = self.view.aba_entregas.get_dados()
        if not busca or not conteudo: return
        self.view.iniciar_carregamento()
        def task():
            try:
                if self.api.lancar_entrega(busca, conteudo):
                    self.view.after(0, self.view.aba_entregas.limpar)
                    self.view.after(0, lambda: self.view.aba_entregas.mostrar_status("Entrega Lançada!", "#7AC142"))
                    self.carregar_fila()
            except: pass
            finally: self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def carregar_fila(self):
        def task():
            try:
                entregas = self.api.listar_pendentes()
                self.view.after(0, lambda: self.view.aba_entregas.desenhar_fila(entregas))
            except: pass
        threading.Thread(target=task).start()

    def alterar_status(self, id_entrega, acao):
        def task():
            try:
                self.api.alterar_status_entrega(id_entrega, acao)
                self.carregar_fila()
                self.carregar_historico()
            except: pass
        threading.Thread(target=task).start()

    def editar_conteudo_entrega(self, id_entrega, novo_conteudo):
        def task():
            try:
                self.api.editar_conteudo_entrega(id_entrega, novo_conteudo)
                self.carregar_fila()
            except: pass
        threading.Thread(target=task).start()

    # --- HISTÓRICO E EXPORTAÇÃO (EXCEL / PDF) ---
    def mudar_filtro_historico(self, escolha=None):
        self.carregar_historico()

    def carregar_historico(self):
        # Proteção caso a interface ainda esteja sendo montada
        if not hasattr(self.view, 'aba_historico'): return 

        mapa = {"Hoje": "hoje", "Últimos 7 dias": "7dias", "Últimos 30 dias": "30dias", "Tudo": "tudo"}
        filtro = mapa.get(self.view.aba_historico.combo_filtro.get(), "hoje")
        tipo = self.view.aba_historico.combo_tipo.get()

        self.view.iniciar_carregamento()
        def task():
            try:
                if tipo == "Histórico de Entregas":
                    dados = self.api.listar_historico(filtro)
                    self.view.after(0, lambda: self.view.aba_historico.desenhar_entregas(dados))
                else:
                    dados = self.api.listar_logs_clientes(filtro)
                    self.view.after(0, lambda: self.view.aba_historico.desenhar_log(dados))
            except: pass
            finally: self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def exportar_excel(self):
        tipo = self.view.aba_historico.combo_tipo.get()
        filtro = {"Hoje": "hoje", "Últimos 7 dias": "7dias", "Últimos 30 dias": "30dias", "Tudo": "tudo"}[self.view.aba_historico.combo_filtro.get()]
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")], title="Salvar Excel")
        if not caminho: return 
        
        def task():
            try:
                dados = self.api.listar_historico(filtro) if tipo == "Histórico de Entregas" else self.api.listar_logs_clientes(filtro)
                with open(caminho, mode='w', newline='', encoding='utf-8-sig') as arquivo:
                    escritor = csv.writer(arquivo, delimiter=';')
                    if tipo == "Histórico de Entregas":
                        escritor.writerow(['ID_Pedido', 'Cliente', 'Telefone', 'Endereco', 'Mercadoria', 'Status', 'Data'])
                        for d in dados: escritor.writerow([d['id'], d['nome_cliente'], d['telefone'], d['endereco'], d['conteudo'], d['status'], d.get('data_formatada', '')])
                    else:
                        escritor.writerow(['Nome', 'Telefone', 'Endereco', 'Desejo_Cliente', 'Data de Cadastro'])
                        for d in dados: escritor.writerow([d['nome'], d['telefone'], d['endereco'], d.get('produto_desejo',''), d.get('data_formatada', '')])
            except: pass
        threading.Thread(target=task).start()

    def exportar_pdf(self):
        tipo = self.view.aba_historico.combo_tipo.get()
        filtro = {"Hoje": "hoje", "Últimos 7 dias": "7dias", "Últimos 30 dias": "30dias", "Tudo": "tudo"}[self.view.aba_historico.combo_filtro.get()]
        caminho = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Salvar PDF")
        if not caminho: return 
        
        def task():
            try:
                dados = self.api.listar_historico(filtro) if tipo == "Histórico de Entregas" else self.api.listar_logs_clientes(filtro)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=f"Relatorio: {tipo}", ln=True, align='C')
                pdf.set_font("Arial", size=10)
                
                for d in dados:
                    if tipo == "Histórico de Entregas":
                        texto = f"[{d.get('data_formatada','')}] #{d['id']} - {d['nome_cliente']} | Status: {d['status']} | Itens: {d['conteudo']}"
                    else:
                        texto = f"[{d.get('data_formatada','')}] Cliente: {d['nome']} | Tel: {d['telefone']} | Faltou: {d.get('produto_desejo','')}"
                    pdf.multi_cell(0, 10, txt=texto)
                pdf.output(caminho)
            except Exception as e: print("Erro PDF:", e)
        threading.Thread(target=task).start()

if __name__ == "__main__":
    app = FarmaciaController()
    app.iniciar()