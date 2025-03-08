import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import textwrap
import gen_pub
import json

def generar_pdf(rutina_estructurada):
    """
    Genera un archivo PDF con la rutina formateada de manera ordenada y precisa.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50  # Posición inicial

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, rutina_estructurada.get("titulo", "Sin título"))
    y -= 20

    # Descripción con manejo de salto de línea
    c.setFont("Helvetica", 12)
    descripcion = textwrap.wrap(rutina_estructurada.get("descripcion", ""), width=80)
    for line in descripcion:
        c.drawString(100, y, line)
        y -= 15
    y -= 10

    # Lista de ejercicios
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Ejercicios:")
    y -= 20

    c.setFont("Helvetica", 11)
    for ejercicio in rutina_estructurada.get("ejercicios", []):
        c.drawString(100, y, f"- {ejercicio['nombre']}")
        y -= 15
        c.drawString(120, y, f"Series: {ejercicio['series']}, Repeticiones: {ejercicio['repeticiones']}")
        y -= 15
        if y < 50:  # Nueva página si no hay espacio
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

def main():
    st.title("Recomendador de Rutinas de Gimnasio")

    # API key (usa variables de entorno o Streamlit secrets)
    api_key = st.secrets.get("API_KEY")
    if not api_key:
        st.error("La API key no está configurada. Por favor, configura la variable de entorno API_KEY.")
        return

    # Inputs del usuario
    edad = st.number_input("Edad", min_value=10, max_value=100, value=25)
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    dias_entrenamiento = st.slider("Días de entrenamiento por semana", min_value=1, max_value=7, value=3)
    tipo_alimentacion = st.selectbox("Tipo de alimentación", ["Omnívoro", "Vegetariano", "Vegano"])
    objetivo = st.selectbox("Objetivo", ["Construir músculo", "Perder peso", "Marcar musculatura"])
    gimnasio = st.checkbox("¿Tienes acceso a un gimnasio?")
    experiencia = st.checkbox("¿Es tu primera vez en el gimnasio?")
    condicion = st.text_input("¿Tienes alguna condición médica?")

    # Variable para almacenar la rutina
    rutina = None

    # Botón para generar la rutina
    if st.button("Generar Rutina"):
        try:
            rutina = gen_pub.generate(edad, sexo, dias_entrenamiento, tipo_alimentacion, objetivo, gimnasio, experiencia, condicion, api_key)
            st.session_state.rutina = rutina
            if "Error" in rutina:
                st.error(rutina)  # Mostrar el error retornado por la API
            else:
                st.write(rutina)  # Mostrar el resultado de la API para ver qué está regresando
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

    if st.button("Imprimir Rutina"):
        try:
            rutina = st.session_state.get("rutina", None)
            if rutina:
                # La rutina puede ser un string, así que hay que procesarla adecuadamente
                if isinstance(rutina, str):  # Si la rutina es texto
                    st.write("Respuesta de la API (en texto):")
                    st.text(rutina)
                    rutina_estructurada = {"titulo": "Rutina Generada", "descripcion": rutina, "ejercicios": []}
                else:
                    rutina_estructurada = gen_pub.analizar_rutina(rutina)
                    st.write(rutina_estructurada)

                # Validar antes de generar el PDF
                if not isinstance(rutina_estructurada, dict) or not rutina_estructurada:
                    st.error("Error: La rutina no tiene el formato correcto.")
                else:
                    pdf_buffer = generar_pdf(rutina_estructurada)
                    st.download_button(
                        label="Descargar Rutina en PDF",
                        data=pdf_buffer,
                        file_name="rutina.pdf",
                        mime="application/pdf",
                    )
            else:
                st.warning("Por favor, genera una rutina primero.")
        except Exception as e:
            st.error(f"Ocurrió un error al generar el PDF: {e}")

if __name__ == "__main__":
    main()
