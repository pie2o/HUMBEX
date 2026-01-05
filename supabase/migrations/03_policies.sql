
-- 03_policies.sql
-- Activer Row Level Security et policies de base pour HUMBEX
-- Idempotent : supprime les policies existantes avant de (re)créer afin d'éviter les erreurs si le fichier est exécuté plusieurs fois.

-- 1) Activer RLS sur les tables (IF EXISTS pour sécurité)
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS orders ENABLE ROW LEVEL SECURITY;

-- 2) Policies pour users
DROP POLICY IF EXISTS "Users: authenticated can manage own user row" ON users;
CREATE POLICY "Users: authenticated can manage own user row"
ON users
FOR ALL
USING (auth.role() = 'authenticated' AND id = auth.uid()::uuid)
WITH CHECK (auth.role() = 'authenticated' AND id = auth.uid()::uuid);

-- 3) Policies pour subscriptions
DROP POLICY IF EXISTS "Subscriptions: user can manage own subscriptions" ON subscriptions;
CREATE POLICY "Subscriptions: user can manage own subscriptions"
ON subscriptions
FOR ALL
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid)
WITH CHECK (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

-- 4) Policies pour api_keys
DROP POLICY IF EXISTS "ApiKeys: service only" ON api_keys;
CREATE POLICY "ApiKeys: service only"
ON api_keys
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- 5) Policies pour signals
DROP POLICY IF EXISTS "Signals: authenticated can insert" ON signals;
CREATE POLICY "Signals: authenticated can insert"
ON signals
FOR INSERT
USING (auth.role() = 'authenticated')
WITH CHECK (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Signals: authenticated can select own signals" ON signals;
CREATE POLICY "Signals: authenticated can select own signals"
ON signals
FOR SELECT
USING (auth.role() = 'authenticated' AND (user_id IS NULL OR user_id = auth.uid()::uuid));

-- 6) Policies pour orders
DROP POLICY IF EXISTS "Orders: user can manage own orders" ON orders;
CREATE POLICY "Orders: user can manage own orders"
ON orders
FOR ALL
USING (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid)
WITH CHECK (auth.role() = 'authenticated' AND user_id = auth.uid()::uuid);

-- Remarques :
-- - Exécuter ce fichier depuis Supabase SQL Editor (rôle postgres/service) ou via CI avec accès admin.
-- - Après exécution, vérifiez que RLS est bien activé et que les policies existent.
-- - Si votre schéma utilise des colonnes id/user_id en type text au lieu de uuid, changez les comparaisons en conséquence (ex: id::text = auth.uid()).
