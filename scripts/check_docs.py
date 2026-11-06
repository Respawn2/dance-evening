#!/usr/bin/env python3
"""Проверка документов репозитория.

Запускается и локально, и в конвейере (задание «Плейсхолдеры и ссылки»
в .github/workflows/checks.yml). Только стандартная библиотека.

Что проверяет:
- кодировка UTF-8, отсутствие BOM и переводов строк CRLF;
- пустая строка в конце файла;
- незаполненные остатки: TODO, FIXME и подобные;
- ссылки на локальные файлы и якоря заголовков.

Выход: 0 — замечаний нет, 1 — замечания перечислены в выводе.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Что считается незаполненным остатком в документах.
FORBIDDEN = ("TODO", "FIXME", "XXX", "待补充", "【", "undefined", "NaN")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


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


def main() -> int:
    md_files = sorted(
        path
        for path in REPO.rglob("*.md")
        if not any(part in path.parts for part in (".git", "node_modules"))
    )
    if not md_files:
        print("Markdown-файлы не найдены — скрипт запущен не из корня репозитория?")
        return 1

    issues = []
    for path in md_files:
        issues.extend(check_file(path))

    if issues:
        print(f"Проверка документов: замечаний {len(issues)}\n")
        for issue in issues:
            print(f"  {issue}")
        return 1
    print(f"Проверка документов: замечаний нет (файлов проверено: {len(md_files)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
