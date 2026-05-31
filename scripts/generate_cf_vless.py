#!/usr/bin/env python3
"""
Генератор свежих VLESS-конфигов на IP-диапазонах Cloudflare.
Сохраняет результат в data/githubmirror/new/cf_fresh.txt.
"""

import uuid
import random
import requests
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "githubmirror" / "new" / "cf_fresh.txt"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

CF_IPV4_URL = "https://www.cloudflare.com/ips-v4"
COUNT = 50
PORT = 443
ENCRYPTION = "none"
FLOW = "xtls-rprx-vision"
SECURITY = "tls"
TYPE = "tcp"

def get_cf_ips():
    resp = requests.get(CF_IPV4_URL, timeout=10)
    resp.raise_for_status()
    cidrs = resp.text.strip().splitlines()
    import ipaddress
    all_ips = []
    for cidr in cidrs:
        try:
            net = ipaddress.ip_network(cidr.strip())
            # Берём не более 5 IP из каждого диапазона, чтобы не перебирать все
            for i, ip in enumerate(net.hosts()):
                if i >= 5:
                    break
                all_ips.append(str(ip))
        except:
            continue
    random.shuffle(all_ips)
    return all_ips[:COUNT * 2]

def generate_vless(ip):
    uid = str(uuid.uuid4())
    params = {
        "encryption": ENCRYPTION,
        "security": SECURITY,
        "type": TYPE,
        "flow": FLOW,
        "sni": "cloudflare.com",
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
