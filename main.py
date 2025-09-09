import argparse

# Импортируем функции для сбора файлов и обработки данных с использованием модели ollama
from file_collector import file_collector
from ollama_process import ollama_process


def main():
    # Создаём парсер аргументов командной строки для удобного взаимодействия с программой
    parser = argparse.ArgumentParser(description="Поиск всех файлов с указанными расширениями в заданной директории.")

    # Добавляем аргумент для пути к директории, которую будем искать
    parser.add_argument("directory", type=str, help="Путь к директории")

    # Добавляем аргумент для имени модели, которая будет использоваться для обработки файлов
    parser.add_argument("-m", "--model", type=str, required=True, help="Имя модели")

    # Добавляем возможность указать несколько расширений файлов для поиска
    parser.add_argument("-e", "--extensions", nargs="+", required=False, help="Список расширений файлов для поиска")

    # Парсим аргументы командной строки
    args = parser.parse_args()

    # Собираем файлы с указанными расширениями в директории
    files = file_collector(args.directory, args.extensions)

    # Проходим по собранным файлам
    for file_path in files:
        # Читаем содержимое файла
        try: # Обрабатываем ошибки чтения файла
            with open(file_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
            continue
        

        # Обрабатываем содержимое файла с использованием указанной модели
        try:
            process_result = ollama_process(original_content, args.model)
        except Exception as e:
            print(f"Ошибка обработки файла {file_path}: {e}")
            continue

        # Записываем результат обратно в файл
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(process_result['result'])

        print(f"Обновлён файл: {file_path}. Время обработки файла: {process_result['processing_time']}")


# Если скрипт запущен как основная программа, вызываем функцию main()
if __name__ == "__main__":
    main()