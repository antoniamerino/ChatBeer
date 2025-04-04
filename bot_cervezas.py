import json
import unicodedata

def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Cargar la base de datos de cervezas
with open("cervezas_estandarizadas.json", "r", encoding="utf-8") as f:
    cervezas = json.load(f)

# Agregar campos normalizados para facilitar comparaciones
for cerveza in cervezas:
    cerveza["nombre_normalizado"] = normalizar(cerveza["nombre"])
    cerveza["cerveceria_normalizado"] = normalizar(cerveza["cerveceria"])
    cerveza["pais_normalizado"] = normalizar(cerveza["Pais Origen"])
    cerveza["region_normalizado"] = normalizar(cerveza.get("Region Origen", ""))
    cerveza["tipo_normalizado"] = normalizar(cerveza["Tipo"])
    cerveza["color_normalizado"] = normalizar(cerveza.get("Color", ""))

# Aplicar filtros sobre la base de datos

def aplicar_filtros(filtros, universo):
    resultados = []
    for cerveza in universo:
        if all(cond(cerveza) for cond in filtros):
            resultados.append(cerveza)
    return sorted(resultados, key=lambda x: int(x["Nota"]) if str(x["Nota"]).isdigit() else 0, reverse=True)

# Mostrar todos los detalles de las cervezas encontradas

def mostrar_detalle(cervezas):
    texto = ""
    for cerveza in cervezas:
        texto += (
            f"🍺 {cerveza['nombre']} ({cerveza['Tipo']})\n"
            f"- Aroma: {cerveza['Aroma (Escala)']} | Sabor: {cerveza['Sabor (Escala)']}\n"
            f"- Amargor: {cerveza['Amargor (Escala)']} | Cuerpo: {cerveza['Cuerpo (Escala)']}\n"
            f"- Alcohol: {cerveza['Alcohol']}% | Frutal: {'Sí' if cerveza['Frutal'] == 1 else 'No'}\n"
            f"- Nota Diego: {cerveza['Nota']}\n"
            f"- Comentario: {cerveza['Comentarios']}\n\n"
        )
    return texto.strip()

# Manejo del flujo de conversación con estados

def responder(mensaje, sesion):
    universo = cervezas.copy()
    condiciones = []

    filtros_validos = {
        "nombre", "cerveceria", "pais", "region", "tipo", "color", "espuma",
        "aroma", "sabor", "amargor", "cuerpo", "alcohol", "carbonatacion", "frutal"
    }

    if sesion["estado"] == "inicio":
        sesion["estado"] = "esperando_filtros"
        return "🍻 Bienvenido al bot cervecero de Diego.\n¿Por qué filtros te gustaría buscar cervezas? Puedes decir por ejemplo: aroma, sabor, país, tipo, nombre, etc."

    elif sesion["estado"] == "esperando_filtros":
        campos = mensaje.replace(" y ", ",")
        campos_seleccionados = [normalizar(c).strip() for c in campos.split(",")]

        sesion["campos_filtrables"] = []
        sesion["criterios_utilizados"] = []

        for campo in campos_seleccionados:
            if campo in filtros_validos:
                sesion["campos_filtrables"].append(campo)
            else:
                return f"⚠️ El filtro '{campo}' no existe o está mal escrito.\n\n¿Puedes intentarlo de nuevo?\nEjemplo: sabor, aroma, país, frutal..."

        if not sesion["campos_filtrables"]:
            return "😅 No se especificaron filtros válidos. Intenta con: nombre, tipo, país, sabor, etc."

        sesion["estado"] = "respondiendo_preguntas"
        sesion["pregunta_actual"] = 0
        sesion["respuestas"] = {}
        return preguntar_siguiente(sesion)

    elif sesion["estado"] == "respondiendo_preguntas":
        campo_actual = sesion["campos_filtrables"][sesion["pregunta_actual"]]
        sesion["respuestas"][campo_actual] = mensaje
        sesion["criterios_utilizados"].append(campo_actual)
        sesion["pregunta_actual"] += 1

        if sesion["pregunta_actual"] < len(sesion["campos_filtrables"]):
            return preguntar_siguiente(sesion)
        else:
            for campo in sesion["campos_filtrables"]:
                valor = normalizar(sesion["respuestas"][campo])
                if campo == "nombre":
                    condiciones.append(lambda c, v=valor: v in c["nombre_normalizado"])
                elif campo == "cerveceria":
                    condiciones.append(lambda c, v=valor: v in c["cerveceria_normalizado"])
                elif campo == "pais":
                    condiciones.append(lambda c, v=valor: v in c["pais_normalizado"])
                elif campo == "region":
                    condiciones.append(lambda c, v=valor: v in c["region_normalizado"])
                elif campo == "tipo":
                    condiciones.append(lambda c, v=valor: v in c["tipo_normalizado"])
                elif campo == "color":
                    condiciones.append(lambda c, v=valor: v in c["color_normalizado"])
                elif campo == "espuma":
                    condiciones.append(lambda c, v=valor: v in normalizar(c.get("Espuma (Estandarizada)", "")))
                elif campo == "aroma":
                    condiciones.append(lambda c, v=valor: v == normalizar(c["Aroma (Escala)"]))
                elif campo == "sabor":
                    condiciones.append(lambda c, v=valor: v == normalizar(c["Sabor (Escala)"]))
                elif campo == "amargor":
                    condiciones.append(lambda c, v=valor: v == normalizar(c["Amargor (Escala)"]))
                elif campo == "cuerpo":
                    condiciones.append(lambda c, v=valor: v == normalizar(c["Cuerpo (Escala)"]))
                elif campo == "alcohol":
                    try:
                        condiciones.append(lambda c, a=float(valor): float(c["Alcohol"]) >= a)
                    except:
                        return "🚫 El valor de alcohol debe ser un número. Intenta de nuevo con algo como '5.5'."
                elif campo == "carbonatacion":
                    condiciones.append(lambda c, v=valor: v in normalizar(c.get("Carbonatación", "")))
                elif campo == "frutal":
                    condiciones.append(lambda c, f=valor: c["Frutal"] == (1 if "s" in f else 0))

            resultados = aplicar_filtros(condiciones, universo)
            sesion["estado"] = "inicio"
            if resultados:
                criterio_texto = ", ".join(sesion["criterios_utilizados"])
                detalle = mostrar_detalle(resultados[:5])
                return f"🎯 Estas cervezas fueron seleccionadas según: {criterio_texto}.\n\n{detalle}"
            else:
                return "😔 No encontré cervezas con esos filtros. ¿Quieres intentarlo de nuevo?"

def preguntar_siguiente(sesion):
    campo = sesion["campos_filtrables"][sesion["pregunta_actual"]]
    preguntas = {
        "nombre": "¿Cuál es el nombre de la cerveza que buscas?",
        "cerveceria": "¿Qué cervecería estás buscando?",
        "pais": "¿Qué país estás buscando?",
        "region": "¿Qué región estás buscando?",
        "tipo": "¿Qué tipo de cerveza te gustaría? (Ej: IPA, Amber Ale...)",
        "color": "¿Qué color prefieres? (negra, rubia, roja...)",
        "espuma": "¿Qué tipo de espuma prefieres? (alta, media, baja)",
        "aroma": "¿Qué intensidad de aroma prefieres? (alto, medio, bajo)",
        "sabor": "¿Qué intensidad de sabor prefieres? (alto, medio, bajo)",
        "amargor": "¿Qué nivel de amargor prefieres? (alto, medio, bajo)",
        "cuerpo": "¿Qué cuerpo prefieres? (alto, medio, bajo)",
        "alcohol": "¿Cuál es el mínimo de alcohol que te gustaría? (Ej: 5.0)",
        "carbonatacion": "¿Qué nivel de carbonatación prefieres? (alta, media, baja)",
        "frutal": "¿Te gustaría que sea frutal? (sí / no)"
    }
    return preguntas.get(campo, "Responde para continuar:")
