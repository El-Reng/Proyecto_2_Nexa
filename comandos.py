import memoria, datetime, asyncio

async def saludar(message): 
    usuario = message.author.name

    if usuario in memoria.usuarios:
        apodo = memoria.usuarios[usuario]
        await message.channel.send(f"Hola {apodo}!! ^^")
    else:
        await message.channel.send("Hola 👀")

async def despedir(message):
    await message.channel.send("Adios!!")

async def ayuda(message):
    await message.channel.send("En que puedo ayudarte?")

async def aviso_de_clases(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        ahora = datetime.datetime.now()

        for clase in memoria.clases:

            if ahora.weekday() == clase["dia"]:

                hora_clase = clase["hora"]

                hora, minuto = map(int, hora_clase.split(":"))

                if ahora.hour == hora and ahora.minute == minuto:
                    canal = bot.get_channel(memoria.id_canal)
                    await canal.send(f"⏰ AVISO: es hora de la clase de {clase['nombre']}!")

                    await asyncio.sleep(60)

        await asyncio.sleep(30)