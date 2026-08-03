-- Colunas de estoque e disponibilidade
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard/project/qfewcmoyzrezyxasvqny/sql/new)

ALTER TABLE produtos ADD COLUMN IF NOT EXISTS estoque INTEGER DEFAULT 0;
ALTER TABLE produtos ADD COLUMN IF NOT EXISTS disponivel BOOLEAN DEFAULT TRUE;
