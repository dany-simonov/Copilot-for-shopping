import os
import os.path
import re
import csv
import sys
import time
import random
import requests
from bs4 import BeautifulSoup

TIMEOUT = 5
MAX_RETRIES = 3
SLEEP_TIME = 1
# URL = 'https://www.lamoda.ru/c/799/accs-muzhskie-chasy/'
DEFAULT_URL = 'https://www.lamoda.ru/c/5374/accs_ns-elektrchasymuj/'
HOST = 'https://www.lamoda.ru'
IMAGE_HOST = 'https://a.lmcdn.ru/img600x866'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; rv:82.0) Gecko/20100101 Firefox/82.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Version/16.0 Mobile/15E148 Safari/604.1'
]

HEADERS = {
    'user-agent': random.choice(USER_AGENTS),
    'accept': '*/*',
}
DEFAULT_FILENAME = 'lamoda.csv'
IMAGE_DIR = 'img'
PAGE_RE = re.compile(r'pagination:\{current:(\d+),total:(\d+),')
IMAGE_RE = re.compile(r'\["([^"]+)"')


def get_response(url: str, params: dict=None) -> requests.Response:
    for attempt in range(0, MAX_RETRIES):
        try:
            HEADERS['user-agent'] = random.choice(USER_AGENTS)
            time.sleep(random.uniform(2, 5)) 
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, params=params)
            if r.status_code == 200:
                return r
        except requests.exceptions.RequestException:
            continue
    return False


def get_html(url: str) -> str:
    r = get_response(url)

    if not r:
        print('Ошибка: не удалось выполнить http-запрос.\n')
        return False

    if r.status_code != requests.codes.ok:
        print(f'Ошибка {r.status_code} при обращении к web-странице.\n')
        return False

    return r.text


def save_image(url: str, filename: str) -> bool:
    r = get_response(url)

    if not r:
        print('Ошибка: не удалось выполнить http-запрос '
              'для получения изображения.\n'
              'Ссылка на изображение: ' + url)
        return False

    if r.status_code != requests.codes.ok:
        print(f'Ошибка {r.status_code} при обращении файлу изображения.\n'
              'Ссылка на изображение: ' + url)
        return False

    try:
        with open(filename, 'wb') as f:
            f.write(r.content)
    except OSError:
        print('Ошибка: не удалось сохранить изображение.')
        return False
    else:
        return True


def get_next_page(html: str, base_url: str) -> str:
    search_results = re.findall(PAGE_RE, ''.join(html.split()))
    if search_results:
        current = int(search_results[0][0])
        total = int(search_results[0][1])
        if current < total:
            print(f'Обрабатывается страница {current + 1} из {total}...')
            if '?' in base_url:
                return f'{base_url}&page={current + 1}'
            else:
                return f'{base_url}?page={current + 1}'
        else:
            return False
    else:
        return False


def get_item_urls(html: str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('a', class_='products-list-item__link link')
    return [HOST + item.get('href') for item in items]


def clean_text(text: str) -> str:
    return ' '.join(text.split())


def get_item(item_url: str) -> dict:
    html = get_html(item_url)

    if not html:
        print('Нет доступа к странице товара.\n'
              'Ссылка на страницу: ' + item_url)
        return False

    item = {'url': item_url}
    soup = BeautifulSoup(html, 'html.parser')

    model_name = soup.find('div', class_='product-title__model-name')
    if model_name:
        item['model_name'] = clean_text(model_name.get_text(strip=True))

    brand_name = soup.find('h1', class_='product-title__brand-name')
    if brand_name:
        item['brand_name'] = clean_text(brand_name.get_text(strip=True))

    price_current = soup.find('span', class_='product-prices__price_current')
    if price_current:
        item['price_current'] = price_current.get_text(strip=True)[:-1] + 'RUB'

    description = soup.find('pre', itemprop='description')
    if description:
        item['description'] = clean_text(description.get_text(strip=True))

    attributes = soup.find_all('span', class_='ii-product__attribute-label')
    for attribute in attributes:
        label_text = attribute.get_text(strip=True)
        value_text = clean_text(attribute.next_sibling.get_text(strip=True))

        if label_text == 'Состав:':
            item['compound'] = value_text
        elif label_text == 'Ширина:':
            item['width'] = clean_text(value_text)
        elif label_text == 'Диаметр циферблата:':
            item['diameter'] = clean_text(value_text)
        elif label_text == 'Сезон:':
            item['season'] = value_text
        elif label_text == 'Цвет:':
            item['color'] = value_text
        elif label_text == 'Механизм часов:':
            item['machinery'] = value_text
        elif label_text == 'Водозащита:':
            item['waterproof'] = value_text
        elif label_text == 'Цвет фурнитуры:':
            item['furniture_color'] = value_text
        elif label_text == 'Гарантийный период:':
            item['duration_of_cover'] = value_text
        elif label_text == 'Страна производства:':
            item['country'] = value_text
        elif label_text == 'Артикул':
            item['marking'] = value_text

    image = soup.find('d-gallery-widget')
    if image:
        search_results = re.findall(IMAGE_RE, image.get(':gallery') or '')
        if search_results:
            image_url = IMAGE_HOST + search_results[0]
            image_filename = os.path.join(
                os.getcwd(), IMAGE_DIR, search_results[0].split('/')[-1])
            if save_image(image_url, image_filename):
                item['image'] = 'file:///' + image_filename

    return item


def get_all_items(category_url: str) -> list:
    print('Обрабатывается начальная страница...')
    items = []
    base_url = category_url
    while category_url:
        html = get_html(category_url)
        if not html:
            print('Нет доступа к странице со списком товаров.\n'
                  'Ссылка на страницу: ' + category_url)
            return items

        for item_url in get_item_urls(html):
            item = get_item(item_url)
            if item:
                items.append(item)

        category_url = get_next_page(html, base_url)

    print(f'Итого товаров получено: {len(items)}')
    return items


def save_items(items: str, filename: str) -> bool:
    keys = ['model_name', 'marking', 'url', 'image', 'brand_name',
            'price_current', 'compound', 'width', 'diameter', 'season',
            'color', 'furniture_color', 'machinery', 'waterproof',
            'duration_of_cover', 'country', 'description']

    titles = ['Название модели', 'Артикул', 'Web-страница', 'Изображение',
              'Брэнд', 'Цена', 'Состав', 'Ширина', 'Диаметр циферблата',
              'Сезон', 'Цвет', 'Цвет фурнитуры', 'Механизм часов',
              'Водозащита', 'Гарантийный период', 'Страна производства',
              'Описание']
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(titles)
            for item in items:
                writer.writerow([item.get(key, '') for key in keys])
    except OSError:
        print('Ошибка: не удалось записать данные в файл.')
        return False
    else:
        print('Данные успешно записаны.')
        return True


if __name__ == '__main__':
    if not os.path.exists(IMAGE_DIR):
        try:
            os.mkdir(IMAGE_DIR)
        except OSError:
            print('Не удалось создать директорию с изображениями.\n'
                  'Работа программы завершена.')
            sys.exit()

    print('Введите адрес первой страницы категории товаров\n'
          '(Enter - ввод значения по умолчанию):')
    url = input().strip() or DEFAULT_URL

    print('Процесс сбора данных запущен.\n'
          'Адрес начальной страницы: ' + url)

    items = get_all_items(url)

    if items:
        print('Введите имя файла для сохранения данных\n'
              '(Enter - ввод имени по умолчанию):')
        filename = input().strip() or DEFAULT_FILENAME
        if save_items(items, filename):
            os.startfile(filename)
    else:
        print('Товары не найдены, работа программы завершена.')
