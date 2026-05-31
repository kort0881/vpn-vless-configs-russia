#!/usr/bin/env python3
"""Генератор реальных VLESS-конфигов на основе собранных хостов"""

import uuid
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = BASE_DIR / "my_sources" / "generated"
CLEAN_VLESS_PATH = BASE_DIR / "data/githubmirror" / "clean" / "vless.txt"
ALL_NEW_PATH = BASE_DIR / "data/githubmirror" / "new" / "all_new.txt"   # все свежие ключи

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_VLESS_PATH.parent.mkdir(parents=True, exist_ok=True)

def make_vless(host: str, port: int = 443, sni: str = None, remark: str = None,
               flow: str = "xtls-rprx-vision", encryption: str = "none",
               security: str = "tls", type_: str = "tcp") -> str:
    """Формирует VLESS-URI с XTLS Vision"""
    uid = str(uuid.uuid4())
    params = {
        "encryption": encryption,
        "security": security,
        "type": type_,
        "flow": flow,
    }
    if sni:
        params["sni"] = sni
    query = "&".join(f"{k}={v}" for k, v in params.items())
    tag = f"#{remark}" if remark else f"#gen-{datetime.now().strftime('%Y%m%d')}"
    return f"vless://{uid}@{host}:{port}?{query}{tag}"

def extract_real_hosts_from_files():
    """
    Извлекает уникальные (host, port, sni) из результатов работы mirror.py.
    Сначала из all_new.txt (все свежие ключи), потом из clean/vless.txt.
    """
    hosts = set()
    # Пытаемся прочитать all_new.txt (богаче)
    if ALL_NEW_PATH.exists():
        with open(ALL_NEW_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith("vless://"):
                    continue
                # Формат: vless://uuid@host:port?params#tag
                m = re.match(r'vless://[^@]+@([^:]+):(\d+)\?(.*)', line)
                if m:
                    host = m.group(1)
                    port = m.group(2)
                    params = m.group(3)
                    sni_match = re.search(r'sni=([^&]+)', params)
                    sni = sni_match.group(1) if sni_match else host
                    hosts.add((host, port, sni))
    # Если нет all_new.txt, пробуем clean/vless.txt
    if not hosts and CLEAN_VLESS_PATH.exists():
        with open(CLEAN_VLESS_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith("vless://"):
                    continue
                m = re.match(r'vless://[^@]+@([^:]+):(\d+)\?(.*)', line)
                if m:
                    host = m.group(1)
                    port = m.group(2)
                    params = m.group(3)
                    sni_match = re.search(r'sni=([^&]+)', params)
                    sni = sni_match.group(1) if sni_match else host
                    hosts.add((host, port, sni))
    return hosts

def generate_my_configs():
    """Генерирует VLESS-конфиги на основе реальных серверов из собранных ключей"""
    real_hosts = extract_real_hosts_from_files()
    if not real_hosts:
        print("[WARN] Нет реальных хостов. Сначала запустите mirror.py.")
        return []
    
    configs = []
    for host, port, sni in real_hosts:
        cfg = make_vless(
            host=host,
            port=int(port),
            sni=sni,
            remark=f"auto-{host}",
            flow="xtls-rprx-vision"
        )
        configs.append(cfg)
    return configs

def load_existing_clean_vless() -> set:
    if not CLEAN_VLESS_PATH.exists():
        return set()
    with open(CLEAN_VLESS_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        return {line.strip() for line in f if line.strip()}

def add_to_clean_vless(new_configs: list) -> int:
    existing = load_existing_clean_vless()
    added = 0
    for cfg in new_configs:
        if cfg not in existing:
            existing.add(cfg)
            added += 1
    if added:
        with open(CLEAN_VLESS_PATH, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(existing)) + "\n")
        print(f"[CLEAN] Добавлено {added} новых VLESS-конфигов в {CLEAN_VLESS_PATH}")
    else:
        print("[CLEAN] Нет новых конфигов – всё уже присутствует")
    return added

def save_to_my_source(configs: list) -> Path:
    out_path = OUTPUT_DIR / "vless.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(configs) + "\n")
    print(f"[SOURCE] Сохранено {len(configs)} конфигов в {out_path}")
    return out_path

def main():
    print("=== Реальный генератор VLESS (на основе ваших источников) ===")
    
    configs = generate_my_configs()
    if not configs:
        print("❌ Нет данных для генерации. Запустите mirror.py сначала.")
        return 1
    
    print(f"[GEN] Сгенерировано {len(configs)} URI на основе реальных серверов")
    save_to_my_source(configs)
    added = add_to_clean_vless(configs)
    
    print(f"\n✅ Готово! Добавлено в основной пул: {added} / {len(configs)}")
    return 0

if __name__ == "__main__":
    exit(main())
