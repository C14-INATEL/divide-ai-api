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

## Feature: Dívidas (Debts)

O sistema agora suporta criar e gerenciar dívidas dentro de um `Group`. Uma dívida tem `creator_id`, `group_id`, `total_amount`, `split_type` (`homogenea` ou `heterogenea`), `due_date` e `status` (`pendente`/`pago`). Participantes são vinculados via `debt_participants` com `percentage`, `amount`, `status` (pendente/pago/confirmado) e campos para comprovantes (`has_proof`, `proof_url`).

Pontos principais:
- Se `participants` não for informado na criação, a dívida é automaticamente associada a todos os membros do grupo (exceto o `creator`).
- `HOMOGENEA` divide porcentagens igualmente; `HETEROGENEA` exige porcentagens que somem 100.
- Participantes fazem upload de comprovante (JPG, PNG ou PDF, máx. **5 MB**); o arquivo é armazenado no **Cloudflare R2** e a URL pública é salva em `proof_url`. O `creator` é quem confirma a quitação. Quando todos os participantes são confirmados, a dívida passa para `pago`.
- Exclusão: somente o `creator` pode apagar uma dívida e apenas se não houver participantes associados.

Endpoints (resumo):
- `POST /debts/` — criar dívida
- `GET /debts/?group_id={id}` — listar dívidas do grupo
- `GET /debts/{debt_id}` — obter dívida
- `DELETE /debts/{debt_id}` — deletar (restrito)
- `POST /debts/{debt_id}/participants/me/proof` — upload de comprovante pelo participante
- `POST /debts/{debt_id}/participants/{user_id}/confirm` — confirmação pelo creator

Recomendações: gerar migration Alembic para as novas tabelas (`debts`, `debt_participants`) e rodar testes que verifiquem somas de porcentagem, permissões e fluxo de upload/confirm.


## Principais bibliotecas

| Biblioteca                  | Função                                               |
| --------------------------- | -----------------------------------------------------|
| **FastAPI**           | Framework web async, geração automática de docs OpenAPI    |
| **SQLAlchemy 2.0**    | ORM para mapeamento de tabelas e queries                   |
| **Pydantic v2**       | Validação de dados de entrada e saída                      |
| **pydantic-settings** | Leitura de variáveis de ambiente via `.env`                |
| **Alembic**           | Migrations de banco de dados                               |
| **bcrypt**            | Hash seguro de senhas                                      |
| **pytest** e **unittest**           | Testes automatizados                                       |

---

## Requisitos

* Python 3.11+
* [uv](https://github.com/astral-sh/uv) - gerenciador de pacotes e ambiente virtual

As dependências são gerenciadas via `pyproject.toml` (PEP 621).

---

## CI/CD

Veja [`pipeline_instructions.md`](pipeline_instructions.md) para orientações sobre a construção do pipeline.

---

## Como rodar

```bash
# 1. Instalar dependências (uv sync lê pyproject.toml)
uv sync

# 2. Copiar e configurar variáveis de ambiente
cp .env.example .env

# 3. Aplicar migrations
uv run alembic upgrade head

# 4. Rodar o servidor
python run.py

# 5. Rodar testes
pytest -v
```

Docs disponíveis em: http://localhost:8000/docs

---

## Testes

```bash
# Rodar todos os testes
pytest -v

# Rodar testes de um arquivo específico unittest
python -m unittest discover tests/unit/schemas -v

# Rodar testes de um arquivo específico pytest
pytest tests/unit/services -v


```

---

## Migrations

```bash
# Criar nova migration
uv run alembic revision --autogenerate -m "descricao"

# Aplicar
uv run alembic upgrade head

# Reverter uma
uv run alembic downgrade -1
```

---

## Variáveis de ambiente

```env
DATABASE_URL=postgresql://user:password@localhost:5432/myproject
DEBUG=false

# Cloudflare R2 (armazenamento de comprovantes)
R2_BUCKET=seu_bucket
R2_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com   # "s3 api" do R2
R2_PUBLIC_URL=https://pub-xxxx.r2.dev                           # public development url
R2_ACCESS_KEY_ID=sua_access_key
R2_SECRET_ACCESS_KEY=sua_secret_access_key
MAX_UPLOAD_SIZE_BYTES=5242880                                   # 5 MB
```
