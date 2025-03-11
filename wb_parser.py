import requests
import pandas as pd
from retry import retry


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
        "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/yubki"
    ],
    "мужская_одежда": [
        "https://www.wildberries.ru/catalog/muzhchinam/odezhda/verhnyaya-odezhda",
        "https://www.wildberries.ru/catalog/muzhchinam/odezhda/pidzhaki-i-zhakety", 
        "https://www.wildberries.ru/catalog/muzhchinam/odezhda/tolstovki",
        "https://www.wildberries.ru/catalog/muzhchinam/odezhda/dzhempery-i-kardigany"
    ],
    "обувь": [
        "https://www.wildberries.ru/catalog/obuv/zhenskaya/sapogi"
    ]
}

def get_catalogs_wb() -> dict:
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
    headers = {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    return requests.get(url, headers=headers).json()

def get_data_category(catalogs_wb: dict) -> list:
    catalog_data = []
    if isinstance(catalogs_wb, dict) and 'childs' not in catalogs_wb:
        catalog_data.append({
            'name': f"{catalogs_wb['name']}",
            'shard': catalogs_wb.get('shard', None),
            'url': catalogs_wb['url'],
            'query': catalogs_wb.get('query', None)
        })
    elif isinstance(catalogs_wb, dict):
        catalog_data.append({
            'name': f"{catalogs_wb['name']}",
            'shard': catalogs_wb.get('shard', None),
            'url': catalogs_wb['url'],
            'query': catalogs_wb.get('query', None)
        })
        catalog_data.extend(get_data_category(catalogs_wb['childs']))
    else:
        for child in catalogs_wb:
            catalog_data.extend(get_data_category(child))
    return catalog_data

def search_category_in_catalog(url: str, catalog_list: list) -> dict:
    for catalog in catalog_list:
        if catalog['url'] == url.split('https://www.wildberries.ru')[-1]:
            print(f'найдено совпадение: {catalog["name"]}')
            return catalog

def get_data_from_json(json_file: dict) -> list:
    data_list = []
    for data in json_file['data']['products']:
        data_list.append({
            'id': data.get('id'),
            'name': data.get('name'),
            'price': int(data.get("priceU") / 100),
            'salePriceU': int(data.get('salePriceU') / 100),
            'cashback': data.get('feedbackPoints'),
            'sale': data.get('sale'),
            'brand': data.get('brand'),
            'rating': data.get('rating'),
            'supplier': data.get('supplier'),
            'supplierRating': data.get('supplierRating'),
            'feedbacks': data.get('feedbacks'),
            'reviewRating': data.get('reviewRating'),
            'promoTextCard': data.get('promoTextCard'),
            'promoTextCat': data.get('promoTextCat'),
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP'
        })
    return data_list

@retry(Exception, tries=-1, delay=0)
def scrap_page(page: int, shard: str, query: str, low_price: int, top_price: int, discount: int = None) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"}
    url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1257786&locale=ru&page={page}&priceU={low_price * 100};{top_price * 100}&sort=popular&spp=0&{query}&discount={discount}'
    r = requests.get(url, headers=headers)
    print(f'Статус: {r.status_code} Страница {page} Идет сбор...')
    return r.json()

def parser(url: str, low_price: int = 1, top_price: int = 1000000, discount: int = 0, page_limit: int = 1):
    catalog_data = get_data_category(get_catalogs_wb())
    try:
        category = search_category_in_catalog(url=url, catalog_list=catalog_data)
        data_list = []
        
        # Меняем range(1, 51) на range(1, page_limit + 1)
        for page in range(1, page_limit + 1):
            data = scrap_page(page=page, shard=category['shard'], query=category['query'],
                            low_price=low_price, top_price=top_price, discount=discount)
            items = get_data_from_json(data)
            print(f'Добавлено позиций: {len(items)}')
            if len(items) > 0:
                data_list.extend(items)
            else:
                break
                
        print(f'Сбор данных завершен. Собрано: {len(data_list)} товаров.')
        return data_list
        
    except TypeError:
        print('Ошибка! Возможно не верно указан раздел. Удалите все доп фильтры с ссылки')


if __name__ == '__main__':
    for category_name, urls in categories.items():
        print(f"\nПарсинг категории: {category_name}")
        for url in urls:
            try:
                results = parser(url=url, low_price=1000, top_price=50000, discount=0, page_limit=1)
                if results:
                    print(f"Найдено товаров: {len(results)}")
                    for item in results[:3]:
                        print(f"- {item['name']}: {item['salePriceU']} руб.")
            except Exception as e:
                print(f"Ошибка при парсинге {url}: {str(e)}")
