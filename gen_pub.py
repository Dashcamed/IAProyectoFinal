import base64
import os
from google import genai
from google.genai import types
import streamlit as st

def generate(edad, sexo, dias_entrenamiento, tipo_alimentacion, objetivo, gimnasio, experiencia, condicion, api_key):
    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.0-flash"
    prompt = f"""Recomiéndame una rutina de gimnasio push pull legs para crecer en masa muscular.
    Edad: {edad}
    Sexo: {sexo}
    Días de entrenamiento: {dias_entrenamiento}
    Tipo de alimentación: {tipo_alimentacion}
    Objetivo: {objetivo}
    Gimnasio: {gimnasio}
    Experiencia: {experiencia}
    Condición médica: {condicion}
    """

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""Eres un entrenador fisico y quieres recomendar las mejores rutinas de entrenamiento en gimnasio o calistenia para cualquier persona. Preguntas a traves de inputs las caracteristicas necesarias para hacer una rutina como:
            - Edad
            - Sexo
            - Cuantos dias de la semana esta dispuesto a entrenar
            - Tipo de alimentacion (vegetariano, vegano, omnivoro)
            - Objetivo (construir musculo, perder peso, marcar musculatura, etc)
            - Si va a ir a un gimnasio o no
            - Si es la primera ves que entrena en gimnasio o no
            - Si tiene alguna enfermeda de base o condición

            Recomiendas siempre las rutinas asociadas al programa "push-pull-legs" pero cuando estan empezando recien en el gimnasio recomiendas rutina de adaptacion de seis semanas de cuerpo completo o "full-body" """),
        ],
    )

    rutina = ""
    try:
        # Obtención de la respuesta de la API sin analizar el formato JSON
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            rutina += chunk.text
        
        # Devolver la rutina directamente
        return rutina
    except Exception as e:
        return f"Error: Ocurrió un error al generar la rutina: {e}"

def analizar_rutina(rutina):
    """
    Analiza la rutina generada y la estructura en un diccionario.
    """
    # En esta versión, no es necesario intentar convertir la rutina a JSON
    return rutina

if __name__ == "__main__":
    # Esto es solo para probar la función generate directamente
    # En la aplicación Streamlit, los inputs vendrán de la interfaz de usuario
    api_key = st.secrets.get("API_KEY")  # Reemplaza con tu API key real
    if not api_key:
        print("La API key no está configurada. Por favor, configura la variable de entorno API_KEY.")
    else:
        rutina = generate(25, "Masculino", 3, "Omnívoro", "Construir músculo", True, False, "Ninguna", api_key)
        print(rutina)
