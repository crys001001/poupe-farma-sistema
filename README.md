# Sistema Integrado de Logística 

Sistema desktop completo desenvolvido para gerenciamento de clientes e controle de entregas (despacho de motoboys) de uma farmácia. O projeto utiliza uma arquitetura moderna dividida entre um aplicativo front-end no Windows e uma API back-end hospedada em um servidor Linux.

## Tecnologias Utilizadas

*   **Front-end (Desktop):** Python, CustomTkinter (UI Moderna), PyInstaller (Empacotamento)
*   **Back-end (API):** FastAPI, Uvicorn, Python
*   **Banco de Dados:** MySQL hospedado via CasaOS
*   **Rede:** Tailscale (VPN Mesh para comunicação segura entre a farmácia e o servidor)
*   **Arquitetura:** MVC (Model-View-Controller)

---

## Como a Arquitetura Funciona

O sistema foi desenhado para ser resiliente e operar em rede através dos seguintes componentes:

### 1. O Servidor (CasaOS + MySQL)
O "cérebro" dos dados fica em um servidor Linux rodando CasaOS. Nele, foi instanciado um contêiner MySQL que guarda a base de dados de clientes e o histórico de entregas. A vantagem dessa abordagem é que os dados ficam centralizados e seguros, separados do computador do balcão da farmácia.

### 2. A API (FastAPI)
Para que o aplicativo da farmácia não acesse o banco de dados diretamente (o que seria uma falha de segurança), construímos uma API RESTful usando FastAPI no servidor Linux. Ela recebe os pedidos do aplicativo, processa e insere no banco de dados.

Rodando a API Infinitamente:
Para garantir que a API não caia se o terminal for fechado, ela foi configurada como um serviço nativo do sistema (`systemd`).
*   Arquivo de serviço criado em: `/etc/systemd/system/apifarmacia.service`
*   Comandos utilizados para manter sempre online:
    ```bash
    sudo systemctl enable apifarmacia
    sudo systemctl start apifarmacia
    ```
Isso garante que, mesmo que o servidor Linux reinicie por falta de energia, a API volte a funcionar automaticamente no boot.

### 3. O Aplicativo Desktop
O front-end foi construído em arquitetura MVC (Model-View-Controller), separando a interface gráfica da lógica de negócio. 
O aplicativo se conecta à API através de um IP fixo fornecido pelo Tailscale, criando um túnel seguro pela internet. O código foi compilado em um único arquivo `.exe` autossuficiente, permitindo que rode em computadores mais antigos (como um Pentium) sem necessidade de instalar o Python localmente.

---

## 👨‍💻 Desenvolvedor Líder
     Crystyan Vicente Gomes de Arruda
(Análise e Desenvolvimento de Sistemas - ADS)