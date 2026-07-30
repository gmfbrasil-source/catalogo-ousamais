#!/usr/bin/env python3
"""
Sync automático: Kyte -> Supabase
Extrai todos os produtos do catálogo e atualiza o banco.
"""

import requests
import re
import json
import time
import os
from urllib.parse import quote

# Configurações via variáveis de ambiente (seguro para GitHub Actions)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
MARGEM_LUCRO = float(os.getenv("MARGEM_LUCRO", "1.30"))

URL_CATALOGO = "https://catalogoatacadospecialdiadospaiss.catalog.kyte.site/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def extrair_produtos():
    print("Acessando catalogo Kyte...")
    for tentativa in range(3):
        try:
            r = requests.get(URL_CATALOGO, headers=HEADERS, timeout=30)
            r.raise_for_status()
            break
        except Exception as e:
            print(f"  Tentativa {tentativa+1}/3: {e}")
            if tentativa < 2:
                time.sleep(3)
            else:
                return None

    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
        r.text,
        re.DOTALL,
    )
    if not match:
        print("__NEXT_DATA__ nao encontrado")
        return None

    try:
        dados = json.loads(match.group(1))
        produtos = dados["props"]["initialReduxState"]["products"]["allProducts"]
        print(f"{len(produtos)} produtos extraidos")
        return produtos
    except Exception as e:
        print(f"Erro ao processar: {e}")
        return None


def sync_supabase(produtos):
    from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    ids_fornecedor = set()
    inseridos = 0
    atualizados = 0

    for p in produtos:
        produto_id = p.get("_id")
        if not produto_id:
            continue

        nome = p.get("name", "Sem nome")
        preco_original = p.get("salePromotionalPrice") or p.get("salePrice") or 0
        preco_venda = round(preco_original * MARGEM_LUCRO, 2)
        categoria = p.get("categoryName", "")
        imagem = p.get("image", "")

        if imagem.startswith("//"):
            imagem = "https:" + imagem
        elif imagem.startswith("/"):
            imagem = "https://firebasestorage.googleapis.com/v0/b/kyte-7c484.appspot.com/o/" + imagem.lstrip("/")

        dados_produto = {
            "id": produto_id,
            "nome": nome,
            "preco_original": preco_original,
            "preco_venda": preco_venda,
            "categoria": categoria,
            "imagem_url": imagem,
            "ativo": True,
        }

        # Upsert: insere ou atualiza
        resultado = supabase.table("produtos").upsert(dados_produto, on_conflict="id").execute()
        ids_fornecedor.add(produto_id)

        if resultado.data:
            if resultado.data[0].get("criado_em") == resultado.data[0].get("atualizado_em"):
                inseridos += 1
            else:
                atualizados += 1

    # Marcar como inativos produtos que não estão mais no catálogo
    todos_bd = supabase.table("produtos").select("id").eq("ativo", True).execute()
    for registro in todos_bd.data:
        if registro["id"] not in ids_fornecedor:
            supabase.table("produtos").update({"ativo": False}).eq("id", registro["id"]).execute()
            print(f"  Desativado: {registro['id']} (removido do catalogo)")

    print(f"Inseridos: {inseridos} | Atualizados: {atualizados}")


def formatar_preco(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_html(produtos):
    """Gera arquivo HTML estático para deploy na Vercel"""
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo Ousamais</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, Arial, sans-serif; background: #f5f5f5; }
  .header { background: #1a1a2e; color: white; padding: 20px; text-align: center; }
  .header h1 { font-size: 24px; }
  .header p { font-size: 14px; opacity: 0.8; margin-top: 5px; }
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
  .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .card img { width: 100%; height: 280px; object-fit: cover; }
  .card-body { padding: 15px; }
  .card-body h3 { font-size: 14px; color: #333; margin-bottom: 10px; }
  .preco-original { font-size: 12px; color: #999; text-decoration: line-through; }
  .preco-venda { font-size: 22px; color: #e63946; font-weight: bold; }
  .parcela { font-size: 13px; color: #666; margin: 5px 0; }
  .btn-whatsapp {
    display: block; background: #25D366; color: white; text-align: center;
    padding: 12px; border-radius: 8px; text-decoration: none;
    font-weight: bold; margin-top: 10px; font-size: 14px;
  }
  .btn-whatsapp:hover { background: #1da951; }
  .categoria-tag { display: inline-block; background: #eee; padding: 3px 8px; border-radius: 4px; font-size: 11px; color: #666; margin-bottom: 8px; }
  .footer { text-align: center; padding: 30px; color: #999; font-size: 13px; }
</style>
</head>
<body>
<div class="header">
  <h1>Catálogo Ousamais</h1>
  <p>Preços com desconto especial - Consulte disponibilidade</p>
</div>
<div class="container">
<div class="grid">
"""
    for p in produtos:
        nome = p.get("nome", "Produto")
        preco_venda = p.get("preco_venda", 0)
        preco_original = p.get("preco_original", 0)
        imagem_url = p.get("imagem_url", "")
        categoria = p.get("categoria", "")
        parcela = round(preco_venda / 6, 2)
        link_whats = f"https://wa.me/5575998078956?text={quote(f'Ola, quero aproveitar a oferta do {nome}!')}"

        html += f"""
<div class="card">
  <img src="{imagem_url}" alt="{nome}" loading="lazy">
  <div class="card-body">
    <span class="categoria-tag">{categoria}</span>
    <h3>{nome}</h3>
    <div class="preco-original">{formatar_preco(preco_original)}</div>
    <div class="preco-venda">{formatar_preco(preco_venda)}</div>
    <div class="parcela">Ou 6x de {formatar_preco(parcela)} sem juros</div>
    <a class="btn-whatsapp" href="{link_whats}" target="_blank">Comprar via WhatsApp</a>
  </div>
</div>
"""

    html += """
</div>
</div>
<div class="footer">
  Ousamais &copy; 2026 - Precos sujeitos a alteracao sem aviso previo
</div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html gerado")


def main():
    print("=" * 60)
    print("  SYNC CATALOGO - KYTE -> SUPABASE")
    print("=" * 60)

    if SUPABASE_URL and SUPABASE_KEY:
        produtos = extrair_produtos()
        if produtos:
            try:
                sync_supabase(produtos)
            except Exception as e:
                print(f"Erro no sync Supabase: {e}")
                print("Gerando HTML como fallback...")
                gerar_html(produtos)
    else:
        print("SUPABASE_URL/KEY nao configurados. Gerando HTML estatico...")
        produtos = extrair_produtos()
        if produtos:
            gerar_html(produtos)


if __name__ == "__main__":
    main()
