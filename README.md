# DivideAI - API REST

![DivideAI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

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

### Rodar Local - Forma 1: Sem Docker

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

### Rodar Local - Forma 2: Com Docker Compose

```bash
# 1. Clonar o repositório
git clone https://github.com/C14-INATEL/divide-ai-api.git
cd divide-ai-api

# 2. Configurar variáveis de ambiente
cp .env.example .env

# 3. Subir containers (API + PostgreSQL)
docker compose up -d --build

# 4. Aplicar migrations
docker compose exec api uv run alembic upgrade head

# 5. Verificar se está rodando
curl http://localhost:8000/docs
```

### Acesso Online

A aplicação está configurada para ser deployada via **Jenkins + Docker** em um servidor de produção. Para detalhes sobre o pipeline de CI/CD, consulte [pipeline_instructions.md](pipeline_instructions.md).

Endpoint de produção: *(será fornecido após deployment)*

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

---

**Última atualização**: Junho 2024
