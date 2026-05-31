#!/usr/bin/env python3
"""
Безопасный рефакторинг репозитория kort0881/vpn-vless-configs-russia.
Запускать в корне репозитория (там, где mirror.py, main.py и т.д.)
"""

import os
import shutil
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).parent.absolute()

# Карта перемещений: "относительный_исходник" -> "новый_относительный_путь"
MOVE_MAP = {
    # Скрипты
    "mirror.py": "scripts/mirror.py",
    "main.py": "scripts/main.py",
    "my_vless_generator.py": "scripts/my_vless_generator.py",
    "filter_ru_sni.py": "scripts/filter_ru_sni.py",
    "filter_ru_sni_local.py": "scripts/filter_ru_sni_local.py",
    "generate_cf_vless.py": "scripts/generate_cf_vless.py",
    "proxy_collect_merge.py": "scripts/proxy_collect_merge.py",
    "parse_mermeroo.py": "scripts/parse_mermeroo.py",
    "compare_mermeroo_mirror.py": "utils/compare_mermeroo_mirror.py",
    "merge_mermeroo_to_config_sources.py": "scripts/merge_mermeroo_to_config_sources.py",
    "convert_extra_sources.py": "scripts/convert_extra_sources.py",
    "merge_proxy_sources.py": "scripts/merge_proxy_sources.py",  # если есть
    # Данные
    "config_sources.json": "data/config_sources.json",
    "stats.json": "data/stats.json",
    "mermeroo_sources.txt": "data/mermeroo_sources.txt",
    "proxy_sources.txt": "data/proxy_sources.txt",
    "extra_sources.txt": "data/extra_sources.txt",
    "test_upload.txt": "archive/test_upload.txt",
    # Папки
    "githubmirror/": "data/githubmirror/",
    "my_sources/": "archive/my_sources/",
    "logs/": "data/logs/",
    "subscriptions/": "archive/subscriptions/",
    "vpn-files/": "archive/vpn-files/",
    "__pycache__/": "archive/__pycache__/",
}

# Файлы, в которых нужно заменить пути (Python и YAML)
PATH_FILES = [
    "scripts/mirror.py",
    "scripts/main.py",
    "scripts/my_vless_generator.py",
    "scripts/filter_ru_sni.py",
    "scripts/filter_ru_sni_local.py",
    "scripts/generate_cf_vless.py",
    "scripts/merge_mermeroo_to_config_sources.py",
    "scripts/convert_extra_sources.py",
    "scripts/parse_mermeroo.py",
    "scripts/proxy_collect_merge.py",
    "utils/compare_mermeroo_mirror.py",
    ".github/workflows/full-update.yml",
]

# Замены путей
PATH_REPLACEMENTS = [
    ('"githubmirror/', '"data/githubmirror/'),
    ("'githubmirror/", "'data/githubmirror/"),
    ('"githubmirror"', '"data/githubmirror"'),
    ("'githubmirror'", "'data/githubmirror'"),
    ('/githubmirror/', '/data/githubmirror/'),
    ('"my_sources/', '"archive/my_sources/'),
    ("'my_sources/", "'archive/my_sources/"),
    ('"logs/', '"data/logs/'),
    ("'logs/", "'data/logs/"),
    ('"config_sources.json', '"data/config_sources.json'),
    ("'config_sources.json", "'data/config_sources.json"),
    ('"stats.json', '"data/stats.json'),
    ("'stats.json", "'data/stats.json"),
]

def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def safe_move(src: Path, dst: Path) -> bool:
    if not src.exists():
        print(f"⚠️ Пропуск {src} – не существует")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if file_sha256(src) == file_sha256(dst):
            print(f"⏭️ {src} уже есть в {dst} (одинаковый) – удаляю оригинал")
            src.unlink()
            return True
        else:
            print(f"❌ {dst} существует и отличается! Пропускаем {src}")
            return False
    shutil.copy2(src, dst)
    if file_sha256(src) == file_sha256(dst):
        print(f"✅ Перемещён: {src} -> {dst}")
        src.unlink()
        return True
    else:
        print(f"❌ Ошибка копирования: хеши не совпадают! {src} не тронут")
        return False

def move_directory(src_dir: Path, dst_dir: Path) -> bool:
    if not src_dir.exists():
        print(f"⚠️ Папка {src_dir} не существует")
        return False
    all_ok = True
    for item in src_dir.glob('**/*'):
        if item.is_file():
            rel = item.relative_to(src_dir)
            target = dst_dir / rel
            all_ok &= safe_move(item, target)
    if all_ok and not any(src_dir.iterdir()):
        src_dir.rmdir()
        print(f"🗑️ Удалена пустая папка {src_dir}")
    return all_ok

def update_paths_in_files():
    for rel_path in PATH_FILES:
        path = REPO_ROOT / rel_path
        if not path.exists():
            print(f"⚠️ {rel_path} не найден, пропускаем")
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        original = content
        for old, new in PATH_REPLACEMENTS:
            content = content.replace(old, new)
        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✏️ Обновлены пути в {rel_path}")
        else:
            print(f"ℹ️ {rel_path} не требует изменений")

def main():
    print("=== Рефакторинг репозитория ===")
    input("Убедитесь, что вы в корне репозитория (там где mirror.py). Нажмите Enter...")
    
    # Создаём папки
    for folder in ['scripts', 'data', 'utils', 'archive']:
        (REPO_ROOT / folder).mkdir(exist_ok=True)
    print("📁 Папки созданы.")
    
    # Перемещаем файлы и папки
    for src_rel, dst_rel in MOVE_MAP.items():
        src = REPO_ROOT / src_rel
        dst = REPO_ROOT / dst_rel
        if src.is_dir():
            move_directory(src, dst)
        else:
            safe_move(src, dst)
    
    # Обновляем пути внутри скриптов
    update_paths_in_files()
    
    print("\n✅ Рефакторинг завершён.")
    print("Проверьте изменения: git status")
    print("Затем: git add . && git commit -m 'refactor: reorganize repo structure'")
    print("И: git push origin main   (или в новую ветку)")

if __name__ == "__main__":
    main()