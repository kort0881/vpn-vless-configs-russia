#!/usr/bin/env python3
import requests, random, ipaddress, uuid, os, sys

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
NEW_DIR = os.path.join(BASE_PATH, "data/githubmirror", "new")
os.makedirs(NEW_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(NEW_DIR, "cf_fresh.txt")


def expand_cidr(cidr_block: str, max_ips: int = 500) -> list:
    """
    Преобразует CIDR-блок (напр., '173.245.48.0/20') в список отдельных IP-адресов,
    но не более max_ips на блок для контроля размера.
    """
    try:
        network = ipaddress.ip_network(cidr_block.strip(), strict=False)
        # Если блок слишком большой (например, /12), берем только первые N адресов.
        # Это экономит ресурсы и время, при этом все IP будут из разрешенных диапазонов.
        addrs = list(network.hosts())
        if len(addrs) == 0:
            # Для очень маленьких блоков (например, /31) может не быть "хостовых" адресов
            return [str(network.network_address)]
        if len(addrs) > max_ips:
            addrs = addrs[:max_ips]
        return [str(ip) for ip in addrs]
    except Exception as e:
        print(f"  ⚠️ Ошибка парсинга CIDR {cidr_block}: {e}")
        return []


def download_cf_ips() -> list:
    """
    Загружает список IP-адресов Cloudflare из официального источника.
    Возвращает плоский список отдельных IPv4-адресов.
    """
    # Официальный источник Cloudflare: https://www.cloudflare.com/ips-v4
    url = "https://www.cloudflare.com/ips-v4"
    timeout_seconds = 15

    print(f"  → Загружаем актуальные IP-диапазоны Cloudflare: {url}")

    try:
        r = requests.get(url, timeout=timeout_seconds)
        r.raise_for_status()  # Проверяем на HTTP-ошибки (404 и т.д.)
        content = r.text

        # Разбираем CIDR-блоки из ответа (каждая строка - это CIDR)
        cidr_list = [line.strip() for line in content.splitlines() if line.strip()]
        if not cidr_list:
            print("  ❌ Не удалось найти IP-диапазоны в полученных данных")
            return []

        print(f"  → Найдено {len(cidr_list)} IPv4 CIDR-блоков. Преобразуем их в IP-адреса...")

        all_ips = []
        for cidr in cidr_list:
            all_ips.extend(expand_cidr(cidr))

        return all_ips

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Критическая ошибка при загрузке {url}: {e}")
        return []


def main():
    print("=" * 70)
    print("🗺️  Генератор свежих VLESS-конфигов на IP Cloudflare")
    print("=" * 70)

    # 1. Загружаем свежие IP
    ip_pool = download_cf_ips()
    if not ip_pool:
        print("\n❌ Не удалось получить ни одного IP-адреса Cloudflare. Генерация остановлена.")
        return 1

    print(f"\n✅ Успешно загружено и подготовлено {len(ip_pool)} IP-адресов для ротации.")

    # 2. Настройки генерации
    ports = [443, 8443, 2053, 2096]
    tags = ["🇩🇪FRK-CF", "🇷🇺MSK-CF", "🇪🇺EU-Fast", "🇩🇪TELECOM", "🇵🇱WARSAW", "🇺🇦KBP-CF"]

    configs = []
    # Генерируем конфиги, гарантированно используя ТОЛЬКО IP из официального списка
    for i in range(1, 51):
        ip = random.choice(ip_pool)
        port = random.choice(ports)
        tag = random.choice(tags)
        uid = str(uuid.uuid4())

        config = (f"vless://{uid}@{ip}:{port}"
                  f"?encryption=none&security=tls&sni=cf.cloudip.ggff.net"
                  f"&type=ws&host=cf.cloudip.ggff.net"
                  f"&path=/ws?ed=2048&fp=randomized"
                  f"#{tag} CF-VLESS {i}")
        configs.append(config)

    # 3. Сохраняем результат
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(configs))

    print(f"\n✨ Сгенерировано и сохранено {len(configs)} VLESS-конфигов.")
    print(f"📂 Файл: {OUTPUT_FILE}")
    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
