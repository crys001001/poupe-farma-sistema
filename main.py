import threading
import csv
from tkinter import filedialog
from models.api_model import FarmaciaAPI
from view.tela_principal import TelaFarmacia

class FarmaciaController:
    def __init__(self):
        self.api = FarmaciaAPI()
        self.view = TelaFarmacia(controller=self)
        self.clientes_cache = []
        
        self.carregar_clientes()
        self.carregar_fila()
        self.carregar_historico()

    def iniciar(self):
        self.view.mainloop()

    #  LÓGICA: CADASTRO E EDIÇÃO 
    def buscar_cliente(self):
        telefone = self.view.get_dados_cadastro()['telefone']
        if not telefone: return
        self.view.mostrar_status_cadastro("Buscando...", "#aaaaaa")
        self.view.iniciar_carregamento()
        
        def task():
            try:
                res = self.api.buscar_cliente(telefone)
                if res and res.get("encontrado"):
                    self.view.after(0, lambda: self.view.preencher_cadastro(res['dados']))
                    self.view.after(0, lambda: self.view.mostrar_status_cadastro("Cliente encontrado!", "#7AC142"))
                else:
                    self.view.after(0, self.view.limpar_cadastro)
                    self.view.after(0, lambda: self.view.mostrar_status_cadastro("Cliente novo. Pode preencher.", "#aaaaaa"))
            except:
                self.view.after(0, lambda: self.view.mostrar_status_cadastro("Erro de conexão.", "#E31E24"))
            finally:
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def salvar_cliente(self):
        dados = self.view.get_dados_cadastro()
        if not dados["telefone"] or not dados["nome"]: return
        self.view.iniciar_carregamento()
        
        def task():
            try:
                sucesso = self.api.salvar_cliente(dados)
                if sucesso:
                    self.view.after(0, lambda: self.view.mostrar_status_cadastro("Cadastro salvo com sucesso!", "#7AC142"))
                    self.carregar_clientes() 
                else:
                    self.view.after(0, lambda: self.view.mostrar_status_cadastro("Falha ao salvar.", "#E31E24"))
            except:
                self.view.after(0, lambda: self.view.mostrar_status_cadastro("Erro de servidor.", "#E31E24"))
            finally:
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    #  LÓGICA: BASE DE CLIENTES 
    def carregar_clientes(self):
        self.view.iniciar_carregamento()
        def task():
            try:
                self.clientes_cache = self.api.listar_clientes()
                self.view.after(0, lambda: self.view.desenhar_lista_clientes(self.clientes_cache))
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def filtrar_clientes(self, event=None):
        texto = self.view.get_texto_pesquisa()
        filtrados = [c for c in self.clientes_cache if texto in c['nome'].lower() or texto in c['telefone']]
        self.view.desenhar_lista_clientes(filtrados)

    def preparar_edicao(self, cliente):
        self.view.set_telefone_cadastro(cliente['telefone'])
        self.view.preencher_cadastro(cliente)
        self.view.mudar_aba("Cadastro")
        self.view.mostrar_status_cadastro("Editando cliente...", "#ffcc00")

    def excluir_cliente(self, telefone):
        self.view.iniciar_carregamento()
        def task():
            try:
                self.api.excluir_cliente(telefone)
                self.carregar_clientes()
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    # LÓGICA: FILA DO MOTOBOY 
    def lancar_entrega(self):
        busca, conteudo = self.view.get_dados_lancamento()
        if not busca or not conteudo: return
            
        self.view.iniciar_carregamento()
        def task():
            try:
                sucesso = self.api.lancar_entrega(busca, conteudo)
                if sucesso:
                    self.view.after(0, self.view.limpar_lancamento)
                    self.carregar_fila()
                    self.view.after(0, lambda: self.view.mostrar_status_lancamento("", ""))
                else:
                    self.view.after(0, lambda: self.view.mostrar_status_lancamento("Cliente não encontrado!", "#ffcc00"))
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def carregar_fila(self):
        self.view.iniciar_carregamento()
        def task():
            try:
                entregas = self.api.listar_pendentes()
                self.view.after(0, lambda: self.view.desenhar_fila(entregas))
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def alterar_status(self, id_entrega, acao):
        self.view.iniciar_carregamento()
        def task():
            try:
                self.api.alterar_status_entrega(id_entrega, acao)
                self.carregar_fila()
                self.carregar_historico()
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def editar_conteudo_entrega(self, id_entrega, novo_conteudo):
        self.view.iniciar_carregamento()
        def task():
            try:
                self.api.editar_conteudo_entrega(id_entrega, novo_conteudo)
                self.carregar_fila()
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    #  LÓGICA: HISTÓRICO E FECHAMENTO EXCEL 
    def mudar_filtro_historico(self, escolha):
        self.carregar_historico()

    def carregar_historico(self):
        mapa = {"Hoje": "hoje", "Últimos 7 dias": "7dias", "Últimos 30 dias": "30dias", "Tudo": "tudo"}
        filtro_str = self.view.combo_filtro.get()
        filtro_api = mapa.get(filtro_str, "hoje")

        self.view.iniciar_carregamento()
        def task():
            try:
                historico = self.api.listar_historico(filtro_api)
                self.view.after(0, lambda: self.view.desenhar_historico(historico))
            except: pass
            finally: 
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

    def exportar_excel(self):
        mapa = {"Hoje": "hoje", "Últimos 7 dias": "7dias", "Últimos 30 dias": "30dias", "Tudo": "tudo"}
        filtro_str = self.view.combo_filtro.get()
        filtro_api = mapa.get(filtro_str, "hoje")
        
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Planilha Excel CSV", "*.csv")], title="Salvar Fechamento")
        if not caminho: return 
        
        self.view.iniciar_carregamento()
        def task():
            try:
                dados = self.api.listar_historico(filtro_api)
                with open(caminho, mode='w', newline='', encoding='utf-8-sig') as arquivo:
                    escritor = csv.writer(arquivo, delimiter=';')
                    escritor.writerow(['ID_Pedido', 'Cliente', 'Telefone', 'Endereco', 'Mercadoria', 'Status', 'Data e Hora'])
                    for d in dados:
                        escritor.writerow([d['id'], d['nome_cliente'], d['telefone'], d['endereco'], d['conteudo'], d['status'], d.get('data_formatada', '')])
            except Exception as e:
                print("Erro ao gerar Excel:", e)
            finally:
                self.view.after(0, self.view.parar_carregamento)
        threading.Thread(target=task).start()

#  INÍCIO DO PROGRAMA 
if __name__ == "__main__":
    app = FarmaciaController()
    app.iniciar()