import os
import json
import re

def detect_framework(directory):
    """Определяет CMS или фреймворк проекта на основе характерных файлов и структуры"""
    # ... существующий код indicators ...
    
    # Проверка через composer.json (приоритетный метод)
    framework = detect_framework_from_composer(directory)
    if framework != 'unknown':
        return framework
    
    # ... остальной код проверок через файловую структуру ...
    
    return 'unknown'


def detect_framework_from_composer(directory):
    """Определяет фреймворк через анализ composer.json"""
    composer_path = os.path.join(directory, 'composer.json')
    
    # Ищем composer.json в родительских директориях
    if not os.path.exists(composer_path):
        current_dir = directory
        while current_dir != os.path.dirname(current_dir):
            current_dir = os.path.dirname(current_dir)
            composer_path = os.path.join(current_dir, 'composer.json')
            if os.path.exists(composer_path):
                break
        else:
            return 'unknown'
    
    try:
        with open(composer_path, 'r', encoding='utf-8') as f:
            composer_data = json.load(f)
            
            # Проверяем зависимости
            requirements = {**composer_data.get('require', {}), **composer_data.get('require-dev', {})}
            
            # Сопоставление пакетов с фреймворками
            framework_mappings = {
                'laravel/framework': 'laravel',
                'symfony/symfony': 'symfony',
                'symfony/framework-bundle': 'symfony',
                'drupal/core': 'drupal',
                'yiisoft/yii2': 'yii2',
                'yiisoft/yii': 'yii',
                'cakephp/cakephp': 'cakephp',
                'codeigniter4/framework': 'codeigniter',
                'phalcon/framework': 'phalcon',
                'slim/slim': 'slim',
                'laminas/laminas-mvc': 'zend',  # Laminas (бывший Zend Framework)
                'laminas/laminasframework': 'zend',
                'zf-commons/zfc-base': 'zend',
                'typo3/cms-core': 'typo3',
                'concrete5/concrete5': 'concrete5',
                'october/rain': 'octobercms',
                'october/cms': 'octobercms',
                'pagekit/pagekit': 'pagekit',
                'pyrocms/pyrocms': 'pyrocms',
                'getkirby/cms': 'kirby',
                'bolt/bolt': 'bolt',
                'backdrop/backdrop': 'backdrop',
                'prestashop/prestashop': 'prestashop',
                'magento/magento2-base': 'magento',
                'magento/product-community-edition': 'magento',
                'opencart/opencart': 'opencart',
                'woocommerce/woocommerce': 'woocommerce',
                'shopware/shopware': 'shopware',
                'sylius/sylius': 'sylius',
                'orocrm/platform': 'orocrm',
                'oro/platform': 'oro',
                'ibexa/core': 'ibexa',  # бывший eZ Platform
                'ezsystems/ezplatform': 'ezplatform',
                'neos/flow': 'neos',
                'neos/neos': 'neos',
                'pimcore/pimcore': 'pimcore',
                'spryker/spryker': 'spryker',
                'api-platform/core': 'api-platform',
            }
            
            # Проверяем каждую зависимость
            for package, framework_name in framework_mappings.items():
                if package in requirements:
                    return framework_name
            
            # Проверяем автозагрузку PSR-4 для определения фреймворков
            autoload = composer_data.get('autoload', {}).get('psr-4', {})
            for namespace, path in autoload.items():
                if 'laravel' in namespace.lower() or 'laravel' in str(path).lower():
                    return 'laravel'
                elif 'symfony' in namespace.lower() or 'symfony' in str(path).lower():
                    return 'symfony'
                elif 'yii' in namespace.lower() or 'yii' in str(path).lower():
                    return 'yii'
                    
    except Exception as e:
        print(f"Ошибка анализа composer.json: {e}")
    
    return 'unknown'