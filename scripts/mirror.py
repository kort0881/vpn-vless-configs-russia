#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mirror.py — WHITELIST ONLY (Super Clean)

import os
import sys
import shutil
import requests
import urllib.parse
import base64
import json
import re
import traceback

print("DEBUG: mirror.py started", flush=True)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"DEBUG: BASE_PATH = {BASE_PATH}", flush=True)

BASE_DIR = os.path.join(BASE_PATH, "data", "githubmirror")
NEW_DIR = os.path.join(BASE_DIR, "new")
CLEAN_DIR = os.path.join(BASE_DIR, "clean")
NEW_BY_PROTO_DIR = os.path.join(NEW_DIR, "by_protocol")

PROTOCOLS = ["vless", "vmess", "trojan", "ss", "hysteria", "hysteria2", "hy2", "tuic"]

GOOD_DOMAINS = [
    "ru", "by", "kz", "su", "rf",
    "de", "nl", "fi", "gb", "uk", "fr", "se", "pl", "cz", "at",
    "ch", "it", "es", "no", "dk", "be", "ie", "lu", "ee", "lv", "lt"
]

GOOD_TAGS = [
    "🇷🇺", "🇧🇾", "🇰🇿", "RUSSIA", "MOSCOW", "SPB", "PETERSBURG", "KAZAKHSTAN",
    "BELARUS", "RU_", "RUS", "РФ", "МОСКВА", "СПБ",
    "🇩🇪", "🇳🇱", "🇫🇮", "🇬🇧", "🇫🇷", "🇸🇪", "🇵🇱", "🇨🇿", "🇦🇹", "🇨🇭",
    "🇮🇹", "🇪🇸", "🇳🇴", "🇩🇰", "🇧🇪", "🇮🇪", "🇱🇺", "🇪🇪", "🇱🇻", "🇱🇹", "🇪🇺",
    "GERMANY", "DEUTSCHLAND", "NETHERLANDS", "HOLLAND", "FINLAND",
    "UK", "UNITED KINGDOM", "BRITAIN", "FRANCE", "SWEDEN", "POLAND",
    "CZECH", "AUSTRIA", "SWISS", "SWITZERLAND", "ITALY", "SPAIN",
    "NORWAY", "DENMARK", "BELGIUM", "IRELAND", "ESTONIA", "LATVIA", "LITHUANIA",
    "EUROPE", "AMSTERDAM", "FRANKFURT", "LONDON", "PARIS", "FALKENSTEIN",
    "LIMBURG", "HELSINKI", "STOCKHOLM", "WARSAW", "PRAGUE", "VIENNA",
    "ZURICH", "OSLO", "COPENHAGEN", "BRUSSELS", "DUBLIN", "TALLINN", "RIGA", "VILNIUS"
]

CONFIG_SOURCES_FILE = os.path.join(BASE_PATH, "data", "config_sources.json")
print(f"DEBUG: CONFIG_SOURCES_FILE = {CONFIG_SOURCES_FILE}", flush=True)

CHUNK_SIZE = 500

def fetch_keys_from_sstap():
    url = "https://sstap.org/node-real-time-update/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, timeout=15, headers=headers)
        if resp.status_code != 200:
            print(f"⚠️ sstap.org вернул HTTP {resp.status_code}", flush=True)
            return []
        patterns = [r'vless://[^\s<>"\'\\]+', r'vmess://[^\s<>"\'\\]+', r'ss://[^\s<>"\'\\]+', r'trojan://[^\s<>"\'\\]+', r'hysteria://[^\s<>"\'\\]+', r'tuic://[^\s<>"\'\\]+']
        keys = []
        for pat in patterns:
            found = re.findall(pat, resp.text)
            keys.extend(found)
        unique = []
        seen = set()
        for k in keys:
            if k not in seen:
                seen.add(k)
                unique.append(k)
        print(f"📡 С sstap.org получено {len(unique)} ключей", flush=True)
        return unique
    except Exception as e:
        print(f"❌ Ошибка при парсинге sstap.org: {e}", flush=True)
        return []

def load_all_urls():
    urls = set()
    if os.path.exists(CONFIG_SOURCES_FILE):
        try:
            with open(CONFIG_SOURCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for u in data:
                        if isinstance(u, str) and u.strip():
                            urls.add(u.strip())
                print(f"📂 Загружено {len(urls)} источников из {CONFIG_SOURCES_FILE}", flush=True)
        except Exception as e:
            print(f"⚠️ Не удалось прочитать config_sources.json: {e}", flush=True)
    else:
        print(f"⚠️ Файл {CONFIG_SOURCES_FILE} не найден", flush=True)
    return sorted(urls)

def clean_start():
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    os.makedirs(NEW_DIR, exist_ok=True)
    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs(NEW_BY_PROTO_DIR, exist_ok=True)

def protocol_of(line: str):
    for p in PROTOCOLS:
        if line.startswith(p + "://"):
            return p
    return None

def extract_host_port_scheme(line: str):
    try:
        u = urllib.parse.urlparse(line)
        return u.hostname, u.port or 443, u.scheme
    except Exception:
        return None, None, None

def is_ip_address(s: str) -> bool:
    if not s:
        return False
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^[0-9a-fA-F:]+$'
    return bool(re.match(ipv4_pattern, s) or re.match(ipv6_pattern, s))

def is_good_key(line: str) -> bool:
    line_upper = line.upper()
    name = ""
    if "#" in line:
        name = urllib.parse.unquote(line.split("#")[-1]).upper()
    for tag in GOOD_TAGS:
        if tag in name or tag in line_upper:
            return True
    host, _, _ = extract_host_port_scheme(line)
    if host and not is_ip_address(host):
        host_lower = host.lower()
        for dom in GOOD_DOMAINS:
            if host_lower.endswith("." + dom) or host_lower == dom:
                return True
    return False

def write_chunks_by_protocol(base_dir: str, protocol: str, items: list, chunk_size: int = 500):
    proto_dir = os.path.join(base_dir, protocol)
    os.makedirs(proto_dir, exist_ok=True)
    for start in range(0, len(items), chunk_size):
        part = items[start:start + chunk_size]
        part_num = start // chunk_size + 1
        with open(os.path.join(proto_dir, f"{protocol}_{part_num:03d}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(part))

def main() -> int:
    try:
        clean_start()
        all_keys = set()
        trash_count = 0

        urls = load_all_urls()
        print(f"🚀 Старт: всего источников: {len(urls)}", flush=True)

        for i, url in enumerate(urls, 1):
            try:
                r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code != 200:
                    print(f"{i}/{len(urls)} ❌ HTTP {r.status_code} — {url}", flush=True)
                    continue
                content = r.text.strip()
                if "://" not in content:
                    try:
                        content = base64.b64decode(content + "==").decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                lines = content.splitlines()
                added_local = 0
                trash_local = 0
                for line in lines:
                    line = line.strip()
                    if not protocol_of(line):
                        continue
                    if is_good_key(line):
                        if line not in all_keys:
                            all_keys.add(line)
                            added_local += 1
                    else:
                        trash_local += 1
                trash_count += trash_local
                print(f"{i}/{len(urls)}: ✅ {added_local} взято | 🗑️ {trash_local} мусор", flush=True)
            except Exception as e:
                print(f"{i}/{len(urls)} ⚠️ Ошибка: {e} — {url}", flush=True)

        sstap_keys = fetch_keys_from_sstap()
        sstap_added = 0
        sstap_trash = 0
        for key in sstap_keys:
            if not protocol_of(key):
                continue
            if is_good_key(key):
                if key not in all_keys:
                    all_keys.add(key)
                    sstap_added += 1
            else:
                sstap_trash += 1
        trash_count += sstap_trash
        if sstap_added > 0:
            print(f"📡 С sstap.org добавлено {sstap_added} ключей (отфильтровано {sstap_trash})", flush=True)
        else:
            print(f"📡 С sstap.org не добавлено ни одного ключа (все {len(sstap_keys)} отклонены фильтром)", flush=True)

        all_keys_list = sorted(all_keys)
        with open(os.path.join(NEW_DIR, "all_new.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(all_keys_list))

        raw_buckets = {p: [] for p in PROTOCOLS}
        for line in all_keys_list:
            p = protocol_of(line)
            if p:
                raw_buckets[p].append(line)
        for p, items in raw_buckets.items():
            if items:
                write_chunks_by_protocol(NEW_BY_PROTO_DIR, p, items, CHUNK_SIZE)

        seen_ip = set()
        clean_keys = []
        for line in all_keys_list:
            host, port, scheme = extract_host_port_scheme(line)
            if not host:
                continue
            key = (host, port, scheme)
            if key not in seen_ip:
                seen_ip.add(key)
                clean_keys.append(line)

        for p in PROTOCOLS:
            items = [k for k in clean_keys if protocol_of(k) == p]
            if items:
                with open(os.path.join(CLEAN_DIR, f"{p}.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(items))

        print("\n✅ ГОТОВО!", flush=True)
        print(f"   📥 Всего ключей после фильтра: {len(all_keys_list)}", flush=True)
        print(f"   🔗 Уникальных IP:PORT:SCHEME: {len(clean_keys)}", flush=True)
        print(f"   🗑️ Выброшено мусора: {trash_count}", flush=True)
        print("\n📊 По протоколам:", flush=True)
        for p in PROTOCOLS:
            count = len([k for k in clean_keys if protocol_of(k) == p])
            if count > 0:
                print(f"   {p}: {count}", flush=True)
        return 0
    except Exception as e:
        print(f"FATAL ERROR in mirror.py: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())


























































































































































