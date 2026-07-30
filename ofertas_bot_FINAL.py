#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AUTOMAÇÃO DE OFERTAS - Kyte → Telegram (VERSÃO FINAL)
"""

import requests
import re
import json
import os
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = "8758182990:AAHK3CuA3Ayf0wbYvngVicUlhsjEYtQyvBY"
TELEGRAM_CHAT_ID = "-5015587918"
WHATSAPP_NUMERO = "5575998078956"
MARGEM_LUCRO = 1.30
NOME_LOJA = "Ousamais"
URL_CATALOGO = os.getenv("URL_CATALOGO", "https://catalogoatacadospecialdiadospaiss.catalog.kyte.site/")
# ═══════════════════════════════════════════════════════════


def formatar_preco(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_parcelas(valor, parcelas=6):
    return formatar_preco(valor / parcelas)


def criar_link_whatsapp(nome_produto):
    texto = f"Olá, quero aproveitar a oferta do {nome_produto}!"
    texto_encoded = texto.replace(" ", "+").replace(",", "%2C")
    return f"https://wa.me/{WHATSAPP_NUMERO}?text={texto_encoded}"


def criar_descricao_produto(nome_produto):
    nome_lower = nome_produto.lower()
    if "kit" in nome_lower or "loção" in nome_lower:
        return "Puro luxo e sofisticação! Kit exclusivo para quem não abre mão da elegância. 💖"
    elif "feminino" in nome_lower:
        return "Fragrância envolvente e marcante. A essência da sofisticação em cada borrifada. 💃✨"
    elif "masculino" in nome_lower:
        return "Presença marcante e atitude sem igual. O perfume que define quem manda. 🕶️🔥"
    elif "carolina herrera" in nome_lower:
        return "A sofisticação da Carolina Herrera em uma fragrância inesquecível. 👑"
    elif "paco rabanne" in nome_lower:
        return "Intensidade e poder em cada nota. Paco Rabanne é pura atitude. ⚡"
    else:
        return "Produto original e de altíssima qualidade. Não perca essa oportunidade! 💎"


def formatar_oferta(produto):
    nome = produto.get("name", "Produto")
    preco_site = produto.get("salePromotionalPrice", produto.get("salePrice", 0))
    preco_venda = preco_site * MARGEM_LUCRO
    parcela = calcular_parcelas(preco_venda)
    link_whatsapp = criar_link_whatsapp(nome)

    return f"""🚨 *OFERTA IMPERDÍVEL: {nome.upper()}* ✨

{criar_descricao_produto(nome)}

*{nome}*

💰 *{formatar_preco(preco_venda)}*
💳 Ou em até *6x de {parcela}* sem juros

✅ *Originalidade {NOME_LOJA}*

🔗 *Essa oferta vai esgotar num piscar de olhos. Garanta no privado:* {link_whatsapp}"""


def extrair_produtos():
    print("🔄 Acessando catálogo Kyte...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        response = requests.get(URL_CATALOGO, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erro ao acessar catálogo: {e}")
        return None

    print(f"📄 HTML carregado: {len(response.text):,} caracteres")

    # Regex para o formato atual do site
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', response.text, re.DOTALL)
    if not match:
        print("❌ Não foi possível extrair dados do catálogo.")
        return None

    try:
        dados = json.loads(match.group(1))
        # CAMINHO CORRETO dos produtos
        produtos = dados["props"]["initialReduxState"]["products"]["productsList"]
        print(f"✅ {len(produtos)} produtos extraídos!")
        return produtos
    except KeyError as e:
        print(f"❌ Erro ao acessar dados: campo {e} não encontrado.")
        return None
    except Exception as e:
        print(f"❌ Erro ao processar dados: {e}")
        return None


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"  ⚠️ Erro ao enviar mensagem: {e}")
        return False


def enviar_foto_telegram(url_imagem, legenda):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    imagem_url = f"https://firebasestorage.googleapis.com/v0/b/kyte-catalog.appspot.com/o{requests.utils.quote(url_imagem, safe='')}?alt=media"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": imagem_url,
        "caption": legenda,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return True
        else:
            return enviar_telegram(legenda)
    except Exception as e:
        return enviar_telegram(legenda)


def main():
    print("=" * 60)
    print("🤖 AUTOMAÇÃO DE OFERTAS - KYTE → TELEGRAM")
    print("=" * 60)

    produtos = extrair_produtos()
    if not produtos:
        print("❌ Falha ao extrair produtos. Encerrando.")
        input("
Pressione ENTER para sair...")
        return

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    abertura = f"🔥 *OFERTAS DO DIA - {NOME_LOJA}* 🔥
📅 {data_hoje}

⚡ Aproveite antes que acabe!"

    print("
📤 Enviando mensagem de abertura...")
    enviar_telegram(abertura)

    enviados = 0
    for i, produto in enumerate(produtos, 1):
        oferta = formatar_oferta(produto)
        imagem = produto.get("image", "")
        nome = produto.get("name", "Produto")

        print(f"  📨 Oferta {i}/{len(produtos)}: {nome[:50]}...")

        if imagem:
            ok = enviar_foto_telegram(imagem, oferta)
        else:
            ok = enviar_telegram(oferta)

        if ok:
            enviados += 1

    fechamento = f"✅ *Fim das ofertas de hoje!*

📲 Dúvidas? Fale conosco: https://wa.me/{WHATSAPP_NUMERO}

🔄 Novas ofertas em breve!"
    enviar_telegram(fechamento)

    print(f"
✅ {enviados}/{len(produtos)} ofertas enviadas com sucesso!")
    print("🎉 Verifique seu Telegram!")
    input("
Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
