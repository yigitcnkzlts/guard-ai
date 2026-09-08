# GUARD AI

GUARD AI, şirket API'lerinde AI agent'ların çalıştırmak istediği işlemleri **çalıştırılmadan önce** kontrol eden bir runtime security gateway'dir.

İlk sürüm deterministik, kural tabanlı bir Policy Engine kullanır. Dashboard mevcut GUARD backend'ine bağlanır.

## Mimari

```text
Client / Agent
       ↓
GUARD AI :8001
       ↓
Policy Engine
       ↓
DemoShop :8000

Dashboard :3000  →  GUARD API :8001
```

Karar seçenekleri: `ALLOW`, `BLOCK`, `REQUIRE_APPROVAL`.

Eşleşen policy yoksa davranış **fail-closed**'dur: `BLOCK`.

## Teknolojiler

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- httpx
- Next.js / TypeScript / Tailwind CSS
- Docker / Docker Compose
- pytest

## Proje yapısı

```text
guard-ai/
├── backend/      # GUARD AI Security Gateway + Policy Engine
├── demo-api/     # DemoShop örnek e-ticaret API'si
├── frontend/     # GUARD dashboard
├── docker-compose.yml
├── .env.example
└── README.md
```

PostgreSQL aynı instance üzerinde iki ayrı database kullanır:

- `demoshop` → DemoShop API
- `guard_ai` → GUARD modelleri (`agents`, `policies`, `security_events`)

## Docker ile çalıştırma

1. Ortam dosyasını oluşturun (veya mevcut `.env` dosyanıza yeni değişkenleri ekleyin):

```bash
cp .env.example .env
```

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

2. Tüm sistemi başlatın:

```bash
docker compose up --build -d
```

Servisler:

- PostgreSQL: host `${POSTGRES_PORT:-5432}` → container `5432`
- DemoShop API: `8000`
- GUARD backend: `8001`
- Frontend dashboard: `3000`

GUARD backend açılışta `guard_ai` database'ini oluşturur, Alembic migration uygular ve seed agent/policy kayıtlarını yükler.

3. DemoShop örnek verisi (ALLOW senaryoları için):

```bash
docker compose exec demo-api python -m scripts.seed
```

## Adresler

- Frontend: [http://localhost:3000](http://localhost:3000)
- DemoShop Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- GUARD Swagger: [http://localhost:8001/docs](http://localhost:8001/docs)
- GUARD health: [http://localhost:8001/health](http://localhost:8001/health)

## Migration komutları

DemoShop:

```bash
docker compose exec demo-api alembic upgrade head
```

GUARD:

```bash
docker compose exec guard-backend alembic upgrade head
```

## Test

DemoShop:

```bash
docker compose exec demo-api pytest
```

GUARD:

```bash
docker compose exec guard-backend pytest
```

Frontend:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

Yerel olarak (`backend` dizininden, SQLite + mock upstream):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Gateway senaryoları

İstekler DemoShop'a doğrudan gitmez. Client / agent `POST /api/gateway/execute` üzerinden geçer.

### ALLOW — tek sipariş iptali

```bash
curl -X POST http://localhost:8001/api/gateway/execute \
  -H "Content-Type: application/json" \
  -d "{\"agent\":\"customer-support-agent\",\"method\":\"POST\",\"path\":\"/api/orders/1/cancel\",\"body\":null}"
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/gateway/execute -ContentType "application/json" -Body '{"agent":"customer-support-agent","method":"POST","path":"/api/orders/1/cancel","body":null}'
```

Policy: `ALLOW` / `MEDIUM`. Request DemoShop'a forward edilir.

### BLOCK — bütün siparişleri iptal etme

```bash
curl -X POST http://localhost:8001/api/gateway/execute \
  -H "Content-Type: application/json" \
  -d "{\"agent\":\"customer-support-agent\",\"method\":\"POST\",\"path\":\"/api/orders/cancel-all\",\"body\":null}"
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/gateway/execute -ContentType "application/json" -Body '{"agent":"customer-support-agent","method":"POST","path":"/api/orders/cancel-all","body":null}'
```

Policy: `BLOCK` / `CRITICAL`. HTTP 403 döner. DemoShop **çağrılmaz**. Dashboard Security Events ekranında görünür.

### REQUIRE_APPROVAL — refund

```bash
curl -X POST http://localhost:8001/api/gateway/execute \
  -H "Content-Type: application/json" \
  -d "{\"agent\":\"customer-support-agent\",\"method\":\"POST\",\"path\":\"/api/orders/1/refund\",\"body\":null}"
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8001/api/gateway/execute -ContentType "application/json" -Body '{"agent":"customer-support-agent","method":"POST","path":"/api/orders/1/refund","body":null}'
```

Policy: `REQUIRE_APPROVAL` / `HIGH`. HTTP 202 döner. DemoShop **çağrılmaz**. Gerçek human approval sonraki aşamada eklenecektir.

## Güvenlik olaylarında arama ve sayfalama

Security Events ekranı kayıtları 50'şer gösterir. `Search all events` düğmesi,
path ve reason alanlarında tüm olay geçmişini büyük/küçük harf ayrımı olmadan
arar. Decision, risk ve agent filtreleri aramayla birlikte uygulanır.
`Previous` / `Next` ile sayfa değiştirilebilir; `Clear filters` filtreleri
sıfırlar, `Refresh` mevcut sayfayı yeniden yükler.

`Export this page (JSON)` yalnızca görüntülenen sayfadaki olayları indirir.
Olay detayındaki `Export event (JSON)` tek kaydı indirir; detayda olay kimliği de
gösterilir. Dosyalar dışa aktarma zamanı ve kayıt sayısını içerir. Request body
alanındaki hassas anahtarlar, detay ekranındaki maskeleme ile aynı şekilde gizlenir.
Frontend sistem fontlarını kullanır; derleme sırasında Google Fonts indirmesi gerekmez.

API örneği: `GET /api/security-events?search=refund&decision=BLOCK&limit=50&offset=0`.
`limit` 1–200, `offset` sıfır veya üzeri, `search` en fazla 200 karakterdir.
Yanıt mevcut liste formatını korur. Aktif trafik sırasında yeni kayıtlar
sayfaları kaydırabilir; sayfalama sabit bir geçmiş görüntüsü sağlamaz.

## Seed policy özeti

Customer Support Agent (`customer-support-agent`):

| Method | Path | Decision | Risk |
|---|---|---|---|
| GET | `/api/orders` | ALLOW | LOW |
| GET | `/api/orders/{order_id}` | ALLOW | LOW |
| POST | `/api/orders/{order_id}/cancel` | ALLOW | MEDIUM |
| POST | `/api/orders/{order_id}/refund` | REQUIRE_APPROVAL | HIGH |
| POST | `/api/orders/cancel-all` | BLOCK | CRITICAL |
