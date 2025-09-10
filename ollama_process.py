import time
import re

import requests


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

    text = "\n".join(lines)

    # Заменяем множественные переносы строк на двойные
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Удаляем переносы в конце файла
    text = re.sub(r'\n+$', '\n', text)

    return text


def ollama_process(file_content, model, framework, requirements):
    # Добавляем информацию о фреймворке
    framework_info = f"\n7. Проект использует {framework.upper()}" if framework != 'unknown' else ""

    # Добавляем дополнительные требования
    requirements_info = ""
    if len(requirements) > 0:
        start_num = 8 if framework == 'unknown' else 7
        for requirement in requirements:
            requirements_info = requirements_info + f"{start_num}. {requirement}\n"
            start_num += 1


    prompt = f"""Проанализируй предоставленный PHP код и выполни следующие преобразования:
    1. Адаптируй синтаксис под PHP 8.4 с использованием новейших возможностей языка
    2. Добавь комментарии на русском языке для методов и сложных логических блоков
    3. Приведи код к стандартам PSR-12 и современным best practices
    5. Сохрани исходную функциональность при модификации
    6. Верни только полностью исправленный код без пояснений
    {framework_info}

    Код для анализа:
    ```php
    {file_content}
    ```"""

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

    print(f"Отправка запроса в ollam {model}: {prompt}")

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
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")