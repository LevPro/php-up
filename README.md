# PHP Code Modernizer

Инструмент для автоматической модернизации PHP-кода с использованием возможностей Ollama AI.

## Возможности

- Автоматическая конвертация кода в стандарт PSR12
- Автоматическое устранение ошибок
- Устранение проблем с безопасностью
- Добавление комментариев на русском языке
- Приведение к стандартам PSR-12

## Установка

1. Установите [Ollama](https://ollama.ai/)
2. Клонируйте репозиторий:
```bash
git clone https://github.com/LevPro/php-up
cd php-up
```
3. Установите зависимости: 
```bash
pip install -r requirements.txt
```

## Использование
```bash
python main.py /path/to/php/project -m codellama:7b -e php phtml -ed "/full/path/vendor" "/full/path/.git" -ep "*.test.php" "temp_*"
```
Параметры командной строки:
- directory (обязательный): Путь к директории с PHP-проектом
- -m/--model (обязательный): Имя модели Ollama
- -r/--requirements: Дополнительные требования (опционально)
- -t/--threads: Количество потоков (опционально)
- -ed/--exclude-dirs - полные пути к директориям для исключения (опционально)
- -ef/--exclude-files - полные пути к файлам для исключения (опционально)
- -ep/--exclude-patterns - маски для исключения (например, *.test.php, temp_*) (опционально)