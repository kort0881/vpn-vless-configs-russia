#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор VLESS-конфигов с автоматической подгрузкой данных.
Если локальный файл отсутствует или пуст – скачивает с репозитория.
"""

import os
import sys
import urllib.request
from pathlib import Path

# ==================== КОНФИГУРАЦИЯ ====================
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "githubmirror" / "clean" / "vless.txt"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "vless.txt"

# ==================== FALLBACK: ЗАГРУЗКА ДАННЫХ ====================
def ensure_data():
    """Проверяет наличие данных, при необходимости скачивает"""
    if DATA_FILE.exists() and DATA_FILE.stat().st_size > 0:
        print(f"✅ Данные найдены: {DATA_FILE} (размер {DATA_FILE.stat().st_size} байт)")
        return True

    print("⚠️ Локальный файл отсутствует или пуст. Скачиваю свежий vless.txt...")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    url = "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt"
    try:
        urllib.request.urlretrieve(url, DATA_FILE)
        print(f"✅ Скачано: {DATA_FILE}")
        return True
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        return False

# ==================== ОСНОВНАЯ ЛОГИКА ====================
def main():
    if not ensure_data():
        print("❌ Не удалось получить данные. Выход.")
        sys.exit(1)

    # Читаем все строки
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("❌ Файл пуст после загрузки. Выход.")
        sys.exit(1)

    print(f"📥 Загружено {len(lines)} VLESS-конфигов.")

    # ====== ВСТАВЬТЕ СЮДА ВАШУ ГЕНЕРАЦИЮ ======
    # Здесь вы можете преобразовывать строки, добавлять параметры,
    # фильтровать, объединять, сохранять в другом формате и т.д.
    # Для примера просто копируем файл в output/
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"✅ Готово! {len(lines)} конфигов сохранено в {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
