# Вечера

[![Проверки](https://github.com/USERNAME/dance-evening/actions/workflows/checks.yml/badge.svg)](https://github.com/USERNAME/dance-evening/actions/workflows/checks.yml)

Платформа городских вечеров: единая афиша (танцы, стэндап, квизы), запись без
переписки, публичный блок «Кто идёт», после вечера — отзывы, рейтинги и фотоотчёты.
Танцевальные вечера — первый вертикальный сценарий: баланс ведущих и ведомых
с динамической ценой на дефицитную роль.

Учебный проект по дисциплине «Технологии разработки программных систем»
(ОмГТУ, 09.03.01). Выполняется в одиночку, по облегчённому процессу.

Название репозитория (dance-evening) историческое: проект начинался с танцевальных
вечеров и обобщён до любых городских вечеров по замечанию преподавателя.

## Принцип

Система не существует на самом мероприятии. Всё взаимодействие — до входа и после
выхода.

## Как запустить

### Требования

- Python 3.13 — ставится командой `uv python install` по файлу `.python-version`
- [uv](https://docs.astral.sh/uv/) — менеджер зависимостей
- Docker с Compose — для базы данных

### Локально

```bash
uv sync                      # поставить зависимости по uv.lock
cp .env.example .env         # создать локальную конфигурацию
docker compose up -d db      # поднять только базу данных
uv run python -m evenings    # запустить сервис
```

Сервис доступен на `http://localhost:8080`, описание API — на
`http://localhost:8080/docs`.

Запись на демо-вечер (существуют `evening-1`…`evening-4`, подробности — в
описании API):

```bash
curl -s -X POST localhost:8080/registrations \
  -H 'Content-Type: application/json' \
  -d '{"evening_id":"evening-1","user_id":"u-1","dance_role":"follower"}'
```

### Полностью в контейнерах

```bash
docker compose up -d --build
curl http://localhost:8080/health
```

### Тесты

```bash
uv run pytest                                              # весь набор
uv run pytest --cov=src/evenings --cov-report=term-missing  # с покрытием
```

### Проверки качества

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src/
```

## Конфигурация

| Переменная | Обязательна | По умолчанию | Назначение |
| --- | --- | --- | --- |
| `DATABASE_URL` | да | — | Адрес PostgreSQL |
| `PORT` | нет | `8080` | Порт сервиса |
| `LOG_LEVEL` | нет | `info` | `debug` / `info` / `warning` / `error` |
| `ENVIRONMENT` | нет | `development` | `development` / `test` / `production`; вне разработки журнал — JSON |
| `APP_VERSION` | нет | `0.0.0-dev` | Подставляется при сборке образа |

Сервис **не стартует**, если `DATABASE_URL` не задана или в `.env` встретилось
неизвестное имя переменной. Опечатка в имени переменной окружения
(`compose.yaml`, оболочка) **не** обнаруживается — сверяйте имена с этой
таблицей.

## Документы

| Файл | Что внутри |
| --- | --- |
| [docs/architecture/overview.md](docs/architecture/overview.md) | **Начните отсюда**: что за система, из чего состоит, какие решения приняты |
| [docs/requirements.md](docs/requirements.md) | Стороны, требования с критериями приёмки, атрибуты качества, приоритизация |
| [docs/traceability.md](docs/traceability.md) | Матрица: требование → решение → код → проверка |
| [docs/adr/README.md](docs/adr/README.md) | Журнал архитектурных решений |
| [docs/domain/event-storming.md](docs/domain/event-storming.md) | Модель предметной области: события, контексты, агрегаты, единый язык |
| [docs/architecture/README.md](docs/architecture/README.md) | Диаграммы: контекст, контейнеры, сценарий, модель данных |
| [docs/api/resources.md](docs/api/resources.md) | Ресурсы и операции REST API |
| [docs/customer-journey-map.md](docs/customer-journey-map.md) | Карты пути клиента: боли и возможности |
| [docs/user-story-map.md](docs/user-story-map.md) | Карта историй, позвоночник MVP, бэклог MoSCoW |
| [docs/roadmap.md](docs/roadmap.md) | Вехи семестра |
| [docs/gantt.md](docs/gantt.md) | План по неделям с параллельными работами, контрольные точки |
| [docs/process.md](docs/process.md) | Процесс: зоны ответственности, DoR/DoD, ритм |
| [docs/pipeline.md](docs/pipeline.md) | Конвейер проверок, ветвление, защита main |
| [CHANGELOG.md](CHANGELOG.md) | Журнал изменений |

## Разработка

Изменения попадают в main только через pull request со squash merge и зелёными
проверками конвейера. Ветки короткоживущие: `feature/…`, `docs/…`, `ci/…`,
`fix/…` от свежего main; сообщения коммитов — Conventional Commits. Те же
проверки запускаются и локально. Подробности: [docs/pipeline.md](docs/pipeline.md).
Процесс и DoD — [docs/process.md](docs/process.md).
