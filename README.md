# API Test Framework for Swagger Petstore

Автотесты на `pytest` для публичного API Swagger Petstore.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Запуск тестов

```bash
source .venv/bin/activate
pytest -q
```

## Настройки

По умолчанию используется базовый URL:

```python
BASE_URL = "https://petstore.swagger.io/v2"
```

Если нужно другой сервер, экспортируйте переменную окружения перед запуском:

```bash
export BASE_URL="https://example.com/api"
pytest -q
```

## Структура

- `conftest.py` — общие фикстуры и клиент API
- `constants.py` — общие константы
- `models/petstore_models.py` — Pydantic-модели
- `tests/` — тесты
