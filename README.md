Bien sûr ! Voici la **version traduite en français**, prête à copier-coller :

---

# HUMBEX - Bot de trading AVAXUSDT Perpétuel

## Vue d’ensemble

HUMBEX est un bot de trading automatisé pour les contrats **AVAXUSDT perpétuels** sur **Bybit**. Le système reçoit les signaux webhook de TradingView, les traite de manière sécurisée et exécute les trades en utilisant les clés API fournies par l’utilisateur (chiffrées au repos).

---

## Architecture

Ceci est un **monorepo** contenant :

* **Backend (FastAPI)** : API REST pour la réception des webhooks, la gestion des utilisateurs et le stockage chiffré des clés API
* **Worker** : processus en arrière-plan qui récupère les nouveaux signaux et exécute les trades via CCXT
* **Dashboard** : (placeholder) frontend Next.js pour la gestion des utilisateurs et le monitoring
* **Base de données** : PostgreSQL (via Supabase) pour stocker utilisateurs, abonnements, clés API, signaux et ordres

---

## Fonctionnalités

* ✅ Intégration webhook TradingView avec vérification de signature HMAC-SHA256
* ✅ Chiffrement AES-GCM des clés API au repos
* ✅ Mode **dry-run** par défaut (tests sécurisés sans trades réels)
* ✅ Support multi-utilisateur avec gestion des abonnements
* ✅ Orchestration Docker Compose
* ✅ Pipeline CI/CD minimal

---

## Sécurité

* **Vérification HMAC Webhook** : tous les webhooks TradingView doivent inclure un header `X-Signature` valide
* **Chiffrement des clés API** : les clés Bybit sont chiffrées avec AES-GCM 256 bits
* **Secrets d’environnement** : données sensibles stockées dans des variables d’environnement (jamais dans le code)
* **Clés de trading uniquement** : les utilisateurs doivent créer des clés API Bybit avec **trading activé** et **retraits désactivés**

---

## Démarrage rapide

### Prérequis

* Docker & Docker Compose
* Compte Supabase (pour PostgreSQL)

### Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/pie2o/HUMBEX.git
cd HUMBEX
```

2. **Générer les secrets**

```bash
# Secret webhook TradingView
openssl rand -hex 32

# Clé de chiffrement pour les clés API
openssl rand -hex 32
```

3. **Configurer l’environnement**

```bash
cp .env.example .env
# Modifier .env pour ajouter vos secrets générés et DATABASE_URL de Supabase
```

4. **Lancer les services**

```bash
docker compose up --build
```

5. **Vérifier la santé**

```bash
curl http://localhost:8000/health
```

---

## Endpoints API

### Health Check

```
GET /health
```

### Webhook TradingView

```
POST /webhook
Headers:
  X-Signature: <signature hex HMAC-SHA256>
Body:
{
  "token": "token_utilisateur",
  "action": "buy|sell|close",
  "symbol": "AVAXUSDT",
  "quantity": 1.0
}
```

---

## Variables d’environnement

### Obligatoires (Production)

* `TRADINGVIEW_SECRET` : Secret partagé pour la vérification HMAC du webhook
* `ENCRYPTION_KEY_HEX` : Clé hexadécimale 32 bytes pour chiffrement AES-GCM
* `DATABASE_URL` : Chaîne de connexion PostgreSQL depuis Supabase

### Optionnelles

* `BACKEND_PORT` : Port du backend (par défaut : 8000)
* `WORKER_POLL_INTERVAL` : Intervalle de polling du worker en secondes (par défaut : 5)
* `CCXT_TEST_MODE` : Activer le mode dry-run (par défaut : true)

---

## Schéma de la base de données

### Tables

1. **users** : Comptes utilisateurs et authentification
2. **subscriptions** : Statut et expiration de l’abonnement
3. **api_keys** : Clés API Bybit chiffrées (stockées sous `api_key_enc` + `iv`)
4. **signals** : Signaux reçus via webhook TradingView
5. **orders** : Historique des trades exécutés

---

## Workflow de développement

### Test local

1. Lancer les services avec `docker compose up`
2. Backend accessible sur `http://localhost:8000`
3. Tester le webhook avec signature HMAC :

```bash
# Calculer la signature
echo -n '{"token":"test","action":"buy","symbol":"AVAXUSDT","quantity":1.0}' | \
  openssl dgst -sha256 -hmac "votre_secret_tradingview" | cut -d' ' -f2

# Envoyer la requête
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: <signature_calculée>" \
  -d '{"token":"test","action":"buy","symbol":"AVAXUSDT","quantity":1.0}'
```

### Tests unitaires

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m pytest

# Worker
cd worker
python -m pytest
```

---

## Déploiement

### DigitalOcean App Platform

1. Créer une nouvelle app depuis le dépôt GitHub
2. Configurer les variables d’environnement dans le dashboard DO
3. Définir les commandes de build pour backend et worker
4. Activer HTTPS et configurer le firewall

---

### Variables d’environnement (Production)

* `DATABASE_URL` : Chaîne de connexion Supabase
* `TRADINGVIEW_SECRET` : Secret généré (32 bytes hex)
* `ENCRYPTION_KEY_HEX` : Clé de chiffrement (32 bytes hex)
* `CCXT_TEST_MODE` : `false` uniquement après tests complets

---

## Checklist sécurité (avant production)

* [ ] Remplacer tous les secrets test par des valeurs réelles (stockées en sécurité)
* [ ] Vérifier que les clés API Bybit ont **trading ON / retrait OFF**
* [ ] Stocker `ENCRYPTION_KEY_HEX` dans les secrets de la plateforme (DO/Supabase)
* [ ] Activer HTTPS sur tous les endpoints
* [ ] Configurer les règles firewall
* [ ] Ne jamais loguer les clés API ou secrets en clair
* [ ] Implémenter le flux d’activation de token après paiement MEXC
* [ ] Tester end-to-end sur Bybit testnet
* [ ] Ajouter idempotence et anti-replay (validation timestamp)
* [ ] Mettre en place monitoring & alerting (Sentry ou logs centralisés)

---

## CI/CD

Pipeline minimal inclus :

* Installer les dépendances
* Tests d’import smoke tests
* (Future) Linting, tests unitaires, builds Docker, déploiement automatique

---

## Licence

MIT

---

## Support

Pour toute question ou problème, ouvrir un issue sur GitHub.

