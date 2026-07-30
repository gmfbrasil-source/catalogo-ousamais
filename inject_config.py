#!/usr/bin/env python3
"""Injeta as configurações do Supabase no index.html para deploy na Vercel."""
import os

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('window.SUPABASE_URL = window.SUPABASE_URL || "__SUPABASE_URL__"', f'window.SUPABASE_URL = "{supabase_url}"')
html = html.replace('window.SUPABASE_KEY = window.SUPABASE_KEY || "__SUPABASE_KEY__"', f'window.SUPABASE_KEY = "{supabase_key}"')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Config injetada no index.html")
