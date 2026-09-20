# Sistema de Cadastro 1.2.0

Aplicação desktop para operação de balcão, desenvolvida em Python e CustomTkinter, com API FastAPI e banco MariaDB/MySQL.

O sistema reúne cadastro de clientes, controle de entregas, histórico, integração com WhatsApp e registro de aferições de pressão com comprovante térmico. A aferição registra apenas os valores informados pelo operador e não realiza diagnóstico médico.

## Funcionalidades

- cadastro, consulta, edição e exclusão de clientes;
- endereço opcional;
- controle de entregas e pedidos pendentes;
- histórico com filtros e exportação em PDF/CSV;
- abertura de conversa no WhatsApp;
- registro de pressão arterial e batimentos;
- histórico diário de aferições e total do serviço;
- impressão térmica via spooler do Windows/ESC-POS;
- status da API exibido no aplicativo;
- atalhos `F1` a `F5` para navegação rápida.

## Arquitetura

```text
Aplicativo Windows
        |
        | HTTP em rede privada
        v
API FastAPI
        |
        v
MariaDB / MySQL
```

O aplicativo desktop não acessa o banco diretamente. As credenciais do banco permanecem somente no servidor.

## Tecnologias

- Python
- CustomTkinter
- FastAPI
- Uvicorn
- PyMySQL
- MariaDB/MySQL
- Requests
- FPDF
- PyInstaller
- pywin32 para impressão no Windows

## Estrutura

```text
backend/      API FastAPI
database/     schema e migration
models/       comunicação com API e impressão
view/         interface gráfica
tests/        testes automatizados
main.py       ponto de entrada do desktop
```

## Configuração do aplicativo

Copie o exemplo:

```powershell
Copy-Item config.example.ini config.ini
```

Depois edite `config.ini`:

```ini
[api]
url = http://SEU_SERVIDOR:8000
```

`config.ini` é local e está ignorado pelo Git para não publicar detalhes da infraestrutura.

A variável `POUPE_FARMA_API_URL` continua suportada por compatibilidade e, quando definida, tem prioridade sobre o arquivo INI.

## Desenvolvimento e testes

```powershell
python -m pip install -r requirements.txt
python -m pip install -r backend/requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q .
```

## Banco de dados

Para uma instalação nova, use:

```text
database/schema.sql
```

Para uma instalação existente anterior ao módulo de aferição, aplique:

```text
database/migration_final_1_2_0.sql
```

Nunca publique dumps reais do banco, arquivos `.env`, credenciais, chaves privadas ou dados de clientes.

## Gerar o executável Windows

Crie primeiro o `config.ini` local e execute:

```powershell
python -m PyInstaller --clean --noconfirm SistemaCadastro.spec
```

O executável será gerado em `dist/SistemaCadastro/`.

## Versão

**1.2.0**

Principais pontos desta versão:

- interface compacta para uso de balcão;
- navegação por `F1` a `F5`;
- carregamento sob demanda das telas;
- módulo de aferição com persistência no banco;
- comprovante térmico;
- correções de formatação de data nas consultas parametrizadas do PyMySQL;
- API com endpoint de saúde e informação de versão.

## Desenvolvedor

**Crystyan Vicente Gomes de Arruda**  
Análise e Desenvolvimento de Sistemas — ADS
