import telebot
from telebot import types
import asyncio
import g4f
from dotenv import load_dotenv
import os
import signal
import sys
from wb_parser import parser

CATEGORIES = {
    'Мужчина': {
        'Верхняя одежда': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/verhnyaya-odezhda',
        'Пиджаки и жилеты': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/pidzhaki-i-zhakety',
        'Толстовки': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/tolstovki',
        'Джемперы и кардиганы': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/dzhempery-i-kardigany',
        'Рубашки': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/rubashki',
        'Джинсы': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/dzhinsy',
        'Брюки': 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/bryuki'
    },
    'Женщина': {
        'Платья': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/platya',
        'Блузки и рубашки': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bluzki-i-rubashki',
        'Джинсы': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/dzhinsy-dzhegginsy',
        'Футболки и топы': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/futbolki-i-topy',
        'Брюки': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bryuki-i-shorty',
        'Джемперы и кардиганы': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/dzhempery-i-kardigany',
        'Пиджаки и жилеты': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/pidzhaki-i-zhakety',
        'Толстовки': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/tolstovki',
        'Юбки': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/yubki',
        'Верхняя одежда': 'https://www.wildberries.ru/catalog/zhenshchinam/odezhda/verhnyaya-odezhda'
    }
}


def get_category_url(gender, clothes_type):
    base_url = CATEGORIES[gender]['base_url']
    category_path = CATEGORIES[gender]['categories'].get(clothes_type, '')
    return base_url + category_path if category_path else base_url


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Провайдеры
PRIMARY_PROVIDERS = [
    g4f.Provider.TeachAnything,
    g4f.Provider.GizAI
]

BACKUP_PROVIDERS = [
    g4f.Provider.Free2GPT,
    g4f.Provider.ChatGLM
]

# Состояния пользователя
user_states = {}
user_answers = {}

# Кнопки для разных этапов
def get_gender_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Мужчина"), types.KeyboardButton("Женщина"))
    return keyboard

def get_occasion_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Конкретное мероприятие"),
        types.KeyboardButton("Просто купить одежду")
    )
    return keyboard

def get_clothes_type_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        "Верхняя одежда",
        "Легкая одежда",
        "Нательная одежда",
        "Обувь",
        "Аксессуары",
        "Весь образ"
    ]
    for button in buttons:
        keyboard.add(types.KeyboardButton(button))
    return keyboard

def get_size_keyboard(gender):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    sizes = ["XS", "S", "M", "L", "XL", "Другой размер"] if gender == "Женщина" else \
            ["M", "L", "XL", "XXL", "3XL", "Другой размер"]
    keyboard.add(*[types.KeyboardButton(size) for size in sizes])
    return keyboard

def get_shoe_size_keyboard(gender):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    sizes = ["36", "37", "38", "39", "40", "Другой размер"] if gender == "Женщина" else \
            ["39", "40", "41", "42", "43", "Другой размер"]
    keyboard.add(*[types.KeyboardButton(size) for size in sizes])
    return keyboard

# Обработчики сообщений
@bot.message_handler(commands=['start'])
def start_dialog(message):
    user_id = message.from_user.id
    user_states[user_id] = 'gender'
    user_answers[user_id] = {}
    bot.send_message(
        message.chat.id,
        "Привет! 👋 Я твой персональный шоппинг-ассистент! 🛍️ Чтобы начать, выбери свой пол:",
        reply_markup=get_gender_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        start_dialog(message)
        return

    current_state = user_states[user_id]
    text = message.text
    
    if current_state == 'gender':
        if text in ["Мужчина", "Женщина"]:
            user_answers[user_id]['gender'] = text
            user_states[user_id] = 'occasion'
            bot.send_message(
                message.chat.id,
                "Для какого случая тебе нужен наряд? Выбери один из вариантов:",
                reply_markup=get_occasion_keyboard()
            )
    
    elif current_state == 'occasion':
        user_answers[user_id]['occasion'] = text
        if text == "Конкретное мероприятие":
            user_states[user_id] = 'event'
            bot.send_message(message.chat.id, "Какое мероприятие?")
        else:
            user_states[user_id] = 'clothes_description'
            bot.send_message(
                message.chat.id,
                "Что ты хочешь приобрести? Опиши свои пожелания (например: свитер и штаны)"
            )
    
    elif current_state in ['event', 'clothes_description']:
        user_answers[user_id]['event_description'] = text
        user_states[user_id] = 'clothes_type'
        bot.send_message(
            message.chat.id,
            "Какую одежду ты ищешь? Выбери один или несколько вариантов:",
            reply_markup=get_clothes_type_keyboard()
        )

    elif current_state == 'clothes_type':
        user_answers[user_id]['clothes_type'] = text
        user_states[user_id] = 'size'
        bot.send_message(
            message.chat.id,
            "Какой у тебя размер одежды? Выбери из списка:",
            reply_markup=get_size_keyboard(user_answers[user_id]['gender'])
        )

    elif current_state == 'size':
        user_answers[user_id]['size'] = text
        user_states[user_id] = 'shoe_size'
        bot.send_message(
            message.chat.id,
            "Какой у тебя размер обуви? Выбери из списка (или введи свой размер):",
            reply_markup=get_shoe_size_keyboard(user_answers[user_id]['gender'])
        )

    elif current_state == 'shoe_size':
        user_answers[user_id]['shoe_size'] = text
        user_states[user_id] = 'color'
        bot.send_message(
            message.chat.id,
            "Какие цвета ты предпочитаешь?",
            reply_markup=types.ReplyKeyboardRemove()
        )

    elif current_state == 'color':
        user_answers[user_id]['color'] = text
        user_states[user_id] = 'wishes'
        bot.send_message(
            message.chat.id,
            "Есть ли у тебя какие-то особые пожелания? (например: хочу платье с открытой спиной, нужна удобная обувь для танцев)"
        )

    elif current_state == 'wishes':
        user_answers[user_id]['wishes'] = text
        user_states[user_id] = 'final'
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_recommendations(message, user_answers[user_id]))
        loop.close()

async def generate_recommendations(message, answers):
    print("\n=== Начало генерации рекомендаций ===")
    print(f"Данные пользователя: {answers}")
    
    prompt = f"""
    Ты - профессиональный стилист. Создай рекомендации для клиента:
    Пол: {answers['gender']}
    {'Мероприятие: ' + answers['event_description'] if 'event_description' in answers else 'Пожелания: ' + answers['clothes_description']}
    Тип одежды: {answers['clothes_type']}
    Размер одежды: {answers['size']}
    Цвета: {answers['color']}
    Особые пожелания: {answers['wishes']}
    
    Напиши список из 2-3 конкретных предметов одежды для поиска в интернет-магазине. Важно:
    - Используй простые и четкие названия товаров
    - Пиши каждый товар с новой строки, начиная с цифры
    - Не используй сложные описания
    """

    # Получаем прямую ссылку из нашей структуры категорий
    search_url = CATEGORIES[answers['gender']]['Верхняя одежда']
    
    items_to_search = await get_best_response(prompt)
    print(f"\nОтвет нейросети:\n{items_to_search}")
    
    try:
        products = parser(url=search_url, low_price=1000, top_price=50000, discount=0)
        if products:
            for product in products[:3]:
                recommendation = await format_recommendation(product)
                bot.send_message(message.chat.id, recommendation)
                
    except Exception as e:
        print(f"Ошибка поиска: {e}")


# async def generate_recommendations(message, answers):
#     print("\n=== Начало генерации рекомендаций ===")
#     print(f"Данные пользователя: {answers}")
    
#     catalogs_wb = get_catalogs_wb()
    
#     prompt = f"""
#     Ты - профессиональный стилист. Создай рекомендации для клиента:
#     Пол: {answers['gender']}
#     {'Мероприятие: ' + answers['event_description'] if 'event_description' in answers else 'Пожелания: ' + answers['clothes_description']}
#     Тип одежды: {answers['clothes_type']}
#     Размер одежды: {answers['size']}
#     Цвета: {answers['color']}
#     Особые пожелания: {answers['wishes']}
    
#        Напиши список из 2-3 конкретных предметов одежды для поиска в интернет-магазине. Важно:  

#    - Используй простые и четкие названия товаров  
#    - Не используй скобки и сложные описания  
#    - Пиши каждый товар с новой строки, начиная с цифры  
#    - Не добавляй лишних комментариев и пояснений  
   
#     Пример правильного ответа:  
#     1. Черный костюм  
#     2. Белая рубашка  
#     3. Черные туфли  
#     и так далее  
#     """
    
#     items_to_search = await get_best_response(prompt)
#     print(f"\nОтвет нейросети:\n{items_to_search}")
    
#     search_results = []
#     catalog_data = get_data_category(catalogs_wb)
    
#     for item in items_to_search.split('\n'):
#         if not item.strip() or not item[0].isdigit():
#             continue
        
#         item = item.split('.')[1].strip()
#         print(f"\nПоиск товара: {item}")
        
#         for category in catalog_data:
#             try:
#                 # Получаем первые 300 товаров
#                 products = parser(
#                     url=category['url'], 
#                     low_price=1000, 
#                     top_price=50000, 
#                     discount=0,
#                     limit=300  # Ограничиваем выборку
#                 )
                
#                 if products:
#                     filtered_products = [p for p in products if item.lower() in p['name'].lower()]
#                     if filtered_products:
#                         search_results.append({
#                             'item': item,
#                             'products': filtered_products[:3]
#                         })
#                         break  # Прерываем поиск если нашли подходящие товары
#             except Exception as e:
#                 continue


async def generate_ai_description(name, brand, rating, price):
    prompt = f"""
    Опиши привлекательно следующий товар:
    Название: {name}
    Бренд: {brand}
    Рейтинг: {rating}
    Цена: {price} руб.

    Напиши 2-3 предложения, почему этот товар отлично подойдет покупателю.
    Упомяни качество, стиль и уникальные особенности.
    Используй дружелюбный тон и добавь эмоциональности.
    """
    
    description = await get_best_response(prompt)
    return description

async def format_recommendation(item):
    recommendation = f"🎀 Ваши персональные рекомендации:\n\n"
    
    product_description = await generate_ai_description(
        name=item['name'],
        brand=item['brand'],
        rating=item['rating'],
        price=item['salePriceU']
    )
    
    recommendation += f"{product_description}\n\n"
    recommendation += f"✨ {item['name']}\n"
    recommendation += f"💰 Цена: {item['salePriceU']} руб.\n"
    if item['sale']:
        recommendation += f"🔥 Скидка: {item['sale']}%\n"
    recommendation += f"👍 Рейтинг: {item['rating']}\n"
    recommendation += f"🛍️ Бренд: {item['brand']}\n\n"
    recommendation += f"Купить здесь: {item['link']}"
    
    return recommendation


# Функции для работы с провайдерами
async def get_response_from_provider(provider, message, timeout=15):
    try:
        response = await asyncio.wait_for(
            g4f.ChatCompletion.create_async(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                provider=provider
            ),
            timeout=timeout
        )
        return {"success": True, "response": response, "provider": provider.__name__}
    except Exception as e:
        print(f"Error with {provider.__name__}: {str(e)}")
        return {"success": False, "provider": provider.__name__}

async def get_best_response(message: str) -> str:
    # Пробуем основных провайдеров
    tasks = [get_response_from_provider(p, message) for p in PRIMARY_PROVIDERS]
    responses = await asyncio.gather(*tasks)
    successful_responses = [r for r in responses if r["success"]]

    # Если основные не сработали, пробуем резервных
    if not successful_responses:
        tasks = [get_response_from_provider(p, message) for p in BACKUP_PROVIDERS]
        responses = await asyncio.gather(*tasks)
        successful_responses = [r for r in responses if r["success"]]

    if successful_responses:
        best_response = max(successful_responses, key=lambda x: len(x["response"]))
        print(f"Using response from {best_response['provider']}")
        return best_response["response"]
    
    return "К сожалению, не удалось сгенерировать рекомендации. Попробуйте повторить запрос позже."

# Обработка завершения работы
def signal_handler(sig, frame):
    print('Завершение работы бота...')
    bot.stop_polling()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@bot.message_handler(commands=['restart'])
def restart(message):
    user_id = message.from_user.id
    if user_id in user_answers:
        del user_answers[user_id]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton('Начать подбор')
    markup.add(start_button)
    bot.send_message(message.chat.id, "Бот перезапущен! Нажмите 'Начать подбор' для старта.", reply_markup=markup)

if __name__ == "__main__":
    try:
        print('Бот запущен...')
        bot.infinity_polling(timeout=60, long_polling_timeout=60, allowed_updates=['message'])
    except Exception as e:
        print(f'Ошибка: {e}')
        bot.stop_polling()