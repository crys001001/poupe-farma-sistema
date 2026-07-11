Sistema Integrado de Logística 
Sistema desktop completo desenvolvido para gerenciamento de clientes e controle de entregas (despacho de motoboys) de uma farmácia. O projeto utiliza uma arquitetura moderna dividida entre um aplicativo front-end no Windows e uma API back-end hospedada em um servidor Linux.

Funcionalidades Principais
Gestão de Clientes: Cadastro rápido, edição, exclusão e log de registros.

Controle de Fila: Lançamento de entregas, atualização de status em tempo real (Pendente, Entregue, Cancelado).

Integração WhatsApp: Abertura direta de conversas com clientes com apenas um clique.

Relatórios: Exportação de histórico de entregas e log de cadastros em formatos PDF e Excel (CSV).

Resiliência: Tratamento de erros de conexão com alertas visuais (Pop-ups) caso o servidor fique offline ou inacessível.

Tecnologias Utilizadas
Front-end (Desktop): Python, CustomTkinter (UI Moderna), PyInstaller (Empacotamento)

Back-end (API): FastAPI, Uvicorn, Python, Python-dotenv

Banco de Dados: MySQL hospedado via CasaOS

Rede: Tailscale (VPN Mesh para comunicação segura entre a farmácia e o servidor)

Arquitetura: MVC (Model-View-Controller) modularizada.

Como a Arquitetura Funciona
O sistema foi desenhado para ser resiliente e operar em rede através dos seguintes componentes:

1. O Servidor (CasaOS + MySQL)
O "cérebro" dos dados fica em um servidor Linux rodando CasaOS. Nele, foi instanciado um contêiner MySQL que guarda a base de dados de clientes e o histórico de entregas. A vantagem dessa abordagem é que os dados ficam centralizados e seguros, separados do computador do balcão da farmácia.

2. A API (FastAPI) & Segurança
Para que o aplicativo da farmácia não acesse o banco de dados diretamente (o que seria uma falha de segurança), construímos uma API RESTful usando FastAPI no servidor Linux. Ela recebe os pedidos do aplicativo, processa e insere no banco de dados.

Segurança de Credenciais: As senhas e os usuários do banco de dados não ficam expostos no código da API. Eles são lidos de forma blindada através de variáveis de ambiente (arquivo oculto .env).

Rodando a API Infinitamente:
Para garantir que a API não caia se o terminal for fechado, ela foi configurada como um serviço nativo do sistema (systemd).

Arquivo de serviço criado em: /etc/systemd/system/apifarmacia.service

Comandos utilizados para manter sempre online:

Bash
sudo systemctl enable apifarmacia
sudo systemctl start apifarmacia
Isso garante que, mesmo que o servidor Linux reinicie por falta de energia, a API volte a funcionar automaticamente no boot.

3. O Aplicativo Desktop
O front-end foi construído em arquitetura MVC (Model-View-Controller), separando a interface gráfica da lógica de negócio de forma modular (telas fatiadas em arquivos independentes).

O aplicativo se conecta à API através de um IP fixo fornecido pelo Tailscale, criando um túnel seguro pela internet. O código foi compilado através do PyInstaller no modo otimizado (--onedir), gerando uma pasta contendo o executável principal e suas DLLs separadas. Isso permite que o programa rode de forma extremamente rápida e leve em computadores mais antigos (como um Pentium) sem necessidade de instalar o Python localmente.

👨‍💻 Desenvolvedor Líder
 Crystyan Vicente Gomes de Arruda
(Análise e Desenvolvimento de Sistemas - ADS)