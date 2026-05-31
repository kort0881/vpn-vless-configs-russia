#!/usr/bin/env python3
"""
filter_ru_sni.py — фильтр конфигов по реальному SNI/host.

Парсит URI каждого протокола, извлекает именно SNI/host параметр,
а не ищет подстроку по всей строке.

Поддерживает: vless://, vmess://, trojan://, ss://, hysteria2://, hy2://
"""

import os
import sys
import json
import base64
import re
from urllib.parse import urlparse, parse_qs, unquote

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_PATH, "data/githubmirror", "clean")
OUT_DIR = os.path.join(BASE_PATH, "data/githubmirror", "ru-sni")

# ─── Белый список доменов (SNI), которые считаем подходящими ───
# Включает RU-домены + популярные глобальные, используемые в Reality/TLS
GOOD_SNI_DOMAINS = [
    # --- RU соцсети ---
    "vk.com",
    "ok.ru",
    "vk.ru",
    "mail.ru",
    # --- RU поисковики/почта ---
    "yandex.ru",
    "ya.ru",
    "yastatic.net",
    "bk.ru",
    "inbox.ru",
    "list.ru",
    # --- RU банки ---
    "sberbank.ru",
    "online.sberbank.ru",
    "vtb.ru",
    "tinkoff.ru",
    "gazprombank.ru",
    "alfabank.ru",
    # --- RU маркетплейсы/сервисы ---
    "ozon.ru",
    "wildberries.ru",
    "avito.ru",
    "hh.ru",
    "gosuslugi.ru",
    "mos.ru",
    "rt.ru",
    "megafon.ru",
    "mts.ru",
    "beeline.ru",
    "tele2.ru",
    "rostelecom.ru",
    "dns-shop.ru",
    "citilink.ru",
    "lamoda.ru",
    "drom.ru",
    "ivi.ru",
    "kinopoisk.ru",
    # --- Глобальные домены (часто в Reality/TLS) ---
    "www.google.com",
    "google.com",
    "www.googleapis.com",
    "dl.google.com",
    "play.google.com",
    "fonts.googleapis.com",
    "www.gstatic.com",
    "www.microsoft.com",
    "microsoft.com",
    "update.microsoft.com",
    "www.apple.com",
    "apple.com",
    "cdn.apple.com",
    "www.cloudflare.com",
    "cloudflare.com",
    "one.one.one.one",
    "cdn.cloudflare.com",
    "www.amazon.com",
    "amazon.com",
    "aws.amazon.com",
    "www.mozilla.org",
    "mozilla.org",
    "addons.mozilla.org",
    "www.yahoo.com",
    "yahoo.com",
    "www.wikipedia.org",
    "wikipedia.org",
    "www.reddit.com",
    "reddit.com",
    "www.github.com",
    "github.com",
    "www.docker.com",
    "docker.com",
    "hub.docker.com",
    "registry-1.docker.io",
    "www.samsung.com",
    "samsung.com",
    "www.sony.com",
    "www.nvidia.com",
    "nvidia.com",
    "www.speedtest.net",
    "speedtest.net",
    "www.whatsapp.com",
    "whatsapp.com",
    "web.whatsapp.com",
    "www.instagram.com",
    "instagram.com",
    "www.facebook.com",
    "facebook.com",
    "www.twitter.com",
    "twitter.com",
    "x.com",
    "www.linkedin.com",
    "linkedin.com",
    "www.spotify.com",
    "spotify.com",
    "www.discord.com",
    "discord.com",
    "gateway.discord.gg",
    "cdn.discordapp.com",
    "www.twitch.tv",
    "twitch.tv",
    "www.tiktok.com",
    "tiktok.com",
    "www.steam.com",
    "store.steampowered.com",
    "steamcommunity.com",
    "www.epic.com",
    "www.ea.com",
    "www.paypal.com",
    "paypal.com",
    "www.visa.com",
    "www.mastercard.com",
    "www.netflix.com",
    "netflix.com",
    "www.youtube.com",
    "youtube.com",
    "yt3.ggpht.com",
    "www.bing.com",
    "bing.com",
    "www.office.com",
    "outlook.office365.com",
    "login.microsoftonline.com",
    "www.icloud.com",
    "icloud.com",
    "swdist.apple.com",
    "xp.apple.com",
    "www.tesla.com",
    "tesla.com",
    "www.oracle.com",
    "www.ibm.com",
    "www.intel.com",
    "www.amd.com",
    "www.hp.com",
    "www.dell.com",
    "www.lenovo.com",
    "www.asus.com",
    "www.cisco.com",
    "www.vmware.com",
    "www.adobe.com",
    "adobe.com",
    "creativecloud.adobe.com",
    "www.zoom.us",
    "zoom.us",
    "www.slack.com",
    "slack.com",
]

# Чёрный список — домены, которые точно НЕ подходят как SNI
BLACKLIST_DOMAINS = [
    "localhost",
    "example.com",
    "example.org",
    "test.com",
    "invalid",
    "local",
]

# ─── Построение множеств для быстрого поиска ───
_GOOD_SET = set(d.lower() for d in GOOD_SNI_DOMAINS)
_BLACK_SET = set(d.lower() for d in BLACKLIST_DOMAINS)


def _is_ip_address(s: str) -> bool:
    """Проверяет, является ли строка IP-адресом (v4 или v6)."""
    # IPv4
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', s):
        return True
    # IPv6 (упрощённая проверка)
    if ':' in s and re.match(r'^[0-9a-fA-F:]+$', s.replace('[', '').replace(']', '')):
        return True
    return False


def _domain_matches(sni: str) -> bool:
    """
    Проверяет, совпадает ли SNI с одним из доменов белого списка.
    Поддерживает точное совпадение и совпадение поддоменов.
    Например: 'cdn.vk.com' совпадёт с 'vk.com'.
    """
    sni = sni.lower().strip().rstrip('.')

    if not sni:
        return False

    if sni in _BLACK_SET:
        return False

    if _is_ip_address(sni):
        return False

    # Точное совпадение
    if sni in _GOOD_SET:
        return True

    # Совпадение поддомена: cdn.vk.com → vk.com
    for good in _GOOD_SET:
        if sni.endswith('.' + good):
            return True

    return False


def _strip_remark(uri: str) -> tuple[str, str]:
    """Отделяет #remark от URI. Возвращает (uri_без_remark, remark)."""
    idx = uri.rfind('#')
    if idx == -1:
        return uri, ''
    return uri[:idx], unquote(uri[idx + 1:])


def _extract_sni_vless_trojan(uri: str) -> str | None:
    """
    Извлекает SNI из vless:// или trojan:// URI.
    Приоритет: sni= > serverName= > host= > hostname из URI.
    """
    try:
        clean_uri, _ = _strip_remark(uri)

        # Парсим query параметры
        qmark = clean_uri.find('?')
        if qmark != -1:
            query_str = clean_uri[qmark + 1:]
            params = parse_qs(query_str, keep_blank_values=True)

            # Приоритет параметров
            for key in ('sni', 'serverName', 'server_name', 'host'):
                values = params.get(key, [])
                if values and values[0]:
                    return values[0].strip()

        # Fallback: hostname из URI
        # vless://uuid@hostname:port?...
        at_idx = clean_uri.find('@')
        if at_idx != -1:
            host_part = clean_uri[at_idx + 1:]
            # Убираем query
            qmark2 = host_part.find('?')
            if qmark2 != -1:
                host_part = host_part[:qmark2]
            # Убираем порт
            colon = host_part.rfind(':')
            if colon != -1:
                hostname = host_part[:colon]
            else:
                hostname = host_part

            hostname = hostname.strip().strip('[]')
            if hostname and not _is_ip_address(hostname):
                return hostname

    except Exception:
        pass

    return None


def _extract_sni_vmess(uri: str) -> str | None:
    """
    Извлекает SNI из vmess:// URI.
    VMess использует base64-encoded JSON.
    Приоритет: sni > host > add.
    """
    try:
        clean_uri, _ = _strip_remark(uri)

        # vmess://base64data
        b64_part = clean_uri[len('vmess://'):]

        # Добавляем padding если нужно
        padding = 4 - len(b64_part) % 4
        if padding != 4:
            b64_part += '=' * padding

        decoded = base64.b64decode(b64_part).decode('utf-8', errors='ignore')
        data = json.loads(decoded)

        # Приоритет полей
        for key in ('sni', 'host', 'add'):
            val = data.get(key, '')
            if val and isinstance(val, str):
                val = val.strip()
                if val and not _is_ip_address(val):
                    return val

    except Exception:
        pass

    return None


def _extract_sni_ss(uri: str) -> str | None:
    """
    Извлекает SNI из ss:// URI.
    SS может иметь plugin с obfs-host или SNI в параметрах.
    """
    try:
        clean_uri, _ = _strip_remark(uri)

        qmark = clean_uri.find('?')
        if qmark != -1:
            query_str = clean_uri[qmark + 1:]
            params = parse_qs(query_str, keep_blank_values=True)

            # Проверяем plugin параметры
            for key in ('sni', 'host', 'obfs-host', 'server_name'):
                values = params.get(key, [])
                if values and values[0]:
                    return values[0].strip()

            # Проверяем внутри plugin=
            plugin_vals = params.get('plugin', [])
            if plugin_vals:
                plugin_str = plugin_vals[0]
                # plugin=obfs-local;obfs=http;obfs-host=example.com
                for part in plugin_str.split(';'):
                    if '=' in part:
                        k, v = part.split('=', 1)
                        k = k.strip()
                        v = v.strip()
                        if k in ('obfs-host', 'host', 'sni', 'server_name') and v:
                            return v

    except Exception:
        pass

    return None


def _extract_sni_hysteria(uri: str) -> str | None:
    """
    Извлекает SNI из hysteria2:// или hy2:// URI.
    """
    try:
        clean_uri, _ = _strip_remark(uri)

        qmark = clean_uri.find('?')
        if qmark != -1:
            query_str = clean_uri[qmark + 1:]
            params = parse_qs(query_str, keep_blank_values=True)

            for key in ('sni', 'server_name', 'host'):
                values = params.get(key, [])
                if values and values[0]:
                    return values[0].strip()

        # Fallback: hostname
        scheme_end = clean_uri.find('://')
        if scheme_end != -1:
            rest = clean_uri[scheme_end + 3:]
            at_idx = rest.find('@')
            if at_idx != -1:
                host_part = rest[at_idx + 1:]
            else:
                host_part = rest

            qmark2 = host_part.find('?')
            if qmark2 != -1:
                host_part = host_part[:qmark2]

            colon = host_part.rfind(':')
            if colon != -1:
                hostname = host_part[:colon]
            else:
                hostname = host_part

            hostname = hostname.strip().strip('[]')
            if hostname and not _is_ip_address(hostname):
                return hostname

    except Exception:
        pass

    return None


def extract_sni(line: str) -> str | None:
    """
    Главная функция: определяет протокол и извлекает реальный SNI/host.
    Возвращает домен или None.
    """
    stripped = line.strip()
    lower = stripped.lower()

    if lower.startswith('vless://') or lower.startswith('trojan://'):
        return _extract_sni_vless_trojan(stripped)

    elif lower.startswith('vmess://'):
        return _extract_sni_vmess(stripped)

    elif lower.startswith('ss://'):
        return _extract_sni_ss(stripped)

    elif lower.startswith('hysteria2://') or lower.startswith('hy2://'):
        return _extract_sni_hysteria(stripped)

    return None


def is_good_config(line: str) -> bool:
    """
    Проверяет, подходит ли конфиг:
    1. Извлекает реальный SNI
    2. Проверяет по белому списку доменов
    """
    sni = extract_sni(line)
    if sni is None:
        return False
    return _domain_matches(sni)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    total_in = 0
    total_out = 0

    for fname in sorted(os.listdir(CLEAN_DIR)):
        if not fname.endswith(".txt"):
            continue

        src_path = os.path.join(CLEAN_DIR, fname)
        dst_path = os.path.join(OUT_DIR, fname)

        good_configs = []
        file_total = 0

        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                file_total += 1

                if is_good_config(line):
                    good_configs.append(line)

        with open(dst_path, "w", encoding="utf-8") as f:
            f.write("\n".join(good_configs))
            if good_configs:
                f.write("\n")

        total_in += file_total
        total_out += len(good_configs)

        print(f"  {fname}: {file_total} → {len(good_configs)} (SNI-filtered)")

    print(f"\n{'='*50}")
    print(f"  Всего входных:  {total_in}")
    print(f"  Прошли фильтр:  {total_out}")
    print(f"  Отброшено:      {total_in - total_out}")
    print(f"{'='*50}")
    print(f"Готово → {OUT_DIR}")


if __name__ == "__main__":
    main()

