import telebot
from telebot import types
import time
import logging
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = "8776279860:AAF7zV96Tp_vqNgE28K3gadqFANM202Q8c8"
REQUIRED_CHANNEL = "@ProxyTrofi"  # Канал для подписки
REQUIRED_CHANNEL_ID = "-1002263162261"  # ID канала (если нужно)

# Список прокси (все ссылки из твоего сообщения)
PROXIES = [
    {"url": "https://t.me/proxy?server=proxy-sosavpn.ru&port=8443&secret=e675e7ab7553ed8aa0ba2a91c575cfcc", "name": "Proxy Sosavpn 1"},
    {"url": "https://t.me/proxy?server=MTPROTO.online&port=443&secret=ee139e0ee36150c1ea3bf299796586b5457777772e7674622e7275", "name": "MTProto Online"},
    {"url": "https://t.me/proxy?server=raven8471-14d968ab.proxytg.ink&port=443&secret=eead14f006e06912127407f9fe07a146cb6465627269732e6c6f63616c", "name": "Raven Proxy"},
    {"url": "https://t.me/proxy?server=2.27.20.156&port=443&secret=ee636c6f7564666c6172652e636f6db6", "name": "Cloudflare Proxy"},
    {"url": "https://t.me/proxy?server=proxy-sosavpn.ru&port=8443&secret=e675e7ab7553ed8aa0ba2a91c575cfcc", "name": "Sosavpn Mirror"},
    {"url": "https://t.me/proxy?server=mt.ascel.la&port=8443&secret=c363767bbdb02912983f17ab2417a20c", "name": "Ascel MTProto"},
    {"url": "https://t.me/proxy?server=tg.scroogevpn.com&port=443&secret=59d307276beb8f4d8a0ed547eb6a461a", "name": "Scrooge VPN"},
    {"url": "https://t.me/proxy?server=t1.staxel.top&port=443&secret=eed821f85a3caff97bd748701cbbc4886a74312e73746178656c2e746f70", "name": "Staxel Top"},
    {"url": "https://t.me/proxy?server=65.20.114.94&port=443&secret=eee3f8727b5b6d7771c319feb04197459d646c2e676f6f676c652e636f6d", "name": "Google Proxy"},
    {"url": "https://t.me/proxy?server=81.90.17.175&port=8443&secret=ee79612e7275494a98c6918e3e987ced", "name": "EU Proxy"},
    {"url": "https://t.me/proxy?server=vaticanic.top&port=8443&secret=870579bd7c908dc115d6dc252cb6a55a", "name": "Vaticanic"},
    {"url": "https://t.me/proxy?server=tumantg.krotmonstr.online&port=443&secret=ddec0367788320df58c479f429956545", "name": "Tuman TG"},
    {"url": "https://t.me/proxy?server=free.tgsecurity.online&port=443&secret=ee7c5d4e1f2a3b9c8d7e6f5a4b3c2d1e0f766b2e636f6d", "name": "TG Security"},
    {"url": "https://t.me/proxy?server=MTPROTO.online&port=443&secret=ee139e0ee36150c1ea3bf299796586b5457777772e7674622e7275", "name": "MTProto Online 2"},
    {"url": "https://t.me/proxy?server=217.76.51.63&port=8443&secret=ee3c699c57134bf3963fa562d5554d87e76b72797468616e6f2e636f6d", "name": "UK Proxy"},
    {"url": "https://t.me/proxy?server=proxydazhenaparkovke.site&port=443&secret=dde8aa2e8c1ad50570b7d6fe7e0ba3d677", "name": "Proxy Dazhena"},
    {"url": "https://t.me/proxy?server=openimp.space&port=443&secret=075d7b345dc0222924ccea508c8edf91", "name": "Open Imp"},
    {"url": "https://t.me/proxy?server=free.FCKRKNBOT.COM&port=443&secret=eef48f621b110f302e468756840c29f916766b2e636f6d", "name": "FCKRKN BOT"}
]

# Создаем бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def check_subscription(user_id):
    """Проверка подписки на канал"""
    try:
        chat_member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return False

def get_proxies_keyboard(page=0):
    """Создает клавиатуру с прокси (пагинация 5 на страницу)"""
    items_per_page = 5
    total_pages = (len(PROXIES) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(PROXIES))
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Добавляем прокси на текущей странице
    for i in range(start_idx, end_idx):
        proxy = PROXIES[i]
        button = types.InlineKeyboardButton(
            f"📡 {proxy['name']}",
            callback_data=f"proxy_{i}"
        )
        markup.add(button)
    
    # Кнопки пагинации
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        pagination_buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page+1}"))
    
    if pagination_buttons:
        markup.add(*pagination_buttons)
    
    # Информация о странице
    page_info = types.InlineKeyboardButton(
        f"📄 {page+1}/{total_pages}",
        callback_data="noop"
    )
    markup.add(page_info)
    
    # Кнопка обновления
    markup.add(types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh"))
    
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    # Проверяем подписку
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "📢 Подписаться на канал", 
            url="https://t.me/ProxyTrofi"
        ))
        markup.add(types.InlineKeyboardButton(
            "✅ Проверить подписку", 
            callback_data="check_sub"
        ))
        
        bot.send_message(
            message.chat.id,
            "🔒 *Доступ ограничен!*\n\n"
            "Для использования бота необходимо подписаться на наш канал:\n"
            f"👉 {REQUIRED_CHANNEL}\n\n"
            "После подписки нажми кнопку *«Проверить подписку»*",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return
    
    # Приветствие для подписанных пользователей
    welcome_text = (
        "🌐 *Добро пожаловать в Proxy Bot!*\n\n"
        f"✅ Подписка на {REQUIRED_CHANNEL} подтверждена!\n\n"
        "📡 *Доступные прокси:*\n"
        f"Всего: {len(PROXIES)} рабочих прокси\n\n"
        "👇 *Нажми на любой прокси для подключения:*"
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_proxies_keyboard(0)
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    # Проверяем подписку при каждом действии
    if call.data != "check_sub" and not check_subscription(user_id):
        bot.answer_callback_query(
            call.id,
            "❌ Вы не подписаны на канал! Подпишитесь и нажмите 'Проверить подписку'",
            show_alert=True
        )
        return
    
    # Обработка проверки подписки
    if call.data == "check_sub":
        if check_subscription(user_id):
            welcome_text = (
                "🌐 *Добро пожаловать в Proxy Bot!*\n\n"
                f"✅ Подписка на {REQUIRED_CHANNEL} подтверждена!\n\n"
                "📡 *Доступные прокси:*\n"
                f"Всего: {len(PROXIES)} рабочих прокси\n\n"
                "👇 *Нажми на любой прокси для подключения:*"
            )
            
            bot.edit_message_text(
                welcome_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=get_proxies_keyboard(0)
            )
            bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
        else:
            bot.answer_callback_query(
                call.id,
                "❌ Вы все еще не подписаны! Нажмите на кнопку подписки.",
                show_alert=True
            )
        return
    
    # Обработка пагинации
    if call.data.startswith("page_"):
        page = int(call.data.split("_")[1])
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_proxies_keyboard(page)
        )
        bot.answer_callback_query(call.id)
        return
    
    # Обработка обновления
    if call.data == "refresh":
        current_page = 0
        # Пытаемся определить текущую страницу из текста кнопки
        for row in call.message.reply_markup.keyboard:
            for button in row:
                if button.callback_data and button.callback_data.startswith("page_"):
                    current_page = int(button.callback_data.split("_")[1])
                    break
        
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_proxies_keyboard(current_page)
        )
        bot.answer_callback_query(call.id, "🔄 Список обновлен!")
        return
    
    # Обработка выбора прокси
    if call.data.startswith("proxy_"):
        proxy_index = int(call.data.split("_")[1])
        proxy = PROXIES[proxy_index]
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "🔗 Открыть прокси", 
            url=proxy['url']
        ))
        markup.add(types.InlineKeyboardButton(
            "📋 Копировать ссылку",
            callback_data=f"copy_{proxy_index}"
        ))
        markup.add(types.InlineKeyboardButton(
            "🔙 Назад к списку",
            callback_data="back_to_list"
        ))
        
        bot.edit_message_text(
            f"📡 *{proxy['name']}*\n\n"
            f"🔗 *Ссылка для подключения:*\n"
            f"`{proxy['url']}`\n\n"
            f"📌 *Инструкция:*\n"
            f"1. Нажми «Открыть прокси»\n"
            f"2. Telegram автоматически настроит подключение\n"
            f"3. Готово! Теперь вы используете прокси\n\n"
            f"⚡ *Совет:* Сохраните ссылку, чтобы быстро подключаться",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"✅ Выбран {proxy['name']}")
        return
    
    # Обработка копирования ссылки
    if call.data.startswith("copy_"):
        proxy_index = int(call.data.split("_")[1])
        proxy = PROXIES[proxy_index]
        
        bot.answer_callback_query(
            call.id,
            f"Ссылка скопирована!",
            show_alert=False
        )
        
        bot.send_message(
            call.message.chat.id,
            f"📋 *Ссылка для {proxy['name']}:*\n"
            f"`{proxy['url']}`\n\n"
            f"Нажмите на ссылку для подключения",
            parse_mode="Markdown"
        )
        return
    
    # Обработка возврата к списку
    if call.data == "back_to_list":
        bot.edit_message_text(
            f"🌐 *Список прокси*\n\n"
            f"Всего: {len(PROXIES)} прокси\n\n"
            f"👇 *Выберите прокси для подключения:*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_proxies_keyboard(0)
        )
        bot.answer_callback_query(call.id)
        return
    
    if call.data == "noop":
        bot.answer_callback_query(call.id)
        return

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_message(
        message.chat.id,
        "🌐 Используй /start для получения списка прокси",
        parse_mode="Markdown"
    )

# Запуск бота
if __name__ == "__main__":
    print("🤖 Proxy Bot запускается...")
    print(f"✅ Бот: @ProxyTrofi_Bot")
    print(f"✅ Канал для подписки: {REQUIRED_CHANNEL}")
    print(f"✅ Всего прокси: {len(PROXIES)}")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 10 секунд...")
            time.sleep(10)