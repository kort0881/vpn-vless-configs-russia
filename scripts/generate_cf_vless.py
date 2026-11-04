#!/usr/bin/env python3
"""
Экстрактор лучших VLESS-конфигов из собранных данных.
Берёт живые ноды из clean/vless.txt, сортирует по задержке,
сохраняет топ-50 в data/githubmirror/new/cf_fresh.txt.

v2: fix — задержка в clean/vless.txt URL-encoded (%5B123ms%7C...),
    старая регулярка "\\| (\\d+)ms" не срабатывала никогда,
    все ключи получали 99999.0, топ-50 был «первые 50 строк файла».
    + дедупликация по ключу без #комментария.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

BASE_DIR = Path(__file__).parent.parent
CLEAN_FILE = BASE_DIR / "data" / "githubmirror" / "clean" / "vless.txt"
OUTPUT_FILE = BASE_DIR / "data" / "githubmirror" / "new" / "cf_fresh.txt"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

COUNT = 50

# Задержка пишется в #комментарии, который URL-кодируется:
#   #[123ms|j45|rc1/1|7cat|TG+VLESS|@channel]
#   #%5B123ms%7Cj45%7Crc1%2F1%7C7cat%7CTG+VLESS%7C%40channel%5D
# Поэтому сначала unquote, потом поиск.
_MS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*ms")


def extract_delay(line: str) -> float:
    """Возвращает задержку в мс из комментария. 99999.0 — если не нашли."""
    if "#" in line:
        comment = unquote(line.split("#", 1)[1])
        m = _MS_RE.search(comment)
        if m:
            return float(m.group(1))
    # fallback: ищем по всей строке (если формат поменяется)
    decoded = unquote(line)
    m = _MS_RE.search(decoded)
    if m:
        return float(m.group(1))
    return 99999.0


def has_delay(line: str) -> bool:
    return extract_delay(line) < 99999.0


def config_identity(line: str) -> str:
    """Ключ без #комментария — чтобы считать один хост:порт:uuid одной нодой."""
    return line.split("#", 1)[0]


def main() -> int:
    print("=== Экстрактор лучших VLESS-конфигов ===")
    if not CLEAN_FILE.exists():
        print(f"❌ Файл {CLEAN_FILE} не найден")
        return 1

    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    lines = [l for l in raw_lines if l.startswith("vless://") and len(l) > 20]
    if not lines:
        print("❌ Нет VLESS-конфигов в clean/vless.txt")
        return 1

    # дедуп по ключу без комментария (комментарий с latency мог обновиться)
    seen: set[str] = set()
    unique: list[str] = []
    for line in lines:
        ident = config_identity(line)
        if ident in seen:
            continue
        seen.add(ident)
        unique.append(line)

    total = len(unique)
    with_delay = [l for l in unique if has_delay(l)]
    without_delay = [l for l in unique if not has_delay(l)]

    with_delay.sort(key=extract_delay)
    top = with_delay[:COUNT]

    # добиваем «без задержки» только если реальных не хватило до COUNT
    if len(top) < COUNT:
        top += without_delay[: COUNT - len(top)]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(top) + "\n")

    print(f"✅ Сохранено {len(top)} лучших VLESS-конфигов из {total} уникальных")
    print(f"📂 Файл: {OUTPUT_FILE}")

    if with_delay:
        real = [l for l in top if has_delay(l)]
        print(f"⚡ С реальной задержкой в топе: {len(real)}/{len(top)}")
        if real:
            print(f"   delay: {extract_delay(real[0]):.0f}ms — {extract_delay(real[-1]):.0f}ms")
    else:
        print("⚠️  Ни у одной ноды нет задержки в комментарии — все delay=99999")
        print("   Проверь формат первой строки:")
        print(f"   {unique[0][:120]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
