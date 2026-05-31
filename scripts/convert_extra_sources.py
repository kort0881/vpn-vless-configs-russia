#!/usr/bin/env python3
import os
import requests
import yaml
from urllib.parse import urlparse

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
EXTRA_FILE = os.path.join(BASE_PATH, "mermeroo_extra_sources.txt")
OUT_FILE = os.path.join(BASE_PATH, "extra_converted_for_mirror.txt")

PROTO_PREFIXES = ("vless://", "vmess://", "trojan://", "ss://", "ssr://", "hysteria://", "hysteria2://", "hy2://", "tuic://")


def load_extra_sources():
    if not os.path.exists(EXTRA_FILE):
        print(f"{EXTRA_FILE} не найден")
        return []
    with open(EXTRA_FILE, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def extract_uris_from_text(text: str):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if any(line.startswith(p) for p in PROTO_PREFIXES):
            out.append(line)
    return out


def extract_uris_from_yaml(text: str):
    out = []
    try:
        data = yaml.safe_load(text)
    except Exception:
        return out

    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        elif isinstance(obj, str):
            s = obj.strip()
            if any(s.startswith(p) for p in PROTO_PREFIXES):
                out.append(s)

    walk(data)
    return out


def looks_yaml_like(url: str) -> bool:
    u = urlparse(url)
    path = (u.path or "").lower()
    if any(path.endswith(ext) for ext in (".yaml", ".yml")):
        return True
    if "clash" in path or "proxies" in path or "general" in path:
        return True
    return False


def main():
    urls = load_extra_sources()
    print(f"Всего extra-источников: {len(urls)}")

    all_uris = set()

    for i, url in enumerate(urls, 1):
        print(f"{i}/{len(urls)}: {url}")
        try:
            r = requests.get(url, timeout=20)
            if r.status_code != 200:
                print(f"  ❌ HTTP {r.status_code}")
                continue
            text = r.text

            if looks_yaml_like(url):
                uris = extract_uris_from_yaml(text)
            else:
                uris = extract_uris_from_text(text)

            print(f"  ✅ найдено URI: {len(uris)}")
            for u in uris:
                all_uris.add(u)
        except Exception as e:
            print(f"  ⚠️ ошибка: {e}")

    all_uris_list = sorted(all_uris)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(all_uris_list))

    print(f"\nВсего уникальных URI: {len(all_uris_list)}")
    print(f"Результат сохранён в {OUT_FILE}")


if __name__ == "__main__":
    main()
