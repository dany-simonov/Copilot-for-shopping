from wb_parser import parser

categories = {
    "женская_одежда": [
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/platya",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bluzki-i-rubashki",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/dzhinsy-dzhegginsy",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/futbolki-i-topy",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bryuki-i-shorty",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/dzhempery-i-kardigany",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/pidzhaki-i-zhakety",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/tolstovki",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/yubki",
    "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/verhnyaya-odezhda",
    "https://www.wildberries.ru/catalog/zhenshchinam/obuv/tufli",
    "https://www.wildberries.ru/catalog/zhenshchinam/obuv/sapogi",
    "https://www.wildberries.ru/catalog/zhenshchinam/obuv/bosonozhki-i-sandali",
    "https://www.wildberries.ru/catalog/zhenshchinam/obuv/krossovki-i-kedy",
    "https://www.wildberries.ru/catalog/zhenshchinam/aksessuary/sumki",
    "https://www.wildberries.ru/catalog/zhenshchinam/aksessuary/remni",
    "https://www.wildberries.ru/catalog/zhenshchinam/aksessuary/sharfy-i-platki",
    "https://www.wildberries.ru/catalog/zhenshchinam/aksessuary/perchatki-i-rukavicy",
    "https://www.wildberries.ru/catalog/zhenshchinam/aksessuary/ochki",
],
    "мужская_одежда":  [
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/verhnyaya-odezhda",
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/pidzhaki-i-zhakety",
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/tolstovki",
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/dzhempery-i-kardigany",
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/rubashki",
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/futbolki-pol"
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/bryuki",
    "https://www.wildberries.ru/catalog/muzhchinam/odezhda/dzhinsy",
    "https://www.wildberries.ru/catalog/muzhchinam/obuv/krossovki-i-kedy",
    "https://www.wildberries.ru/catalog/muzhchinam/obuv/tufli",
    "https://www.wildberries.ru/catalog/muzhchinam/obuv/sapogi-i-botinki",
    "https://www.wildberries.ru/catalog/muzhchinam/aksessuary/sumki",
    "https://www.wildberries.ru/catalog/muzhchinam/aksessuary/remni",
    "https://www.wildberries.ru/catalog/muzhchinam/aksessuary/shapki-i-snudy",
    "https://www.wildberries.ru/catalog/muzhchinam/aksessuary/perchatki-i-rukavicy",
    "https://www.wildberries.ru/catalog/muzhchinam/aksessuary/ochki",
]
}



def test_catalog_search():
    for category_name, urls in categories.items():
        print(f"\nТестируем категорию: {category_name}")
        for url in urls:
            print(f"\nПарсинг: {url}")
            try:
                results = parser(url=url, low_price=1000, top_price=50000, discount=0, page_limit=1)
                print(f"Найдено товаров: {len(results) if results else 0}")
                if results:
                    for item in results[:3]:
                        print(f"- {item['name']}: {item['salePriceU']} руб.")
            except Exception as e:
                print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    test_catalog_search()
