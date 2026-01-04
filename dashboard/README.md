
# Tableau de bord HUMBEX

## Vue d’ensemble

Ce répertoire est un **placeholder** pour la future application **Next.js** du tableau de bord.

---

## Fonctionnalités prévues

* Authentification et inscription des utilisateurs
* Gestion des abonnements
* Gestion des clés API (stockage chiffré)
* Historique des signaux de trading
* Historique des ordres et analyses
* Suivi du solde du compte
* Notifications en temps réel

---

## Stack technologique (prévue)

* **Framework** : Next.js 14+ (App Router)
* **Bibliothèque UI** : React + Tailwind CSS
* **Gestion d’état** : React Query / Zustand
* **Graphiques** : Recharts / Widgets TradingView
* **Client API** : Axios / Fetch
* **Authentification** : JWT tokens

---

## Développement (futur)

```bash
cd dashboard
npm install
npm run dev
```

Le tableau de bord sera disponible sur `http://localhost:3000`

---

## Intégration

Le tableau de bord communiquera avec l’API backend à :

* Local : `http://localhost:8000`
* Production : `https://api.humbex.com`

---

## Sécurité

* Toutes les clés API chiffrées avant transmission
* HTTPS uniquement en production
* Authentification basée sur JWT
* CORS configuré uniquement pour le domaine frontend

---
