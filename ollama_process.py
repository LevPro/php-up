import time
import re
import requests
import hashlib

from functools import lru_cache
from cache import load_cache, save_cache

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

    # Заменяем множественные переносы строк
    text = re.sub(r'\n{2,}', '\n', text)
    # Удаляем переносы в конце файла
    text = re.sub(r'\n+$', '\n', text)

    return text


@lru_cache(maxsize=1000)
def _generate_prompt_hash(file_content, framework, requirements):
    """Генерирует хэш для кэширования промптов"""
    content = f"{file_content}_{framework}_{'_'.join(requirements)}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def ollama_process(file_content, model, framework, requirements):
    # Генерируем хэш для кэширования
    content_hash = _generate_prompt_hash(file_content, framework or "unknown", tuple(requirements))

    # Проверяем, есть ли результат в кэше
    cache = load_cache()

    if content_hash in cache:
        cached_result = cache[content_hash]
        return {
            "processing_time": cached_result["processing_time"],
            "result": cached_result["result"]
        }

    # Добавляем информацию о фреймворке
    framework_info = f"\n6. Проект использует {framework.upper()}" if framework != 'unknown' else ""

    # Добавляем дополнительные требования
    requirements_info = ""
    if len(requirements) > 0:
        start_num = 7 if framework != 'unknown' else 6
        for requirement in requirements:
            requirements_info = requirements_info + f"{start_num}. {requirement}\n"
            start_num += 1

    # Упрощенный промпт для ускорения обработки
    prompt = f"""Модернизируй PHP код:
    1. Адаптируй под PHP 8.4
    2. Добавь комментарии на русском
    3. Приведи к стандартам PSR-12
    4. Сохрани функциональность
    5. В ответе предоставь только код без пояснений
    {framework_info}
    {requirements_info}

    Код:
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

    try:
        response = requests.post(url, headers=headers, json=data, timeout=600)
        response.raise_for_status()

        # Извлекаем результат из поля 'response' в JSON
        result = response.json()
        result = result['response']
        result = _strip_code_fences(result)

        # Окончание отсчета времени
        end_time = time.time()
        processing_time = end_time - start_time

        # Сохраняем результат в кэш
        cache[content_hash] = {
            "processing_time": processing_time,
            "result": result
        }

        save_cache(cache)

        return {
            "processing_time": processing_time,
            "result": result
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")