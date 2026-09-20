# Histórico de versões

## 1.2.0 — 19/09/2026

### Release final

- Desktop e API consolidados na versão final 1.2.0.
- Migração de aferições renomeada e fechada como `migration_final_1_2_0.sql`.
- Guia único de implantação com backup, atualização, validação e rollback.
- URL da API passou a ser editável em `config.ini`, sem recompilar o executável.
- `config.ini` incluído automaticamente no pacote PyInstaller.
- Testes adicionados para a versão da API, publicação das rotas de aferição e configuração externa da URL.
- Mantidas as correções de estabilidade da aferição e da troca para o Histórico entregues na 1.1.1.
- Hotfix final no backend: escape dos formatos `DATE_FORMAT` em consultas parametrizadas do PyMySQL, corrigindo o erro 500 ao registrar aferições e prevenindo a mesma falha em consultas de histórico.

## 1.1.1 — 04/09/2026

### Correções

- Diagnóstico confirmado para o erro `404 Not Found`: API ativa sem as rotas de aferição.
- Mensagem genérica substituída por orientação para atualizar API e migration.
- Registro e impressão bloqueados até a integração de aferição responder corretamente.
- Healthcheck ampliado para informar disponibilidade da tabela `afericoes_pressao`.
- Resposta HTTP 503 específica quando a API existe, mas a tabela ainda não foi criada.
- Renderização progressiva removida da tela Histórico para eliminar cintilação na troca de aba.
- Histórico usa indicador local e mantém o layout estável durante a atualização.
- Barra global de carregamento passou a ser sobreposta, sem deslocar o conteúdo.
- Instruções de implantação alinhadas à stack Docker em `/DATA/Motherbase`.

## 1.1.0 — 04/09/2026

### Interface

- Navegação lateral com atalhos F1–F5 e status do servidor.
- Paleta dark + verde refinada, tipografia Segoe UI e melhor hierarquia visual.
- Contadores nas listas e estados vazios preservados.
- Carrinho da entrega convertido em lista vertical rolável.
- Data e hora incluídas nos cartões de entregas pendentes.

### Correções

- Impressão e detecção de impressoras não bloqueiam mais a thread da interface.
- Bloqueio temporário dos botões evita entregas, cadastros e aferições duplicadas.
- Tokens de requisição impedem que respostas antigas sobrescrevam filtros recentes.
- A pesquisa ativa de clientes é preservada após atualizar a lista.
- Relatórios PDF e CSV deixam de ser truncados em 100 registros.
- Mensagens de erro do FastAPI passam a exibir detalhes de validação.
- Limites dos campos passam a respeitar o schema do MariaDB.
- Aferições recebem as mesmas regras no desktop e no backend.
- O status de conexão não é marcado como offline quando a API responde com erro HTTP.
- O comprovante passa a selecionar PC850 e verifica escrita parcial no spooler.
- O empacotamento passa a incluir os temas e recursos internos do CustomTkinter.

### Validação

- Compilação de todos os módulos Python concluída.
- Regras puras do backend, formatação, parâmetros de exportação e geração do comprovante validadas.
- Testes unitários adicionados em `tests/`.

### Pendente no ambiente real

- Teste físico da impressora Epson no Windows.
- Teste integrado com a API e o MariaDB de produção.
- Geração e validação final do executável PyInstaller em Windows.
