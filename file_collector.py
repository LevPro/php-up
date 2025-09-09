import fnmatch
import os
import re


def should_exclude(path, exclude_dirs, exclude_files, exclude_patterns):
    """Проверяет, нужно ли исключить путь"""
    # Проверка точных совпадений директорий
    if any(os.path.abspath(path) == os.path.abspath(ex_dir) for ex_dir in exclude_dirs):
        return True

    # Проверка точных совпадений файлов
    if any(os.path.abspath(path) == os.path.abspath(ex_file) for ex_file in exclude_files):
        return True

    # Проверка по паттернам
    filename = os.path.basename(path)
    if any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns):
        return True

    return False


def file_collector(directory, extensions=None, exclude_dirs=None, exclude_files=None, exclude_patterns=None):
    if not os.path.exists(directory):
        raise ValueError(f"{directory} не найден")

    if extensions is None:
        extensions = ['php']

    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
    if exclude_patterns is None:
        exclude_patterns = []

    files = []

    for root, dirs, filenames in os.walk(directory):
        # Исключаем директории из дальнейшего обхода
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_dirs, [], exclude_patterns)]

        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, filename)

                if should_exclude(file_path, [], exclude_files, exclude_patterns):
                    print(f"Исключен файл: {file_path}")
                    continue

                print(f"Добавлен файл: {file_path}")
                files.append(file_path)

    return files


def find_dependencies(file_path):
    """Находит зависимости PHP файла (include, require, use statements)"""
    dependencies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Поиск include/require statements
            include_patterns = [
                r'include\s*[\'"]([^\'"]+)[\'"]',
                r'require\s*[\'"]([^\'"]+)[\'"]',
                r'include_once\s*[\'"]([^\'"]+)[\'"]',
                r'require_once\s*[\'"]([^\'"]+)[\'"]'
            ]

            for pattern in include_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)

            # Поиск use statements (импорты классов)
            use_pattern = r'use\s+([^;]+);'
            use_matches = re.findall(use_pattern, content)
            for match in use_matches:
                # Убираем пробелы и добавляем в зависимости
                cleaned = match.strip()
                if cleaned:
                    dependencies.append(cleaned)

    except Exception as e:
        print(f"Ошибка поиска зависимостей в файле {file_path}: {e}")

    return dependencies