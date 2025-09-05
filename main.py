# AkulinkyCardBOT - Gives out random shark cards
# Copyright (C) 2025  WinK / MEGStone™
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
import telebot
import sqlite3
import random
import time
import threading
from datetime import timedelta
from flask import Flask

TOKEN = ""
CHAT_ID = "-4842781952"  
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


conn = sqlite3.connect("shark_cards.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                last_used INTEGER,
                acuvki INTEGER DEFAULT 0
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, 
                image TEXT
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS user_cards (
                user_id INTEGER,
                card_id INTEGER,
                PRIMARY KEY (user_id, card_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (card_id) REFERENCES cards(id)
            )''')
conn.commit()

shark_cards = [
    ("Акула Кушает", "https://www.dropbox.com/scl/fi/i41jo3onfzxf2dnplzbs9/akuva.png?rlkey=k73tvvagstzpi9yixzgugi9qo&raw=1"),
    ("Деловая Акула", "https://www.dropbox.com/scl/fi/u8w20fbecg559hb611iy7/akuvi.jpg?rlkey=xvpr5dczyh2xrrzf80oc8nd0g&raw=1"),
    ("Музыкальная Акувка", "https://www.dropbox.com/scl/fi/oo8psr2absc5oo6vw4o0w/akuvo.jpg?rlkey=1gyaipvk72oeuxz4wllzyimn2&raw=1"),
    ("Акува с Гитарой", "https://www.dropbox.com/scl/fi/z0si5e8b6814ijeha67k5/gitara.jpg?rlkey=xfo0hndn3g6l441ou1y76y6hv&st=ws3wddsf&raw=1"),
    ("Бизнес Акува", "https://www.dropbox.com/scl/fi/2qozxbzlpp8x2cd84ymgc/delovaya.jpg?rlkey=t9w0rk7hs7a3ue37zepl76gw1&st=yxoh5yml&raw=1"),
    ("Акува в Бипрессии", "https://www.dropbox.com/scl/fi/0ptv0eitujf1fk2w1j1a6/bipressia.jpg?rlkey=z1kxxgg137eg0gs838if6yswg&st=g9qs7hr5&raw=1"),
    ("Новостная Акувка", "https://www.dropbox.com/scl/fi/c03p7xwr8iki0iyc10mja/novosti.jpg?rlkey=av5h9rihnglmc0pmd08p0zcaz&st=vqsmi2jj&raw=1"),
    ("Военная Акувка", "https://www.dropbox.com/scl/fi/qyis44qkcjd1hs1ljqunb/War2.jpg?rlkey=zr2n2u7jfbsbaazepw5dydpfp&st=c6dbcdjs&raw=1"),
    ("Военная Акувка 2.0", "https://www.dropbox.com/scl/fi/pqlmudhu3wf2xm1ee0hth/war..jpg?rlkey=wzori0hxgvtfe7uxrwl1g1b23&st=14pmbwke&raw=1"),
    ("Виндовс Акувка", "https://www.dropbox.com/scl/fi/shizjduditl35z6uwlbgu/Windows.jpg?rlkey=8eluwt45ovhmkzv8p6cj06xtm&st=eo6keebr&raw=1"),
    ("Морская Акувка", "https://www.dropbox.com/scl/fi/3c76uayms1l64gg5zaxqf/Akulenok.jpg?rlkey=rz0cvo61c8fa8uz2h0htmn18y&st=k7oa71jp&raw=1"),
    ("Просто Акувка", "https://www.dropbox.com/scl/fi/jysnyuiv2fv4beiyu30g1/aboA123.jpg?rlkey=96wdlyca64df4vawts9ioluiu&st=8e8vpdma&raw=1"),
    ("Упоротая Акувка", "https://www.dropbox.com/scl/fi/nbiel20tdra0xi9m9byvq/yporuto.jpg?rlkey=0kfzqfj5i7qvdnmrrszt4z75u&st=rf1kp2dj&raw=1")


]

c.execute("SELECT COUNT(*) FROM cards")
if c.fetchone()[0] == 0:
    c.executemany("INSERT INTO cards (name, image) VALUES (?, ?)", shark_cards)
    conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Используй команду /Акува, \n Чтобы получить карточку с акулой!")

@bot.message_handler(commands=['Акува', 'акува', 'Акула', 'акула'])
def get_card(message):
    user_id = message.from_user.id
    c.execute("SELECT last_used, acuvki FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if not row:
        c.execute("INSERT INTO users (user_id, last_used, acuvki) VALUES (?, ?, ?)", (user_id, int(time.time()), 0))
        conn.commit()
        row = (0, 0)

    last_used, acuvki = row
    now = int(time.time())
    cooldown = 2 * 60 * 60  

    if now - last_used < cooldown:
        remaining_time = timedelta(seconds=(cooldown - (now - last_used)))
        bot.send_message(message.chat.id, "Подожди ещё {} перед следующим использованием!".format(remaining_time))
        return

    c.execute("SELECT name, image, id FROM cards ORDER BY RANDOM() LIMIT 1")
    card = c.fetchone()
    c.execute("INSERT INTO user_cards (user_id, card_id) VALUES (?, ?)", (user_id, card[2]))
    conn.commit()
    acuvki_earned = 2000
    c.execute("UPDATE users SET acuvki = acuvki + ? WHERE user_id = ?", (acuvki_earned, user_id))
    conn.commit()
    bot.send_photo(message.chat.id, card[1], caption="Тебе выпала карточка: {}!\nАкувки: {} (+{})".format(card[0], acuvki, acuvki_earned))
    c.execute("UPDATE users SET last_used = ? WHERE user_id = ?", (now, user_id))
    conn.commit()

from telebot.types import InputMediaPhoto

@bot.message_handler(commands=['mycards'])
def mycards(message):
    user_id = message.from_user.id
    c = conn.cursor()
    c.execute("""SELECT cards.name, cards.image 
                 FROM user_cards 
                 JOIN cards ON user_cards.card_id = cards.id 
                 WHERE user_cards.user_id = ?""", (user_id,))
    user_cards = c.fetchall()
    c.close()

    if not user_cards:
        bot.send_message(message.chat.id, "У тебя пока нет карточек 😔. Попробуй получить через /Акува!")
        return

    text = "📦 Твои карточки ({} шт.):\n".format(len(user_cards))
    for name, _ in user_cards:
        text += f"• {name}\n"
    bot.send_message(message.chat.id, text)

    batch_size = 10
    for i in range(0, len(user_cards), batch_size):
        batch = user_cards[i:i+batch_size]
        media_group = []
        for idx, (name, image) in enumerate(batch):
            if idx == 0:
                media_group.append(InputMediaPhoto(media=image, caption=f""))
            else:
                media_group.append(InputMediaPhoto(media=image))
        bot.send_media_group(message.chat.id, media_group)
    
    
@bot.message_handler(commands=['bootdeeptrue'])
def bootdeeptrue(message):
    developer_id = 6378736359  
    if message.from_user.id != developer_id:
        bot.send_message(message.chat.id, "Эта команда доступна только разработчику!")
        return
    c.execute("SELECT name, image FROM cards ORDER BY RANDOM() LIMIT 1")
    card = c.fetchone()
    bot.send_photo(message.chat.id, card[1], caption="Тебе выпала карточка: {}!".format(card[0]))

def auto_ping():
    while True:
        bot.send_message(CHAT_ID, "/ping")  
        time.sleep(300)  


threading.Thread(target=auto_ping, daemon=True).start()

@bot.message_handler(commands=['profile'])
def profile(message):
    args = message.text.split()

    if len(args) == 1:
        target_id = message.from_user.id
        target_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    else:
        query = args[1]

        if query.isdigit():
            target_id = int(query)
            try:
                user_obj = bot.get_chat(target_id)
                target_name = f"@{user_obj.username}" if user_obj.username else user_obj.first_name
            except:
                target_name = f"ID:{target_id}"
        
        elif query.startswith("@"):
            username = query[1:]
            c.execute("SELECT user_id FROM users")
            all_users = [u[0] for u in c.fetchall()]
            
            target_id = None
            target_name = query
            for uid in all_users:
                try:
                    user_obj = bot.get_chat(uid)
                    if user_obj.username and user_obj.username.lower() == username.lower():
                        target_id = uid
                        target_name = f"@{user_obj.username}"
                        break
                except:
                    pass
            
            if not target_id:
                bot.send_message(message.chat.id, "❌ Пользователь с таким @username не найден в базе.")
                return
        else:
            bot.send_message(message.chat.id, "❌ Укажи ID или @username.")
            return

    c.execute("SELECT acuvki FROM users WHERE user_id = ?", (target_id,))
    row = c.fetchone()
    if not row:
        bot.send_message(message.chat.id, f"{target_name} ещё не получал карточки 😔")
        return
    acuvki = row[0]

    c.execute("SELECT COUNT(*) FROM user_cards WHERE user_id = ?", (target_id,))
    cards_count = c.fetchone()[0]

    c.execute("SELECT user_id FROM users ORDER BY acuvki DESC")
    all_users = [u[0] for u in c.fetchall()]
    rank_acuvki = all_users.index(target_id) + 1 if target_id in all_users else "—"

    c.execute("""SELECT user_id, COUNT(card_id) as cnt 
                 FROM user_cards 
                 GROUP BY user_id 
                 ORDER BY cnt DESC""")
    all_cards_rank = [u[0] for u in c.fetchall()]
    rank_cards = all_cards_rank.index(target_id) + 1 if target_id in all_cards_rank else "—"

    profile_text = (
        f"👤 Профиль {target_name}\n\n"
        f"💰 Акувки: {acuvki}\n"
        f"🃏 Карточек: {cards_count}\n"
        f"🏆 Ранг по Акувкам: {rank_acuvki}\n"
        f"📦 Ранг по Карточкам: {rank_cards}"
    )

    bot.send_message(message.chat.id, profile_text)


@bot.message_handler(commands=['list', 'top', 'topakuv', 'leaderakuv', 'leaderbalance', 'leaderakul'])
def list_top(message):
    try:
        c.execute("SELECT user_id, acuvki FROM users ORDER BY acuvki DESC LIMIT 10")
        top_users = c.fetchall()

        if not top_users:
            bot.send_message(message.chat.id, "Пока нет данных по топу 😔")
            return

        result = "🏆 Топ 10 по Акувкам 🏆\n\n"
        for i, (user_id, acuvki) in enumerate(top_users, start=1):
            try:
                user = bot.get_chat(user_id)
                if user.username:
                    name = f"@{user.username}"
                else:
                    name = user.first_name or "Безымянный"
            except:
                name = f"ID:{user_id}"

            result += f"{i}. {name} — {acuvki} Акувок 💰\n"

        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении топа: {e}")

from telebot.types import InputMediaPhoto

@bot.message_handler(commands=['topcards', 'top', 'leadercard', 'leadercards'])
def topcards(message):
    c = conn.cursor()
    c.execute("""
        SELECT users.user_id, COUNT(uc.card_id) AS total_cards
        FROM users
        LEFT JOIN user_cards uc ON users.user_id = uc.user_id
        GROUP BY users.user_id
        ORDER BY total_cards DESC
        LIMIT 10
    """)
    rows = c.fetchall()
    c.close()

    def display_name(uid):
        try:
            ch = bot.get_chat(uid)
            if getattr(ch, 'username', None):
                return f"@{ch.username}"
            fullname = " ".join(x for x in [getattr(ch, 'first_name', None), getattr(ch, 'last_name', None)] if x)
            return fullname.strip() if fullname.strip() else "Неизвестный"
        except Exception:
            return "Неизвестный"

    if not rows:
        bot.send_message(message.chat.id, "❌ Пока нет ни одного участника в топе.")
        return

    text = "🏆 Топ 10 по картам 🏆\n\n"
    for pos, (uid, total) in enumerate(rows, start=1):
        name = display_name(uid)
        text += f"{pos}. {name} — {total} карт\n"

    bot.send_message(message.chat.id, text)

                
@bot.message_handler(commands=['allcards'])
def allcards(message):
    developer_id = 123456789
    if message.from_user.id != developer_id:
        bot.send_message(message.chat.id, "Эта команда доступна только разработчику!")
        return
    
    c.execute("SELECT name, image FROM cards")
    all_cards = c.fetchall()
    if not all_cards:
        bot.send_message(message.chat.id, "Карточек пока нет!")
        return
    
    for card in all_cards:
        bot.send_photo(message.chat.id, card[1], caption=f"Карточка: {card[0]}")


@bot.message_handler(commands=['ping'])
def handle_ping(message):
    bot.send_message(message.chat.id, "Пингую бота, проверяю, не заснул ли он... ✅")

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <meta charset="utf-8">
            <title>АквуКарточки</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    background: linear-gradient(to right, #6dd5fa, #2980b9);
                    color: white;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }
                .button {
                    background: #ffffff;
                    color: #2980b9;
                    padding: 15px 25px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-size: 20px;
                    font-weight: bold;
                    transition: 0.3s;
                }
                .button:hover {
                    background: #dddddd;
                }
            </style>
        </head>
        <body>
            <h1>Добро пожаловать в АквуКарточки!</h1>
            <p>Получай случайные карточки с акулами в Telegram-боте.</p>
            <a class="button" href="https://t.me/KART_AKUV_bot" target="_blank">Перейти в бота</a>
        </body>
    </html>
    '''

if __name__ == "__main__":
    from threading import Thread
    Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    app.run(host="0.0.0.0", port=7000)
