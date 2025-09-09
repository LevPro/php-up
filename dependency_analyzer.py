import os
import json
from functools import lru_cache

from file_collector import find_dependencies

def is_dependency_in_file(dep, file_path):
    """Проверяет наличие зависимости в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return dep in content
    except Exception:
        return False

# Кэшируем анализ composer.json для улучшения производительности
@lru_cache(maxsize=1)
def analyze_composer_dependencies_cached(project_dir):
    """Кэшированная версия анализа composer.json"""
    return analyze_composer_dependencies(project_dir)


def analyze_dependencies(main_file_path, all_files):
    """Анализирует зависимости и находит соответствующие файлы"""
    dependencies = find_dependencies(main_file_path)
    dependency_files = {}
    
    # Получаем зависимости из composer.json (кэшированные)
    project_dir = os.path.dirname(main_file_path)
    composer_deps = analyze_composer_dependencies_cached(project_dir)

    # Кэшируем содержимое файлов один раз для снижения IO
    file_cache = {}
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_cache[file_path] = f.read()
        except Exception as e:
            # Пропускаем проблемные файлы, но продолжаем анализ
            print(f"Ошибка чтения файла {file_path}: {e}")

    for dep in dependencies:
        # Ищем файл, соответствующий зависимости, используя кэш
        for file_path, content in file_cache.items():
            if dep in content:
                dependency_files[dep] = content
                break

    return {
        'file_dependencies': dependency_files,
        'composer_dependencies': composer_deps
    }


def analyze_composer_dependencies(project_dir):
    """Анализирует зависимости из composer.json"""
    composer_path = os.path.join(project_dir, 'composer.json')
    
    # Ищем composer.json в родительских директориях
    if not os.path.exists(composer_path):
        current_dir = project_dir
        while current_dir != os.path.dirname(current_dir):
            current_dir = os.path.dirname(current_dir)
            composer_path = os.path.join(current_dir, 'composer.json')
            if os.path.exists(composer_path):
                break
        else:
            return {}  # composer.json не найден
    
    try:
        with open(composer_path, 'r', encoding='utf-8') as f:
            composer_data = json.load(f)
            
            # Извлекаем зависимости
            require = composer_data.get('require', {})
            require_dev = composer_data.get('require-dev', {})
            
            # Объединяем зависимости
            all_dependencies = {**require, **require_dev}
            
            # Фильтруем только PHP-зависимости (исключаем расширения PHP и системные пакеты)
            php_dependencies = {}
            for package, version in all_dependencies.items():
                if not package.startswith(('ext-', 'lib-', 'php')):
                    php_dependencies[package] = version
                    
            return php_dependencies
                
    except Exception as e:
        print(f"Ошибка анализа composer.json: {e}")
        return {}