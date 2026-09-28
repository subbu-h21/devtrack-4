# TeamBoard

Backend for TeamBoard, a B2B knowledge-base API. Companies register, get an API key and a JWT, search the knowledge base, and an admin can see platform-wide usage stats.

## Setup

**1. Database (Postgres via Docker)**

```
cp .env.example .env
docker compose up -d
```

This starts Postgres using the credentials in `.env`. Nothing is hardcoded in `settings.py` — it's all read from the environment via `python-dotenv`.

**2. Python environment**

```
python -m venv venv
venv\Scripts\activate        # on Windows
pip install -r requirements.txt
```

**3. Migrations**

```
python manage.py makemigrations
python manage.py migrate
```

**4. Seed the knowledge base**

```
python manage.py seed_kb
```

Loads 12 Q&A entries across categories (api, database, cloud, framework, general), with overlapping keywords like `select_related`, `transaction.atomic`, `JWT`, and `Q objects` so search actually returns multiple hits.

**5. Run the server**

```
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000/`.

## Endpoints

| Method | URL | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | none | Create a company account, returns a JWT access token and the auto-generated API key |
| POST | `/api/auth/login/` | none | Log in with username/password, returns a fresh JWT plus `company_name` and `api_key` |
| POST | `/api/kb/query/` | JWT | Search the knowledge base by keyword, logs the query (even on zero results) |
| GET | `/api/admin/usage-summary/` | JWT + admin role | Total queries, distinct companies, top 5 search terms |

Everything except register/login requires `Authorization: Bearer <access_token>`.

To test the admin endpoint, promote a company to admin manually (this is intentional — there's no self-service admin signup):

```sql
UPDATE api_company SET role = 'admin' WHERE company_name = 'Acme Corp';
```

Then log in again so the fresh JWT reflects the role check.

## Postman

`TeamBoard.postman_collection.json` covers all 11 required scenarios (register success/duplicate, login success/invalid, KB query no-token/success/missing-search/zero-results, usage-summary no-token/client-forbidden/admin-success). Requests 1 and 3 auto-capture the JWT into a collection variable; request 10/11's descriptions explain the manual admin-promotion step needed between them.

## Design decision

The knowledge base search and its `QueryLog` write both happen inside one `transaction.atomic()` block in the view, and the log is written unconditionally — even when zero rows match. Usage-based billing counts requests made, not answers found, so a query that finds nothing still has to show up in the usage numbers. Wrapping both in one transaction means a logged query and its result count can never drift apart if something fails mid-request.
