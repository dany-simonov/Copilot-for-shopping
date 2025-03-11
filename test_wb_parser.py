import unittest
from lamoda_parser.parser import get_catalogs_wb, get_data_category, scrap_page

class TestWildberriesParser(unittest.TestCase):
    def setUp(self):
        self.test_url = 'https://www.wildberries.ru/catalog/elektronika/planshety'
        self.test_shard = 'electronic'
        self.test_query = 'subject=515'
        
    def test_get_catalogs(self):
        """Тест получения каталога"""
        catalogs = get_catalogs_wb()
        self.assertIsNotNone(catalogs)
        self.assertIsInstance(catalogs, dict)
        
    def test_get_data_category(self):
        """Тест получения данных категории"""
        catalogs = get_catalogs_wb()
        categories = get_data_category(catalogs)
        self.assertIsInstance(categories, list)
        self.assertTrue(len(categories) > 0)
        
    def test_scrap_page(self):
        """Тест скрапинга страницы"""
        data = scrap_page(
            page=1,
            shard=self.test_shard,
            query=self.test_query,
            low_price=1000,
            top_price=100000
        )
        self.assertIsInstance(data, dict)
        self.assertIn('data', data)
        self.assertIn('products', data['data'])
