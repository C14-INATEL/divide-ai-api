# DivideAi

API REST construída com FastAPI, SQLAlchemy e PostgreSQL, seguindo arquitetura em camadas (Router → Service → Repository).

---

## Arquitetura

```
app/
├── routers/        # Entrada HTTP — valida request/response, chama o service
├── services/       # Lógica de negócio — regras, validações, hash de senha
├── repositories/   # Acesso ao banco — queries SQLAlchemy, sem lógica de negócio
├── models/         # Tabelas ORM (SQLAlchemy)
├── schemas/        # Contratos de entrada/saída (Pydantic)
├── utils/          # Utilitários — ex: security.py (bcrypt)
├── database.py     # Engine, SessionLocal, get_db (singleton)
└── config.py       # Settings via variáveis de ambiente (pydantic-settings)
```

**Regra de ouro:** router não fala com repository. Todo acesso ao banco passa pelo service.

---
 
## Models
 
Os models representam as tabelas do banco via SQLAlchemy ORM. Todos usam `UUID` como chave primária e carregam `created_at` / `updated_at` automáticos.
 
| Model | Tabela | Descrição |
|---|---|---|
| `User` | `users` | Usuário da plataforma — email, senha (hash bcrypt), chave pix opcional |
| `Group` | `groups` | Grupo de divisão de despesas — possui um criador (`creator_id`) e vários membros |
| `GroupMember` | `group_members` | Tabela de junção N:M entre `User` e `Group` — registra quando o usuário entrou no grupo (`joined_at`) |
 
A relação entre `Group` e `User` é muitos-para-muitos: um usuário pode estar em vários grupos e um grupo pode ter vários usuários. O `GroupMember` é o elo entre eles, e existe como model explícito por carregar dados próprios da relação (`joined_at`).
 
Novos models devem ser registrados em `app/models/__init__.py` para que o Alembic os detecte na geração de migrations.
 
---

## Principais bibliotecas

| Biblioteca                  | Função                                               |
| --------------------------- | -----------------------------------------------------|
| **FastAPI**           | Framework web async, geração automática de docs OpenAPI    |
| **SQLAlchemy 2.0**    | ORM para mapeamento de tabelas e queries                   |
| **Pydantic v2**       | Validação de dados de entrada e saída                      |
| **pydantic-settings** | Leitura de variáveis de ambiente via `.env`                |
| **Alembic**           | Migrations de banco de dados                               |
| **bcrypt**            | Hash seguro de senhas                                      |
| **pytest**            | Testes automatizados                                       |

---

## Requisitos

* Python 3.11+
* [uv](https://github.com/astral-sh/uv)

---

## Como rodar

```bash
# 1. Instalar dependências
pip install -e ".[dev]"

# 2. Copiar e configurar variáveis de ambiente
cp .env.example .env

# 3. Aplicar migrations
alembic upgrade head

# 4. Rodar o servidor
python run.py

#5. Rodar testes
python -m pytest caminhodoteste/arquivo_teste.py -v -s
```

Docs disponíveis em: http://localhost:8000/docs

---

## Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=app
```

---

## Migrations

```bash
# Criar nova migration
alembic revision --autogenerate -m "descricao"

# Aplicar
alembic upgrade head

# Reverter uma
alembic downgrade -1
```

---

## Variáveis de ambiente

```env
DATABASE_URL=postgresql://user:password@localhost:5432/myproject
DEBUG=false
```
