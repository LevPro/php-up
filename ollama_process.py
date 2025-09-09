import time

import requests
from dependency_analyzer import analyze_dependencies


def ollama_process(file_content, model, file_path, all_files):
    # Анализируем зависимости
    dependencies = analyze_dependencies(file_path, all_files)

    # Формируем контекст зависимостей
    dependency_context = "\n\nЗависимости:\n"
    for dep_name, dep_content in dependencies.items():
        dependency_context += f"--- {dep_name} ---\n{dep_content}\n\n"

    prompt = f"""Проанализируй предоставленный PHP код и выполни следующие преобразования:
    1. Адаптируй синтаксис под PHP 8.4 с использованием новейших возможностей языка
    2. Добавь комментарии на русском языке для методов и сложных логических блоков
    3. Приведи код к стандартам PSR-12 и современным best practices
    4. Учитывай контекст зависимостей (приложены ниже):
       - Проверь корректность использования методов
       - Убедись в правильности наследования и реализации интерфейсов
       - Проверь соответствие сигнатур методов
    5. Сохрани исходную функциональность при модификации
    6. Верни только полностью исправленный код без пояснений

    Код для анализа:
    ```php
    {file_content}
    ```
    
    {dependency_context}"""

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
        result = result['response'].replace("```", '').replace(" php", '')

        # Окончание отсчета времени
        end_time = time.time()
        processing_time = end_time - start_time

        return {
            "processing_time": processing_time,
            "result": result
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")