import telebot
import asyncio
import g4f
from dotenv import load_dotenv
import os
from database import Database
import signal
import sys

# Инициализация
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
db = Database()

# Провайдеры
PRIMARY_PROVIDERS = [
    g4f.Provider.HuggingSpace,
    g4f.Provider.TeachAnything
]

BACKUP_PROVIDERS = [
    g4f.Provider.GizAI,
    g4f.Provider.Free2GPT,
    g4f.Provider.ChatGLM
]

# Состояния и данные пользователей
user_states = {}
user_answers = {}

# Вопросы для диалога
questions = {
    'greeting': "Привет! Я твой персональный Шоппинг-Ассистент! 🛍️ Для какого случая тебе нужен наряд?",
    'style': "Какой стиль ты предпочитаешь? (классический, романтический, casual, бохо, минимализм)",
    'budget': "Какой у тебя бюджет на этот наряд? (до 5000 руб, до 10000 руб, без ограничений)",
    'color': "Какие цвета ты предпочитаешь? (черный, красный, пастельные тона, яркие цвета)",
    'size': "Какой у тебя размер одежды? (XS, S, M, L, XL)",
    'shoe_size': "Какой у тебя размер обуви? (36, 37, 38, 39, 40)",
    'wishes': "Есть ли у тебя какие-то особые пожелания? (например: хочу платье с открытой спиной, нужна удобная обувь для танцев)",
    'marketplace': "Ты предпочитаешь какие-то определенные маркетплейсы? (Lamoda, ASOS, Wildberries, Ozon)"
}

# Обработка завершения работы
def signal_handler(sig, frame):
    print('Завершение работы бота...')
    bot.stop_polling()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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
    
    return "Попробуйте повторить запрос позже."

# Обработчики сообщений
@bot.message_handler(commands=['start'])
def start_dialog(message):
    user_id = message.from_user.id
    user_states[user_id] = 'greeting'
    user_answers[user_id] = {}
    bot.send_message(message.chat.id, questions['greeting'])

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        start_dialog(message)
        return

    current_state = user_states[user_id]
    user_answers[user_id][current_state] = message.text
    
    # Сохранение в БД
    db.save_dialog(
        user_id,
        message.chat.id,
        questions[current_state],
        message.text
    )

    # Переход к следующему вопросу
    next_state = {
        'greeting': 'style',
        'style': 'budget',
        'budget': 'color',
        'color': 'size',
        'size': 'shoe_size',
        'shoe_size': 'wishes',
        'wishes': 'marketplace',
        'marketplace': 'final'
    }

    if current_state in next_state:
        next_question = next_state[current_state]
        if next_question == 'final':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_recommendations(message, user_answers[user_id]))
            loop.close()
        else:
            user_states[user_id] = next_question
            bot.send_message(message.chat.id, questions[next_question])

# Генерация рекомендаций
async def generate_recommendations(message, answers):
    prompt = f"""
    Пользователь ищет наряд со следующими параметрами:
    Случай: {answers['greeting']}
    Стиль: {answers['style']}
    Бюджет: {answers['budget']}
    Цвета: {answers['color']}
    Размер одежды: {answers['size']}
    Размер обуви: {answers['shoe_size']}
    Особые пожелания: {answers['wishes']}
    Маркетплейс: {answers['marketplace']}
    
    Сгенерируй список поисковых запросов для поиска подходящей одежды.
    """
    
    response = await get_best_response(prompt)
    bot.send_message(message.chat.id, f"Вот что я подобрал для тебя:\n\n{response}")

# Запуск бота
if __name__ == "__main__":
    try:
        print('Бот запущен...')
        bot.infinity_polling(timeout=60, long_polling_timeout=60, allowed_updates=['message'])
    except Exception as e:
        print(f'Ошибка: {e}')
        bot.stop_polling()
