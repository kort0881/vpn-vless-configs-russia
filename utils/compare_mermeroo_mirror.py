#!/usr/bin/env python3
import os
import json
from urllib.parse import urlparse
from pathlib import Path

# Определяем корень репозитория (поднимаемся из utils/ в корень)
BASE_PATH = Path(__file__).parent.parent

CONFIG_SOURCES_FILE = BASE_PATH / "data" / "config_sources.json"
MERMEROO_FILE = BASE_PATH / "mermeroo_sources.txt"   # этот файл создаётся parse_mermeroo.py в корне? Проверим.
OUT_FILE = BASE_PATH / "mermeroo_only_new_for_mirror.txt"
OUT_EXTRA_FILE = BASE_PATH / "mermeroo_extra_sources.txt"

def load_mermeroo_sources(path):
    if not path.exists():
        print(f"{path} не найден")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def load_config_sources():
    """Загружает URL из data/config_sources.json"""
    urls = set()
    if CONFIG_SOURCES_FILE.exists():
        try:
            with open(CONFIG_SOURCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for u in data:
                        if isinstance(u, str) and u.strip():
                            urls.add(u.strip())
                print(f"📂 Загружено {len(urls)} источников из {CONFIG_SOURCES_FILE}")
        except Exception as e:
            print(f"⚠️ Не удалось прочитать config_sources.json: {e}")
    else:
        print(f"⚠️ Файл {CONFIG_SOURCES_FILE} не найден")
    return urls

def extract_repo_key(url: str) -> str:
    if "raw.githubusercontent.com" in url:
        parts = url.split("/")
        try:
            i = parts.index("raw.githubusercontent.com")
            owner = parts[i + 1]
            repo = parts[i + 2]
            return f"{owner}/{repo}"
        except Exception:
            return url

    if "github.com" in url and "/raw/" in url:
        parts = url.split("/")
        try:
            i = parts.index("github.com")
            owner = parts[i + 1]
            repo = parts[i + 2]
            return f"{owner}/{repo}"
        except Exception:
            return url

    return url

def is_good_source_url(url: str) -> bool:
    u = urlparse(url)
    if not u.scheme.startswith("http"):
        return False
    host = (u.netloc or "").lower()
    path = (u.path or "").lower()

    # Git raw / CDN raw
    if "raw.githubusercontent.com" in host:
        return True
    if "github.com" in host and "/raw/" in path:
        return True
    if "gitlab.com" in host and "/-/raw/" in path:
        return True
    if "bitbucket.org" in host and "/raw/" in path:
        return True
    if "jsdelivr.net" in host and "/gh/" in path:
        return True

    bad_substrings = [
        "/clash/proxies",
        "/api/v1/client/subscribe",
        "/subscribe?",
        "token=",
        "/wp-content/",
        ".html",
        ".htm",
        "/free-ss",
        "/free-ssr",
        "/v2ray/",
        "/free/",
    ]
    for b in bad_substrings:
        if b in url.lower():
            return False

    good_exts = (".txt", ".yaml", ".yml", ".json")
    if any(path.endswith(ext) for ext in good_exts):
        return True

    return False

def main():
    mer_all = load_mermeroo_sources(MERMEROO_FILE)
    print(f"Всего в mermeroo_sources.txt: {len(mer_all)}")

    mer_filtered = [u for u in mer_all if is_good_source_url(u)]
    print(f"Из них после фильтра по типу URL: {len(mer_filtered)}")

    # Только один источник: config_sources.json
    known_urls = load_config_sources()

    mer_new_urls = [u for u in mer_filtered if u not in known_urls]

    known_repos = {extract_repo_key(u) for u in known_urls}
    mer_repos = {extract_repo_key(u) for u in mer_filtered}
    mer_new_repos = sorted(r for r in mer_repos if r not in known_repos)

    print(f"Новых URL (нет в Mirror, после фильтра): {len(mer_new_urls)}")
    print(f"Новых репозиториев-доноров: {len(mer_new_repos)}")
    for r in mer_new_repos:
        print("  ", r)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(mer_new_urls))
    print(f"\nСписок новых отфильтрованных URL сохранён в {OUT_FILE}")

    mer_bad = [u for u in mer_all if u not in mer_filtered]
    if mer_bad:
        with open(OUT_EXTRA_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(set(mer_bad))))
        print(f"Дополнительные источники сохранены в {OUT_EXTRA_FILE}")

if __name__ == "__main__":
    main()
