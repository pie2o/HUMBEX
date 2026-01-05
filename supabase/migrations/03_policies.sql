
--- 03_policies.sql
-- Activer Row Level Security et policies de base pour HUMBEX
-- Idempotent : DROP POLICY IF EXISTS avant CREATE, et cast explicite auth.uid()::uuid

-- 1) Activer RLS sur les tables
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS orders ENABLE ROW LEVEL SECURITY;

-- =========================
-- USERS (id UUID)
-- =========================
DROP POLICY IF EXISTS "Users: select own" ON users;
CREATE POLICY "Users: select own"
ON users
FOR SELECT
USING (auth.role() = 'authenticated' AND id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Users: insert own" ON users;
CREATE POLICY "Users: insert own"
ON users
FOR INSERT
WITH CHECK (auth.role() = 'authenticated' AND id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Users: update own" ON users;
CREATE POLICY "Users: update own"
ON users
FOR UPDATE
USING (auth.role() = 'authenticated' AND id = auth.uid()::uuid)
WITH CHECK (auth.role() = 'authenticated' AND id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Users: delete own" ON users;
CREATE POLICY "Users: delete own"
ON users
FOR DELETE
USING (auth.role() = 'authenticated' AND id = auth.uid()::uuid);

-- =========================
-- SUBSCRIPTIONS (user_id UUID)
-- =========================
DROP POLICY IF EXISTS "Subscriptions: select own" ON subscriptions;
CREATE POLICY "Subscriptions: select own"
ON subscriptions
FOR SELECT
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Subscriptions: insert own" ON subscriptions;
CREATE POLICY "Subscriptions: insert own"
ON subscriptions
FOR INSERT
WITH CHECK (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Subscriptions: update own" ON subscriptions;
CREATE POLICY "Subscriptions: update own"
ON subscriptions
FOR UPDATE
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid)
WITH CHECK (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Subscriptions: delete own" ON subscriptions;
CREATE POLICY "Subscriptions: delete own"
ON subscriptions
FOR DELETE
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

-- =========================
-- API_KEYS (user_id UUID) - accès restreint au service_role pour la plupart
-- =========================
DROP POLICY IF EXISTS "ApiKeys: service only" ON api_keys;
CREATE POLICY "ApiKeys: service only"
ON api_keys
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- =========================
-- SIGNALS (pas de user_id dans le schéma)
-- =========================
-- On autorise les inserts par des utilisateurs authentifiés.
DROP POLICY IF EXISTS "Signals: insert authenticated" ON signals;
CREATE POLICY "Signals: insert authenticated"
ON signals
FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Optionnel : si tu veux que le backend/service lise/écrive tout, tu peux ajouter une policy service_role pour FOR ALL :
DROP POLICY IF EXISTS "Signals: service_role full" ON signals;
CREATE POLICY "Signals: service_role full"
ON signals
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- =========================
-- ORDERS (user_id UUID)
-- =========================
DROP POLICY IF EXISTS "Orders: select own" ON orders;
CREATE POLICY "Orders: select own"
ON orders
FOR SELECT
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Orders: insert own" ON orders;
CREATE POLICY "Orders: insert own"
ON orders
FOR INSERT
WITH CHECK (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Orders: update own" ON orders;
CREATE POLICY "Orders: update own"
ON orders
FOR UPDATE
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid)
WITH CHECK (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS "Orders: delete own" ON orders;
CREATE POLICY "Orders: delete own"
ON orders
FOR DELETE
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

-- Remarques :
-- - Ce fichier suppose que id/user_id sont de type UUID (d'après le schéma fourni). Nous castons auth.uid() en uuid.
-- - Pour signals on ne tente pas de vérifier user_id puisque ta table ne la contient pas.
-- - Exécute depuis Supabase SQL Editor (rôle postgres/service) ou via CI avec SUPABASE_SERVICE_ROLE_KEY.
