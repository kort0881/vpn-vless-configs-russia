markdown
<div align="center">

# 🔐 VPN VLESS Configs Russia

### Автоматическая коллекция VPN конфигураций с фокусом на РФ и СНГ регион

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Auto Update](https://img.shields.io/badge/Auto_Update-Every_2h-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

## ⚠️ Дисклеймер

<div align="center">

### 📜 Образовательный проект

</div>

> **Этот репозиторий создан исключительно в образовательных целях для изучения криптографических протоколов и сетевой безопасности.**

**Автор:**
- ✅ **НЕ призывает** к нарушению законодательства
- ✅ **НЕ гарантирует** работоспособность конфигураций
- ✅ **НЕ несёт ответственности** за действия пользователей
- ✅ Все данные получены из **публичных источников**

**⚖️ Любое использование — на ваш собственный риск**

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 Автоматизация
- 🔄 Обновление каждые 2 часа (cron)
- 📥 Сбор из 50+ GitHub репозиториев + sstap.org
- 🧬 **Генерация собственных VLESS-конфигов** (50 шт.)
- 🤖 GitHub Actions workflow
- 💾 Автоматический коммит и пуш результатов

</td>
<td width="50%">

### 🎯 Умная фильтрация
- 🌍 Geo-фильтр (RU/СНГ/EU) по тегам и SNI
- 🔍 Дедупликация по (IP, port, scheme)
- 🏆 Приоритет быстрых серверов
- 📊 Детальная статистика (stats.json)
- 🧹 Очистка от дублей и мусора

</td>
</tr>
</table>

**Поддерживаемые протоколы:**
- 🟩 **VLESS** — современный протокол с XTLS
- 🟦 **VMess** — классический протокол V2Ray
- 🟥 **Trojan** — протокол Trojan-GFW
- ⚫ **Shadowsocks** — прокси на базе SOCKS5

---

## 📊 Live Statistics (пример)

<div align="center">

| Protocol | Total Configs | RU/CIS Filtered | Status |
|:--------:|:-------------:|:---------------:|:------:|
| 🟩 VLESS | 1247 | 342 | ✅ Active |
| 🟦 VMess | 892 | 198 | ✅ Active |
| 🟥 Trojan | 534 | 87 | ✅ Active |
| ⚫ Shadowsocks | 312 | 45 | ✅ Active |
| **📦 Total** | **2985** | **672** | **✅ Online** |

![Updated](https://img.shields.io/badge/Last_Update-Auto-orange?style=flat-square)
![Sources](https://img.shields.io/badge/Sources-53_repos-blue?style=flat-square)
![Uptime](https://img.shields.io/badge/Uptime-99.9%25-success?style=flat-square)

</div>

---

## 🚀 Quick Start

### 1️⃣ Прямая загрузка с GitHub

```bash
# Все VLESS конфигурации (после geo-фильтра)
wget https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt

# Только российские/СНГ серверы (по SNI)
wget https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless.txt

# Сгенерированные собственные VLESS-конфиги (бэкап)
wget https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/my_sources/generated/vless.txt
2️⃣ Clone репозитория
bash
git clone https://github.com/kort0881/vpn-vless-configs-russia.git
cd vpn-vless-configs-russia

# Просмотр конфигураций
cat githubmirror/clean/vless.txt | head -10
📱 Настройка клиентов
Hiddify (Рекомендуется)
Android / iOS / Windows / macOS / Linux

Скачать: hiddify.com

Открыть → Add Profile → Subscription URL

Вставить ссылку на raw версию файла, например:

text
https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless.txt
Import → выбрать сервер

⚠️ Cloudflare Worker подписка временно недоступна из-за блокировок. Используйте прямую загрузку.

V2RayN (Windows)
Подписка → Группы подписок → Добавить

URL: как указано выше

Обновить подписку → выбрать сервер

Правая кнопка → Test Real Latency (выбрать быстрый)

V2RayNG (Android)
Menu (≡) → Подписки → +

URL → вставить URL → OK

Обновить подписку → выбрать сервер

📂 Project Structure (с изменениями)
text
vpn-vless-configs-russia/
├── 📁 githubmirror/
│   ├── 📁 clean/                 # Все валидные конфиги после geo-фильтра
│   │   ├── vless.txt
│   │   ├── vmess.txt
│   │   ├── trojan.txt
│   │   └── ss.txt
│   ├── 📁 ru-sni/                # Отфильтровано по SNI (РФ/СНГ)
│   │   ├── vless.txt
│   │   ├── vmess.txt
│   │   └── ...
│   ├── 📁 new/                   # Сырые новые конфиги
│   │   ├── all_new.txt
│   │   └── by_protocol/
│   └── 📁 ru-sni-local/          # Экспериментальный локальный SNI-фильтр
├── 📁 my_sources/
│   └── 📁 generated/             # Сгенерированные собственные VLESS-конфиги
│       └── vless.txt
├── 📁 logs/                      # Логи выполнения
├── 📄 my_vless_generator.py      # 🆕 Генератор собственных VLESS
├── 📄 mirror.py                  # Сборщик из публичных источников
├── 📄 main.py                    # Оркестратор всех шагов
├── 📄 filter_ru_sni.py           # Основной SNI-фильтр (РФ/СНГ)
├── 📄 filter_ru_sni_local.py     # Экспериментальный SNI-фильтр
├── 📄 generate_cf_vless.py       # Генерация 50 свежих CF-VLESS
├── 📄 config_sources.json        # Список URL источников (из секрета)
├── 📄 stats.json                 # Статистика (обновляется при каждом запуске)
├── 📄 requirements.txt           # Зависимости Python
└── 📂 .github/workflows/
    └── FullAutomatedUpdate.yml   # GitHub Actions (каждые 2 часа)
🔄 Автоматизация (GitHub Actions)
Workflow FullAutomatedUpdate.yml запускается:

⏰ По расписанию: 0 */2 * * * (каждые 2 часа)

🖱️ Вручную: через кнопку Run workflow на вкладке Actions

Последовательность шагов:
text
1. Reset репозитория до origin/main
2. Установка Python и зависимостей
3. Создание config_sources.json из секрета VPN_SOURCES
4. mirror.py          → загрузка и geo-фильтрация → githubmirror/
5. proxy_collect_merge.py → объединение источников
6. my_vless_generator.py  → 🆕 генерация 50 собственных VLESS → my_sources/generated/ и добавление в githubmirror/clean/vless.txt
7. main.py            → запуск оркестратора (включая generate_cf_vless, filter_ru_sni и др.)
8. parse_mermeroo.py  → парсинг дополнительных источников
9. compare_* / merge_* → сравнение и слияние
10. convert_extra_sources.py → преобразование
11. git commit & push → все изменения (включая my_sources/generated) отправляются в репозиторий
Результат: свежие конфиги в githubmirror/clean/, githubmirror/ru-sni/, а также в my_sources/generated/vless.txt.

🛠️ Локальная установка и запуск
Требования
bash
Python 3.11+
Git
Установка
bash
git clone https://github.com/kort0881/vpn-vless-configs-russia.git
cd vpn-vless-configs-russia
pip install -r requirements.txt
Настройка (опционально)
Создайте файл config_sources.json со списком URL источников (если не хотите получать их из секрета GitHub). Пример:

json
[
  "https://raw.githubusercontent.com/.../configs.txt",
  "https://example.com/proxies.txt"
]
Запуск
bash
# Полный цикл (все шаги, как в GitHub Actions)
python main.py

# Только сбор зеркала
python mirror.py

# Только генерация собственных VLESS
python my_vless_generator.py

# Только SNI-фильтр (РФ/СНГ)
python filter_ru_sni.py
Просмотр логов и статистики
bash
# Последний лог
tail -f logs/vpn-checker-*.log

# Статистика
cat stats.json | python -m json.tool
🌍 Географическая фильтрация
mirror.py использует белый список доменов и тегов (РФ/СНГ/Европа)

filter_ru_sni.py извлекает реальный SNI из URI и оставляет только те, где SNI соответствует РФ/СНГ доменам (vk.com, yandex.ru, mail.ru, госуслуги и т.д.)

Приоритетные регионы:

🇷🇺 Россия

🇰🇿 Казахстан

🇧🇾 Беларусь

🇪🇺 Европа (Германия, Нидерланды, Франция, Великобритания)

🔒 Безопасность
⚠️ Предупреждения
Риски при использовании публичных VPN:

📝 Логирование трафика — владелец сервера может видеть ваши данные

🔓 Незашифрованный HTTP — данные могут быть перехвачены

🕵️ Отсутствие гарантий приватности — публичные серверы небезопасны

🚫 Возможная блокировка — серверы могут быть заблокированы

💡 Рекомендации
✅ Используйте только для:

Тестирования и образования

Разработки и отладки

Временного доступа к заблокированным ресурсам

❌ НЕ используйте для:

Банковских операций

Конфиденциальной переписки

Работы с личными данными

Коммерческой деятельности

🔐 Для серьезных задач используйте платные VPN-сервисы!

❓ FAQ
<details> <summary><b>Q: Почему некоторые конфигурации не работают?</b></summary>
Причины:

Сервер заблокирован провайдером

Конфигурация устарела

Лимит подключений исчерпан

Сервер выключен

Решение: Обновите конфиги — GitHub Actions делает это каждые 2 часа.

</details><details> <summary><b>Q: Как часто обновляются конфигурации?</b></summary>
⏰ GitHub Actions: каждые 2 часа (автоматически)

📡 Telegram парсинг: 2 раза в день

🚀 Ручной запуск: в любое время

</details><details> <summary><b>Q: Что такое my_sources/generated/vless.txt?</b></summary>
Это файл, который генерирует скрипт my_vless_generator.py. Он создаёт 50 собственных VLESS-конфигов (с реальными UUID) и автоматически добавляет их в общий пул githubmirror/clean/vless.txt. Это позволяет вам иметь свои уникальные конфиги, которые не зависят от внешних источников.

</details><details> <summary><b>Q: Можно ли изменить количество генерируемых конфигов или хосты?</b></summary>
Да. Отредактируйте в my_vless_generator.py функцию generate_my_configs(count=50, custom_hosts=None). Передайте свой список хостов или измените count.

</details>
🔗 Полезные ссылки
Источники (частично)
sstap.org — актуальные ключи в реальном времени

V2RayAggregator

NoMoreWalls

Клиенты
Hiddify — мультиплатформенный клиент

Xray-core — движок

🤝 Contributing
Как помочь проекту
Добавить новые источники — отредактируйте config_sources.json или секрет VPN_SOURCES.

Улучшить фильтрацию — дополните списки GOOD_DOMAINS и GOOD_TAGS в mirror.py.

Сообщить об ошибке — создайте Issue с описанием и логами.

Pull Request Process
Fork репозитория

Создайте ветку: git checkout -b feature/improvement

Закоммитьте изменения: git commit -m "Описание"

Запушьте: git push origin feature/improvement

Откройте Pull Request

📜 License
MIT License с ограничениями
Copyright (c) 2026 VPN VLESS Configs Russia

РАЗРЕШЕНО:
✅ Личное использование в образовательных целях
✅ Модификация исходного кода
✅ Форки репозитория

ЗАПРЕЩЕНО:
❌ Коммерческое использование
❌ Распространение в странах с запретом VPN
❌ Использование для незаконной деятельности

АВТОР НЕ НЕСЁТ ОТВЕТСТВЕННОСТИ ЗА:
⚠️ Действия пользователей
⚠️ Нарушение законодательства
⚠️ Утечки данных
⚠️ Блокировки провайдерами

Полный текст: LICENSE

📞 Контакты
📱 Telegram: @vlesstrojan

🐛 Issues: GitHub Issues

💬 Discussions: GitHub Discussions

<div align="center">
🌟 Если проект полезен — поставьте звезду!
https://img.shields.io/github/stars/kort0881/vpn-vless-configs-russia?style=social
https://img.shields.io/github/forks/kort0881/vpn-vless-configs-russia?style=social
https://img.shields.io/github/watchers/kort0881/vpn-vless-configs-russia?style=social

💡 Сделано с ❤️ для свободного интернета
Last Update: автоматически каждые 2 часа | Total Configs: см. stats.json | Sources: 50+ | Uptime: 99.9%

</div> ```

### 💡 Сделано с ❤️ для свободного интернета

**Last Update**: 2026-02-17 | **Total Configs**: 2985+ | **Sources**: 53+ | **Uptime**: 99.9%

</div>
