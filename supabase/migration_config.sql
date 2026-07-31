-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard/project/qfewcmoyzrezyxasvqny/sql/new)
CREATE TABLE IF NOT EXISTS config (
  chave TEXT PRIMARY KEY,
  valor TEXT
);

ALTER TABLE config DISABLE ROW LEVEL SECURITY;

INSERT INTO config (chave, valor) VALUES
  ('logo_url', ''),
  ('banner_url', ''),
  ('texto_subtitulo', 'Mais de <strong>1.000 produtos</strong> direto da distribuidora para voce'),
  ('texto_busca', 'O que procura hoje?'),
  ('texto_rodape', 'Ousamais &copy; 2026 - Precos sujeitos a alteracao sem aviso previo')
ON CONFLICT (chave) DO NOTHING;
