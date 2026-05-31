#!/usr/bin/env python3
"""
filter_ru_sni_local.py — экспериментальный фильтр именно по RU‑SNI.

Берёт конфиги из githubmirror/clean/*.txt,
извлекает реальный SNI/host (как в основном фильтре),
и оставляет только те, где SNI в списке RU‑доменов.

Результат пишет в githubmirror/ru-sni-local/*.txt
"""

import os
import re
import json
import base64
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path

# Определяем корень репозитория (поднимаемся на уровень выше из scripts/)
BASE_DIR = Path(__file__).parent.parent
CLEAN_DIR = BASE_DIR / "data" / "githubmirror" / "clean"
OUT_DIR = BASE_DIR / "data" / "githubmirror" / "ru-sni-local"

# Только RU-домены, которые хотим тестировать как SNI
RU_SNI_DOMAINS = [
    "vk.com", "ok.ru", "vk.ru",
    "yandex.ru", "ya.ru", "yastatic.net",
    "mail.ru", "bk.ru", "inbox.ru", "list.ru",
    "sberbank.ru", "online.sberbank.ru",
    "vtb.ru", "tinkoff.ru", "gazprombank.ru", "alfabank.ru",
    "ozon.ru", "wildberries.ru", "avito.ru",
    "hh.ru", "gosuslugi.ru", "mos.ru",
    "megafon.ru", "mts.ru", "beeline.ru", "tele2.ru", "rt.ru",
]

_RU_SET = set(d.lower() for d in RU_SNI_DOMAINS)


def _is_ip_address(s: str) -> bool:
    if not s:
        return False
    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', s):
        return True
    if ':' in s and re.match(r'^[0-9a-fA-F:]+$', s.replace('[', '').replace(']', '')):
        return True
    return False


def _strip_remark(uri: str) -> tuple[str, str]:
    idx = uri.rfind('#')
    if idx == -1:
        return uri, ''
    return uri[:idx], unquote(uri[idx + 1:])


def _domain_is_ru_sni(sni: str) -> bool:
    sni = sni.lower().strip().rstrip('.')
    if not sni or _is_ip_address(sni):
        return False
    if sni in _RU_SET:
        return True
    for dom in _RU_SET:
        if sni.endswith("." + dom):
            return True
    return False


def _extract_sni_vless_trojan(uri: str) -> str | None:
    try:
        clean_uri, _ = _strip_remark(uri)
        qmark = clean_uri.find('?')
        if qmark != -1:
            query_str = clean_uri[qmark + 1:]
            params = parse_qs(query_str, keep_blank_values=True)
            for key in ('sni', 'serverName', 'server_name', 'host'):
                v = params.get(key, [])
                if v and v[0]:
                    return v[0].strip()
        at_idx = clean_uri.find('@')
        if at_idx != -1:
            host_part = clean_uri[at_idx + 1:]
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
    except:
        pass
    return None


def _extract_sni_vmess(uri: str) -> str | None:
    try:
        clean_uri, _ = _strip_remark(uri)
        b64_part = clean_uri[len("vmess://"):]
        pad = 4 - (len(b64_part) % 4)
        if pad != 4:
            b64_part += "=" * pad
        decoded = base64.b64decode(b64_part).decode("utf-8", errors="ignore")
        data = json.loads(decoded)
        for key in ("sni", "host", "add"):
            val = data.get(key, "")
            if isinstance(val, str):
                val = val.strip()
                if val and not _is_ip_address(val):
                    return val
    except:
        pass
    return None


def _extract_sni_ss(uri: str) -> str | None:
    try:
        clean_uri, _ = _strip_remark(uri)
        qmark = clean_uri.find("?")
        if qmark != -1:
            query_str = clean_uri[qmark + 1:]
            params = parse_qs(query_str, keep_blank_values=True)
            for key in ("sni", "host", "obfs-host", "server_name"):
                v = params.get(key, [])
                if v and v[0]:
                    return v[0].strip()
            plugin_vals = params.get("plugin", [])
            if plugin_vals:
                plugin_str = plugin_vals[0]
                for part in plugin_str.split(";"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        k, v = k.strip(), v.strip()
                        if k in ("obfs-host", "host", "sni", "server_name") and v:
                            return v
    except:
        pass
    return None


def _extract_sni_hysteria(uri: str) -> str | None:
    try:
        clean_uri, _ = _strip_remark(uri)
        qmark = clean_uri.find("?")
        if qmark != -1:
            query_str = clean_uri[qmark + 1:]
            params = parse_qs(query_str, keep_blank_values=True)
            for key in ("sni", "server_name", "host"):
                v = params.get(key, [])
                if v and v[0]:
                    return v[0].strip()
        scheme_end = clean_uri.find("://")
        if scheme_end != -1:
            rest = clean_uri[scheme_end + 3:]
            at_idx = rest.find("@")
            if at_idx != -1:
                host_part = rest[at_idx + 1:]
            else:
                host_part = rest
            qmark2 = host_part.find("?")
            if qmark2 != -1:
                host_part = host_part[:qmark2]
            colon = host_part.rfind(":")
            if colon != -1:
                hostname = host_part[:colon]
            else:
                hostname = host_part
            hostname = hostname.strip().strip("[]")
            if hostname and not _is_ip_address(hostname):
                return hostname
    except:
        pass
    return None


def extract_sni(line: str) -> str | None:
    s = line.strip()
    lower = s.lower()
    if lower.startswith("vless://") or lower.startswith("trojan://"):
        return _extract_sni_vless_trojan(s)
    if lower.startswith("vmess://"):
        return _extract_sni_vmess(s)
    if lower.startswith("ss://"):
        return _extract_sni_ss(s)
    if lower.startswith("hysteria2://") or lower.startswith("hy2://"):
        return _extract_sni_hysteria(s)
    return None


def is_ru_sni_config(line: str) -> bool:
    sni = extract_sni(line)
    if not sni:
        return False
    return _domain_is_ru_sni(sni)


def main():
    # Проверяем, существует ли входная директория
    if not CLEAN_DIR.exists():
        print(f"Ошибка: директория {CLEAN_DIR} не найдена")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total_in = 0
    total_out = 0

    for fname in sorted(os.listdir(CLEAN_DIR)):
        if not fname.endswith(".txt"):
            continue

        src_path = CLEAN_DIR / fname
        dst_path = OUT_DIR / fname

        ru_configs = []
        file_total = 0

        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                file_total += 1
                if is_ru_sni_config(line):
                    ru_configs.append(line)

        with open(dst_path, "w", encoding="utf-8") as f:
            if ru_configs:
                f.write("\n".join(ru_configs) + "\n")
            # Если нет конфигов, создаём пустой файл (или не создаём? оставим пустой)

        total_in += file_total
        total_out += len(ru_configs)
        print(f"{fname}: {file_total} → {len(ru_configs)} (RU-SNI)")

    print("\n" + "=" * 50)
    print(f"Всего входных:  {total_in}")
    print(f"Прошли RU-SNI:  {total_out}")
    print(f"Отброшено:      {total_in - total_out}")
    print("=" * 50)
    print(f"Готово → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    exit(main())
