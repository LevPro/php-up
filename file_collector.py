import os
import re

def file_collector(directory, extensions=None):
    if not os.path.exists(directory):
        raise ValueError(f"{directory} не найден")

    if extensions is None:
        extensions = ['php']  # Добавлен комментарий: значение по умолчанию для расширений файлов

    files = []

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file = os.path.join(root, filename)
                print(f"Добавлен файл: {file}")  # Добавлен комментарий: сообщение о добавлении файла
                files.append(file)

    return files

def find_dependencies(file_path):
    """Находит зависимости файла (импорты, включения, наследование)"""
    dependencies = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # Добавлен комментарий: открытие файла с указанием кодировки
            content = file.read()

            # Регулярные выражения для поиска зависимостей
            patterns = [
                r'use\s+([\w\\\\]+)(?:\s+as\s+\w+)?;',  # use statements
                r'extends\s+([\w\\\\]+)',  # class inheritance
                r'implements\s+([\w\\\\]+(?:\s*,\s*[\w\\\\]+)*)',  # interfaces
                r'new\s+([\w\\\\]+)\s*\(',  # object instantiation
                r'([\w\\\\]+)::',  # static calls
                r'function\s+([\w]+)\s*\([^)]*\)\s*:',  # type hints in parameters
                r':\s*\??\s*([\w\\\\]+)\s*\{',  # return type hints
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, str):
                        dependencies.append(match)  # Добавлен комментарий: добавление найденной зависимости в список
                    else:
                        dependencies.extend([m.strip() for m in match.split(',')])  # Добавлен комментарий: расширение списка зависимостей для массивов

    except Exception as e:
        print(f"Ошибка анализа зависимостей файла {file_path}: {e}")  # Добавлен комментарий: обработка ошибок при чтении файла

    return list(set(dependencies))  # Убираем дубликаты и добавлен комментарий: возвращение списка зависимостей без дубликатов