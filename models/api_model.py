import requests

URL_API = "http://100.110.221.91:8000"

class FarmaciaAPI:
    @staticmethod
    def buscar_cliente(telefone):
        res = requests.get(f"{URL_API}/api/clientes/{telefone}", timeout=5)
        return res.json() if res.status_code == 200 else None

    @staticmethod
    def salvar_cliente(dados):
        res = requests.post(f"{URL_API}/api/clientes", json=dados, timeout=5)
        return res.status_code == 200

    @staticmethod
    def listar_clientes():
        res = requests.get(f"{URL_API}/api/clientes", timeout=5)
        return res.json() if res.status_code == 200 else []

    @staticmethod
    def excluir_cliente(telefone):
        res = requests.delete(f"{URL_API}/api/clientes/{telefone}", timeout=5)
        return res.status_code == 200

    @staticmethod
    def lancar_entrega(cliente_busca, conteudo):
        dados = {"cliente_busca": cliente_busca, "conteudo": conteudo}
        res = requests.post(f"{URL_API}/api/entregas", json=dados, timeout=5)
        return res.status_code == 200

    @staticmethod
    def listar_pendentes():
        res = requests.get(f"{URL_API}/api/entregas/pendentes", timeout=5)
        return res.json() if res.status_code == 200 else []

    @staticmethod
    def alterar_status_entrega(id_entrega, acao):
        res = requests.put(f"{URL_API}/api/entregas/{id_entrega}/{acao}", timeout=5)
        return res.status_code == 200

    @staticmethod
    def editar_conteudo_entrega(id_entrega, novo_conteudo):
        dados = {"conteudo": novo_conteudo}
        res = requests.put(f"{URL_API}/api/entregas/{id_entrega}/editar", json=dados, timeout=5)
        return res.status_code == 200

    @staticmethod
    def listar_historico(filtro="tudo"):
        res = requests.get(f"{URL_API}/api/entregas/historico?filtro={filtro}", timeout=5)
        return res.json() if res.status_code == 200 else []