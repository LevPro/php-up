import re
import json
import requests


def _extract_json_from_string(text):
    # Паттерн для поиска JSON-массива, начинающегося с [{ и заканчивающегося }]
    pattern = r"\[\s*\{.*?\}\s*\]"
    matches = re.findall(pattern, text, re.DOTALL)

    for match in matches:
        try:
            # Пытаемся распарсить найденную строку как JSON
            data = json.loads(match)
            # Проверяем, что это список словарей с нужными полями
            if isinstance(data, list) and all(
                isinstance(item, dict)
                and {"file", "text", "changes"}.issubset(item.keys())
                for item in data
            ):
                return data
        except json.JSONDecodeError:
            continue  # Если парсинг не удался, пробуем следующий match
    return None  # Если ничего не найдено


def ollama_process(files_content, model):
    files_info = ""

    for file in files_content:
        files_info += f"""{file['file_path']}:
        {file['content']}

        """

    # Промт для обработки
    prompt = f"""Analyze the provided PHP code files and perform the following comprehensive refactoring:
    {files_info}

    ## **Primary Objectives:**
    1. **PSR-12 Compliance:**
   - Apply PSR-12 coding standards to all files
   - Use 4 spaces for indentation (no tabs)
   - Ensure proper brace placement and line breaks
   - Standardize class, method, and property declarations
   - Format namespaces and use statements according to PSR-12
   - Apply proper naming conventions (PascalCase for classes, camelCase for methods/variables)
   - Handle line length limits appropriately (soft limit 120 characters)
    2. **Error Correction:**
   - Fix all syntax errors and parse issues
   - Resolve undefined variables, functions, and methods
   - Correct scope and visibility issues
   - Fix type-related problems and incompatible operations
   - Remove unreachable code and logical errors
    3. **Modernization:**
   - Replace deprecated functions (e.g., `mysql_*` → `mysqli_*` or PDO)
   - Update array functions to modern equivalents
   - Replace `create_function()` with arrow functions or closures
   - Update `ereg`/`split` to PCRE functions (`preg_*`)
   - Modernize error handling (replace `@` operator with proper try/catch)
   - Update short opening tags `<?` to `<?php`
   - Replace `each()` with `foreach`
   - Update `list()` to destructuring assignment where applicable

    ## **File Processing Instructions:**
    - Process each file separately and maintain file structure
    - Preserve original functionality and business logic
    - Add `declare(strict_types=1);` where appropriate
    - Replace `array()` with short array syntax `[]`
    - Use modern string interpolation instead of concatenation
    - Update JSON functions to use modern flags and error handling
    - Apply type hints and return type declarations where possible
    - Add `@throws` annotations for exception documentation

    ## **Security & Best Practices:**
    - Sanitize input/output handling where evident issues exist
    - Update SQL queries to use parameterized statements if raw queries are found
    - Validate and escape output where obvious XSS risks are present

    ## **Output Format:**
    The response must be only a valid JSON array. Use the following schema as the exact format. The "text" field must be the complete, corrected code for the file.
    
    JSON schema for the response::
    """
    prompt += '[{"file": "/path/to/example.php", "text": "<?php [$var["test"] ?? "", $var["test3"]] # This is the full corrected code ...", "changes": "Change Array() to shorts array"}]'

    print(f"Отправка запроса {prompt}")

    # Указываем корректный URL для локального сервера Ollama
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    # Формируем тело запроса с указанием модели и промта
    data = {"model": model, "prompt": prompt, "stream": False}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=3600)
        response.raise_for_status()

        # Извлекаем результат из поля 'response' в JSON
        result = response.json()
        result = result["response"]

        print(f"Получен ответ {result}")

        result = _extract_json_from_string(result)

        return result

    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к Ollama: {str(e)}")
