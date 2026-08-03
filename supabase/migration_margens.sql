-- Margens configuraveis (global, por marca, por produto)
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard/project/qfewcmoyzrezyxasvqny/sql/new)

-- 1. Coluna de margem por produto (% adicionado sobre o preco da distribuidora)
ALTER TABLE produtos ADD COLUMN IF NOT EXISTS margem DECIMAL(5,2);

-- 2. Chaves de configuracao
INSERT INTO config (chave, valor) VALUES
  ('margem_global', '30'),
  ('margens_marcas', '{}'),
  ('url_catalogo', '')
ON CONFLICT (chave) DO NOTHING;

-- 3. Funcao para recalcular todos os precos conforme as margens configuradas
--    (ignora espacos extras nas categorias e nas chaves das marcas)
CREATE OR REPLACE FUNCTION recalcular_precos()
RETURNS INTEGER AS $$
DECLARE
  v_global NUMERIC := 30;
  v_marcas JSONB := '{}'::jsonb;
  v_count INTEGER := 0;
BEGIN
  SELECT COALESCE(NULLIF((SELECT valor FROM config WHERE chave='margem_global'), ''), '30')::numeric
  INTO v_global;

  SELECT COALESCE(NULLIF((SELECT valor FROM config WHERE chave='margens_marcas'), ''), '{}')::jsonb
  INTO v_marcas;

  WITH mapa AS (
    SELECT jsonb_object_agg(trim(key), value::numeric) AS m
    FROM jsonb_each_text(v_marcas)
  )
  UPDATE produtos
  SET preco_venda = ROUND(preco_original * (1 + COALESCE(
      margem,
      ((SELECT m FROM mapa) ->> trim(categoria)),
      v_global) / 100), 2)
  WHERE ativo AND preco_original > 0;

  GET DIAGNOSTICS v_count = ROW_COUNT;
  RETURN v_count;
END;
$$ LANGUAGE plpgsql;
