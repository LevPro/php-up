import time

import requests
from dependency_analyzer import analyze_dependencies
from dependency_utils import get_relevant_dependencies, format_dependencies_for_prompt  # Новые импорты


def _strip_code_fences(text: str) -> str:
    """Убирает внешние тройные бэктики ```...``` и возможный язык после них, не трогая содержимое.
    Работает построчно: если первая строка начинается с ``` — убираем её; если последняя строка — тоже ``` — убираем.
    Ничего не удаляем внутри тела.
    """
    if not text:
        return text
    lines = text.splitlines()
    # trim leading/trailing empty lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    if not lines:
        return ""

    first = lines[0].strip()
    last = lines[-1].strip()

    if first.startswith("```"):
        # убрать первую строку (может быть ``` или ```php)
        lines = lines[1:]
        # убрать возможные пустые строки в начале
        while lines and lines[0].strip() == "":
            lines.pop(0)
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    elif last.startswith("```"):
        # только закрывающая — убираем её
        lines = lines[:-1]

    return "\n".join(lines)


def ollama_process(file_content, model, file_path, all_files, framework, composer_deps):
    # Анализируем зависимости
    dependencies = analyze_dependencies(file_path, all_files)

    # Формируем контекст зависимостей из файлов
    dependency_context = "\n\nЗависимости из файлов:\n"
    for dep_name, dep_content in dependencies['file_dependencies'].items():
        dependency_context += f"--- {dep_name} ---\n{dep_content}\n\n"

    # Фильтруем composer зависимости, оставляя только используемые в файле
    relevant_composer_deps = get_relevant_dependencies(file_content, composer_deps)
    composer_context = format_dependencies_for_prompt(relevant_composer_deps)

    # Добавляем информацию о фреймворке
    framework_info = f"\n7. Учти, что проект использует {framework.upper()}" if framework != 'unknown' else ""

    prompt = f"""Проанализируй предоставленный PHP код и выполни следующие преобразования:
    1. Адаптируй синтаксис под PHP 8.4 с использованием новейших возможностей языка
    2. Добавь комментарии на русском языке для методов и сложных логических блоков
    3. Приведи код к стандартам PSR-12 и современным best practices
    4. Учитывай контекст зависимостей (приложены ниже):
       - Проверь корректность использования методов
       - Убедись в правильности наследования и реализации интерфейсов
       - Проверь соответствие сигнатур методов
       - Учти версии внешних библиотек из composer.json
    5. Сохрани исходную функциональность при модификации
    6. Верни только полностью исправленный код без пояснений
    {framework_info}

    Код для анализа:
    ```php
    {file_content}
    ```
    
    {dependency_context}
    {composer_context}"""

    # Начало отсчета времени
    start_time = time.time()

    # Указываем корректный URL для локального сервера Ollama
    url = 'http://localhost:11434/api/generate'
    headers = {'Content-Type': 'application/json'}

    # Формируем тело запроса с указанием модели и промта
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=600)
        response.raise_for_status()

        # Извлекаем результат из поля 'response' в JSON
        result_json = response.json()
        raw = result_json.get('response', '')
        result = _strip_code_fences(raw)

        # Окончание отсчета времени
        end_time = time.time()
        processing_time = end_time - start_time

        return {
            "processing_time": processing_time,
            "result": result,
            "file_path": file_path,
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")