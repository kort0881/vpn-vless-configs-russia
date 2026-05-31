#!/usr/bin/env python3
"""
Генератор свежих VLESS-конфигов на IP-диапазонах Cloudflare.
Сохраняет результат в data/githubmirror/new/cf_fresh.txt.
"""

import os
import uuid
import random
import requests
from pathlib import Path

# Пути после рефакторинга
BASE_DIR = Path(__file__).parent.parent  # корень репозитория
OUTPUT_DIR = BASE_DIR / "data" / "githubmirror" / "new"
OUTPUT_FILE = OUTPUT_DIR / "cf_fresh.txt"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CF_IPV4_URL = "https://www.cloudflare.com/ips-v4"
COUNT = 50
PORT = 443
ENCRYPTION = "none"
FLOW = "xtls-rprx-vision"
SECURITY = "tls"
TYPE = "tcp"


def get_cf_ips():
    """Загружает список IPv4-адресов Cloudflare."""
    resp = requests.get(CF_IPV4_URL, timeout=10)
    resp.raise_for_status()
    cidrs = resp.text.strip().splitlines()
    ips = []
    for cidr in cidrs:
        # Для простоты генерируем один случайный IP из диапазона /24 (можно расширить)
        # Но здесь для демонстрации сделаем просто список всех IP из диапазона (опасно, лучше выбрать несколько случайных)
        # Упрощённо: берём первый IP из каждого CIDR (не эффективно, но для генерации 50 ключей достаточно)
        # На практике лучше сгенерировать 50 случайных IP из общего пула CIDR
        # Я сделаю так: соберу все IP из всех CIDR (осторожно, их много тысяч, но для 50 ключей можно взять только первые 100)
        pass
    # Более простой способ: взять первые 100 IP из всех диапазонов (чтобы не перегружать память)
    # Реализуем функцию, которая возвращает список уникальных IP
    import ipaddress
    all_ips = []
    for cidr in cidrs:
        try:
            net = ipaddress.ip_network(cidr.strip())
            # Берём не более 10 IP из каждого диапазона, чтобы не перебирать все
            for i, ip in enumerate(net.hosts()):
                if i >= 10:
                    break
                all_ips.append(str(ip))
        except:
            continue
    # Перемешиваем и берём первые COUNT
    random.shuffle(all_ips)
    return all_ips[:COUNT * 2]  # запас


def generate_vless(ip):
    uid = str(uuid.uuid4())
    params = {
        "encryption": ENCRYPTION,
        "security": SECURITY,
        "type": TYPE,
        "flow": FLOW,
        "sni": "cloudflare.com",  # общий sni
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"vless://{uid}@{ip}:{PORT}?{query}#CF-{ip}"


def main():
    print("=== Генератор свежих VLESS-конфигов на IP Cloudflare ===")
    ips = get_cf_ips()
    if not ips:
        print("❌ Не удалось получить IP Cloudflare")
        return 1
    configs = [generate_vless(ip) for ip in ips[:COUNT]]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(configs) + "\n")
    print(f"✅ Сгенерировано и сохранено {len(configs)} VLESS-конфигов.")
    print(f"📂 Файл: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    exit(main())
