#!/usr/bin/env python3
"""
Экстрактор лучших VLESS-конфигов из собранных данных.
Берёт живые ноды из clean/vless.txt, сортирует по задержке,
сохраняет топ-50 в data/githubmirror/new/cf_fresh.txt.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CLEAN_FILE = BASE_DIR / "data" / "githubmirror" / "clean" / "vless.txt"
OUTPUT_FILE = BASE_DIR / "data" / "githubmirror" / "new" / "cf_fresh.txt"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

COUNT = 50

def extract_delay(line: str) -> float:
    m = re.search(r'\| (\d+)ms', line)
    if m:
        return float(m.group(1))
    return 99999.0

def main():
    print("=== Экстрактор лучших VLESS-конфигов ===")
    if not CLEAN_FILE.exists():
        print(f"❌ Файл {CLEAN_FILE} не найден")
        return 1

    with open(CLEAN_FILE, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and l.startswith('vless://')]

    if not lines:
        print("❌ Нет VLESS-конфигов в clean/vless.txt")
        return 1

    # Сортируем по задержке (меньше = лучше)
    lines.sort(key=extract_delay)
    top = lines[:COUNT]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(top) + '\n')

    print(f"✅ Сохранено {len(top)} лучших VLESS-конфигов из {len(lines)}")
    print(f"📂 Файл: {OUTPUT_FILE}")
    if top:
        best_delay = extract_delay(top[0])
        worst_delay = extract_delay(top[-1])
        print(f"⚡ Задержка: {best_delay:.0f}ms - {worst_delay:.0f}ms")
    return 0

if __name__ == "__main__":
    exit(main())
