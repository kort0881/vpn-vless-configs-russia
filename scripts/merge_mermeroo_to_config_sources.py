#!/usr/bin/env python3
import os
import json
from pathlib import Path

# Корень репозитория (скрипт лежит в корне, как в твоём workflow)
BASE_PATH = Path(__file__).parent
MERMEROO_FILE = BASE_PATH / "mermeroo_only_new_for_mirror.txt"
CFG_FILE = BASE_PATH / "data" / "config_sources.json"

def load_lines(path):
    if not path.exists():
        print(f"{path} не найден")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def main():
    new_urls = load_lines(MERMEROO_FILE)
    if CFG_FILE.exists():
        with open(CFG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    else:
        data = []
    if not isinstance(data, list):
        data = []
    known = set(data)
    added = 0
    for u in new_urls:
        if u not in known:
            data.append(u)
            known.add(u)
            added += 1
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Добавлено новых источников: {added}")
    print(f"Всего в config_sources.json: {len(data)}")

if __name__ == "__main__":
    main()
