#!/usr/bin/env python3
"""Генератор реальных VLESS-конфигов на основе реальных UUID из собранных ключей"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ALL_NEW_FILE = BASE_DIR / "data" / "githubmirror" / "new" / "all_new.txt"
CLEAN_VLESS_FILE = BASE_DIR / "data" / "githubmirror" / "clean" / "vless.txt"
OUTPUT_GENERATED = BASE_DIR / "data" / "githubmirror" / "new" / "generated_real.txt"

def extract_components_from_vless(line: str):
    """Извлекает uuid, host, port, sni из строки vless://..."""
    line = line.strip()
    if not line.startswith("vless://"):
        return None
    # Формат: vless://uuid@host:port?params
    match = re.match(r'vless://([^@]+)@([^:]+):(\d+)\?(.*)', line)
    if not match:
        return None
    uuid = match.group(1)
    host = match.group(2)
    port = match.group(3)
    params = match.group(4)
    sni_match = re.search(r'sni=([^&]+)', params)
    sni = sni_match.group(1) if sni_match else host
    return (uuid, host, port, sni)

def extract_components_from_file(file_path):
    """Возвращает список (uuid, host, port, sni) для всех vless-строк в файле"""
    if not file_path.exists():
        return []
    components = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            comp = extract_components_from_vless(line)
            if comp:
                components.append(comp)
    # Дедупликация по host+port
    seen = set()
    unique = []
    for uuid, host, port, sni in components:
        key = (host, port)
        if key not in seen:
            seen.add(key)
            unique.append((uuid, host, port, sni))
    return unique

def generate_vless_from_real(uuid, host, port, sni, remark=None):
    """Генерирует конфиг с реальным UUID, но с изменёнными параметрами (sni, flow)"""
    params = {
        "encryption": "none",
        "security": "tls",
        "type": "tcp",
        "flow": "xtls-rprx-vision",
    }
    if sni:
        params["sni"] = sni
    query = "&".join(f"{k}={v}" for k, v in params.items())
    tag = remark if remark else f"real-{host}"
    return f"vless://{uuid}@{host}:{port}?{query}#{tag}"

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
    print("=== Реальный генератор VLESS (на основе оригинальных UUID) ===")
    components = extract_components_from_file(ALL_NEW_FILE)
    if not components:
        components = extract_components_from_file(CLEAN_VLESS_FILE)
    if not components:
        print("❌ Нет данных для генерации. Запустите mirror.py сначала.")
        return 1

    print(f"🔍 Найдено уникальных серверов с реальными UUID: {len(components)}")
    generated = []
    for uuid, host, port, sni in components:
        cfg = generate_vless_from_real(uuid, host, port, sni, remark=f"real-{host}")
        generated.append(cfg)

    OUTPUT_GENERATED.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_GENERATED, 'w', encoding='utf-8') as f:
        f.write("\n".join(generated) + "\n")

    print(f"📁 Сгенерировано {len(generated)} конфигов, сохранено в {OUTPUT_GENERATED}")

    added = add_to_clean_vless(generated)
    print(f"✅ Добавлено в основной пул (clean/vless.txt): {added} новых конфигов")
    return 0

if __name__ == "__main__":
    exit(main())
