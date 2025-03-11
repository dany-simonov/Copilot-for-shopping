import unittest
from unittest.mock import Mock, patch
import requests
from lamoda_parser.parser import LamodaParser

class TestLamodaParser(unittest.TestCase):
    def setUp(self):
        self.parser = LamodaParser()
        self.test_url = "https://www.lamoda.ru/c/369/clothes-platiya/"

    def test_initialization(self):
        """Тест инициализации парсера"""
        self.assertIsNotNone(self.parser)
        self.assertEqual(self.parser.HOST, 'https://www.lamoda.ru')
        self.assertEqual(self.parser.MAX_RETRIES, 3)

    @patch('requests.get')
    def test_get_response(self, mock_get):
        """Тест метода получения ответа от сервера"""
        # Мокаем успешный ответ
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response = self.parser.get_response(self.test_url)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

    @patch('requests.get')
    def test_failed_response(self, mock_get):
        """Тест обработки неудачного запроса"""
        mock_get.side_effect = requests.exceptions.RequestException
        response = self.parser.get_response(self.test_url)
        self.assertIsNone(response)

    def test_parse_product_page(self):
        """Тест парсинга страницы товара"""
        test_html = """
        <html>
            <h1 class="product-title__brand-name">Test Brand</h1>
            <span class="product-prices__price_current">1000 руб.</span>
            <div class="product-title__model-name">Test Model</div>
            <pre itemprop="description">Test Description</pre>
        </html>
        """
        with patch('parser.LamodaParser.get_response') as mock_response:
            mock_response.return_value.text = test_html
            product = self.parser.parse_product_page(self.test_url)
            
            self.assertEqual(product['title'], 'Test Brand')
            self.assertEqual(product['price'], '1000 руб.')

    def test_save_results(self):
        """Тест сохранения результатов"""
        test_items = [
            {'title': 'Test1', 'price': '1000'},
            {'title': 'Test2', 'price': '2000'}
        ]
        self.parser.items = test_items
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            self.parser.save_results('test.csv')
            mock_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
