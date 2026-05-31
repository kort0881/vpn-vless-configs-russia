#!/usr/bin/env python3
"""
main.py - Основной скрипт для проверки и обновления VPN конфигураций
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import subprocess
from urllib.parse import urlparse

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

BASE_DIR = Path(__file__).parent.parent  # корень репозитория
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "logs"
STATS_FILE = BASE_DIR / "data" / "stats.json"

LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

def setup_logging():
    log_file = LOGS_DIR / f"vpn-checker-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# ОСНОВНЫЕ ФУНКЦИИ
# ============================================================================

def run_script(script_name: str, description: str, timeout: int = 300) -> bool:
    """Запускает скрипт из папки scripts/"""
    logger.info(f"🚀 Запуск {script_name} ({description})...")
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        logger.error(f"❌ Скрипт {script_name} не найден в {SCRIPTS_DIR}")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"  → {line}")
        if result.returncode != 0:
            logger.error(f"❌ {script_name} завершился с кодом {result.returncode}")
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        logger.error(f"  ⚠️  {line}")
            return False
        logger.info(f"✅ {script_name} завершён успешно")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {script_name} превысил timeout ({timeout}с)")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при запуске {script_name}: {e}")
        return False

def run_mirror_script():
    return run_script("mirror.py", "Загрузка и фильтрация по РФ/СНГ/Европа", timeout=600)

def generate_cf_vless():
    return run_script("generate_cf_vless.py", "50 новых CF-VLESS", timeout=90)

def merge_cf_with_clean():
    clean_path = BASE_DIR / "data" / "githubmirror" / "clean" / "vless.txt"
    cf_fresh_path = BASE_DIR / "data" / "githubmirror" / "new" / "cf_fresh.txt"
    if not cf_fresh_path.exists():
        logger.info("ℹ️ Нет свежих CF-конфигов (cf_fresh.txt) – пропускаем слияние")
        return True
    old_configs = []
    if clean_path.exists():
        try:
            with open(clean_path, 'r', encoding='utf-8') as f:
                old_configs = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"❌ Ошибка чтения {clean_path}: {e}")
            return False
    try:
        with open(cf_fresh_path, 'r', encoding='utf-8') as f:
            new_configs = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"❌ Ошибка чтения {cf_fresh_path}: {e}")
        return False
    if not new_configs:
        logger.info("ℹ️ cf_fresh.txt пуст – нечего добавлять")
        return True
    def extract_key(line):
        try:
            u = urlparse(line)
            return (u.hostname, u.port or 443, u.scheme)
        except:
            return None
    old_keys = {extract_key(c) for c in old_configs if extract_key(c)}
    unique_new = []
    for cfg in new_configs:
        key = extract_key(cfg)
        if key and key not in old_keys:
            unique_new.append(cfg)
            old_keys.add(key)
    if not unique_new:
        logger.info("✅ Все новые CF-конфиги уже есть в clean/vless.txt")
        return True
    all_configs = old_configs + unique_new
    all_configs.sort()
    try:
        with open(clean_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_configs))
    except Exception as e:
        logger.error(f"❌ Ошибка записи в {clean_path}: {e}")
        return False
    logger.info(f"🔄 Добавлено {len(unique_new)} новых CF-VLESS в {clean_path}")
    logger.info(f"📊 Всего в clean/vless.txt теперь: {len(all_configs)}")
    return True

def run_filter_script():
    return run_script("filter_ru_sni.py", "Фильтр по реальному SNI (CDN+RU)", timeout=120)

def run_filter_local_script():
    return run_script("filter_ru_sni_local.py", "Экспериментальный фильтр по RU-SNI", timeout=120)

def collect_statistics():
    logger.info("📊 Сбор статистики...")
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "github_mirror_clean": {},
            "ru_sni_filtered": {},
            "totals": {"clean": 0, "ru_sni": 0, "filter_rate": 0.0}
        }
        clean_dir = BASE_DIR / "data" / "githubmirror" / "clean"
        if clean_dir.exists():
            logger.info("  📁 githubmirror/clean:")
            for protocol_file in sorted(clean_dir.glob("*.txt")):
                try:
                    with open(protocol_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [l.strip() for l in f if l.strip()]
                    count = len(lines)
                    protocol = protocol_file.stem
                    stats["github_mirror_clean"][protocol] = count
                    stats["totals"]["clean"] += count
                    logger.info(f"    • {protocol:12s}: {count:5d} конфигов")
                except Exception as e:
                    logger.warning(f"    ⚠️  Ошибка чтения {protocol_file.name}: {e}")
        else:
            logger.warning("  ⚠️  Директория githubmirror/clean не найдена")
        ru_sni_dir = BASE_DIR / "data" / "githubmirror" / "ru-sni"
        if ru_sni_dir.exists():
            logger.info("  📁 githubmirror/ru-sni:")
            for protocol_file in sorted(ru_sni_dir.glob("*.txt")):
                try:
                    with open(protocol_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = [l.strip() for l in f if l.strip()]
                    count = len(lines)
                    protocol = protocol_file.stem
                    stats["ru_sni_filtered"][protocol] = count
                    stats["totals"]["ru_sni"] += count
                    clean_count = stats["github_mirror_clean"].get(protocol, 0)
                    rate = (count / clean_count * 100) if clean_count > 0 else 0
                    logger.info(f"    • {protocol:12s}: {count:5d} конфигов ({rate:5.1f}% от clean)")
                except Exception as e:
                    logger.warning(f"    ⚠️  Ошибка чтения {protocol_file.name}: {e}")
        else:
            logger.warning("  ⚠️  Директория githubmirror/ru-sni не найдена")
        cf_fresh_path = BASE_DIR / "data" / "githubmirror" / "new" / "cf_fresh.txt"
        new_cf_count = 0
        if cf_fresh_path.exists():
            with open(cf_fresh_path, 'r', encoding='utf-8') as f:
                new_cf_count = sum(1 for line in f if line.strip())
        stats["new_cf_added"] = new_cf_count
        logger.info(f"  ✨ Новых CF-VLESS в этом запуске: {new_cf_count}")
        total_clean = stats["totals"]["clean"]
        total_ru_sni = stats["totals"]["ru_sni"]
        if total_clean > 0:
            filter_rate = (total_ru_sni / total_clean) * 100
            stats["totals"]["filter_rate"] = round(filter_rate, 2)
        logger.info("")
        logger.info("  " + "─" * 50)
        logger.info(f"  📈 ИТОГО:")
        logger.info(f"    Clean (после geo-фильтра):   {total_clean:6d}")
        logger.info(f"    RU-SNI (после SNI-фильтра):  {total_ru_sni:6d}")
        logger.info(f"    Прошло фильтр:               {stats['totals']['filter_rate']:6.1f}%")
        logger.info("  " + "─" * 50)
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Статистика сохранена: {STATS_FILE}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при сборе статистики: {e}", exc_info=True)
        return False

def check_dependencies():
    logger.info("🔍 Проверка наличия скриптов...")
    required_scripts = ["mirror.py", "generate_cf_vless.py", "filter_ru_sni.py", "filter_ru_sni_local.py"]
    missing = []
    for script in required_scripts:
        script_path = SCRIPTS_DIR / script
        if script_path.exists():
            logger.info(f"  ✅ {script}")
        else:
            logger.error(f"  ❌ {script} НЕ НАЙДЕН")
            missing.append(script)
    if missing:
        logger.error(f"❌ Отсутствуют обязательные скрипты: {', '.join(missing)}")
        return False
    return True

def main():
    logger.info("=" * 70)
    logger.info("🔍 VPN KEY CHECKER - Начало проверки")
    logger.info(f"⏰ Время старта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📂 Рабочая директория: {BASE_DIR}")
    logger.info("=" * 70)
    logger.info("")
    if not check_dependencies():
        logger.error("❌ Проверка зависимостей не пройдена")
        return 2
    steps = [
        ("mirror",      "Загрузка и geo-фильтрация",          run_mirror_script),
        ("cf_generate", "Генерация 50 уникальных CF-VLESS",   generate_cf_vless),
        ("cf_merge",    "Слияние CF с основным списком",      merge_cf_with_clean),
        ("filter_sni",  "Фильтрация по реальному SNI",        run_filter_script),
        ("filter_ru",   "Экспериментальный RU-SNI фильтр",    run_filter_local_script),
        ("stats",       "Сбор статистики",                    collect_statistics),
    ]
    results = {}
    for step_id, step_name, step_func in steps:
        logger.info("")
        logger.info("─" * 70)
        logger.info(f"📌 ЭТАП: {step_name}")
        logger.info("─" * 70)
        success = step_func()
        results[step_id] = success
        if not success:
            logger.warning(f"⚠️  Этап '{step_name}' завершился с ошибкой")
        logger.info("")
    success_count = sum(1 for v in results.values() if v)
    total_steps = len(steps)
    logger.info("=" * 70)
    logger.info("📊 ИТОГОВЫЙ ОТЧЁТ")
    logger.info("=" * 70)
    for step_id, step_name, _ in steps:
        status = "✅ OK" if results[step_id] else "❌ ОШИБКА"
        logger.info(f"  {status:12s} | {step_name}")
    logger.info("─" * 70)
    if success_count == total_steps:
        logger.info(f"✅ ВСЕ ЭТАПЫ УСПЕШНЫ ({success_count}/{total_steps})")
        exit_code = 0
    elif success_count > 0:
        logger.warning(f"⚠️  ЧАСТИЧНЫЙ УСПЕХ ({success_count}/{total_steps})")
        exit_code = 1
    else:
        logger.error(f"❌ ВСЕ ЭТАПЫ НЕ УДАЛИСЬ (0/{total_steps})")
        exit_code = 2
    logger.info(f"⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Прервано пользователем (Ctrl+C)")
        exit_code = 130
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        exit_code = 3
    sys.exit(exit_code)
