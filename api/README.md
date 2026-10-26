# Local Setup

## Prerequisites

- Ruby (see `.ruby-version`)
- Node.js + npm
- PostgreSQL (running locally or via Docker)
- Docker (for Redis)

---

## 1. Environment variables

```bash
cp config/application.yml.sample config/application.yml
```

Fill in the required values in `config/application.yml`:

| Variable | Description |
|---|---|
| `SECRET_KEY_BASE` | Must match `upstream authentication service` — JWT tokens are shared |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USERNAME` / `DB_PASSWORD` | Shared PostgreSQL instance |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `GEMINI_LIVE_MODEL` | e.g. `gemini-3.1-flash-live-preview` |
| `GEMINI_ANALYSIS_MODEL` | e.g. `gemini-2.0-flash-001` |
| `GEMINI_PRO_MODEL` | e.g. `gemini-2.5-pro` |
| `REDIS_URL` | e.g. `redis://localhost:6379/1` |
| `ALLOWED_ORIGINS` | CORS origin for the frontend, e.g. `http://localhost:5173` |
| `WEB_APP_BASE_URL` | Public frontend origin used in candidate invitation links, e.g. `http://localhost:5173` |
| `APP_BASE_URL` | Backend base URL, e.g. `http://localhost:3001` |

---

## 2. Install dependencies

```bash
bundle install
```

---

## 3. Set up the database

```bash
rails db:create   # skip if DB already exists
rails db:migrate
rails db:seed
```

---

## 4. Start Redis via Docker

```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

---

## 5. Start Sidekiq

```bash
bundle exec sidekiq -r ./config/environment.rb -C config/sidekiq.yml
```

---

## 6. Start the Rails server

```bash
bundle exec rails server
```

Runs on **port 3001** by default.

---

## 7. Start the frontend

```bash
cd ../web
npm install
npm run dev
```

Runs on **port 5173** by default.

---

## All services at a glance

| Service | Command | Port |
|---|---|---|
| Redis | `docker run -d -p 6379:6379 --name redis redis:alpine` | 6379 |
| Sidekiq | `bundle exec sidekiq -r ./config/environment.rb -C config/sidekiq.yml` | — |
| Rails API | `bundle exec rails server` | 3001 |
| Frontend | `npm run dev` (in `web/`) | 5173 |

## Tenant membership provisioning

Administrative tokens are tenant-bound. A valid admin password is no longer enough to
select an arbitrary organization. Grant access explicitly before expecting login to
succeed. This is a **case-study fail-closed policy** pending product/SSO approval.

In an isolated development Rails console, after creating an admin user and the
target organization through your normal authorized provisioning process:

```ruby
admin = User.find_by!(email: ENV.fetch("DEV_ADMIN_EMAIL"))
tenant = Organization.find_by!(scheme: ENV.fetch("DEV_TENANT_SCHEME"))
TenantMembership.find_or_create_by!(user: admin, organization: tenant)
```

Do not create wildcard grants or backfill every existing admin into every
organization. Accounts with one grant can log in without specifying a tenant.
Accounts with multiple grants must provide their organization code on the login
form (or `tenant_scheme` in the request). Removing a grant also prevents use
of an already-issued token on protected endpoints.

The release remains blocked until the business owner approves actual global
administration and SSO enrollment semantics. No test account or password is
embedded in the repository.
