# DivideAI - API REST

![DivideAI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

Endpoint de produção: **https://divide-ai-api-repe.onrender.com/docs**

Henrique Pizzoni/Back-end (Dev, QA e DevOps) e Scrum Master 

Davi Rosim/Back-end (Dev e QA) 

João Pedro Martins/Back-end (Tech-lead, Dev e QA)  

Tiago Andrade/Front-end (Dev e QA), Scrum Master 

Juliano Aleixo/Front end (Dev, Tech Lead, QA e DevOps) 

Leonardo Ferreira/Front end (Dev e QA) 

---

## 📋 Descrição da Aplicação

**DivideAI** é uma API REST para gerenciamento de despesas compartilhadas em grupos. A aplicação permite que usuários criem grupos, registrem despesas coletivas, dividam valores entre participantes de forma igualitária ou heterogênea, façam upload de comprovantes e realizem confirmações de pagamentos de forma organizada e transparente.

### Principais Funcionalidades:

- **Autenticação e Controle de Usuários**: Registro, login com JWT e gerenciamento de perfis
- **Gerenciamento de Grupos**: Criar grupos, adicionar/remover membros, atualizar informações
- **Sistema de Dívidas**: Registrar despesas coletivas com divisão automática de valores
- **Divisão Inteligente**: Dois modos de divisão:
  - **Homogênea**: Divide automaticamente em partes iguais
  - **Heterogênea**: Permite definir porcentagens customizadas por participante
- **Comprovantes Digitais**: Upload de comprovantes com armazenamento seguro em Cloudflare R2
- **Confirmação de Pagamentos**: Sistema de validação de pagamentos pelo criador da dívida
- **Rastreamento de Balances**: Cálculo automático de quem deve a quem dentro de cada grupo

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Função |
| --- | --- | --- |
| **Python** | 3.11+ | Linguagem principal |
| **FastAPI** | Latest | Framework web async com geração automática de OpenAPI docs |
| **SQLAlchemy** | 2.0+ | ORM para mapeamento de tabelas e queries |
| **Pydantic** | v2 | Validação robusta de dados de entrada e saída |
| **PostgreSQL** | 13+ | Banco de dados relacional |
| **Alembic** | Latest | Gerenciamento de migrations de banco de dados |
| **bcrypt** | Latest | Hash seguro de senhas |
| **PyJWT** | Latest | Geração e validação de tokens JWT |
| **boto3** | Latest | Integração com Cloudflare R2 (S3-compatible) |
| **pytest** | Latest | Framework de testes automatizados |
| **Docker** | Latest | Containerização da aplicação |
| **uv** | Latest | Gerenciador de pacotes e ambientes virtuais |

---

## 🚀 Como Acessar Online e Rodar Local

### Pré-requisitos

- Python 3.11+
- PostgreSQL 13+
- Docker e Docker Compose (opcional)
- [uv](https://github.com/astral-sh/uv) - gerenciador de pacotes

### Rodar Local

```bash
# 1. Clonar o repositório
git clone https://github.com/C14-INATEL/divide-ai-api.git
cd divide-ai-api

# 2. Instalar dependências
uv sync

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 4. Criar banco de dados (se ainda não existir)
# Certifique-se de que PostgreSQL está rodando

# 5. Aplicar migrations
uv run alembic upgrade head

# 6. Rodar o servidor
python run.py
```

O servidor estará disponível em: **http://localhost:8000**

Documentação interativa (Swagger): **http://localhost:8000/docs**

---

## 🧪 Como Testar

### Executar Todos os Testes

```bash
# Com coverage report
pytest -v

# Apenas testes unitários
pytest tests/unit/ -v

# Apenas testes de integração
pytest tests/integration/ -v

# Testes de um arquivo específico
pytest tests/unit/services/test_debt_service.py -v
```

### Testes Disponíveis

- **Unit Tests**: Testes de schemas, services e utilitários
- **Integration Tests**: Testes de fluxos completos (ex: cascata de deleção de grupos)

### Exemplo de Requisição para Testar Manualmente

```bash
# 1. Criar um usuário
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "password": "senha123"
  }'

# 2. Fazer login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "password": "senha123"
  }'

# 3. Usar o token retornado nas próximas requisições
curl -X GET http://localhost:8000/groups/ \
  -H "Authorization: Bearer <seu_token_jwt>"
```

---

## 📁 Esquema de Pastas

```
divide-ai-api/
├── app/                          # Código principal da aplicação
│   ├── __init__.py
│   ├── main.py                   # Configuração principal do FastAPI
│   ├── config.py                 # Variáveis de ambiente (pydantic-settings)
│   ├── database.py               # Configuração de banco de dados
│   ├── exceptions.py             # Exceções customizadas
│   │
│   ├── models/                   # Camada ORM (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py               # Model User
│   │   ├── group.py              # Model Group
│   │   ├── group_member.py       # Model GroupMember (relação N:M)
│   │   ├── debt.py               # Model Debt
│   │   ├── debt_participant.py   # Model DebtParticipant
│   │   └── enums/                # Enumerações
│   │       ├── debt_split_type.py    # Enum para HOMOGENEA/HETEROGENEA
│   │       ├── participant_status.py # Enum para status de participante
│   │       └── pix_key_type.py      # Enum para tipos de chave Pix
│   │
│   ├── schemas/                  # Camada de Contrato (Pydantic)
│   │   ├── user.py               # Schemas: UserCreate, UserResponse, etc.
│   │   ├── group.py              # Schemas: GroupCreate, GroupResponse, etc.
│   │   └── debt.py               # Schemas: DebtCreate, DebtResponse, etc.
│   │
│   ├── repositories/             # Camada de Acesso a Dados
│   │   ├── user_repository.py    # Queries SQLAlchemy para User
│   │   ├── group_repository.py   # Queries SQLAlchemy para Group
│   │   └── debt_repository.py    # Queries SQLAlchemy para Debt
│   │
│   ├── services/                 # Camada de Lógica de Negócio
│   │   ├── user_service.py       # Regras de usuário (auth, validação)
│   │   ├── group_service.py      # Regras de grupo (CRUD, membros)
│   │   └── debt_service.py       # Regras de dívida (divisão, confirmação)
│   │
│   ├── routers/                  # Camada HTTP (FastAPI Routers)
│   │   ├── auth.py               # POST /auth/login
│   │   ├── users.py              # CRUD /users
│   │   ├── groups.py             # CRUD /groups + membros
│   │   └── debts.py              # CRUD /debts + comprovantes
│   │
│   ├── utils/                    # Utilitários
│   │   ├── api_errors.py         # Funções de erro customizado
│   │   ├── dependencies.py       # Dependências FastAPI (get_current_user)
│   │   ├── jwt.py                # Geração e validação de JWT
│   │   ├── security.py           # Hash com bcrypt
│   │   ├── storage.py            # Integração Cloudflare R2
│   │   └── validators.py         # Validadores customizados
│   │
│   └── validators/               # Validadores de negócio
│       ├── group_validators.py
│       └── user_validators.py
│
├── migrations/                   # Migrations Alembic
│   ├── env.py                    # Configuração Alembic
│   ├── script.py.mako
│   └── versions/                 # Scripts de migration
│       ├── 0001_add_debts.py
│       ├── 0002_add_group_description.py
│       └── 0003_rename_proof_url.py
│
├── tests/                        # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py               # Configuração compartilhada pytest
│   ├── unit/                     # Testes unitários
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   └── integration/              # Testes de integração
│       └── test_group_delete_cascade.py
│
├── docs/                         # Documentação
│   └── debt_feature.md           # Detalhes técnicos da feature de dívidas
│
├── jenkins/                      # Configuração Jenkins
│   ├── casc.yml
│   ├── Dockerfile
│   └── plugins.txt
│
├── alembic.ini                   # Configuração Alembic
├── docker-compose.yml            # Compose para API + PostgreSQL
├── Dockerfile                    # Image da aplicação
├── Jenkinsfile                   # Pipeline de CI/CD
├── pyproject.toml                # Dependências e configurações PEP 621
├── run.py                        # Script para rodar o servidor
├── README.md                     # Este arquivo
└── pipeline_instructions.md      # Instruções do pipeline Jenkins

```

---

## 📡 Endpoints da API (Backend)

### Autenticação

| Método | Endpoint | Descrição |
| --- | --- | --- |
| POST | `/auth/login` | Fazer login com email e senha, retorna JWT |

### Usuários

| Método | Endpoint | Descrição |
| --- | --- | --- |
| GET | `/users/` | Listar usuários com filtro por nome (requer auth) |
| POST | `/users/` | Registrar novo usuário |
| GET | `/users/{user_id}` | Obter dados de um usuário (requer auth) |
| PATCH | `/users/{user_id}` | Atualizar perfil do usuário (requer auth) |
| PATCH | `/users/{user_id}/password` | Alterar senha (requer auth) |

### Grupos

| Método | Endpoint | Descrição |
| --- | --- | --- |
| POST | `/groups/` | Criar novo grupo (requer auth) |
| GET | `/groups/` | Listar grupos do usuário (requer auth) |
| GET | `/groups/{group_id}` | Obter detalhes de um grupo (requer auth) |
| PATCH | `/groups/{group_id}` | Atualizar grupo (apenas criador, requer auth) |
| DELETE | `/groups/{group_id}` | Deletar grupo (apenas criador, requer auth) |
| POST | `/groups/{group_id}/members` | Adicionar membro ao grupo (requer auth) |
| DELETE | `/groups/{group_id}/members/{user_id}` | Remover membro do grupo (requer auth) |

### Dívidas

| Método | Endpoint | Descrição |
| --- | --- | --- |
| POST | `/debts/` | Criar nova dívida (requer auth) |
| GET | `/debts/` | Listar dívidas de um grupo (query param: `group_id`, requer auth) |
| GET | `/debts/{debt_id}` | Obter detalhes de uma dívida (requer auth) |
| PATCH | `/debts/{debt_id}` | Atualizar dívida (apenas criador, requer auth) |
| DELETE | `/debts/{debt_id}` | Deletar dívida (apenas criador e sem participantes, requer auth) |
| POST | `/debts/{debt_id}/participants/me/proof` | Upload comprovante pelo participante (file upload, requer auth) |
| POST | `/debts/{debt_id}/participants/{user_id}/confirm` | Confirmar pagamento (apenas criador, requer auth) |
| GET | `/debts/{debt_id}/participants/{user_id}/proof` | Download comprovante (requer auth) |

### Resposta Padrão

Toda resposta segue este formato:

```json
{
  "id": "uuid",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  ...dados específicos do endpoint
}
```

Em caso de erro:

```json
{
  "error": {
    "error_code": "error_type",
    "message": "Descrição do erro"
  }
}
```

---

## 🌍 Exemplo de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# === Banco de Dados ===
DATABASE_URL=postgresql://user:password@localhost:5432/divide_ai

# === Aplicação ===
DEBUG=false
SECRET_KEY=sua_chave_secreta_muito_segura_aqui

# === Cloudflare R2 (Armazenamento de Comprovantes) ===
R2_BUCKET=divide-ai-bucket
R2_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://pub-xxxx.r2.dev
R2_ACCESS_KEY_ID=sua_access_key_aqui
R2_SECRET_ACCESS_KEY=sua_secret_access_key_aqui
MAX_UPLOAD_SIZE_BYTES=5242880

# === Autenticação ===
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Descrição dos campos:**

- `DATABASE_URL`: String de conexão com PostgreSQL
- `DEBUG`: Se `true`, ativa modo debug; se `false`, produção
- `SECRET_KEY`: Chave para assinatura de JWT (use um valor aleatório longo e seguro)
- `R2_*`: Credenciais da Cloudflare R2 para upload de arquivos
- `MAX_UPLOAD_SIZE_BYTES`: Tamanho máximo de upload (padrão: 5 MB = 5242880 bytes)
- `JWT_*`: Configurações de token JWT

---

## ✅ Critérios Atendidos

Este projeto atende aos seguintes critérios e requisitos:

### ✔️ Arquitetura e Estrutura

- [x] **Arquitetura em Camadas**: Implementação correta (Routers → Services → Repositories → Database)
- [x] **Separação de Responsabilidades**: Cada camada tem função específica e clara
- [x] **Modularização**: Código organizado em pacotes bem definidos
- [x] **Documentação**: README completo e documentação técnica

### ✔️ Banco de Dados

- [x] **PostgreSQL 13+**: Banco relacional com suporte completo
- [x] **SQLAlchemy 2.0 ORM**: Mapeamento objeto-relacional moderno
- [x] **Migrations com Alembic**: Versionamento de schema de banco
- [x] **Tipos de Dados Corretos**: UUID para IDs, Numeric(12,2) para valores monetários
- [x] **Timestamps Automáticos**: created_at e updated_at em todas as tabelas
- [x] **Relacionamentos Definidos**: N:M com GroupMember, Foreign Keys corretas

### ✔️ API REST

- [x] **FastAPI Moderno**: Framework async e geração automática de OpenAPI docs
- [x] **Endpoints RESTful**: CRUD completo com verbos HTTP corretos
- [x] **Validação com Pydantic v2**: Schemas de entrada e saída validados
- [x] **Tratamento de Erros**: Exceções customizadas com status codes apropriados
- [x] **Autenticação com JWT**: Login e proteção de rotas
- [x] **Documentação Automática**: Swagger UI em `/docs`

### ✔️ Autenticação e Segurança

- [x] **Hash de Senhas com bcrypt**: Senhas nunca armazenadas em plain text
- [x] **JWT para Autenticação**: Tokens com expiração configurável
- [x] **Validação de Autorização**: Verificação de permissões por endpoint
- [x] **CORS Configurado**: Para requisições cross-origin seguras

### ✔️ Feature de Dívidas (Debts)

- [x] **Criação de Dívidas**: Com suporte a participantes parciais ou todos do grupo
- [x] **Divisão Homogênea**: Divisão automática em partes iguais
- [x] **Divisão Heterogênea**: Divisão customizada com porcentagens
- [x] **Validação de Porcentagens**: Soma deve ser 100% (com precisão Decimal)
- [x] **Upload de Comprovantes**: Integração com Cloudflare R2
- [x] **Confirmação de Pagamentos**: Fluxo de validação pelo criador
- [x] **Limitação de Arquivo**: Máximo 5 MB com tipos permitidos (JPG, PNG, PDF)
- [x] **Rastreamento de Status**: Pendente → Pago → Confirmado
- [x] **Prevenção de Remoção**: Não permite deletar dívida com participantes

### ✔️ Testes Automatizados

- [x] **Testes Unitários**: Services, schemas, validadores
- [x] **Testes de Integração**: Fluxos completos
- [x] **pytest**: Framework padrão com coverage
- [x] **Fixtures**: Conftest com dados de teste
- [x] **Mock de Repositórios**: Testes sem tocar no banco
- [x] **Assertions Corretas**: Decimal para dinheiro, UUID para IDs

### ✔️ CI/CD e DevOps

- [x] **Docker**: Containerização da aplicação
- [x] **Docker Compose**: Orquestração local (API + PostgreSQL)
- [x] **Jenkins Pipeline**: Automação de build, test e deploy

### ✔️ Dependências e Ferramentas

- [x] **Python 3.11+**: Linguagem moderna com type hints
- [x] **uv**: Gerenciador de pacotes rápido
- [x] **pyproject.toml**: PEP 621 com especificação de dependencies
- [x] **Type Hints**: Tipagem explícita em todo o código
- [x] **Async/Await**: Operações I/O não-bloqueantes

### ✔️ Boas Práticas de Código

- [x] **Sem Floats para Dinheiro**: Sempre Decimal
- [x] **Type Checking**: Mypy-ready
- [x] **Code Standards**: Seguindo PEP 8 (snake_case, imports organizados)
- [x] **Logging**: Rastreamento de eventos importantes
- [x] **Sem Magic Numbers**: Constantes nomeadas
- [x] **Validação em Camadas**: Schemas, Services e Database

---

## 📚 Referências Adicionais

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Documentação Pydantic v2](https://docs.pydantic.dev/latest/)
- [Documentação Alembic](https://alembic.sqlalchemy.org/)
- [Documentação Cloudflare R2](https://developers.cloudflare.com/r2/)
- [Detalhes Técnicos de Dívidas](docs/debt_feature.md)
- [Instruções do Pipeline](pipeline_instructions.md)

---
## Metodologia de desenvolvimento
O grupo adotou uma abordagem ágil híbrida, utilizando conceitos de Scrum e Kanban. O gerenciamento das atividades foi realizado através do Jira, onde foram registradas histórias de usuário, tarefas e o acompanhamento do progresso do projeto. 

O Jira foi utilizado por por possuir tanto o método de Scrum quanto o Kanban, facilitando para mover uma tarefa pela esteira de produção, definir histórias de usuário, quebrar uma tarefa em subtasks menores, realizar reuniões com certa frequência, e o grupo já possuía uma certa familiaridade devido à experiência profissional individual de cada um. 

As sprints foram definidas de acordo com as entregas previstas no lab da disciplina, com duração média de duas semanas. A exceção foi a sprint final, que durou mais de um mês e concentrou a implementação das funcionalidades restantes, integração do sistema, correções e documentação. 

Uma tarefa era considerada concluída quando a funcionalidade estivesse implementada e integrada ao projeto, e nas etapas finais constantemente era rodado o pipe de CI/CD para garantir que tudo estava nos conformes. Sessões semanais de code review e alinhamento eram feitas pra definir etapas novas e o que precisava ser feito, especialmente no último mês de desenvolvimento. 

Como métricas, foram registrados 66 work items no Jira, sendo a maioria concluída (Done). Além disso, a análise de lead time indicou uma redução gradual do tempo médio de conclusão das tarefas ao longo do desenvolvimento, demonstrando maior familiaridade da equipe com o projeto e suas tecnologias, bem como uma prioridade para finalizar o que precisava ser feito no projeto.

Link para o jira: https://labengsoftware.atlassian.net/?continue=https%3A%2F%2Flabengsoftware.atlassian.net%2Fwelcome%2Fsoftware%3FprojectId%3D10000&atlOrigin=eyJpIjoiZGMxNGY1NjdiMjUxNGQ0MDhlN2VjMDRlMmRhNTZiY2QiLCJwIjoiamlyYS1zb2Z0d2FyZSJ9
---
## Dinâmica de desenvolvimento 
As tarefas foram distribuídas entre os integrantes de acordo com as necessidades de cada sprint. As decisões técnicas eram discutidas em grupo e registradas através das tarefas e histórias de usuário cadastradas no Jira. 

O desenvolvimento foi realizado utilizando GitHub para versionamento e integração das funcionalidades desenvolvidas pelos membros da equipe. 

Durante o projeto ocorreram alguns ajustes de prioridades e redistribuição de atividades, principalmente na sprint final, que concentrou boa parte do desenvolvimento e refinamento do sistema. 

Como lição aprendida, a equipe percebeu a importância de utilizar ferramentas de gerenciamento de projetos de forma consistente desde o início. Embora o Jira tenha sido criado já no início do lab, seu uso tornou-se mais efetivo quando passou a ser um critério obrigatório da disciplina. Ainda assim, para ganhar tempo a comunicação costumava também ocorrer de forma extraoficial e nem sempre o Jira foi usado para toda e qualquer task. Todavia, a ferramenta contribuiu para a organização das tarefas, definição das histórias de usuário e acompanhamento do progresso do projeto, mostrando-se útil para o planejamento e execução das atividades, e em futuros projetos é importante que seja bem utilizado desde o começo. 

---
# Uso da IA
## Modelos Utilizados

Durante o desenvolvimento do projeto **Divide AI API**, foram utilizadas ferramentas de Inteligência Artificial para auxiliar em atividades de desenvolvimento, documentação, depuração e infraestrutura.

Modelos e ferramentas utilizados:

* ChatGPT (OpenAI – GPT-5 e GPT-5.5)
* GitHub Copilot (auto e modelos disponíveis, como gpt 5 mini, claude haiku, etc)
* Claude AI (Anthropic)

---

## Para Que Foram Utilizados

As ferramentas de IA foram utilizadas como apoio técnico nas seguintes atividades:

* Geração e refatoração de código Python (FastAPI).
* Estruturação de rotas, serviços e repositórios.
* Auxílio na modelagem de entidades e relacionamentos.
* Correção de erros de configuração em Docker.
* Configuração de Jenkins para integração contínua (CI/CD).
* Depuração de erros relacionados a ambiente, dependências e execução de pipelines.
* Criação e revisão da documentação do projeto.
* Brainstorming de soluções arquiteturais.
* Análise de mensagens de erro e sugestões de correção.
* Revisão de configurações de deploy e containers.
* Montagem de história de usuário e dessa seção.

A IA foi utilizada como ferramenta de apoio ao desenvolvimento, sendo todas as sugestões avaliadas e validadas pela equipe antes de serem incorporadas ao projeto.

---

## Exemplos Reais de Prompts Utilizados

### Exemplo 1: Configuração de Ambiente Python no Jenkins

**Prompt:**

> "A pipeline do Jenkins está falhando ao executar o comando pytest com o erro 'pytest: not found'. Como posso configurar corretamente o ambiente para executar os testes?"

**Resultado:**

A IA identificou que o ambiente do Jenkins não possuía um ambiente virtual Python configurado corretamente e sugeriu a criação de uma virtualenv dentro da pipeline, além da instalação das dependências utilizando o arquivo requirements.txt.

**Ação:**

**Aceito.** A pipeline foi modificada para criar e ativar um ambiente virtual Python antes da execução dos testes automatizados.

---

### Exemplo 2: Correção do Dockerfile do Jenkins

**Prompt:**

> "Eu estou com dois dockerfiles, o da aplicação e um Dockerfile.jenkins que copiei de um projeto anterior. Ele instala Node.js, XVFB e bibliotecas gráficas. Está correto para um projeto FastAPI?"

**Resultado:**

A IA identificou que o Dockerfile utilizado havia sido originalmente criado para projetos frontend com Cypress e que continha dependências desnecessárias para o contexto atual. Foi sugerida a remoção dos pacotes gráficos e a instalação dos pacotes necessários para execução de aplicações Python e ambientes virtuais.

**Ação:**

**Aceito.** O Dockerfile do Jenkins foi simplificado, removendo dependências não utilizadas e adicionando suporte adequado para Python e virtual environments.

---

### Exemplo 3: Inicialização do Container Jenkins com Suporte ao Docker

**Prompt:**

> "Estou executando o Jenkins em um container Docker, mas minhas pipelines não conseguem executar comandos Docker. Como devo iniciar o container?"

**Resultado:**

A IA identificou que o container Jenkins não possuía acesso ao daemon Docker do host. Foi sugerido o mapeamento do socket Docker (/var/run/docker.sock) e a utilização de um volume persistente para armazenamento dos dados do Jenkins.

**Ação:**

**Aceito.** O comando de inicialização do Jenkins foi alterado para incluir o mapeamento do socket Docker e a persistência de dados. Após a alteração, as pipelines passaram a conseguir construir e executar imagens Docker durante o processo de CI/CD.

---

### Exemplo 4: Investigação de Erro CORS no Deploy

**Prompt:**

> "O frontend hospedado na Vercel está recebendo erro de CORS ao acessar arquivos enviados para o Cloudflare R2. Como identificar a origem do problema?"

**Resultado:**

A IA auxiliou na análise do fluxo de requisições, identificando que a API retornava um redirecionamento para uma URL hospedada no Cloudflare R2 e que o bloqueio ocorria devido à ausência de configuração CORS adequada no bucket de armazenamento.

**Ação:**

**Aceito parcialmente.** A análise foi utilizada para direcionar a investigação do problema e validar que o erro não estava relacionado às rotas FastAPI, mas sim à integração com o serviço de armazenamento.

---
### Exemplo 5: Controle de Status de Pagamento

**Prompt:**

"Qual a melhor forma de modelar os estados de pagamento de uma dívida compartilhada entre vários participantes?"

**Resultado:**

A IA sugeriu a utilização de estados distintos para representar o ciclo de vida do pagamento (PENDENTE, PAGO e CONFIRMADO), permitindo que o criador da dívida validasse os comprovantes enviados pelos participantes antes da conclusão da cobrança.

**Ação:**

Aceito com adaptações. A equipe utilizou a proposta como base para implementar o fluxo de aprovação dos pagamentos, ajustando as regras conforme os requisitos específicos do sistema.
---

## Dinâmica de Uso

A utilização das ferramentas de IA ocorreu principalmente de forma individual pelos integrantes durante o desenvolvimento das funcionalidades.

As ferramentas foram utilizadas para:

* Esclarecimento de dúvidas técnicas.
* Implementações de features (com revisão e critério de aceite)
* Revisão de implementações.
* Investigação de erros.
* Apoio na configuração de infraestrutura.
* Geração de documentação.
* Apoio em atividades de integração contínua (CI/CD).

Nenhuma resposta gerada por IA foi incorporada automaticamente ao projeto sem revisão humana. Todas as sugestões foram analisadas, adaptadas quando necessário e validadas pelos integrantes antes de serem utilizadas.

---

## O Que Não Foi Feito por IA

As seguintes atividades foram realizadas diretamente pelos integrantes da equipe:

* Definição dos requisitos do sistema.
* Modelagem das regras de negócio.
* Implementação final das funcionalidades.
* Criação e manutenção do banco de dados.
* Tomada de decisões arquiteturais.
* Integração entre frontend e backend.
* Testes manuais e validação funcional.
* Correção de problemas específicos encontrados durante o desenvolvimento.
* Deploy e validação final da aplicação e do pipe de CI/CD.
* 
A Inteligência Artificial foi utilizada como ferramenta de apoio e consulta técnica, não substituindo o entendimento, a implementação e a validação realizadas pelos integrantes do grupo.


**Última atualização**: Junho 2026
