import sqlite3
import telebot
import string
import webbrowser
from telebot import types
import random
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


today = datetime.now().strftime("%Y-%m-%d")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Welcome to ShymAdventure RPG! Lets move to registration! (type /register)')
    conn = sqlite3.connect('rpg.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, username TEXT, hp INT, money INT, level INT)')
    cur.execute('CREATE TABLE IF NOT EXISTS items (user_id INTEGER PRIMARY KEY, item_name TEXT)')
    conn.commit()
    conn.close()
@bot.message_handler(commands=['register'])
def register0(message):
    bot.send_message(message.chat.id, 'Hello! Type you new username.')
    bot.register_next_step_handler(message, register1)
def register1(message):
    user_id = message.from_user.id
    nick = message.text.strip()
    if is_nickname_available(nick):
        try:
            con = sqlite3.connect('rpg.db')
            cur = con.cursor()
            cur.execute(
                "INSERT INTO players (user_id, username, hp, money, level) VALUES (?, ?, ?, ?, ?)",
                (user_id, nick, 100, 1000, 0)
            )
            con.commit()

            # Непосредственная проверка, чтобы убедиться, что строка в базе
            row = cur.execute("SELECT user_id, username, hp, money FROM players WHERE user_id = ?", (user_id,)).fetchone()
            con.close()

            if row is None:
                bot.send_message(message.chat.id, f"DEBUG: insert executed but row IS NONE (user_id={user_id})")
                return

            bot.send_message(message.chat.id, f"Registered successfully!")
            profile(message)
        except sqlite3.IntegrityError as e:
            bot.send_message(message.chat.id, f"Registration error (Integrity): {e}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Registration unexpected error: {e}")
    else:
        bot.send_message(message.chat.id, 'Sorry, that username is already registered. Please try again.')
@bot.message_handler(commands=['profile'])
def profile(message):
    show_profile(message.chat.id, message.from_user.id)
def show_profile(chat_id, user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Fight", callback_data="fight"))
    markup.add(types.InlineKeyboardButton("Random game 🎲", callback_data="random", row_width=1))
    markup.row(
    types.InlineKeyboardButton("Shop", callback_data="shop"),
        types.InlineKeyboardButton("Inventory", callback_data="inventory")
    )

    con = sqlite3.connect('rpg.db')
    cur = con.cursor()
    player = cur.execute(
        'SELECT username, hp, money, level FROM players WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    con.close()

    if player is None:
        bot.send_message(chat_id, "Вы не зарегистрированы. Введите /register")
        return
    nick1, hp1, money1, level1 = player
    bot.send_message(chat_id,
        f'Hello, {nick1} 🛡️.  Welcome to ShymAdventure RPG! \nYour stats:\nHP:  {hp1} ❤️\nMoney:  {money1} 💰\nLevel:  {level1} ⚔️',
        reply_markup=markup)
    # следующий шаг Update
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if call.data == 'fight':
        fight1(call)
        return
    elif call.data == 'random':
        random1(call)
    elif call.data == 'shop':
        shop1(call)
    elif call.data == 'inventory':
        inventory1(call)
    elif call.data == 'battle' or call.data == 'run':
        option(call)
    elif call.data == 'case':
        case1(call)
    elif call.data == 'iron_sword' or call.data == 'shield' or call.data == 'ring_power' or call.data == 'hp_potion':
        shop2(call)
    elif call.data == 'back':
        show_profile(chat_id, user_id)
def fight1(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    a = 1 #random.randint(1, 3)
    if a == 1:
        global goblin_hp
        goblin_hp = random.randint(60, 120)
        goblin_damage = random.randint(20, 60)
        markup = types.InlineKeyboardMarkup()
        markup.row (
            types.InlineKeyboardButton("Battle ", callback_data="battle"),
            types.InlineKeyboardButton("Run (-50 HP)", callback_data="run")
        )
        bot.send_message(chat_id, f'Goblin attacked you! He has {goblin_hp} HP. What will you do?', reply_markup=markup)
def option(call):
    print("CALLBACK TRIGGERED:", call.data)
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if call.data == "battle":
        con = sqlite3.connect('rpg.db')
        cur = con.cursor()
        sword = cur.execute('SELECT item_name from items WHERE item_name = ?', ('sword',)).fetchall()
        ring = cur.execute('SELECT item_name from items WHERE item_name = ?', ('ring',)).fetchall()
        damage = random.randint(80, 100)
        if sword:
            damage = random.randint(100, 150)
        if ring:
            damage = damage + (damage * 0.2)
        goblin_new_hp = goblin_hp - damage
        con.commit()
        con.close()
        while goblin_new_hp > 0:
            con = sqlite3.connect('rpg.db')
            cur = con.cursor()
            bot.send_message(chat_id, f'You hit him with {damage} damage! Goblin has {goblin_new_hp} HP left.')
            shield = cur.execute('SELECT item_name from items WHERE item_name = ?', ('shield',)).fetchall()
            defence = cur.execute('SELECT item_name from items WHERE item_name = ?', ('defence',)).fetchall()
            goblin_damage = random.randint(70, 90)
            if shield:
                goblin_damage = random.randint(40, 80)
            if defence:
                goblin_damage = goblin_damage - (goblin_damage * 0.2)
            current_hp = cur.execute('SELECT hp from players WHERE user_id = ?', (user_id,)).fetchone()
            current_hp = current_hp[0] - goblin_damage
            cur.execute('UPDATE players SET hp = ? WHERE user_id = ?', (current_hp, user_id))
            if current_hp <= 0:
                bot.send_message(chat_id, 'You are dead! Type /register to start again')
                con.close()
                clear1(call)
                return
            goblin_new_hp = goblin_new_hp - damage
            bot.send_message(chat_id, f'Goblin hit you with {goblin_damage} damage! You have {current_hp} HP left.')
            con.commit()
            con.close()
        conn = sqlite3.connect('rpg.db')
        cur = conn.cursor()
        recmoney = random.randint(200, 1000)
        bot.send_message(chat_id, f'You killed Goblin and received {recmoney} money')
        current_money = cur.execute('SELECT money from players WHERE user_id = ?', (user_id,)).fetchone()
        current_money = current_money[0] + recmoney
        cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (current_money, user_id))
        conn.commit()
        conn.close()
        show_profile(chat_id, user_id)


    if call.data == "run":
        con = sqlite3.connect('rpg.db')
        cur = con.cursor()
        hp_value = cur.execute("SELECT hp FROM players WHERE user_id = ?", (user_id,)).fetchone()
        hp_new = hp_value[0] - 50
        if hp_new <= 0:
            bot.send_message(chat_id, 'You are dead! Type /register to start again')
            con.commit()
            con.close()
            clear1(call)
        else:
            cur.execute('UPDATE players SET hp = ? WHERE user_id = ?', (hp_new, user_id))
            con.commit()
            bot.send_message(chat_id, f'You escaped the battle! You have {hp_new} HP.')
            con.close()
def random1(call):
    # берем user_id из call (правильно для inline-кнопок)
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    con = sqlite3.connect('rpg.db')
    cur = con.cursor()

    # безопасность: достаём hp и money за один SELECT
    player = cur.execute('SELECT hp, money FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if player is None:
        # отладочная инфа — покажем несколько записей из базы, чтобы понять, что там
        sample = cur.execute("SELECT user_id, username FROM players LIMIT 10").fetchall()
        bot.send_message(chat_id, f"DEBUG: player not found for user_id={user_id}.\nSample rows: {sample}")
        con.close()
        return

    hp_value, money_value = player
    a = random.randint(1, 2)

    if a == 1:
        b = random.randint(-50, 100)
        new_hp = hp_value + b
        if new_hp <= 0:
            cur.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
            con.commit()
            bot.send_message(chat_id, f'You received {abs(b)} dmg and died. Profile removed.')
            con.close()
            return
        cur.execute('UPDATE players SET hp = ? WHERE user_id = ?', (new_hp, user_id))
        con.commit()
        if b < 0:
            bot.send_message(chat_id, f'You have lost {abs(b)} HP.')
        elif b > 0:
            bot.send_message(chat_id, f'You have received {b} HP.')
        else:
            bot.send_message(chat_id, 'You did not receive anything.')
        bot.send_message(chat_id, f'You have {new_hp} HP left.')
        show_profile(chat_id, user_id)
    elif a == 2:
        b = random.randint(-100, 500)
        new_money = money_value + b
        cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (new_money, user_id))
        con.commit()
        if b < 0:
            bot.send_message(chat_id, f'You have lost {abs(b)} money.')
            show_profile(chat_id, user_id)
        elif b > 0:
            bot.send_message(chat_id, f'You have received {b} money.')
            show_profile(chat_id, user_id)
        else:
            bot.send_message(chat_id, 'You did not receive anything.')
            show_profile(chat_id, user_id)
    else:
        # в разработке
        return
    con.close()

def shop1(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Mysterious Case - 900 💰', callback_data='case'))
    markup.add(types.InlineKeyboardButton('Iron Sword (+50 damage) - 1000 💰', callback_data='iron_sword'))
    markup.add(types.InlineKeyboardButton('Health Potion - 750 💰', callback_data='hp_potion'))
    markup.add(types.InlineKeyboardButton('Titan Shield - 800 💰', callback_data='shield'))
    markup.add(types.InlineKeyboardButton('Ring of power - 600💰', callback_data='ring_power'))
    markup.add(types.InlineKeyboardButton('<-- Back', callback_data='back'))
    bot.send_message(chat_id, f'Welcome to shop! Choose the item: ', reply_markup=markup)
def case1(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    con = sqlite3.connect('rpg.db')
    cur = con.cursor()
    money = cur.execute('SELECT money FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if money[0] < 900:
        bot.send_message(chat_id, f'You dont have enough money.')
        show_profile(chat_id, user_id)
    money = money[0] - 900
    cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (money, user_id))
    bot.send_message(chat_id, 'Purchased successfully!')
    items = ['Iron Sword', 'Health Potion', 'Titan Shield', 'Ring of power']
    a = random.choice(items)
    bot.send_message(chat_id, 'You received ' + a + ' !')
    cur.execute('INSERT INTO items VALUES (?, ?)', (user_id, a))
    con.commit()
    con.close()
def shop2(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    con = sqlite3.connect('rpg.db')
    cur = con.cursor()
    money = cur.execute('SELECT money FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if call.data == 'iron_sword':
       if money[0] < 1000:
           bot.send_message(chat_id, f'You dont have enough money.')
           show_profile(chat_id, user_id)
           con.close()
       else:
           money = money[0] - 1000
           cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (money, user_id))
           cur.execute('INSERT INTO items VALUES (?, ?)', (user_id, 'Iron Sword'))
           bot.send_message(chat_id, 'Purchased successfully!')
           con.commit()
           con.close()
           show_profile(chat_id, user_id)
    if call.data == 'hp_potion':
        if money[0] < 750:
            bot.send_message(chat_id, f'You dont have enough money.')
            show_profile(chat_id, user_id)
            con.close()
        else:
            money = money[0] - 750
            cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (money, user_id))
            hp = cur.execute('SELECT hp FROM players WHERE user_id = ?', (user_id,)).fetchone()
            hp = hp[0] + 100
            bot.send_message(chat_id, 'Purchased successfully! You added +100 HP.')
            cur.execute('UPDATE players SET hp = ? WHERE user_id = ?', (hp, user_id))
            con.commit()
            con.close()
            show_profile(chat_id, user_id)
    if call.data == 'shield':
        if money[0] < 800:
            bot.send_message(chat_id, f'You dont have enough money.')
            show_profile(chat_id, user_id)
            con.close()
        else:
            money = money[0] - 800
            cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (money, user_id))
            cur.execute('INSERT INTO items VALUES (?, ?)', (user_id, 'Shield'))
            bot.send_message(chat_id, 'Purchased successfully!')
            con.commit()
            con.close()
            show_profile(chat_id, user_id)
    if call.data == 'ring_power':
        if money[0] < 600:
            bot.send_message(chat_id, f'You dont have enough money.')
            show_profile(chat_id, user_id)
            con.close()
        else:
            money = money[0] - 600
            cur.execute('UPDATE players SET money = ? WHERE user_id = ?', (money, user_id))
            cur.execute('INSERT INTO items VALUES (?, ?)', (user_id, 'Ring of power'))
            bot.send_message(chat_id, 'Purchased successfully!')
            con.commit()
            con.close()
            show_profile(chat_id, user_id)
def inventory1(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    con = sqlite3.connect('rpg.db')
    cur = con.cursor()
    items = cur.execute('SELECT item_name FROM items WHERE user_id = ?', (user_id,)).fetchall()
    if len(items) == 0:
        bot.send_message(chat_id, 'You dont have any items.')
        show_profile(chat_id, user_id)
        con.close()
    else:
        bot.send_message(chat_id, 'Your items: ')
        info = ' '
        for el in items:
            info += f'{el[0]} , '
        bot.send_message(chat_id, info)
        con.close()
        show_profile(chat_id, user_id)
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "List of commands: \n/password - Random password\n/passwset - Random password with settings\n/check - password checker")


@bot.message_handler(commands=['clear'])
def clear(message):
    user_id = message.from_user.id
    con = sqlite3.connect('rpg.db')
    cur = con.cursor()
    cur.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
    cur.execute('DELETE FROM items WHERE user_id = ?', (user_id,))
    con.commit()
    con.close()
    bot.send_message(message.chat.id, 'Your profile has been cleared.')
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id, "Unknown command. Type /help for available commands.")

def clear1(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    con = sqlite3.connect('rpg.db')
    cur = con.cursor()
    all = cur.execute("SELECT user_id, username FROM players LIMIT 10").fetchall()
    if all is None:
        con.close()
    else:
        cur.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
        cur.execute('DELETE FROM items WHERE user_id = ?', (user_id,))
        con.commit()
        con.close()
    bot.send_message(chat_id, 'Your profile has been cleared.')
def is_nickname_available(nickname):
    conn = sqlite3.connect('rpg.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM players WHERE username = ?", (nickname,))
    result = cur.fetchone()
    conn.close()
    return result is None

bot.polling(none_stop=True)


