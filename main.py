import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from file_collector import file_collector
from ollama_process import ollama_process
from framework_detector import detect_framework
from dependency_analyzer import analyze_composer_dependencies_cached  # Новый импорт


def main():
    # Создаём парсер аргументов командной строки для удобного взаимодействия с программой
    parser = argparse.ArgumentParser(description="Поиск всех файлов с указанными расширениями в заданной директории.")

    # Добавляем аргумент для пути к директории, которую будем искать
    parser.add_argument("directory", type=str, help="Путь к директории")

    # Добавляем аргумент для имени модели, которая будет использоваться для обработки файлов
    parser.add_argument("-m", "--model", type=str, required=True, help="Имя модели")

    # Добавляем возможность указать несколько расширений файлов для поиска
    parser.add_argument("-e", "--extensions", nargs="+", required=False, default=[], help="Список расширений файлов для поиска")

    # Добавляем возможность указать количество потоков
    parser.add_argument("-t", "--threads", type=int, required=False, default=3, help="Количество потоков")

    # Добавляем возможность указать фреймворк или cms вручную
    parser.add_argument("-f", "--framework", type=str, required=False, help="Фреймворк/CMS")

    # Добавляем директории, которые необходимо исключить
    parser.add_argument("-ed", "--exclude-dirs", nargs="+", help="Директории для исключения", default=[])

    # Добавляем файлы, которые необходимо исключить
    parser.add_argument("-ef", "--exclude-files", nargs="+", help="Файлы для исключения", default=[])

    # Добавляем паттерны, которые необходимо исключить
    parser.add_argument("-ep", "--exclude-patterns", nargs="+", help="Патерны для исключения", default=[])
    
    args = parser.parse_args()

    # Определяем фреймворк
    if args.framework:
        framework = args.framework.lower()
    else:
        framework = detect_framework(args.directory)
        print(f"Определен фреймворк: {framework}")

    # Собираем файлы с указанными расширениями в директории
    files = file_collector(args.directory, args.extensions, exclude_dirs=args.exclude_dirs, exclude_files=args.exclude_files, exclude_patterns=args.exclude_patterns)

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

if __name__ == "__main__":
    main()