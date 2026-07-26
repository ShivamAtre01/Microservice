# Microservices Demo — User / Order / Payment / Notification

Four small Flask microservices that call each other over HTTP, matching the
architecture in Project 1 (Microservices on Kubernetes with End-to-End CI/CD).
This is the **application layer** — once this is working and pushed to
GitHub, you build the CI/CD pipeline (Jenkins → Docker → ECR → EKS) on top of it.

## Services

| Service              | Port | Responsibility                                      |
|----------------------|------|------------------------------------------------------|
| user-service          | 5001 | Stores/returns users                                 |
| payment-service       | 5002 | Simulates processing a payment                       |
| notification-service  | 5003 | Simulates sending an email/Slack notification         |
| order-service         | 5000 | Orchestrator — calls the other three to place an order |

## How they're connected

`order-service` is the entry point. When you POST to `/orders`, it:
1. Calls `user-service` → `GET /users/<id>` to validate the user exists
2. Calls `payment-service` → `POST /payments` to process payment
3. Calls `notification-service` → `POST /notify` to confirm the order

Service-to-service URLs are read from environment variables
(`USER_SERVICE_URL`, `PAYMENT_SERVICE_URL`, `NOTIFICATION_SERVICE_URL`), set
in `docker-compose.yml` using Docker's internal DNS (container/service
names). This is the same pattern Kubernetes Services use later, so you won't
need to rewrite the code when you move to EKS — only the env values change.

## Run locally with Docker Compose

```bash
docker compose up --build
```

This builds and starts all four containers on one bridge network
(`microservices-net`) so they can reach each other by service name.

## Test the connected flow

```bash
# 1. Check everyone is healthy
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5000/health

# 2. List seeded users
curl http://localhost:5001/users

# 3. Place an order for an existing user (u1) — this triggers the
#    order -> user -> payment -> notification chain
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "items": ["laptop"], "amount": 55000}'

# 4. Confirm the notification actually fired
curl http://localhost:5003/notifications

# 5. Try an order with a bad user_id — should be rejected with 400
curl -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "does-not-exist", "items": ["mouse"], "amount": 500}'
```

## Push to GitHub

```bash
cd microservices-project
git init
git add .
git commit -m "Initial commit: 4 connected microservices"
git branch -M main
git remote add origin https://github.com/ShivamAtre01/<your-repo-name>.git
git push -u origin main
```

## Suggested repo layout for the DevOps work

Keep this exact folder structure — it maps 1:1 onto the CI/CD guide:

```
your-repo/
├── user-service/
├── order-service/
├── payment-service/
├── notification-service/
├── docker-compose.yml       # local dev only
├── Jenkinsfile               # add this next: checkout → test → docker build → scan → push
├── k8s/                      # Deployment + Service manifests per microservice
└── README.md
```

## What's deliberately kept simple (so you can extend it as a talking point)

- In-memory storage instead of RDS/Aurora — swap in Postgres/MySQL when you
  add the database layer.
- No auth between services — add JWT or mTLS via Istio later, matching the
  service mesh in the architecture diagram.
- No retries/circuit breaker in `order-service` — a good place to show you
  understand resilience patterns in an interview.
