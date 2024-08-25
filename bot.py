import discord
from discord.ext import commands, tasks
import json
import os
import logging
from config import TOKEN, PREFIX, channel
from data_manager import DataManager

# Khởi tạo DataManager
data_manager = DataManager()

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Xóa lệnh help mặc định bot.remove_command('help')
extensions = ["commands", "help_cog"] # Danh sách các cog cần gọi

@bot.event
async def on_ready():
    print(f'{bot.user.name} is online!')
    print('--------------------')
    print('Bot is ready!')
    # Load extension
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logging.info('Loaded extension %s', ext)
        except Exception as e:
            logging.error('Failed to load extension %s: %s', ext, e)

    log_channel = bot.get_channel(int(channel))
    if log_channel:
        loaded_msg = f"Loaded extensions: {', '.join(extensions)}"
        await log_channel.send(loaded_msg)
    else:
        logging.error("Log channel not found. Please check the channel ID in the config.")

if __name__ == '__main__':
    bot.run(TOKEN)