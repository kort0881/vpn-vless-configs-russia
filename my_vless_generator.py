#!/usr/bin/env python3
"""Генератор собственных VLESS-конфигов с интеграцией в vpn-vless-configs-russia"""

import uuid
import json
import time
from pathlib import Path
from datetime import datetime

# Пути
BASE_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = BASE_DIR / "my_sources"
OUTPUT_DIR.mkdir(exist_ok=True)

def make_vless(host: str, port: int = 443, path: str = "/ws", 
              sni: str | None = None, remark: str | None = None,
              flow: str = "xtls-rprx-vision") -> str:
    """Формирует VLESS-URI с Reality/XTLS"""
    uid = str(uuid.uuid4())
    params = {
        "encryption": "none",
        "security": "tls",
        "type": "tcp",
        "flow": flow,
    }
    if sni:
        params["sni"] = sni
    if path and path != "/ws":
        params["path"] = path
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    remark_part = f"#{remark}" if remark else f"#generated-{datetime.now().strftime('%Y-%m-%d')}"
    return f"vless://{uid}@{host}:{port}?{query}{remark_part}"

def generate_my_configs(count: int = 30, custom_hosts: list = None):
    """Генерирует VLESS конфиги"""
    # Ваши хосты или генерируемые
    if custom_hosts:
        hosts = custom_hosts
    else:
        # Пример хостов - замените на свои реальные домены
        hosts = [f"node{i}.myvpn.example" for i in range(1, count + 1)]
    
    configs = []
    for i, host in enumerate(hosts[:count]):
        cfg = make_vless(
            host=host,
            port=443,
            sni=host,
            remark=f"MySource-{i+1}",
            flow="xtls-rprx-vision"  # Reality
        )
        configs.append(cfg)
    
    return configs

def save_to_source(configs: list, subdir: str = "generated"):
    """Сохраняет конфиги в источник"""
    out_path = OUTPUT_DIR / subdir / f"vless.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(configs), encoding="utf-8")
    print(f"[SAVED] {out_path} ({len(configs)} configs)")
    return out_path

def create_source_entry():
    """Создаёт запись в config_sources.json для своего источника"""
    config_sources_path = BASE_DIR / "config_sources.json"
    
    # Читаем существующие источники
    if config_sources_path.exists():
        with open(config_sources_path, 'r', encoding='utf-8') as f:
            sources = json.load(f)
    else:
        sources = []
    
    # Формируем file:// URL
    file_url = f"file://{OUTPUT_DIR / 'generated' / 'vless.txt'}"
    
    # Проверяем, нет ли уже нашего источника
    if file_url not in sources:
        sources.append(file_url)
        with open(config_sources_path, 'w', encoding='utf-8') as f:
            json.dump(sources, f, indent=2, ensure_ascii=False)
        print(f"[ADDED] Source entry: {file_url}")
    else:
        print(f"[SKIP] Source already exists")

def main():
    """Main entry point - генерирует и сохраняет конфиги"""
    print("=== VLESS Generator (My Source) ===")
    
    # Генерируем конфиги
    configs = generate_my_configs(count=50)
    
    # Сохраняем
    save_to_source(configs, subdir="generated")
    
    # Добавляем в config_sources.json
    create_source_entry()
    
    # Интеграция с CF генератором
    print("\n[INFO] Configs saved. Run 'python3 main.py' to process them.")

if __name__ == "__main__":
    main()