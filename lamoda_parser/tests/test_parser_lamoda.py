import unittest
import os
from lamoda_parser.parser import get_response, get_html, get_item_urls, get_item, save_items, HOST, HEADERS
#Lamoda блокирует наши запросы. 
class TestLamodaParser(unittest.TestCase):
    def setUp(self):
        self.test_url = 'https://www.lamoda.ru/c/5374/accs_ns-elektrchasymuj/'
        self.test_item_url = 'https://www.lamoda.ru/p/mp002xw1k7ta/accs-casio-chasy/'

    def test_get_response(self):
        response = get_response('https://www.lamoda.ru')
        self.assertNotEqual(response, False)

    def test_get_html(self):
        """Тест получения HTML"""
        html = get_html(self.test_url)
        self.assertNotEqual(html, False)
        self.assertIsInstance(html, str)

    def test_get_item_urls(self):
        """Тест получения ссылок на товары"""
        html = get_html(self.test_url)
        if html:  # Проверяем, что HTML получен успешно
            urls = get_item_urls(html)
            self.assertTrue(len(urls) > 0)
            self.assertTrue(all(url.startswith(HOST) for url in urls))

    def test_get_item(self):
        """Тест получения информации о товаре"""
        item = get_item(self.test_item_url)
        if item:  # Проверяем, что товар получен успешно
            required_fields = ['url', 'brand_name', 'price_current']
            for field in required_fields:
                self.assertIn(field, item)

    def test_save_items(self):
        """Тест сохранения данных"""
        test_items = [
            {
                'model_name': 'Test Model',
                'marking': '12345',
                'url': 'http://test.com',
                'brand_name': 'Test Brand',
                'price_current': '1000 RUB'
            }
        ]
        result = save_items(test_items, 'test_output.csv')
        self.assertTrue(result)
        if os.path.exists('test_output.csv'):
            os.remove('test_output.csv')

if __name__ == '__main__':
    unittest.main()
