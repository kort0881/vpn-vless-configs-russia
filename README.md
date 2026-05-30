<div align="center">

# 🔐 VPN VLESS Configs Russia

### Автоматическая коллекция VPN конфигураций с фокусом на РФ и СНГ регион

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Auto Update](https://img.shields.io/badge/Auto_Update-Every_15min-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status

</div>

---

## 🎬 Live Demo

<div align="center">

![VPN Collector Demo](гифка.gif)

*Автоматический сбор, фильтрация и валидация VPN конфигураций в реальном времени*

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
- 🔄 Обновление каждые 15 минут
- 📥 Сбор из 50+ GitHub репозиториев
- 📡 Парсинг Telegram каналов
- 🤖 GitHub Actions workflow
- 💾 Автоматический commit результатов

</td>
<td width="50%">

### 🎯 Умная фильтрация
- 🌍 Geo-фильтр (RU/СНГ/EU)
- 🔍 Дедупликация по MD5
- ✅ Валидация синтаксиса
- 🏆 Приоритет быстрых серверов
- 📊 Детальная статистика

</td>
</tr>
</table>

**Поддерживаемые протоколы:**
- 🟩 **VLESS** - Modern protocol with XTLS
- 🟦 **VMess** - Classic V2Ray protocol
- 🟥 **Trojan** - Trojan-GFW protocol
- ⚫ **Shadowsocks** - SOCKS5-based proxy

---

## 📊 Live Statistics

<div align="center">

| Protocol | Total Configs | RU/CIS Filtered | Status |
|:--------:|:-------------:|:---------------:|:------:|
| 🟩 VLESS | 1247 | 342 | ✅ Active |
| 🟦 VMess | 892 | 198 | ✅ Active |
| 🟥 Trojan | 534 | 87 | ✅ Active |
| ⚫ Shadowsocks | 312 | 45 | ✅ Active |
| **📦 Total** | **2985** | **672** | **✅ Online** |

![Updated](https://img.shields.io/badge/Last_Update-2026--02--17-orange?style=flat-square)
![Sources](https://img.shields.io/badge/Sources-53_repos-blue?style=flat-square)
![Uptime](https://img.shields.io/badge/Uptime-99.9%25-success?style=flat-square)

</div>

---

## 🚀 Quick Start

### 1️⃣ Cloudflare Worker подписка (временно недоступна)

> 🔒 Внимание: Cloudflare Workers сейчас частично блокируются в РФ, поэтому **подписка через `vlesstrojan.alexanderyurievich88.workers.dev` временно отключена** и ссылки убраны, чтобы не оставлять нерабочие конфиги и мёртвые подписки.

> 🔁 Как только ситуация стабилизируется и доступ к Cloudflare Workers станет более предсказуемым, здесь снова появятся **актуальные подписочные ссылки**.

> 📝 Пока используйте прямую загрузку с GitHub (см. пункт ниже) или локальный запуск скриптов.

### 2️⃣ Прямая загрузка с GitHub

```bash
# Все VLESS конфигурации
wget https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt

# Только российские серверы
wget https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/ru-sni/vless_ru.txt
```

### 3️⃣ Clone Repository

```bash
git clone https://github.com/kort0881/vpn-vless-configs-russia.git
cd vpn-vless-configs-russia

# Просмотр конфигураций
cat githubmirror/clean/vless.txt | head -10
```

---

## 📱 Настройка клиентов

### Hiddify (Рекомендуется)

**Android / iOS / Windows / macOS / Linux**

1. Скачать: [hiddify.com](https://hiddify.com)
2. Открыть → **Add Profile** → **Subscription URL**
3. Вставить:
   - пока Cloudflare-подписка временно отключена, используйте:
     - прямой импорт отдельных ссылок из файлов `githubmirror/clean/*.txt`
     - либо свой собственный backend/подписку
4. **Import** → выбрать сервер

### V2RayN (Windows)

1. **Подписка** → **Группы подписок** → **Добавить**
2. Указать свой рабочий URL подписки или локальный/самостоятельный endpoint
3. **Обновить подписку** → выбрать сервер
4. Правая кнопка → **Test Real Latency** (выбрать быстрый)

### V2RayNG (Android)

1. **Menu (≡)** → **Подписки** → **+**
2. **URL** → вставить ваш URL подписки → **OK**
3. **Обновить подписку** → выбрать сервер

### Clash Meta / Mihomo

```yaml
proxy-providers:
  vless-sub:
    type: http
    url: "https://<your-own-endpoint>/sub?filter=vless"
    interval: 3600
    path: ./providers/vless.yaml
    health-check:
      enable: true
      interval: 600
      url: http://www.gstatic.com/generate_204
```

---

## 📂 Project Structure

```
vpn-vless-configs-russia/
├── 📁 githubmirror/
│   ├── 📁 clean/                    # Все валидные конфигурации
│   │   ├── vless.txt                # 1247 VLESS configs
│   │   ├── vmess.txt                # 892 VMess configs
│   │   ├── trojan.txt               # 534 Trojan configs
│   │   └── ss.txt                   # 312 Shadowsocks configs
│   ├── 📁 ru-sni/                   # Только RU/CIS серверы
│   │   ├── vless_ru.txt             # 342 RU VLESS
│   │   ├── vmess_ru.txt             # 198 RU VMess
│   │   └── ...
│   ├── 📁 new/                      # Новые конфигурации
│   └── 📁 ru-sni-local/             # Локальные RU конфиги
├── 📁 vpn-files/
│   ├── all_posts.txt                # История постов
│   └── post_YYYYMMDD_HHMMSS.txt     # Последние посты
├── 📁 subscriptions/                # Subscription форматы
├── 📁 data/                         # Служебные данные
├── 📄 main.py                       # Основной оркестратор
├── 📄 mirror.py                     # Сборщик конфигураций
├── 📄 filter_ru_sni.py              # Географический фильтр
└── 📄 requirements.txt              # Python зависимости
```

---

## 🔄 Автоматизация

### GitHub Actions Workflow

```
┌─────────────────────────────────────┐
│ GitHub Actions (Every 15 min)       │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │ 1. 📥 Сбор     │
       │ конфигураций   │
       │ - GitHub       │
       │   (50+ repos)  │
       │ - Telegram     │
       │ - RSS          │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ 2. 🔍          │
       │ Фильтрация     │
       │ - Дедупликация │
       │ - Geo-фильтр   │
       │ - Валидация    │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ 3. 💾          │
       │ Сохранение     │
       │ - clean/       │
       │ - ru-sni/      │
       └───────┬────────┘
               │
       ┌───────▼────────┐
       │ 4. 📤 Commit   │
       │    & Push      │
       └────────────────┘
```

**Расписание:**
- ⏰ Каждые 15 минут (автоматически)
- 🚀 Ручной запуск (workflow_dispatch)
- 📊 Обновление статистики
- 💬 Уведомления в Telegram

---

## 🛠️ Локальная установка

### Требования

```bash
Python 3.8+
Git
```

### Установка

```bash
# Clone repository
git clone https://github.com/kort0881/vpn-vless-configs-russia.git
cd vpn-vless-configs-russia

# Install dependencies
pip install -r requirements.txt

# Настроить переменные окружения (опционально)
cp .env.example .env
# Редактировать .env (добавить TELEGRAM_BOT_TOKEN если нужно)
```

### Запуск

```bash
# Полный цикл (сбор + фильтрация + статистика)
python main.py

# Только сбор конфигураций
python mirror.py

# Только фильтрация RU/CIS
python filter_ru_sni.py
```

### Логи

```bash
# Просмотр последнего лога
tail -f logs/vpn-checker-*.log

# Статистика выполнения
cat stats.json | python -m json.tool
```

---

## 🌍 Географическая фильтрация

### Приоритетные регионы

**Высокий приоритет:**
- 🇷🇺 Россия - минимальный latency
- 🇰🇿 Казахстан - низкий ping
- 🇺🇦 Украина - близкие серверы
- 🇧🇾 Беларусь - стабильное соединение

**Средний приоритет:**
- 🇩🇪 Германия - высокая скорость
- 🇳🇱 Нидерланды - отличные каналы
- 🇫🇷 Франция - надежные датацентры
- 🇬🇧 Великобритания - быстрые серверы

### Критерии фильтрации

```python
# Проверка домена SNI
RU_DOMAINS = [
    'ru', 'рф', 'russia', 'moscow', 'spb', 'msk',
    'kazakh', 'kz', 'ukraine', 'ua', 'belarus', 'by'
]

# Проверка IP диапазонов
# GeoIP lookup по MaxMind DB
```

---

## 📊 Статистика и мониторинг

### Метрики (stats.json)

```json
{
  "timestamp": "2026-02-17T18:15:00",
  "github_mirror": {
    "vless": 1247,
    "vmess": 892,
    "trojan": 534,
    "ss": 312
  },
  "ru_sni": {
    "vless": 342,
    "vmess": 198,
    "trojan": 87,
    "ss": 45
  },
  "sources": {
    "github_repos": 53,
    "telegram_posts": 2,
    "total_raw": 3847,
    "after_dedup": 2985,
    "success_rate": 77.6
  }
}
```

**Отслеживаем:**
- ✅ Success rate (% рабочих конфигураций)
- ⚡ Average response time
- 🌍 Geographic distribution
- 📈 Quality trends
- 🔄 Update frequency

---

## 🔒 Безопасность

### ⚠️ Предупреждения

**Риски при использовании публичных VPN:**

1. 📝 **Логирование трафика** - владелец сервера может видеть ваши данные
2. 🔓 **Незашифрованный HTTP** - данные могут быть перехвачены
3. 🕵️ **Отсутствие гарантий приватности** - публичные серверы небезопасны
4. 🚫 **Возможная блокировка** - серверы могут быть заблокированы

### 💡 Рекомендации

✅ **Используйте только для:**
- Тестирования и образования
- Разработки и отладки
- Временного доступа к заблокированным ресурсам

❌ **НЕ используйте для:**
- Банковских операций
- Конфиденциальной переписки
- Работы с личными данными
- Коммерческой деятельности

**🔐 Для серьезных задач используйте платные VPN-сервисы!**

---

## ❓ FAQ

<details>
<summary><b>Q: Почему некоторые конфигурации не работают?</b></summary>

**Причины:**
1. Сервер заблокирован провайдером
2. Конфигурация устарела
3. Лимит подключений исчерпан
4. Сервер выключен

**Решение:** Используйте подписку - она автоматически обновляется каждые 15 минут.
</details>

<details>
<summary><b>Q: Как выбрать самые быстрые серверы?</b></summary>

**В клиентах есть функция ping test:**
- **Hiddify**: Long tap → Test Latency
- **V2RayN**: Right click → Test Real Latency  
- **Clash**: Config → Test All

Выбирайте серверы с latency < 150ms.
</details>

<details>
<summary><b>Q: Как часто обновляются конфигурации?</b></summary>

- ⏰ **GitHub Actions**: каждые 15 минут
- 📡 **Telegram парсинг**: 2 раза в день
- 🚀 **Ручной запуск**: в любое время
</details>

<details>
<summary><b>Q: Можно ли использовать в коммерческих целях?</b></summary>

❌ **Нет**. Репозиторий только для образования.
</details>

---

## 🔗 Полезные ссылки

### Telegram каналы (источники)

[![Telegram](https://img.shields.io/badge/Telegram-@vlesstrojan-blue?style=for-the-badge&logo=telegram)](https://t.me/vlesstrojan)
[![Telegram](https://img.shields.io/badge/Telegram-@kibersosnew-blue?style=for-the-badge&logo=telegram)](https://t.me/kibersosnew)

### Связанные проекты

- [V2RayAggregator](https://github.com/mahdibland/V2RayAggregator) - V2Ray агрегатор
- [NoMoreWalls](https://github.com/peasoft/NoMoreWalls) - Proxy листы
- [Xray-core](https://github.com/XTLS/Xray-core) - Proxy движок
- [Hiddify](https://github.com/hiddify) - Multi-platform VPN клиент

### Документация

- 📖 [USAGE.md](USAGE.md) - Подробное руководство
- 📜 [LICENSE](LICENSE) - Лицензия проекта

---

## 🤝 Contributing

### Как помочь проекту

**1. Добавить новые источники**
```python
# В mirror.py
SOURCES = [
    "https://your-source.com/configs.txt",
]
```

**2. Улучшить фильтрацию**
- Добавить домены в `RU_DOMAINS`
- Улучшить GeoIP определение
- Оптимизировать валидацию

**3. Репортить баги**
- [Создать Issue](https://github.com/kort0881/vpn-vless-configs-russia/issues)
- Приложить логи
- Указать версию Python

### Pull Request Process

1. Fork repository
2. Create branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -m "Add new feature"`
4. Push: `git push origin feature/new-feature`
5. Open Pull Request

---

## 📜 License

### MIT License с ограничениями
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

text

Полный текст: [LICENSE](LICENSE)

---

## 📞 Контакты

- 📱 **Telegram**: [@vlesstrojan](https://t.me/vlesstrojan)
- 🐛 **Issues**: [GitHub Issues](https://github.com/kort0881/vpn-vless-configs-russia/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/kort0881/vpn-vless-configs-russia/discussions)

---

<div align="center">

## 🌟 Если проект полезен - поставьте звезду!

[![GitHub stars](https://img.shields.io/github/stars/kort0881/vpn-vless-configs-russia?style=social)](https://github.com/kort0881/vpn-vless-configs-russia/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kort0881/vpn-vless-configs-russia?style=social)](https://github.com/kort0881/vpn-vless-configs-russia/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/kort0881/vpn-vless-configs-russia?style=social)](https://github.com/kort0881/vpn-vless-configs-russia/watchers)

---

### 💡 Сделано с ❤️ для свободного интернета

**Last Update**: 2026-02-17 | **Total Configs**: 2985+ | **Sources**: 53+ | **Uptime**: 99.9%

</div>
