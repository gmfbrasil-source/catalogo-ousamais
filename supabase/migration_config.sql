-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard/project/qfewcmoyzrezyxasvqny/sql/new)
CREATE TABLE IF NOT EXISTS config (
  chave TEXT PRIMARY KEY,
  valor TEXT
);

INSERT INTO config (chave, valor) VALUES
  ('logo_url', ''),
  ('banner_url', '')
ON CONFLICT (chave) DO NOTHING;
