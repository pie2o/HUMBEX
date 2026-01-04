# HUMBEX - AVAXUSDT Perpetual Trading Bot

## Overview

HUMBEX is an automated trading bot for AVAXUSDT perpetual futures on Bybit. The system receives TradingView webhook signals, processes them securely, and executes trades using user-provided API keys (encrypted at rest).

## Architecture

This is a monorepo containing:

- **Backend (FastAPI)**: REST API for webhook reception, user management, and encrypted API key storage
- **Worker**: Background process that polls for new signals and executes trades via CCXT
- **Dashboard**: (Placeholder) Next.js frontend for user management and monitoring
- **Database**: PostgreSQL (via Supabase) for storing users, subscriptions, API keys, signals, and orders

## Features

- ✅ TradingView webhook integration with HMAC-SHA256 signature verification
- ✅ AES-GCM encryption for API keys at rest
- ✅ Dry-run mode by default (safe testing without real trades)
- ✅ Multi-user support with subscription management
- ✅ Docker Compose orchestration
- ✅ Minimal CI/CD pipeline

## Security

- **HMAC Webhook Verification**: All TradingView webhooks must include a valid `X-Signature` header
- **API Key Encryption**: Bybit API keys are encrypted using AES-GCM with a 256-bit key
- **Environment Secrets**: Sensitive data stored in environment variables (never in code)
- **Read-Only Trading Keys**: Users should create Bybit API keys with trading permissions enabled but withdrawals disabled

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Supabase account (for PostgreSQL database)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pie2o/HUMBEX.git
   cd HUMBEX
   ```

2. **Generate secrets**
   ```bash
   # TradingView webhook secret
   openssl rand -hex 32
   
   # Encryption key for API keys
   openssl rand -hex 32
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your generated secrets and DATABASE_URL from Supabase
   ```

4. **Start services**
   ```bash
   docker compose up --build
   ```

5. **Verify health**
   ```bash
   curl http://localhost:8000/health
   ```

## API Endpoints

### Health Check
```
GET /health
```

### TradingView Webhook
```
POST /webhook
Headers:
  X-Signature: <HMAC-SHA256 hex signature>
Body:
{
  "token": "user_token",
  "action": "buy|sell|close",
  "symbol": "AVAXUSDT",
  "quantity": 1.0
}
```

## Environment Variables

### Required (Production)

- `TRADINGVIEW_SECRET`: Shared secret for webhook HMAC verification
- `ENCRYPTION_KEY_HEX`: 32-byte hex key for AES-GCM encryption
- `DATABASE_URL`: PostgreSQL connection string from Supabase

### Optional

- `BACKEND_PORT`: Backend server port (default: 8000)
- `WORKER_POLL_INTERVAL`: Worker polling interval in seconds (default: 5)
- `CCXT_TEST_MODE`: Enable dry-run mode (default: true)

## Database Schema

### Tables

1. **users**: User accounts and authentication
2. **subscriptions**: User subscription status and expiry
3. **api_keys**: Encrypted Bybit API keys (stored as `api_key_enc` + `iv`)
4. **signals**: TradingView webhook signals received
5. **orders**: Trade execution records

## Development Workflow

### Local Testing

1. Start the services with `docker compose up`
2. Backend runs on `http://localhost:8000`
3. Test webhook with HMAC signature:
   ```bash
   # Calculate signature
   echo -n '{"token":"test","action":"buy","symbol":"AVAXUSDT","quantity":1.0}' | \
     openssl dgst -sha256 -hmac "your_tradingview_secret" | cut -d' ' -f2
   
   # Send request
   curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/json" \
     -H "X-Signature: <calculated_signature>" \
     -d '{"token":"test","action":"buy","symbol":"AVAXUSDT","quantity":1.0}'
   ```

### Running Tests

```bash
# Backend tests
cd backend
pip install -r requirements.txt
python -m pytest

# Worker tests
cd worker
python -m pytest
```

## Deployment

### Digital Ocean App Platform

1. Create a new app from this GitHub repository
2. Configure environment variables in the DO dashboard
3. Set build commands for backend and worker services
4. Enable HTTPS and configure firewall rules

### Environment Variables (Production)

Set these in your deployment platform's secrets/environment configuration:

- `DATABASE_URL`: Your Supabase connection string
- `TRADINGVIEW_SECRET`: Generated secret (32-byte hex)
- `ENCRYPTION_KEY_HEX`: Generated encryption key (32-byte hex)
- `CCXT_TEST_MODE`: Set to `false` only after thorough testing

## Security Checklist (Before Production)

- [ ] Replace all test secrets in `.env.example` with real values (stored securely)
- [ ] Verify Bybit API keys have trading ON / withdrawal OFF
- [ ] Store `ENCRYPTION_KEY_HEX` in platform secrets (DO/Supabase)
- [ ] Enable HTTPS on all endpoints
- [ ] Configure firewall rules
- [ ] Never log API keys or secrets in plaintext
- [ ] Implement admin flow for token activation after MEXC payment
- [ ] Test end-to-end with Bybit testnet first
- [ ] Add idempotence and anti-replay (timestamp validation)
- [ ] Set up monitoring & alerting (Sentry, centralized logs)

## CI/CD

Minimal CI workflow included:
- Install dependencies
- Run import smoke tests
- (Future) Linting, unit tests, Docker builds, automated deployment

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
