-- Margens configuraveis (global, por marca, por produto)
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard/project/qfewcmoyzrezyxasvqny/sql/new)

-- 1. Coluna de margem por produto (% adicionado sobre o preco da distribuidora)
ALTER TABLE produtos ADD COLUMN IF NOT EXISTS margem DECIMAL(5,2);

-- 2. Chaves de configuracao
INSERT INTO config (chave, valor) VALUES
  ('margem_global', '30'),
  ('margens_marcas', '{}')
ON CONFLICT (chave) DO NOTHING;

-- 3. Funcao para recalcular todos os precos conforme as margens configuradas
CREATE OR REPLACE FUNCTION recalcular_precos()
RETURNS INTEGER AS $$
DECLARE
  v_global NUMERIC := 30;
  v_marcas JSONB := '{}'::jsonb;
  v_count INTEGER := 0;
  v_reg RECORD;
BEGIN
  SELECT COALESCE(NULLIF((SELECT valor FROM config WHERE chave='margem_global'), ''), '30')::numeric
  INTO v_global;

  SELECT COALESCE(NULLIF((SELECT valor FROM config WHERE chave='margens_marcas'), ''), '{}')::jsonb
  INTO v_marcas;

  FOR v_reg IN
    SELECT id, preco_original, margem, categoria
    FROM produtos
    WHERE ativo AND preco_original > 0
  LOOP
    UPDATE produtos SET preco_venda = ROUND(v_reg.preco_original * (1 + COALESCE(
      v_reg.margem,
      (v_marcas->>v_reg.categoria)::numeric,
      v_global) / 100), 2)
    WHERE id = v_reg.id;
    v_count := v_count + 1;
  END LOOP;

  RETURN v_count;
END;
$$ LANGUAGE plpgsql;
