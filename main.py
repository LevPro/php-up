import argparse
import chardet

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

    # Добавляем директории, которые необходимо исключить
    parser.add_argument("-ed", "--exclude-dirs", nargs="+", help="Директории для исключения", default=[])

    # Добавляем файлы, которые необходимо исключить
    parser.add_argument("-ef", "--exclude-files", nargs="+", help="Файлы для исключения", default=[])

    # Добавляем паттерны, которые необходимо исключить
    parser.add_argument("-ep", "--exclude-patterns", nargs="+", help="Патерны для исключения", default=[])

    # Парсим аргументы командной строки
    args = parser.parse_args()

    # Собираем файлы с указанными расширениями в директории
    files = file_collector(args.directory, ['.php', '.phtml'], exclude_dirs=args.exclude_dirs, exclude_files=args.exclude_files, exclude_patterns=args.exclude_patterns)

    try:
        # Получаем контент файлов
        files_content = []

        for file_path in files:
            try:
                # Читаем содержимое файла
                with open(file_path, 'rb') as file:
                    data = file.read()
                    detected_encoding = chardet.detect(data)  # Определяем кодировку
                    encoding = detected_encoding['encoding']
                    confidence = detected_encoding['confidence']
                    if encoding is None or confidence < 0.5:
                        print(f"Не удалось определить кодировку для {file_path} (уверенность: {confidence})")
                        continue
                    text = data.decode(encoding)  # Декодируем байты в строку
                    # Добавляем в коллекцию для анализа
                    files_content.append({
                        'file_path': file_path,
                        'content': text
                    })
            except Exception as e:
                print(f"Ошибка чтения файла {file_path}: {e}")
        if len(files_content) > 0:
            # Получаем результат
            result = ollama_process(files_content, args.model)

            changes = ''

            if result is not None:
                for item in result:
                    print(f"Обновляем файл {item['file']}")

                    # Записываем изменения по файлу в строку для отдельного документа
                    changes += f"""{item['file']}:
                    {item['changes']}

                    """

                    # Записываем изменения
                    with open(item['file'], 'w', encoding='utf-8') as file:
                        file.write(item['text'])

                with open('report.txt', 'w') as file:
                    file.write(changes)
            else:
                print("Нет файлов для изменений") 
        else:
            print("Не найдено файлов для анализа и изменений")
    except Exception as e:
        print(f"Ошибка обработки файлов: {e}")
        return None


# Если скрипт запущен как основная программа, вызываем функцию main()
if __name__ == "__main__":
    main()