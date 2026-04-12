import memoria, asyncio, random
from datetime import datetime
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")

def ahora():
    return datetime.now(ZONA)

def crear_datetime(fecha, hora):
    dia, mes = map(int, fecha.split("/"))
    h, m = map(int, hora.split(":"))

    ahora_local = ahora()

    return datetime(
        year=ahora_local.year,
        month=mes,
        day=dia,
        hour=h,
        minute=m,
        tzinfo=ZONA
    )

def agregar_recordatorio(usuario, texto, momento, notificacion):
    memoria.recordatorios.append({
        "usuario": usuario,
        "texto": texto,
        "momento": momento,
        "notificacion": notificacion
    })

async def responder_mensaje(message):
    contenido = message.content.lower().replace(",", "").replace(".", "")
    palabras = contenido.split()

    if "nexa" in palabras:

        if any(s in contenido for s in memoria.SALUDOS):
            await saludar(message)

        elif any(d in contenido for d in memoria.DESPEDIDAS):
            await despedir(message)

        elif any(a in contenido for a in memoria.AYUDA):
            await ayuda(message)

        elif "recordame" in palabras or "recordanos" in palabras:
            await recordar(message)

async def saludar(message): 
    usuario = str(message.author.id)
    nombre = memoria.usuarios.get(usuario, message.author.name)

    respuesta = random.choice(memoria.RESPUESTAS_SALUDO)

    await message.channel.send(f"{respuesta.replace('Hola.', f'Hola {nombre}.')}")

async def despedir(message):
    respuesta = random.choice(memoria.RESPUESTAS_DESPEDIDA)
    await message.channel.send(respuesta)

async def ayuda(message):
    await message.channel.send(
        "Claro. Puedo explicarte cómo funciono.\n\n"
        "Actualmente estoy diseñada para asistirte con tareas simples.\n"
        "Podés interactuar conmigo usando comandos directos como 'nexa hola' o 'nexa chau'.\n\n"
        "Mi función principal es gestionar recordatorios.\n"
        "Por ejemplo, podés decir:\n"
        "'nexa recordame estudiar - 18:00'\n"
        "y voy a avisarte en ese momento.\n\n"
        "También podés especificar una fecha:\n"
        "'nexa recordame parcial - 15/04 - 20:00'\n\n"
        "Si usás 'recordanos', el aviso se envía a todo el canal.\n"
        "Si usás 'recordame', el aviso es solo para vos.\n\n"
        "Todavía estoy en desarrollo, pero mi objetivo es ampliar mis capacidades progresivamente."
    )

async def recordar(message):
    usuario = str(message.author.id)

    try:
        contenido = message.content.lower()
        palabras = contenido.split()

        if "recordanos" in palabras:
            notificacion = "grupal"
            contenido = contenido.split("recordanos", 1)[1].strip()
        else:
            notificacion = "individual"
            contenido = contenido.split("recordame", 1)[1].strip()

        partes = [p.strip() for p in contenido.split("-")]

        if len(partes) == 3:
            texto, fecha, hora = partes

        elif len(partes) == 2:
            texto, hora = partes
            momento_actual = ahora()
            fecha = f"{momento_actual.day:02d}/{momento_actual.month:02d}"

        else:
            await message.channel.send(
                "No pude interpretar el formato.\nUsá: recordame/recordanos texto - [día/mes] - hora"
            )
            return

        try:
            momento = crear_datetime(fecha, hora)
        except ValueError:
            await message.channel.send(
                "La fecha o la hora no son válidas."
            )
            return

        if momento <= ahora():
            await message.channel.send(
                "El momento indicado ya pasó. Ingresá una fecha u hora futura."
            )
            return

        nombre = memoria.usuarios.get(usuario, message.author.name)

        agregar_recordatorio(usuario, texto, momento, notificacion)

        await message.channel.send(
            f"Registro completado, {nombre}.\n"
            f"Contenido: {texto}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}"
        )

    except IndexError:
        await message.channel.send(
            "No pude interpretar el comando."
        )

async def aviso_de_clases(bot):
    await bot.wait_until_ready()

    notificados = {}

    while not bot.is_closed():
        momento_actual = ahora()
        canal = bot.get_channel(memoria.id_canal)

        if not canal:
            await asyncio.sleep(30)
            continue

        if momento_actual.hour == 0 and momento_actual.minute == 0:
            notificados.clear()

        for clase in memoria.clases:

            if momento_actual.weekday() != clase["dia"]:
                continue

            hora, minuto = map(int, clase["hora"].split(":"))

            if momento_actual.hour == hora and momento_actual.minute == minuto:
                clave = f"{clase['nombre']}-{momento_actual.day}-{hora}:{minuto}-inicio"

                if clave not in notificados:
                    notificados[clave] = True
                    await canal.send(
                        f"||@everyone||\nAviso de clase.\nEs momento de: {clase['nombre']}"
                    )

            hora_previa = hora
            minuto_previo = minuto - 5

            if minuto_previo < 0:
                minuto_previo += 60
                hora_previa -= 1

            if momento_actual.hour == hora_previa and momento_actual.minute == minuto_previo:
                clave = f"{clase['nombre']}-{momento_actual.day}-{hora_previa}:{minuto_previo}-previo"

                if clave not in notificados:
                    notificados[clave] = True
                    await canal.send(
                        f"||@everyone||\nAviso previo.\nLa clase '{clase['nombre']}' comienza en 5 minutos."
                    )

        await asyncio.sleep(30)

async def aviso_cuota(bot):
    await bot.wait_until_ready()

    notificado = False

    while not bot.is_closed():
        momento_actual = ahora()
        canal = bot.get_channel(memoria.id_canal)

        if not canal:
            await asyncio.sleep(30)
            continue

        if momento_actual.day != 10:
            notificado = False

        if momento_actual.day == 11 and momento_actual.hour == 22 and momento_actual.minute == 0:
            if not notificado:
                notificado = True
                await canal.send(
                    "||@everyone||\nAviso.\nEs el último momento disponible para registrar el pago de la cuota mínima del mes."
                )

        await asyncio.sleep(30)

async def aviso_de_recordatorios(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        ahora_local = ahora()
        canal = bot.get_channel(memoria.id_canal)

        if not canal:
            await asyncio.sleep(30)
            continue

        for recordatorio in memoria.recordatorios[:]:

            if ahora_local >= recordatorio["momento"]:

                usuario = recordatorio["usuario"]
                texto = recordatorio["texto"]

                if recordatorio["notificacion"] == "grupal":
                    await canal.send(
                        f"||@everyone||\nRecordatorio.\n{texto}"
                    )
                else:
                    await canal.send(
                        f"<@{usuario}>\nRecordatorio.\n{texto}"
                    )

                memoria.recordatorios.remove(recordatorio)

        await asyncio.sleep(30)