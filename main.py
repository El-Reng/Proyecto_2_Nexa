#NEXA — Núcleo de Ejecución y eXperiencia Asistida

import discord, comandos, memoria
from discord.ext import commands

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
    
    contenido = message.content.lower().split()

    if "nexa" in contenido:

        if "hola" in contenido:
            await comandos.saludar(message)

        elif "chau" in contenido:
            await comandos.despedir(message)

        elif "ayuda" in contenido:
            await comandos.ayuda(message)

    await bot.process_commands(message)

@bot.event
async def setup_hook():
    bot.loop.create_task(comandos.aviso_de_clases(bot))

bot.run(memoria.token)