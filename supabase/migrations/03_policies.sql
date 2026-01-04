-- 03_policies.sql
-- Activer Row Level Security et policies de base pour HUMBEX

-- 1) Activer RLS sur les tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 2) Policies pour users
-- Permettre à un utilisateur authentifié de SELECT/UPDATE/DELETE/INSERT seulement sur sa propre ligne (id = auth.uid()).
CREATE POLICY "Users: authenticated can manage own user row"
ON users
FOR ALL
USING (auth.role() = 'authenticated' AND id::text = auth.uid())
WITH CHECK (auth.role() = 'authenticated' AND id::text = auth.uid());

-- 3) Policies pour subscriptions
-- Permettre aux utilisateurs authentifiés d'agir seulement sur leurs subscriptions (user_id = auth.uid()).
CREATE POLICY "Subscriptions: user can manage own subscriptions"
ON subscriptions
FOR ALL
USING (auth.role() = 'authenticated' AND user_id::text = auth.uid())
WITH CHECK (auth.role() = 'authenticated' AND user_id::text = auth.uid());

-- 4) Policies pour api_keys
-- Interdire l'accès aux clients publics ; seulement le service (service_role) peut voir/écrire.
-- Note: les requêtes exécutées avec la SUPABASE_SERVICE_ROLE_KEY utilisent le role 'service_role'
CREATE POLICY "ApiKeys: service only"
ON api_keys
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- 5) Policies pour signals
-- Autoriser insertion par des utilisateurs authentifiés (ajuste si tu veux autoriser webhooks externes via ton backend)
CREATE POLICY "Signals: authenticated can insert"
ON signals
FOR INSERT
USING (auth.role() = 'authenticated')
WITH CHECK (auth.role() = 'authenticated');

-- Autoriser lecture des signals pour l'utilisateur propriétaire si tu as un champ user_id (ici on suppose token/public signals)
-- (Adaptation possible selon ton modèle)
CREATE POLICY "Signals: authenticated can select own signals"
ON signals
FOR SELECT
USING (auth.role() = 'authenticated' AND (user_id IS NULL OR user_id::text = auth.uid()));

-- 6) Policies pour orders
-- Permettre aux utilisateurs d'accéder à leurs propres orders
CREATE POLICY "Orders: user can manage own orders"
ON orders
FOR ALL
USING (auth.role() = 'authenticated' AND user_id::text = auth.uid())
WITH CHECK (auth.role() = 'authenticated' AND user_id::text = auth.uid());

-- Remarques :
-- - Les opérations d'administration (migration/seed) peuvent être exécutées depuis SQL Editor (rôle postgres/service) ou via le backend utilisant SUPABASE_SERVICE_ROLE_KEY.
-- - Si tu veux autoriser des webhooks externes (TradingView) à poster, préférer que seul ton backend les reçoive et insère en DB via la key service_role.
