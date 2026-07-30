#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTOMACAO DE OFERTAS - Kyte -> Telegram v2
Catálogo Kyte com 30% de margem + link WhatsApp
"""

import requests
import re
import json
import sys
import time
import random
from datetime import datetime
import os
from urllib.parse import quote

# CONFIGURACOES
TELEGRAM_BOT_TOKEN = "8758182990:AAHK3CuA3Ayf0wbYvngVicUlhsjEYtQyvBY"
TELEGRAM_CHAT_ID = "-5015587918"
WHATSAPP_NUMERO = "5575998078956"
MARGEM_LUCRO = 1.30
NOME_LOJA = "Ousamais"
URL_CATALOGO = os.getenv("URL_CATALOGO", "https://catalogoatacadospecialdiadospaiss.catalog.kyte.site/")
QUANTIDADE_OFERTAS = 15
INTERVALO_MIN = 15
INTERVALO_MAX = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def formatar_preco(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_parcelas(valor, parcelas=6):
    return formatar_preco(valor / parcelas)


def criar_link_whatsapp(nome_produto):
    texto = f"Ola, quero aproveitar a oferta do {nome_produto}!"
    texto_encoded = quote(texto)
    return f"https://wa.me/{WHATSAPP_NUMERO}?text={texto_encoded}"


def frase_efeito(nome_produto):
    nome_lower = nome_produto.lower()
    if "kit" in nome_lower and "masculino" in nome_lower:
        return "✨ Kit completo que todo homem poderoso merece!"
    if "kit" in nome_lower and "feminino" in nome_lower:
        return "👑 O luxo que toda mulher merece em um so kit!"
    if "body splash" in nome_lower or "body spray" in nome_lower:
        return "🌺 A fragrancia que todo mundo esta amando!"
    if "masculino" in nome_lower:
        return "🔥 O perfume que define quem manda!"
    if "feminino" in nome_lower:
        return "💐 A essencia da sofisticacao em cada borrifada!"
    return "💎 Original e de altissima qualidade!"


def formatar_oferta(produto):
    nome = produto.get("name", "Produto")
    preco_site = produto.get("salePromotionalPrice") or produto.get("salePrice") or 0
    preco_venda = preco_site * MARGEM_LUCRO
    parcela = calcular_parcelas(preco_venda)
    link_whatsapp = criar_link_whatsapp(nome)

    return (
        f"{frase_efeito(nome)}\n\n"
        f"{nome}\n\n"
        f"💰 *{formatar_preco(preco_venda)}*\n"
        f"💳 Ou em ate *6x de {parcela}* sem juros\n\n"
        f"🔗 Garanta ja: {link_whatsapp}"
    )


def extrair_produtos():
    print("Acessando catalogo Kyte...")
    for tentativa in range(3):
        try:
            response = requests.get(URL_CATALOGO, headers=HEADERS, timeout=30)
            response.raise_for_status()
            break
        except Exception as e:
            print(f"  Tentativa {tentativa + 1}/3 falhou: {e}")
            if tentativa < 2:
                time.sleep(3)
            else:
                return None

    html = response.text

    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        print("Nao foi possivel extrair dados do catalogo.")
        print("Verifique se o site esta acessivel.")
        return None

    try:
        dados = json.loads(match.group(1))
        todos_produtos = dados["props"]["initialReduxState"]["products"]["allProducts"]
        print(f"{len(todos_produtos)} produtos encontrados no catalogo!")
        return todos_produtos
    except KeyError as e:
        print(f"Erro ao acessar dados: campo {e} nao encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return None


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return True
        else:
            print(f"  Erro Telegram: {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  Erro ao enviar mensagem: {e}")
        return False


FIREBASE_BUCKET = "https://firebasestorage.googleapis.com/v0/b/kyte-7c484.appspot.com/o/"


def montar_url_imagem(caminho):
    if not caminho:
        return None
    if caminho.startswith("http"):
        return caminho
    caminho = caminho.lstrip("/")
    return FIREBASE_BUCKET + caminho


def enviar_foto_telegram(url_imagem, legenda):
    url_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    url_completa = montar_url_imagem(url_imagem)

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": url_completa,
        "caption": legenda,
    }
    try:
        r = requests.post(url_api, json=payload, timeout=30)
        if r.status_code == 200:
            return True
        else:
            return enviar_telegram(legenda)
    except Exception:
        return enviar_telegram(legenda)


def formatar_oferta_whatsapp(produto):
    nome = produto.get("name", "Produto")
    preco_site = produto.get("salePromotionalPrice") or produto.get("salePrice") or 0
    preco_venda = preco_site * MARGEM_LUCRO
    parcela = calcular_parcelas(preco_venda)
    link_whatsapp = criar_link_whatsapp(nome)

    return (
        f"{frase_efeito(nome)}\n\n"
        f"{nome}\n\n"
        f"💰 {formatar_preco(preco_venda)}\n"
        f"💳 Ou em ate 6x de {parcela} sem juros\n\n"
        f"🔗 Garanta ja: {link_whatsapp}"
    )


def gerar_arquivo_ofertas(produtos, quantidade):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    nome_arquivo = f"ofertas_{datetime.now().strftime('%d%m%Y')}.txt"

    linhas = []
    linhas.append(f"OFERTAS DO DIA - {NOME_LOJA}")
    linhas.append(f"Data: {data_hoje}")
    linhas.append("")
    linhas.append("━" * 40)

    for i, produto in enumerate(produtos, 1):
        oferta = formatar_oferta_whatsapp(produto)
        linhas.append(f"📌 OFERTA {i}")
        linhas.append("")
        linhas.append(oferta)
        linhas.append("")
        linhas.append("━" * 40)
        linhas.append("")

    fechamento = (
        f"✅ Fim das ofertas de hoje!\n\n"
        f"📲 Duvidas? https://wa.me/{WHATSAPP_NUMERO}"
    )
    linhas.append(fechamento)

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return nome_arquivo


def main():
    print("=" * 60)
    print("  AUTOMACAO DE OFERTAS - KYTE -> TELEGRAM v2")
    print("=" * 60)

    produtos = extrair_produtos()
    if not produtos:
        print("Falha ao extrair produtos. Encerrando.")
        input("Pressione ENTER para sair...")
        return

    print(f"\nProdutos encontrados no catalogo: {len(produtos)}")

    quantidade = min(QUANTIDADE_OFERTAS, len(produtos))
    produtos_selecionados = random.sample(produtos, quantidade)
    print(f"Selecionados aleatoriamente: {quantidade} produtos para enviar")

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    abertura = (
        f"OFERTAS DO DIA - {NOME_LOJA}\n"
        f"Data: {data_hoje}\n\n"
        f"Aproveite as ofertas abaixo:"
    )

    print("\nEnviando mensagem de abertura...")
    enviar_telegram(abertura)

    intervalo_inicial = random.randint(10, 20)
    print(f"Aguardando {intervalo_inicial}s antes da primeira oferta...")
    time.sleep(intervalo_inicial)

    enviados = 0
    for i, produto in enumerate(produtos_selecionados, 1):
        oferta = formatar_oferta(produto)
        imagem = produto.get("image", "")
        nome = produto.get("name", "Produto")
        preco_site = produto.get("salePromotionalPrice") or produto.get("salePrice") or 0
        preco_venda = preco_site * MARGEM_LUCRO

        print(
            f"  [{i}/{quantidade}] {nome[:40]}... | "
            f"{formatar_preco(preco_site)} -> {formatar_preco(preco_venda)}"
        )

        if imagem:
            ok = enviar_foto_telegram(imagem, oferta)
        else:
            ok = enviar_telegram(oferta)

        if ok:
            enviados += 1

        intervalo = random.randint(INTERVALO_MIN, INTERVALO_MAX)
        print(f"  Aguardando {intervalo}s ate a proxima...")
        time.sleep(intervalo)

    intervalo_final = random.randint(10, 20)
    print(f"Aguardando {intervalo_final}s para encerramento...")
    time.sleep(intervalo_final)

    fechamento = (
        f"Fim das ofertas de hoje!\n\n"
        f"Duvidas? Fale conosco: https://wa.me/{WHATSAPP_NUMERO}\n\n"
        f"Novas ofertas em breve!"
    )
    enviar_telegram(fechamento)

    print(f"\n{enviados}/{quantidade} ofertas enviadas com sucesso!")

    nome_arquivo = gerar_arquivo_ofertas(produtos_selecionados, quantidade)
    print(f"\nArquivo gerado: {nome_arquivo}")
    print("Copie as ofertas para o WhatsApp!")
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    main()
