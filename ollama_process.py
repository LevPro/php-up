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
    # Используем регулярное выражение для поиска блока кода
    match = re.search(r'```php(.*?)```', text, re.DOTALL)
        
    if not match:
        return ''
        
    # Извлекаем содержимое блока кода
    code_block = match.group(1).strip()

    # Если ничего не нашли - возвращаем пустую строку
    if code_block == '':
        return code_block
        
    # Удаляем лишние пустые строки в начале и конце
    while code_block and code_block[0] == '':
        code_block = code_block[1:]
    while code_block and code_block[-1] == '':
        code_block = code_block[:-1]
    
    return code_block


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
    framework_info = f"\nУчитывай, что проект использует {framework.upper()}" if framework != 'unknown' else ""

    # Добавляем дополнительные требования
    requirements_info = ""
    if len(requirements) > 0:
        start_num = 1
        requirements_info = "Дополнительные требования:\n"
        for requirement in requirements:
            requirements_info = requirements_info + f"{start_num}. {requirement}\n"
            start_num += 1

    # Упрощенный промпт для ускорения обработки
    prompt = f"""Задача: Привести предоставленный ниже PHP-код к стандартам PSR12.
    
    Исходный код:
    ```php
    {file_content}
    ```
    {requirements_info}

    {framework_info}"""

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
        result = result.replace('<? ', '<?php ')

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
