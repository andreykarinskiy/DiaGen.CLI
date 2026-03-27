# DiaGen CLI

DiaGen - консольная утилита для запуска скриптов автоматизации и их объединения в конвейеры.

Текущая версия репозитория содержит MVP-каркас CLI, упаковку Python-пакета и базовый CI/CD.

## Требования

- Python 3.11+

## Локальный запуск

```bash
pip install -e .[dev]
diagen --version
diagen --help
```

## Тесты и проверки

```bash
ruff check .
pytest -q
```

## Docker

```bash
docker build -t diagen-cli .
docker run --rm diagen-cli --version
```

## Релизы

- CI запускается на `push` и `pull_request`.
- Публикация артефактов в GitHub Releases запускается при теге формата `vX.Y.Z`.
- Для сборки изменений рекомендуется conventional commits + Commitizen.

## Установка из GitHub Releases

После публикации релиза пакет можно установить через `pip` по ссылке на wheel/sdist из GitHub Releases.
