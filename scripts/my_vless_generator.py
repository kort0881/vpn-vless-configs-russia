#!/usr/bin/env python3
"""Генератор реальных VLESS-конфигов на основе собранных ключей (mirror.py)"""

import os
import re
import uuid
from pathlib import Path

# Пути после рефакторинга
BASE_DIR = Path(__file__).parent.parent  # корень репозитория
ALL_NEW_FILE = BASE_DIR / "data" / "githubmirror" / "new" / "all_new.txt"
CLEAN_VLESS_FILE = BASE_DIR / "data" / "githubmirror" / "clean" / "vless.txt"
OUTPUT_GENERATED = BASE_DIR / "data" / "githubmirror" / "new" / "generated_real.txt"

def extract_hosts_from_file(file_path):
    """Извлекает из файла с ключами уникальные тройки (host, port, sni)"""
    if not file_path.exists():
        return set()
    hosts = set()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line.startswith("vless://"):
                continue
            # Формат: vless://uuid@host:port?params#tag
            match = re.match(r'vless://[^@]+@([^:]+):(\d+)\?(.*)', line)
            if match:
                host = match.group(1)
                port = match.group(2)
                params = match.group(3)
                sni_match = re.search(r'sni=([^&]+)', params)
                sni = sni_match.group(1) if sni_match else host
                hosts.add((host, port, sni))
    return hosts

def generate_vless(host, port, sni, remark=None):
    """Генерирует новый VLESS-URI со случайным UUID"""
    uid = str(uuid.uuid4())
    params = {
        "encryption": "none",
        "security": "tls",
        "type": "tcp",
        "flow": "xtls-rprx-vision",
    }
    if sni:
        params["sni"] = sni
    query = "&".join(f"{k}={v}" for k, v in params.items())
    tag = remark if remark else f"gen-{host}"
    return f"vless://{uid}@{host}:{port}?{query}#{tag}"

def load_existing_clean_vless():
    if not CLEAN_VLESS_FILE.exists():
        return set()
    with open(CLEAN_VLESS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        return {line.strip() for line in f if line.strip()}

def add_to_clean_vless(new_configs):
    existing = load_existing_clean_vless()
    added = [cfg for cfg in new_configs if cfg not in existing]
    if not added:
        return 0
    all_configs = sorted(existing.union(added))
    with open(CLEAN_VLESS_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_configs) + "\n")
    return len(added)

def main():
    print("=== Реальный генератор VLESS (на основе ваших источников) ===")
    # Извлекаем уникальные хосты из результатов mirror.py
    hosts = extract_hosts_from_file(ALL_NEW_FILE)
    if not hosts:
        print("⚠️ Не найден all_new.txt, пробуем clean/vless.txt...")
        hosts = extract_hosts_from_file(CLEAN_VLESS_FILE)
    if not hosts:
        print("❌ Нет данных для генерации. Убедитесь, что mirror.py уже был запущен и собрал ключи.")
        return 1
    print(f"🔍 Найдено уникальных серверов (host:port:sni): {len(hosts)}")
    generated = []
    for host, port, sni in hosts:
        cfg = generate_vless(host, port, sni, remark=f"auto-{host}")
        generated.append(cfg)
    with open(OUTPUT_GENERATED, 'w', encoding='utf-8') as f:
        f.write("\n".join(generated) + "\n")
    print(f"📁 Сгенерировано {len(generated)} конфигов, сохранено в {OUTPUT_GENERATED}")
    added = add_to_clean_vless(generated)
    print(f"✅ Добавлено в основной пул (clean/vless.txt): {added} новых конфигов")
    return 0

if __name__ == "__main__":
    exit(main())
