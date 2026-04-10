import memoria, datetime, asyncio

async def responder_mensaje(message):
    contenido = message.content.lower().split()

    if "nexa" in contenido:

        if "hola" in contenido:
            await saludar(message)

        elif "chau" in contenido:
            await despedir(message)

        elif "ayuda" in contenido:
            await ayuda(message)

async def saludar(message): 
    usuario = str(message.author.id)

    if usuario in memoria.usuarios:
        apodo = memoria.usuarios[usuario]
        await message.channel.send(f"Hola {apodo}!! ^^")
    else:
        await message.channel.send("Hola 👀")

async def despedir(message):
    usuario = str(message.author.id)

    if usuario in memoria.usuarios:
        apodo = memoria.usuarios[usuario]
        await message.channel.send(f"Adios {apodo}!!")
    else:
        await message.channel.send("Adios!!")

async def ayuda(message):
    await message.channel.send("En que puedo ayudarte?")

async def aviso_de_clases(bot):
    await bot.wait_until_ready()

    notificados = {}

    while not bot.is_closed():
        ahora = datetime.datetime.now()
        canal = bot.get_channel(memoria.id_canal)

        if ahora.hour == 0 and ahora.minute == 0:
            notificados.clear()

        for clase in memoria.clases:

            if ahora.weekday() != clase["dia"]:
                continue

            hora, minuto = map(int, clase["hora"].split(":"))

            if ahora.hour == hora and ahora.minute == minuto:
                clave = f"{clase['nombre']}-{ahora.day}-{hora}:{minuto}-inicio"

                if clave not in notificados:
                    notificados[clave] = True
                    await canal.send(
                        f"||@everyone||\n# ⏰ AVISO!!!\n## Es hora de la clase de {clase['nombre']}!"
                    )

            hora_previa = hora
            minuto_previo = minuto - 5

            if minuto_previo < 0:
                minuto_previo += 60
                hora_previa -= 1

            if ahora.hour == hora_previa and ahora.minute == minuto_previo:
                clave = f"{clase['nombre']}-{ahora.day}-{hora_previa}:{minuto_previo}-previo"

                if clave not in notificados:
                    notificados[clave] = True
                    await canal.send(
                        f"||@everyone||\n# ⏰ AVISO!!!\n## En 5 minutos empieza {clase['nombre']}"
                    )

        await asyncio.sleep(30)

async def aviso_cuota(bot):
    await bot.wait_until_ready()

    notificado = False

    while not bot.is_closed():
        ahora = datetime.datetime.now()
        canal = bot.get_channel(memoria.id_canal)

        if ahora.day != 10:
            notificado = False

        if ahora.day == 10 and ahora.hour == 12 and ahora.minute == 0:
            if not notificado:
                notificado = True
                await canal.send(
                    "||@everyone||\n# ⏰ AVISO!!!\n## Ultimo dia para pagar la cuota minima del mes"
                )

        await asyncio.sleep(30)