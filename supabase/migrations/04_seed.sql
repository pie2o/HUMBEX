-- 04_seed.sql - données de test
-- Idempotent : suppression des enregistrements de test avant insertion

-- NOTE: utilises gen_random_uuid() si pgcrypto présent ou fournis UUID fixes.

-- Exemple user test
DELETE FROM users WHERE email = 'test@example.com';
INSERT INTO users (id, email, created_at)
VALUES
  ('11111111-1111-1111-1111-111111111111'::uuid, 'test@example.com', now());

-- Subscription pour le user test
DELETE FROM subscriptions WHERE user_id = '11111111-1111-1111-1111-111111111111'::uuid;
INSERT INTO subscriptions (id, user_id, plan, expires_at, created_at)
VALUES
  ('22222222-2222-2222-2222-222222222222'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 'pro', now() + interval '30 days', now());

-- Order test
DELETE FROM orders WHERE exchange_order_id = 'seed-order-1';
INSERT INTO orders (id, user_id, signal_id, exchange_order_id, status, side, price, quantity, created_at)
VALUES
  ('33333333-3333-3333-3333-333333333333'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, NULL, 'seed-order-1', 'new', 'buy', 100.0, 0.01, now());

-- Signal test (table signals has no user_id)
DELETE FROM signals WHERE token = 'seed-token-1';
INSERT INTO signals (id, token, action, symbol, quantity, payload, received_at)
VALUES
  ('44444444-4444-4444-4444-444444444444'::uuid, 'seed-token-1', 'buy', 'BTCUSDT', 0.01, '{"note":"seed"}'::jsonb, now());

-- API key test
DELETE FROM api_keys WHERE api_key_enc = 'seed-api-key';
INSERT INTO api_keys (id, user_id, api_key_enc, iv, created_at)
VALUES
  ('55555555-5555-5555-5555-555555555555'::uuid, '11111111-1111-1111-1111-111111111111'::uuid, 'seed-api-key', 'seed-iv', now());
