import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from file_collector import file_collector
from ollama_process import ollama_process
from framework_detector import detect_framework
from dependency_analyzer import analyze_composer_dependencies_cached  # Новый импорт


def main():
    parser = argparse.ArgumentParser(description="Поиск всех файлов с указанными расширениями в заданной директории.")
    
    # ... существующие аргументы ...
    
    args = parser.parse_args()

    # Определяем фреймворк
    if args.framework:
        framework = args.framework.lower()
    else:
        framework = detect_framework(args.directory)
        print(f"Определен фреймворк: {framework}")

    # Собираем файлы с указанными расширениями в директории
    files = file_collector(args.directory, args.extensions)
    
    # Анализируем composer зависимости один раз для всего проекта
    composer_deps = analyze_composer_dependencies_cached(args.directory)

    # Определяем количество асинхронных потоков
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Передаем composer зависимости в process_file
        futures = [executor.submit(process_file, file_path, args.model, args.extensions, files, framework, composer_deps) for file_path in files]

        # Ожидаем завершения всех задач и обрабатываем результаты
        for future in futures:
            try:
                result = future.result()
                print(f"Обновлён файл: {result['file_path']}. Время обработки файла: {result['processing_time']}")
            except Exception as e:
                print(f"Ошибка при обработке файла: {e}")


def process_file(file_path, model, extensions, all_files, framework, composer_deps):
    """Функция для обработки отдельного файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        # Передаем composer зависимости в ollama_process
        process_result = ollama_process(file_content, model, file_path, all_files, framework, composer_deps)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(process_result['result'])

        return {
            "processing_time": process_result['processing_time'],
            "file_path": file_path
        }
    except Exception as e:
        raise Exception(f"Ошибка при обработке файла {file_path}: {e}")