#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from urllib.parse import urlparse

import requests

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

from mirror import URLS_BASE, CONFIG_SOURCES_FILE  # mirror.py в корне репо

MANIFEST_URL = "https://github.com/cook369/proxy-collect/raw/refs/heads/main/dist/manifest.json"
OUT_FILE = os.path.join(BASE_PATH, "proxy_collect_only_new_for_mirror.txt")
OUT_EXTRA_FILE = os.path.join(BASE_PATH, "proxy_collect_extra_sources.txt")


def load_config_sources():
    urls = set()
    if os.path.exists(CONFIG_SOURCES_FILE):
        try:
            with open(CONFIG_SOURCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for u in data:
                    if isinstance(u, str) and u.strip():
                        urls.add(u.strip())
        except Exception as e:
            print(f"⚠️ Не удалось прочитать config_sources.json: {e}")
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


def load_manifest_urls():
    try:
        r = requests.get(MANIFEST_URL, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"⚠️ Не удалось скачать/разобрать manifest.json: {e}")
        return []

    urls = []
    sites = data.get("sites", {})
    for site_name, info in sites.items():
        files = info.get("files", {})
        for fname, fmeta in files.items():
            if not isinstance(fmeta, dict):
                continue
            url = fmeta.get("url")
            success = fmeta.get("success", False)
            if isinstance(url, str) and url.strip():
                # можно оставить и неуспешные, если хочешь вручную проверить
                urls.append(url.strip())
    return urls


# --- добавлено: автозапись в config_sources.json ---
def save_sources(urls: set[str]) -> None:
    data = sorted(urls)
    with open(CONFIG_SOURCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Записано {len(data)} источников в {CONFIG_SOURCES_FILE}")
# ---------------------------------------------------


def main():
    manifest_urls_all = load_manifest_urls()
    print(f"Всего URL из manifest.json: {len(manifest_urls_all)}")

    manifest_filtered = [u for u in manifest_urls_all if is_good_source_url(u)]
    print(f"Из них после фильтра по типу URL: {len(manifest_filtered)}")

    known_urls = set(URLS_BASE)
    known_urls |= load_config_sources()

    manifest_new_urls = [u for u in manifest_filtered if u not in known_urls]

    known_repos = {extract_repo_key(u) for u in known_urls}
    man_repos = {extract_repo_key(u) for u in manifest_filtered}
    man_new_repos = sorted(r for r in man_repos if r not in known_repos)

    print(f"Новых URL (нет в Mirror, после фильтра): {len(manifest_new_urls)}")
    print(f"Новых репозиториев-доноров: {len(man_new_repos)}")
    for r in man_new_repos:
        print("  ", r)

    # сохраняем список только новых, как и раньше
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_new_urls))
    print(f"\nСписок новых отфильтрованных URL сохранён в {OUT_FILE}")

    man_bad = [u for u in manifest_urls_all if u not in manifest_filtered]
    if man_bad:
        with open(OUT_EXTRA_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(set(man_bad))))
        print(f"Дополнительные источники (подозрительные/нестандартные) сохранены в {OUT_EXTRA_FILE}")

    # --- добавлено: автоприменение в config_sources.json ---
    merged = known_urls.union(manifest_filtered)
    added = len(merged) - len(known_urls)
    print(f"\n🔹 Всего известных URL после слияния: {len(merged)} (добавлено {added})")
    if added > 0:
        save_sources(merged)
    else:
        print("ℹ️ Новых источников нет, config_sources.json не меняем")
    # ------------------------------------------------------


if __name__ == "__main__":
    main()
