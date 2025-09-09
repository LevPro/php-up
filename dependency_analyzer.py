import re

from file_collector import find_dependencies


def analyze_dependencies(main_file_path, all_files):
    """Анализирует зависимости и находит соответствующие файлы"""
    dependencies = find_dependencies(main_file_path)
    dependency_files = {}

    for dep in dependencies:
        # Ищем файл, соответствующий зависимости
        for file_path in all_files:
            if is_dependency_in_file(dep, file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        dependency_files[dep] = f.read()
                except Exception as e:
                    print(f"Ошибка чтения файла зависимости {file_path}: {e}")
                break

    return dependency_files


def is_dependency_in_file(dependency, file_path):
    """Проверяет, содержится ли зависимость в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Простые проверки на соответствие
            class_pattern = r'class\s+' + re.escape(dependency.split('\\')[-1])
            interface_pattern = r'interface\s+' + re.escape(dependency.split('\\')[-1])
            trait_pattern = r'trait\s+' + re.escape(dependency.split('\\')[-1])

            return (re.search(class_pattern, content) or
                    re.search(interface_pattern, content) or
                    re.search(trait_pattern, content))

    except Exception as e:
        print(f"Ошибка проверки зависимости {dependency} в файле {file_path}: {e}")
        return False