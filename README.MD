# 🏠 AIbnb

> Умный поиск жилья с интеграцией ИИ и MCP протокола


**AIbnb** - это инновационное приложение для поиска жилья на Airbnb с использованием современных технологий ИИ и MCP (Model Context Protocol) серверов. Приложение преобразует естественный язык пользователя в структурированные поисковые запросы и предоставляет детальную аналитику с интеграцией TripAdvisor.

## 🎯 Возможности

- **🧠 Natural Language Processing** - Поиск жилья обычными словами
- **🔗 MCP Protocol Integration** - Прямая интеграция с Airbnb и TripAdvisor через MCP
- **🤖 AI-анализ жилья** - Детальные отчеты с рекомендациями от GPT-4
- **📍 Геоконтекстная аналитика** - Рестораны и достопримечательности рядом с жильем
- **💻 Два интерфейса** - Веб-приложение и консольная версия
- **🌍 Мультиязычность** - Поддержка русского и английского языков

## 📺 Презентация

### 🎥 Видео-демонстрация
Посмотрите, как работает AIbnb в реальном времени:

https://disk.yandex.ru/d/unduuuGcO39YPA

> **В видео показано:**
> - Поиск жилья на естественном языке
> - AI-анализ выбранного жилья
> - Интеграция с TripAdvisor для поиска ресторанов
> - Веб-интерфейс и консольная версия

### 📄 Презентация проекта
Детальная техническая презентация с архитектурой и возможностями:

https://drive.google.com/file/d/149wbgWT8xp7m6UH7yU3hgCL6hFd9SAJc/view?usp=sharing

> **Презентация включает:**
> - Архитектуру системы
> - Технические детали MCP интеграции
> - Примеры AI-анализа
> - Сравнение с конкурентами
> - Планы развития

## 🚀 Демо

### Примеры запросов:
```
"Нужно жилье в Киеве на выходные для двоих дешево"
"Париж с 15 июля по 20 июля для семьи с ребенком"  
"Airbnb в Нью-Йорке рядом с Таймс Сквер недорого"
```

### Веб-интерфейс:
```bash
streamlit run streamlit_app.py
```

### Консольная версия:
```bash
python main.py
```

## 🛠️ Установка

### Требования
- Python 3.8+
- Node.js 16+ (для MCP серверов)
- OpenAI API ключ
- TripAdvisor API ключ

### Быстрый старт

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/Maskedxxx/MCP_HAC_OGON.git
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваши API ключи
```

4. **Запустите приложение:**
```bash
# Веб-версия
streamlit run streamlit_app.py

# Или консольная версия
python main.py
```

## 📋 Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TRIPADVISOR_API_KEY=your_actual_tripadvisor_key
```

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐
│  Console App    │    │  Streamlit Web  │
│   (main.py)     │    │ (streamlit_app/)│
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 ▼
         ┌───────────────┐
         │  Shared Core  │
         │               │
         │ • ai_agent.py │ ← GPT-4 + Pydantic
         │ • analyzer.py │ ← AI Reports  
         │ • airbnb/     │ ← MCP Client
         │ • tripadvisor/│ ← MCP Client
         └───────────────┘
```

### Основные модули:

- **`shared/`** - ИИ агенты и анализаторы
- **`airbnb/`** - Клиент для Airbnb MCP сервера
- **`tripadvisor/`** - Интеграция с TripAdvisor MCP
- **`streamlit_app/`** - Веб-интерфейс с компонентами
- **`config.py`** - Общие настройки

## 🔧 Использование

### Веб-интерфейс

1. Запустите Streamlit приложение
2. Введите запрос естественным языком
3. Просмотрите результаты поиска
4. Выберите жилье для детального анализа
5. Изучите отчеты по вкладкам

### Консольная версия

```python
from airbnb import MCPClient as AirbnbClient
from shared import AIAgent

# Инициализация
airbnb_client = AirbnbClient()
ai_agent = AIAgent()

# Запуск сервера
airbnb_client.start_server()

# Поиск
listings, location = ai_agent.search_with_ai(
    "Жилье в Киеве для двоих", 
    airbnb_client, 
    formatter
)
```

## 🧠 ИИ возможности

### Natural Language Processing
```python
# Вход: "Жилье в Киеве на выходные для двоих дешево"
# Выход:
{
    "location": "Kiev, Ukraine",
    "adults": 2,
    "maxPrice": 50,
    "checkin": "2025-06-21",
    "checkout": "2025-06-23"
}
```

### AI Анализ жилья
- 🏠 Общая информация
- ⭐ Рейтинг и отзывы
- 💰 Стоимость и ценность
- 🏢 Расположение
- 🛏️ Удобства и особенности
- ✅ Плюсы
- ⚠️ Возможные минусы
- 🎯 Персональные рекомендации

## 🌍 MCP Integration

### Поддерживаемые MCP серверы:

- **[@openbnb/mcp-server-airbnb](https://github.com/openbnb/mcp-server-airbnb)** - Поиск жилья
- **[tripadvisor-mcp-node](https://github.com/modelcontextprotocol/servers)** - POI и отзывы

### Геоконтекстная связка:
```python
# 1. Поиск жилья через Airbnb MCP
listings = airbnb_client.search_accommodations(location="Paris")

# 2. Получение координат выбранного жилья
coordinates = selected_listing["coordinates"]

# 3. Поиск контекста через TripAdvisor MCP
restaurants = tripadvisor_client.search_nearby_locations(
    lat=coordinates["latitude"], 
    lon=coordinates["longitude"], 
    category="restaurants"
)
```

## 📊 Технологии

- **Backend**: Python
- **AI**: OpenAI GPT-4.1, Pydantic
- **MCP**: Model Context Protocol
- **Frontend**: Streamlit
- **Data**: JSON-RPC, REST APIs

## 🔄 Workflow

1. **Пользователь** вводит запрос на естественном языке
2. **GPT-4.1** извлекает структурированные параметры
3. **Airbnb MCP** выполняет поиск жилья
4. **Пользователь** выбирает вариант для анализа
5. **TripAdvisor MCP** находит POI рядом с жильем
6. **GPT-4** генерирует персонализированный отчет

## 🚧 Разработка

### Структура проекта
```
├── airbnb/                 # Airbnb MCP клиент
│   ├── client.py          # MCP протокол
│   ├── formatter.py       # Форматирование данных
│   └── config.py          # Настройки
├── tripadvisor/           # TripAdvisor интеграция
│   ├── client.py          # MCP клиент
│   ├── integrator.py      # AI интеграция
│   └── config.py          # Настройки
├── shared/                # Общие ИИ модули
│   ├── ai_agent.py        # GPT-4 парсер
│   └── listing_analyzer.py # AI анализатор
├── streamlit_app/         # Веб-интерфейс
│   ├── components/        # UI компоненты
│   ├── utils/            # Утилиты
│   └── app.py            # Главное приложение
├── main.py               # Консольное приложение
└── config.py             # Общая конфигурация
```


## 📈 Roadmap

- [ ] **Q3 2025**: Интеграция с Booking.com MCP
- [ ] **Q3 2025**: Redis кэширование для снижения costs
- [ ] **Q4 2025**: Мобильное приложение
- [ ] **Q4 2025**: Поддержка дополнительных языков (ES, FR, DE)
- [ ] **2026**: Voice interface через Whisper API
- [ ] **2026**: Analytics dashboard для travel агентств

## 🤝 Поддержка

- 📧 Email: [aangers07@gmail.com]
- 💬 Telegram: [@dixilx]

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- [Model Context Protocol](https://modelcontextprotocol.io) - за революционный подход к AI интеграциям
- [OpenBnB](https://github.com/openbnb) - за Airbnb MCP сервер
- [Anthropic](https://anthropic.com) - за создание MCP стандарта
- [OpenAI](https://openai.com) - за GPT-4.1 API

---

**Сделано с ❤️ для путешественников**