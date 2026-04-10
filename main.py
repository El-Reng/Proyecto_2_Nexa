#NEXA — Núcleo de Ejecución y eXperiencia Asistida

import discord, os, comandos, memoria
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError('La variable "TOKEN" no ha sido cargada.')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await comandos.responder_mensaje(message)
    await bot.process_commands(message)

@bot.event
async def setup_hook():
    bot.loop.create_task(comandos.aviso_de_clases(bot))
    bot.loop.create_task(comandos.aviso_cuota(bot))

bot.run(TOKEN)