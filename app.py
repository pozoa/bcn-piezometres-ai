import os
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

# 1. Configuración de la página web de Streamlit
st.set_page_config(page_title="Agent de Pous de Barcelona", layout="wide", page_icon="🤖")

# Cargar variables de entorno
load_dotenv()

# Archivo de datos global
ARCHIVO_CSV = "piezometres_equipaments.csv"

@st.cache_data
def cargar_datos():
    try:
        return pd.read_csv(ARCHIVO_CSV)
    except Exception as e:
        st.error(f"❌ Error al carregar el fitxer de dades: {e}")
        return None

df_global = cargar_datos()

# 2. Inicializar Estados de la Sesión en Streamlit (Memoria visual)
if "historial_conversacion" not in st.session_state:
    st.session_state.historial_conversacion = []

if "coordenadas_mapa" not in st.session_state:
    # Coordenadas por defecto (Centro de Barcelona)
    st.session_state.coordenadas_mapa = {"lat": 41.3851, "lon": 2.1734, "zoom": 12, "nombre": "Barcelona"}

# 3. DEFINIMOS LA NUEVA HERRAMIENTA QUE CAMBIA EL MAPA EN LA WEB (CORREGIDA)
@tool
def actualizar_mapa_interactivo(codi_aca: str) -> str:
    """
    Obre o mostra un pou o piezòmetre ESPECÍFIC i CONCRET al mapa utilitzant el seu codi o referència.
    S'ha d'utilitzar ÚNICAMENT quan l'usuari demani de forma directa visualitzar la ubicació d'un sol pou (Ex: 'abre pozo 5', 'veure el pou 22').
    NO S'HA D'UTILITZAR MAI per a preguntes generals, estadístiques, recomptes, càlculs, gràfics o agrupacions de dades per columnes (com districte, barri o estat).
    """
    if df_global is None:
        return "Error: La base de dades no està disponible."
    
    try:
        codi_cercat = str(codi_aca).strip()
        if "pozo" in codi_cercat.lower():
            codi_cercat = codi_cercat.lower().replace("pozo", "").strip()
        if "pou" in codi_cercat.lower():
            codi_cercat = codi_cercat.lower().replace("pou", "").strip()

        fila = df_global[df_global['Codi_Estacio_ACA'].astype(str).str.strip() == codi_cercat]
        if fila.empty:
            fila = df_global[df_global['Codi_Estacio_ACA'].astype(str).str.contains(codi_cercat, case=False, na=False)]
            
        if fila.empty:
            return f"No s'ha trobat cap pou amb el codi Codi_Estacio_ACA: '{codi_cercat}'."
        
        # Extraemos datos reales del CSV
        latitud = float(fila.iloc[0]['Latitud'])
        longitud = float(fila.iloc[0]['Longitud'])
        nom_estacio = fila.iloc[0].get('Nom_Estacio', f"Pou {codi_cercat}")
        
        # Guardamos en el estado de Streamlit para cambiar el mapa de la pantalla
        st.session_state.coordenadas_mapa = {
            "lat": latitud,
            "lon": longitud,
            "zoom": 16,
            "nombre": nom_estacio
        }
        
        return f"S'ha actualitzat el mapa web per al pou {nom_estacio} (Codi ACA: {codi_cercat}) a les coordenades: {latitud}, {longitud}."
    except Exception as e:
        return f"Error al processar el mapa: {e}"

# 4. Configuración del Agente de Inteligencia Artificial
def obtener_agente():
    if df_global is None or not os.getenv("GROQ_API_KEY"):
        return None
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    return create_pandas_dataframe_agent(
        llm,
        df_global,
        verbose=True, 
        agent_type="tool-calling", 
        allow_dangerous_code=True,
        extra_tools=[actualizar_mapa_interactivo],
        prefix=(
            "Ets un assistent expert i un agent de dades per als pous de Barcelona. Respon sempre en català de forma educada i clara. "
            "Totes les teves respostes han d'estar basades estrictament en la informació i operacions matemàtiques que facis sobre el fitxer CSV. "
            "Si l'usuari et demana veure, obrir o mostrar un pou específic al mapa (Ex: 'abre pozo 5'), identifica el seu "
            "identificador a la columna 'Codi_Estacio_ACA' de la taula i crida immediatament a l'eina "
            "'actualizar_mapa_interactivo' passant-li aquest codi. "
            "Si la pregunta demana recomptes, càlculs totals o agrupacions generals (com districtes), NO usis l'eina del mapa; executa directament codi Pandas sobre el DataFrame per respondre amb la taula de dades o el número corresponent."
        )
    )

asistente = obtener_agente()

# ==============================================================================
# 5. DISEÑO DE LA INTERFAZ GRÁFICA (Doble columna: Chat | Mapa)
# ==============================================================================
st.title("🤖 Agent Intel·ligent de Piezòmetres i Pous - Barcelona")
st.markdown("Analitza dades en temps real del catàleg de pous i visualitza'ls interactivament.")

if not os.getenv("GROQ_API_KEY"):
    st.error("🔑 Falta la clau GROQ_API_KEY al fitxer .env")
else:
    # Creamos dos columnas visuales: Columna 1 (Ancho 7), Columna 2 (Ancho 5)
    col1, col2 = st.columns([7, 5])
    
    # --- COLUMNA 1: EL CHAT ---
    with col1:
        st.subheader("💬 Xat amb les dades")
        
        # Contenedor para la caja del historial para que se vea limpio
        container_chat = st.container(height=500)
        with container_chat:
            for msg in st.session_state.historial_conversacion:
                if isinstance(msg, HumanMessage):
                    # Avatar verde para el usuario
                    with st.chat_message("user", avatar="🟢"):
                        st.write(msg.content)
                elif isinstance(msg, AIMessage):
                    # Devolvemos el avatar del asistente por defecto (el robot clásico de Streamlit)
                    with st.chat_message("assistant"):
                        st.write(msg.content)
        
        # Caja de entrada de texto del usuario al final de la pantalla
        if pregunta := st.chat_input("Pregunta al teu CSV (Ex: 'Abre el pozo 5' o 'Quants pous hi ha per districte?')"):
            # Mostrar la pregunta inmediatamente en pantalla con el icono verde
            with container_chat:
                with st.chat_message("user", avatar="🟢"):
                    st.write(pregunta)
            
            # El agente procesa la respuesta
            with st.spinner("L'agent està pensant i analitzant el CSV..."):
                try:
                    respuesta = asistente.invoke({
                        "input": pregunta,
                        "chat_history": st.session_state.historial_conversacion
                    })
                    
                    output_text = respuesta['output']
                    
                    # Mostrar respuesta de la IA con su robot clásico
                    with container_chat:
                        with st.chat_message("assistant"):
                            st.write(output_text)
                    
                    # Guardar en memoria de sesión
                    st.session_state.historial_conversacion.append(HumanMessage(content=pregunta))
                    st.session_state.historial_conversacion.append(AIMessage(content=output_text))
                    
                    if len(st.session_state.historial_conversacion) > 6:
                        st.session_state.historial_conversacion = st.session_state.historial_conversacion[-6:]
                    
                    # Forzar recarga rápida de la web para mover el mapa si la tool se activó
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al processar: {e}")

    # --- COLUMNA 2: EL MAPA INTERACTIVO (Folium) ---
    with col2:
        st.subheader("📍 Geolocalització en temps real")
        st.info(f"Mostrant: **{st.session_state.coordenadas_mapa['nombre']}**")
        
        # Creamos el mapa usando la librería Folium
        m = folium.Map(
            location=[st.session_state.coordenadas_mapa["lat"], st.session_state.coordenadas_mapa["lon"]], 
            zoom_start=st.session_state.coordenadas_mapa["zoom"]
        )
        
        # Añadimos un marcador (Pin) si no es la ubicación por defecto de Barcelona
        if st.session_state.coordenadas_mapa["nombre"] != "Barcelona":
            folium.Marker(
                [st.session_state.coordenadas_mapa["lat"], st.session_state.coordenadas_mapa["lon"]],
                popup=st.session_state.coordenadas_mapa["nombre"],
                tooltip=st.session_state.coordenadas_mapa["nombre"],
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            
        # Dibujamos el mapa interactivo dentro del componente web de Streamlit
        st_folium(m, width="100%", height=500, key="mapa_barcelona")