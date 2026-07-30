-- Tabela principal de produtos
CREATE TABLE produtos (
  id TEXT PRIMARY KEY,
  nome TEXT NOT NULL,
  preco_original DECIMAL(10,2) NOT NULL,
  preco_venda DECIMAL(10,2) NOT NULL,
  preco_marca DECIMAL(10,2),
  categoria TEXT,
  imagem_url TEXT,
  ativo BOOLEAN DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT NOW(),
  atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Trigger para atualizar o timestamp automaticamente
CREATE OR REPLACE FUNCTION trigger_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
  NEW.atualizado_em = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_atualizado_em
  BEFORE UPDATE ON produtos
  FOR EACH ROW
  EXECUTE FUNCTION trigger_atualizado_em();

-- View para exibir apenas produtos ativos
CREATE VIEW catalogo_ativos AS
SELECT
  id,
  nome,
  preco_original,
  preco_venda,
  categoria,
  imagem_url,
  criado_em
FROM produtos
WHERE ativo = TRUE
ORDER BY categoria, nome;

-- Índices para busca
CREATE INDEX idx_produtos_categoria ON produtos(categoria);
CREATE INDEX idx_produtos_ativo ON produtos(ativo);

-- Tabela de configuração (logo, banner etc)
CREATE TABLE config (
  chave TEXT PRIMARY KEY,
  valor TEXT
);

INSERT INTO config (chave, valor) VALUES
  ('logo_url', ''),
  ('banner_url', '');
