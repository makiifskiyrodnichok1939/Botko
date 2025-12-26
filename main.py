import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import random
from threading import Thread
from flask import Flask

# Flask app for health check
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# Start Flask in a separate thread
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Rest of your Discord bot code below...
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='฿ ', intents=intents)

# [All your existing code continues here...]
# ... [keeping all your existing functions and commands]

# Файлы для хранения данных
DATA_FILE = 'user_data.json'
CONFIG_FILE = 'config.json'
CASES_FILE = 'cases.json'
ITEMS_FILE = 'items.json'

def load_data():
    """Загрузка данных пользователей"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Сохранение данных пользователей"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_config():
    """Загрузка конфигурации сервера"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'currency_symbol': '฿',
        'currency_name': 'батов'
    }

def save_config(config):
    """Сохранение конфигурации"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_cases():
    """Загрузка кейсов"""
    if os.path.exists(CASES_FILE):
        with open(CASES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cases(cases):
    """Сохранение кейсов"""
    with open(CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=4)

def load_items():
    """Загрузка предметов"""
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_items(items):
    """Сохранение предметов"""
    with open(ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

user_data = load_data()
config = load_config()
cases = load_cases()
items_db = load_items()

def init_user_inventory(user_id):
    """Инициализация инвентаря пользователя"""
    if 'inventory' not in user_data[user_id]:
        user_data[user_id]['inventory'] = []
    if 'luck_boost' not in user_data[user_id]:
        user_data[user_id]['luck_boost'] = 0

class RulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Я согласен с правилами', style=discord.ButtonStyle.green, custom_id='accept_rules')
    async def accept_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        if user_id in user_data:
            await interaction.response.send_message('Вы уже авторизованы!', ephemeral=True)
            return
        
        money_ranges = [
            (500, 1000, 40),
            (1001, 5000, 30),
            (5001, 10000, 20),
            (10001, 15000, 7),
            (15001, 20000, 3)
        ]
        
        chosen_range = random.choices(
            money_ranges,
            weights=[r[2] for r in money_ranges]
        )[0]
        
        money = random.randint(chosen_range[0], chosen_range[1])
        
        user_data[user_id] = {
            'username': interaction.user.name,
            'money': money,
            'inventory': [],
            'luck_boost': 0
        }
        save_data(user_data)
        
        role_name = "Участник"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f'🎉 **Поздравляем!**\n\n'
                f'Вы успешно авторизованы!\n'
                f'Вам выпало: **{money:,} {config["currency_symbol"]}**\n'
                f'Роль "{role_name}" была выдана!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'🎉 **Поздравляем!**\n\n'
                f'Вы успешно авторизованы!\n'
                f'Вам выпало: **{money:,} {config["currency_symbol"]}**\n\n'
                f'⚠️ Роль "{role_name}" не найдена на сервере.',
                ephemeral=True
            )

@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен!')
    bot.add_view(RulesView())

# [Include all your other commands here - I'll skip repeating them for brevity]

# At the end:
if __name__ == '__main__':
    bot.run(token, log_handler=handler)
