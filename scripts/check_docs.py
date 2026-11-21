#!/usr/bin/env python3
"""Проверка документов репозитория.

Запускается и локально, и в конвейере (задание «Плейсхолдеры и ссылки»
в .github/workflows/checks.yml). Только стандартная библиотека.

Что проверяет:
- кодировка UTF-8, отсутствие BOM и переводов строк CRLF;
- пустая строка в конце файла;
- незаполненные остатки: TODO, FIXME и подобные;
- ссылки на локальные файлы и якоря заголовков;
- строки таблиц матрицы прослеживаемости без идентификатора требования (ЛР 2А);
- разделы требований к качеству без величины с единицей (ЛР 2А).

Выход: 0 — замечаний нет, 1 — замечания перечислены в выводе.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Что считается незаполненным остатком в документах.
FORBIDDEN = ("TODO", "FIXME", "XXX", "待补充", "【", "undefined", "NaN")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

ID_RE = re.compile(r"(FR|NFR|BR|C)-\d+")

NFR_UNIT_RE = re.compile(r"\d+ *(мс|с|%|мин|команд)")


def heading_anchors(text: str) -> set:
    """Якоря заголовков в стиле GitHub: «Карта пути» → #карта-пути."""
    anchors = set()
    for line in text.splitlines():
        match = re.match(r"#{1,6}\s+(.*)", line)
        if not match:
            continue
        title = re.sub(r"[*`]", "", match.group(1)).strip().lower()
        title = re.sub(r"[^\w\s-]", "", title)
        anchors.add(re.sub(r"\s+", "-", title))
    return anchors


def check_file(path: Path) -> list:
    """Возвращает список замечаний по одному Markdown-файлу."""
    issues = []
    rel = path.relative_to(REPO)
    raw = path.read_bytes()

    if raw.startswith(b"\xef\xbb\xbf"):
        issues.append(f"{rel}: файл начинается с BOM — сохранить в UTF-8 без BOM")
    if b"\r" in raw:
        issues.append(f"{rel}: переводы строк CRLF — должен быть LF (см. .gitattributes)")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        issues.append(f"{rel}: файл не читается как UTF-8 ({error})")
        return issues
    if not text.endswith("\n"):
        issues.append(f"{rel}: в конце файла нет пустой строки")

    anchors = heading_anchors(text)
    in_code = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for token in FORBIDDEN:
            if token in line:
                issues.append(f"{rel}:{lineno}: незаполненный остаток «{token}»")
        for match in LINK_RE.finditer(line):
            target = match.group(1).split()[0]
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if target.startswith("#"):
                anchor = target[1:]
                if anchor and anchor not in anchors:
                    issues.append(f"{rel}:{lineno}: якоря нет в файле: #{anchor}")
                continue
            target_path = (path.parent / target.split("#")[0]).resolve()
            if not target_path.exists():
                issues.append(f"{rel}:{lineno}: файл по ссылке не найден: {target}")
    return issues


def check_traceability(text: str) -> list:
    """Строки таблиц матрицы без идентификатора требования (ЛР 2А).

    Заголовки и разделители таблиц пропускаются; пустой список — проверка
    пройдена.
    """
    issues = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[-:| ]+$", line):
            continue
        if line.startswith(("| ID", "| Критерий", "| Шаг пути")):
            continue
        if not ID_RE.search(line):
            issues.append(f"docs/traceability.md:{lineno}: строка матрицы без идентификатора")
    return issues


def check_nfr_numbers(text: str) -> list:
    """Разделы NFR без величины с единицей (ЛР 2А).

    Раздел просматривается целиком, до следующего заголовка. Пустой список —
    проверка пройдена.
    """
    issues = []
    header = ""
    has_number = False
    for line in text.splitlines():
        if line.startswith("### `NFR"):
            if header and not has_number:
                issues.append(f"docs/requirements.md: {header}: нет величины с единицей")
            header, has_number = line, False
        elif line.startswith("#"):
            if header and not has_number:
                issues.append(f"docs/requirements.md: {header}: нет величины с единицей")
            header, has_number = "", False
        elif header and NFR_UNIT_RE.search(line):
            has_number = True
    if header and not has_number:
        issues.append(f"docs/requirements.md: {header}: нет величины с единицей")
    return issues


def main() -> int:
    md_files = sorted(
        path
        for path in REPO.rglob("*.md")
        if not any(part in path.parts for part in (".git", ".venv", "node_modules"))
    )
    if not md_files:
        print("Markdown-файлы не найдены — скрипт запущен не из корня репозитория?")
        return 1

    issues = []
    for path in md_files:
        issues.extend(check_file(path))

    traceability = REPO / "docs" / "traceability.md"
    if traceability.exists():
        issues.extend(check_traceability(traceability.read_text(encoding="utf-8")))

    requirements = REPO / "docs" / "requirements.md"
    if requirements.exists():
        issues.extend(check_nfr_numbers(requirements.read_text(encoding="utf-8")))

    if issues:
        print(f"Проверка документов: замечаний {len(issues)}\n")
        for issue in issues:
            print(f"  {issue}")
        return 1
    print(f"Проверка документов: замечаний нет (файлов проверено: {len(md_files)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
