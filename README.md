# Sistema Integrado de Clientes e Entregas

Sistema desktop desenvolvido para cadastro de clientes, controle de entregas e apoio ao atendimento de uma farmácia.

O projeto utiliza uma arquitetura cliente-servidor. O aplicativo desktop funciona no Windows e se comunica com uma API FastAPI hospedada em um servidor Linux. Os dados ficam armazenados em um banco MariaDB/MySQL no servidor.

## Versão

**Versão estável atual: 0.9.1**

Esta versão representa o congelamento inicial do sistema para uso interno.

Depois do congelamento, novas alterações devem ser realizadas primeiro em ambiente de teste e publicadas por meio de uma nova versão.

---

## Funcionalidades

### Gestão de clientes

- Cadastro de clientes por telefone;
- nome e telefone obrigatórios;
- endereço completamente opcional;
- busca por nome ou telefone;
- edição de dados;
- exclusão de clientes;
- registro da data de cadastro;
- histórico de cadastros;
- campo para registrar produtos que faltaram na loja.

### Controle de entregas

- Criação de entregas;
- inclusão de vários produtos em um pedido;
- fila de pedidos pendentes;
- edição do conteúdo da entrega;
- finalização como entregue;
- cancelamento de pedidos;
- histórico de entregas;
- filtros por hoje, últimos 7 dias, últimos 30 dias ou todo o período.

### Integração com WhatsApp

O sistema pode abrir diretamente uma conversa com o cliente no WhatsApp utilizando o telefone cadastrado.

### Relatórios

- Exportação do histórico em PDF;
- exportação em CSV;
- relatório de entregas;
- relatório de cadastros.

### Monitoramento da API

A interface exibe o estado da conexão com o servidor:

- Servidor online;
- Servidor offline;
- alertas em caso de timeout ou falha de conexão.

---

## Tecnologias utilizadas

### Aplicativo desktop

- Python;
- CustomTkinter;
- Requests;
- Pillow;
- PyInstaller;
- arquitetura MVC.

### API

- Python;
- FastAPI;
- Uvicorn;
- PyMySQL;
- Pydantic;
- Python-dotenv.

### Infraestrutura

- servidor Linux;
- CasaOS;
- MariaDB/MySQL em contêiner;
- systemd;
- Tailscale.

---

## Arquitetura

O sistema é dividido em três partes principais:

```text
Aplicativo Windows
        |
        | Requisições HTTP pela rede privada
        v
API FastAPI no servidor Linux
        |
        | Consultas SQL
        v
Banco MariaDB/MySQL

O aplicativo desktop não acessa o banco diretamente.

Toda operação de cadastro, edição, consulta ou entrega passa pela API.

Isso evita que as credenciais do banco sejam armazenadas no computador do balcão.

Estrutura do projeto
.
├── assets/
│   └── final_image.png
│
├── backend/
│   ├── apifarmacia.service
│   ├── requirements.txt
│   └── servidor.py
│
├── database/
│   └── schema.sql
│
├── models/
│   ├── __init__.py
│   └── api_model.py
│
├── view/
│   ├── __init__.py
│   ├── aba_cadastro.py
│   ├── aba_clientes.py
│   ├── aba_entregas.py
│   ├── aba_historico.py
│   ├── config.py
│   └── tela_principal.py
│
├── .gitignore
├── main.py
├── PoupeFarma.spec
└── README.md

As pastas abaixo são geradas automaticamente e não devem ser enviadas ao GitHub:

__pycache__/
build/
dist/
Configuração do banco de dados

O arquivo de criação do banco está em:

database/schema.sql

Para criar uma nova instalação:

mysql -u root -p < database/schema.sql

O banco padrão utilizado é:

farmacia

As tabelas principais são:

clientes
entregas
Campos obrigatórios do cliente
telefone;
nome.
Campos opcionais
endereço;
número;
bairro;
complemento;
produto desejado.
Configuração da API

Entre na pasta do backend:

cd backend

Instale as dependências:

python3 -m pip install -r requirements.txt

Crie um arquivo .env no servidor:

DB_HOST=ENDERECO_DO_BANCO
DB_PORT=3306
DB_USER=USUARIO_DO_BANCO
DB_PASSWORD=SENHA_DO_BANCO
DB_NAME=farmacia

O arquivo .env contém informações privadas e não deve ser enviado ao GitHub.

Execute a API manualmente:

python3 -m uvicorn servidor:app --host 0.0.0.0 --port 8000

Teste a saúde da API:

curl http://127.0.0.1:8000/api/saude

Resposta esperada:

{
  "status": "ok",
  "banco": "conectado",
  "versao": "0.9.1"
}
Serviço systemd

A API de produção é executada como serviço do Linux.

Arquivo:

/etc/systemd/system/apifarmacia.service

Configuração utilizada:

[Unit]
Description=API Poupe Farma - FastAPI
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=drajen
WorkingDirectory=/home/drajen/api_farmacia
ExecStart=/usr/bin/python3 -m uvicorn servidor:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

Instalar ou atualizar o serviço:

sudo cp apifarmacia.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable apifarmacia.service
sudo systemctl restart apifarmacia.service

Verificar o estado:

sudo systemctl status apifarmacia.service

Consultar os logs:

sudo journalctl -u apifarmacia.service -n 100 --no-pager
Aplicativo desktop

O aplicativo principal é iniciado pelo arquivo:

main.py

Execução:

python main.py

A URL da API pode ser definida por variável de ambiente:

POUPE_FARMA_API_URL=http://ENDERECO_DO_SERVIDOR:8000

Na operação normal, o computador da farmácia e o servidor devem estar conectados à mesma rede privada do Tailscale.

Geração do executável

O projeto utiliza PyInstaller para gerar uma versão executável para Windows.

Execute o arquivo .spec oficial do projeto:

python -m PyInstaller PoupeFarma.spec

Os arquivos gerados aparecerão nas pastas:

build/
dist/

Essas pastas não fazem parte do código-fonte e são ignoradas pelo Git.

Segurança

As credenciais do banco são carregadas por variáveis de ambiente e não ficam gravadas diretamente no código.

Arquivos que nunca devem ser enviados ao GitHub:

.env
backups do banco
arquivos com senhas
logs de produção
chaves privadas
certificados privados

A API deve permanecer acessível apenas por rede privada, firewall ou Tailscale.

A versão 0.9.1 ainda não possui autenticação individual por usuário. Por esse motivo, a porta da API não deve ser exposta diretamente à internet.

Privacidade e LGPD

O sistema deve armazenar somente dados necessários para o atendimento e para a entrega.

O endereço é opcional porque alguns clientes utilizam o cadastro apenas para atendimento pelo WhatsApp.

Boas práticas recomendadas:

limitar o acesso aos dados;
utilizar senhas fortes;
manter backups protegidos;
não publicar dumps do banco;
remover registros quando houver solicitação válida;
evitar armazenar informações desnecessárias;
registrar quem possui acesso ao sistema.

O uso deste projeto, isoladamente, não garante conformidade automática com a LGPD. A conformidade também depende dos processos da empresa e da forma como os dados são utilizados.

Backup

Os backups do banco devem ser armazenados fora do repositório Git.

Exemplo:

mysqldump -u USUARIO -p farmacia > farmacia_backup.sql

O arquivo gerado não deve ser enviado ao GitHub.

Antes de publicar uma nova versão, recomenda-se testar:

criação do backup;
validação do arquivo;
restauração em banco de teste;
comparação da quantidade de registros;
teste da API no ambiente restaurado.
Fluxo de atualização

O projeto possui dois ambientes:

Produção
/home/drajen/api_farmacia
Porta 8000
Banco farmacia
Teste
/home/drajen/api_farmacia_teste
Porta 8002
Banco farmacia_teste

Toda alteração deve seguir a ordem:

fazer backup;
alterar o ambiente de teste;
validar sintaxe;
testar as rotas;
testar o aplicativo;
copiar a alteração para produção;
reiniciar o serviço;
validar novamente;
criar uma nova versão no Git.
Congelamento da versão 0.9.1

A versão 0.9.1 inclui:

API estabilizada;
conexões com o banco fechadas corretamente;
tratamento de rollback;
endpoint de saúde;
endereço opcional;
validação das ações de entrega;
correção do filtro de horário UTC-3;
tratamento de erros no aplicativo;
status visual do servidor;
interface reorganizada;
integração com WhatsApp;
exportação em PDF e CSV;
ambiente de teste separado da produção.

Depois da criação da tag v0.9.1, esta versão deve receber apenas correções críticas.

Novas funcionalidades devem utilizar uma nova versão.

Desenvolvedor

Crystyan Vicente Gomes de Arruda

Análise e Desenvolvimento de Sistemas — ADS

GitHub:

https://github.com/crys001001

LinkedIn:

https://www.linkedin.com/in/crystyan-vicente-92723a26b/