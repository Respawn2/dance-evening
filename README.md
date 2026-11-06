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

## Документы

| Файл | Что внутри |
| --- | --- |
| [docs/requirements.md](docs/requirements.md) | Домен, проблема, персоны, путь, MVP, границы |
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
