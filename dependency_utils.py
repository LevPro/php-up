import re

def get_relevant_dependencies(file_content, composer_dependencies):
    """Определяет зависимости, которые действительно используются в файле"""
    relevant_deps = {}
    
    # Приводим содержимое файла к нижнему регистру для поиска
    content_lower = file_content.lower()
    
    for dep_name, dep_version in composer_dependencies.items():
        # Извлекаем короткое имя зависимости (последнюю часть после /)
        short_name = dep_name.split('/')[-1]
        
        # Ищем упоминания в различных контекстах
        patterns = [
            r'use\s+[^;]*' + re.escape(short_name),  # use statements
            r'new\s+' + re.escape(short_name),       # object instantiation
            r'extends\s+' + re.escape(short_name),   # class inheritance
            r'implements\s+' + re.escape(short_name), # interface implementation
            r'\\' + re.escape(short_name),           # namespaced references
        ]
        
        # Проверяем, есть ли совпадения с любым из паттернов
        for pattern in patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                relevant_deps[dep_name] = dep_version
                break
    
    return relevant_deps


def format_dependencies_for_prompt(dependencies):
    """Форматирует зависимости для включения в промпт"""
    if not dependencies:
        return ""
    
    formatted = "\n\nComposer зависимости (используемые в файле):\n"
    for dep_name, dep_version in dependencies.items():
        formatted += f"- {dep_name}: {dep_version}\n"
    
    return formatted