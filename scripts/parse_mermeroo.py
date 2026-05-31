import requests

# Список источников для обработки
URL_SOURCES = [
    "https://raw.githubusercontent.com/mermeroo/V2RAY-CLASH-BASE64-Subscription.Links/main/SUB%20LINKS",
    "https://raw.githubusercontent.com/Leon406/jsdelivr/master/subscribe/subpools",
]

OUT_FILE = "mermeroo_sources.txt"

def is_potential_source(line: str) -> bool:
    """Проверяет, похожа ли строка на URL прокси-подписки"""
    line = line.strip()
    if not line.startswith("http"):
        return False
    # Исключаем явно не подходящие файлы
    bad_ext = (".md", ".html", ".htm")
    if any(line.endswith(ext) for ext in bad_ext):
        return False
    return True

def extract_urls_from_text(text: str) -> set:
    """Извлекает все потенциальные URL из текста"""
    urls = set()
    lines = text.splitlines()
    
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        # Разделяем строку на части, используя пробелы и запятые как разделители
        parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip()]
        for p in parts:
            if is_potential_source(p):
                urls.add(p)
    
    return urls

def main():
    all_urls = set()
    
    # Обрабатываем каждый источник по очереди
    for url_source in URL_SOURCES:
        print(f"Загружаю SUB LINKS из {url_source}...")
        try:
            r = requests.get(url_source, timeout=15)
            r.raise_for_status()
            urls = extract_urls_from_text(r.text)
            print(f"  Найдено {len(urls)} URL в этом источнике.")
            all_urls.update(urls)
        except Exception as e:
            print(f"  Ошибка при загрузке {url_source}: {e}")
    
    # Сортируем и сохраняем результат
    urls_list = sorted(all_urls)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(urls_list))
    
    print(f"\nГотово. Всего собрано уникальных URL: {len(urls_list)}")
    print(f"Результат сохранён в файл: {OUT_FILE}")

if __name__ == "__main__":
    main()
