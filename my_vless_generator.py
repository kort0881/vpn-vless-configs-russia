#!/usr/bin/env python3
"""Генератор собственных VLESS-конфигов с интеграцией в githubmirror/clean/vless.txt"""

import uuid
import json
import os
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# Пути
BASE_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = BASE_DIR / "my_sources" / "generated"
CLEAN_VLESS_PATH = BASE_DIR / "githubmirror" / "clean" / "vless.txt"

# Создаём папки
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_VLESS_PATH.parent.mkdir(parents=True, exist_ok=True)


def make_vless(host: str, port: int = 443, path: str = "/", 
              sni: str | None = None, remark: str | None = None,
              flow: str = "xtls-rprx-vision", encryption: str = "none",
              security: str = "tls", type_: str = "tcp") -> str:
    """Формирует VLESS-URI с Reality/XTLS"""
    uid = str(uuid.uuid4())
    params = {
        "encryption": encryption,
        "security": security,
        "type": type_,
        "flow": flow,
    }
    if sni:
        params["sni"] = sni
    if path and path != "/":
        params["path"] = path
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    remark_part = f"#{remark}" if remark else f"#my-generated-{datetime.now().strftime('%Y%m%d')}"
    return f"vless://{uid}@{host}:{port}?{query}{remark_part}"


def generate_my_configs(count: int = 50, custom_hosts: list = None) -> list:
    """Генерирует VLESS-конфиги, можно передать свой список хостов"""
    if custom_hosts:
        hosts = custom_hosts
    else:
        # Пример хостов – замените на свои реальные домены или IP
        # Лучше использовать реальные рабочие серверы
        hosts = [f"node{i}.myvpn.example" for i in range(1, count + 1)]
    
    configs = []
    for i, host in enumerate(hosts[:count], 1):
        cfg = make_vless(
            host=host,
            port=443,
            sni=host if not re.match(r'^\d+\.\d+\.\d+\.\d+$', host) else None,
            remark=f"MySrc-{i}",
            flow="xtls-rprx-vision"
        )
        configs.append(cfg)
    return configs


def extract_key(line: str):
    """Извлекает (host, port, scheme) для дедупликации – как в mirror.py"""
    try:
        u = urlparse(line)
        return (u.hostname, u.port or 443, u.scheme)
    except:
        return None


def load_existing_clean_vless() -> set:
    """Загружает существующие строки из githubmirror/clean/vless.txt и возвращает множество URI"""
    if not CLEAN_VLESS_PATH.exists():
        return set()
    with open(CLEAN_VLESS_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    return set(lines)


def add_to_clean_vless(new_configs: list) -> int:
    """Добавляет новые конфиги в clean/vless.txt, если их ещё нет (проверка по полной строке)"""
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
    """Сохраняет копию в my_sources/generated/vless.txt"""
    out_path = OUTPUT_DIR / "vless.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(configs) + "\n")
    print(f"[SOURCE] Сохранено {len(configs)} конфигов в {out_path}")
    return out_path


def main():
    print("=== VLESS Generator (интегрированный) ===")
    
    # 1. Генерируем конфиги (можно изменить количество или подставить свои хосты)
    configs = generate_my_configs(count=50)
    print(f"[GEN] Сгенерировано {len(configs)} URI")
    
    # 2. Сохраняем в my_sources/generated/vless.txt (для отладки/истории)
    save_to_my_source(configs)
    
    # 3. Добавляем в githubmirror/clean/vless.txt (с дедупликацией)
    added = add_to_clean_vless(configs)
    
    print(f"\n✅ Готово! Добавлено в основной пул: {added} / {len(configs)}")
    print("Следующие шаги (main.py) обработают их через SNI-фильтры и т.д.")


if __name__ == "__main__":
    main()
