import os
import streamlit as st
import base64
from openai import OpenAI

# ==============================
# FUNCIÓN PARA ENCODEAR LA IMAGEN
# ==============================
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ==============================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================
st.set_page_config(
    page_title="Análisis de Imagen con IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==============================
# ENCABEZADO Y PRESENTACIÓN
# ==============================
st.title("🤖🏞️ Análisis de Imagen con Inteligencia Artificial")
st.markdown("""
Carga una imagen y deja que el modelo **GPT-4o** la describa en español.  
Opcionalmente, puedes añadir contexto o una pregunta específica para un análisis más detallado.
""")

# ==============================
# INGRESO DE API KEY
# ==============================
ke = st.text_input('🔑 Ingresa tu clave de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key) if api_key else None

# ==============================
# SUBIR IMAGEN
# ==============================
uploaded_file = st.file_uploader("📂 Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("👁️ Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# ==============================
# OPCIÓN DE PREGUNTA ESPECÍFICA
# ==============================
show_details = st.toggle("¿Quieres hacer una pregunta específica sobre la imagen?", value=False)

if show_details:
    additional_details = st.text_area(
        "📝 Escribe tu pregunta o contexto aquí:",
        placeholder="Ejemplo: ¿Qué emociones transmiten las personas en la foto?"
    )
else:
    additional_details = None

# ==============================
# BOTÓN DE ANÁLISIS
# ==============================
analyze_button = st.button("🔍 Analizar imagen", type="primary")

if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("⏳ Analizando la imagen..."):
        # Encode la imagen
        base64_image = encode_image(uploaded_file)

        # Prompt base
        prompt_text = "Describe lo que ves en la imagen en español."

        # Agregar detalles adicionales si los hay
        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional proporcionado por el usuario:\n{additional_details}"

        # Mensajes para la API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    },
                ],
            }
        ]

        # Llamada al modelo con streaming de la respuesta
        try:
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"⚠️ Ha ocurrido un error: {e}")

# ==============================
# ADVERTENCIAS SI FALTA ALGO
# ==============================
else:
    if not uploaded_file and analyze_button:
        st.warning("📥 Por favor sube una imagen para analizar.")
    if not api_key:
        st.warning("🔑 Debes ingresar tu API key de OpenAI para continuar.")
