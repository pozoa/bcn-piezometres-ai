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
        df = pd.read_csv(ARCHIVO_CSV)
        # Limpieza inicial para asegurar que los strings no tengan espacios ocultos
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error al carregar el fitxer de dades ({ARCHIVO_CSV}): {e}")
        return None

df_global = cargar_datos()

# 2. Inicializar Estados de la Sesión en Streamlit (Memoria visual)
if "historial_conversacion" not in st.session_state:
    st.session_state.historial_conversacion = []

if "coordenadas_mapa" not in st.session_state:
    # Coordenadas por defecto (Centro de Barcelona)
    st.session_state.coordenadas_mapa = {"lat": 41.3851, "lon": 2.1734, "zoom": 12, "nombre": "Barcelona"}

# 3. HERRAMIENTA VINCULANTE PARA EL MAPA
@tool
def actualizar_mapa_interactivo(codi_aca: str) -> str:
    """
    Actualitza el mapa integrat a la pantalla amb la ubicació del pou utilitzant el text o número exacte de 'Codi_Estacio_ACA'.
    S'ha d'utilitzar ÚNICAMENT quan l'usuari demani explícitament veure o localitzar un pou concret (Ex: 'Codi_Estacio_ACA 5', 'veure el pou 22').
    NO s'ha d'utilitzar per llistats, recomptes o consultes generals.
    """
    if df_global is None:
        return "Error: La base de dades no està disponible."
    
    try:
        codi_cercat = str(codi_aca).strip()
        
        # Buscar coincidencia exacta en la columna Codi_Estacio_ACA
        fila = df_global[df_global['Codi_Estacio_ACA'].astype(str) == codi_cercat]
        
        # Si falla, buscar coincidencia parcial
        if fila.empty:
            fila = df_global[df_global['Codi_Estacio_ACA'].astype(str).str.contains(codi_cercat, case=False, na=False)]
            
        if fila.empty:
            return f"No s'ha trobat cap registre que coincideixi exactament amb el Codi_Estacio_ACA: '{codi_cercat}' al CSV."
        
        latitud = float(fila.iloc[0]['Latitud'])
        longitud = float(fila.iloc[0]['Longitud'])
        nom_estacio = fila.iloc[0].get('Nom_Estacio', f"Pou {codi_cercat}")
        
        st.session_state.coordenadas_mapa = {
            "lat": latitud,
            "lon": longitud,
            "zoom": 16,
            "nombre": f"{nom_estacio} (ACA: {codi_cercat})"
        }
        
        return f"S'ha mogut el mapa correctament al pou {nom_estacio} (Codi ACA: {codi_cercat})."
    except Exception as e:
        return f"Error al processar el mapa: {e}"

# 4. CONFIGURACIÓN DEL AGENTE ULTRA-ESTRICTO CON EL CSV
def obtener_agente():
    if df_global is None or not os.getenv("GROQ_API_KEY"):
        return None
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,  # Temperatura 0 para evitar alucinaciones e inventos
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Prefix reforzado para forzar el uso de código Pandas real sobre las columnas del CSV
    prefix_estricto = (
        "Ets un agent de dades connectat directament al fitxer CSV 'piezometres_equipaments.csv'.\n"
        "La teva única font de veritat són les dades d'aquest DataFrame. Està prohibit inventar dades, llistats o coordenades.\n\n"
        "INSTRUCCIONS DE LOGICA CRÍTIQUES:\n"
        "1. Si l'usuari et pregunta per una columna com 'Codi_Estacio_ACA', 'Nom_Estacio', 'Districte' o qualsevol altra, "
        "executa SEMPRE codi Python (Ex: `df['Codi_Estacio_ACA'].unique()`) per extreure els valors reals exactes del fitxer.\n"
        "2. Si l'usuari et demana directament veure, mostrar o obrir un codi específic al mapa (Ex: 'Codi_Estacio_ACA 5' o 'veure pou 12'), "
        "identifica primer el valor alfanumèric i crida immediatament l'eina 'actualizar_mapa_interactivo' passant-li exclusivamente aquest codi.\n"
        "3. Per a qualsevol consulta que demani quantitats, recomptes per districte o llistats d'identificadors, NO cridis l'eina del mapa; "
        "executa codi Pandas (`value_counts()`, `groupby()`, etc.) i respon amb les dades textues en català.\n"
        "Respon sempre de forma clara, professional i estrictament basat en el resultat de l'execució del teu codi."
    )
    
    return create_pandas_dataframe_agent(
        llm,
        df_global,
        verbose=True, 
        agent_type="tool-calling", 
        allow_dangerous_code=True,
        extra_tools=[actualizar_mapa_interactivo],
        prefix=prefix_estricto
    )

asistente = obtener_agente()

# ==============================================================================
# 5. DISEÑO DE LA INTERFAZ GRÁFICA MEJORADA
# ==============================================================================
st.title("🤖 Agent de Dades de Pous de Barcelona")

if not os.getenv("GROQ_API_KEY"):
    st.error("🔑 Falta la clau GROQ_API_KEY al fitxer .env")
else:
    # --- BARRA LATERAL: ENTRADAS VINCULANTES Y GUÍA DE PROMPTS ---
    with st.sidebar:
        st.header("📋 Prompts d'Exemple Vinculants")
        st.markdown(
            "Copia i enganxa aquests exemples exactes al xat per interactuar amb les columnes reals del teu CSV:"
        )
        
        # Sugerencias formateadas con las columnas del CSV para copiar fácilmente
        st.info("**Consulta de columnes i codis:**\n`Dona'm tots els codis de la columna Codi_Estacio_ACA`")
        st.info("**Cerca per identificador:**\n`Codi_Estacio_ACA 5` o `Muestra el Codi_Estacio_ACA 10`")
        st.info("**Estadística vinculada:**\n`Quants pous hi ha per cada Districte?`")
        st.info("**Consulta de dades generals:**\n`Quines columnes té aquest fitxer CSV?`")
        
        if st.button("🔄 Netejar historial de xat"):
            st.session_state.historial_conversacion = []
            st.session_state.coordenadas_mapa = {"lat": 41.3851, "lon": 2.1734, "zoom": 12, "nombre": "Barcelona"}
            st.rerun()

    # Diseño de doble columna para la aplicación web principal
    col1, col2 = st.columns([7, 5])
    
    # --- COLUMNA 1: EL CHAT ---
    with col1:
        st.subheader("💬 Consulta interactiva al CSV")
        
        container_chat = st.container(height=550)
        with container_chat:
            for msg in st.session_state.historial_conversacion:
                if isinstance(msg, HumanMessage):
                    with st.chat_message("user", avatar="🟢"):
                        st.write(msg.content)
                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.write(msg.content)
        
        # El chat input interactúa con las reglas estrictas del agente
        if pregunta := st.chat_input("Escriu aquí (Ex: 'Dona'm tots els codis de la columna Codi_Estacio_ACA')"):
            with container_chat:
                with st.chat_message("user", avatar="🟢"):
                    st.write(pregunta)
            
            with st.spinner("L'agent està executant codi sobre el CSV..."):
                try:
                    respuesta = asistente.invoke({
                        "input": pregunta,
                        "chat_history": st.session_state.historial_conversacion
                    })
                    
                    output_text = respuesta['output']
                    
                    with container_chat:
                        with st.chat_message("assistant"):
                            st.write(output_text)
                    
                    st.session_state.historial_conversacion.append(HumanMessage(content=pregunta))
                    st.session_state.historial_conversacion.append(AIMessage(content=output_text))
                    
                    if len(st.session_state.historial_conversacion) > 8:
                        st.session_state.historial_conversacion = st.session_state.historial_conversacion[-8:]
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error de lògica en processar la petició: {e}")

    # --- COLUMNA 2: EL MAPA INTERACTIVO (Folium) ---
    with col2:
        st.subheader("📍 Visualització Dinàmica (Folium)")
        st.success(f"📍 Marcador actual: **{st.session_state.coordenadas_mapa['nombre']}**")
        
        m = folium.Map(
            location=[st.session_state.coordenadas_mapa["lat"], st.session_state.coordenadas_mapa["lon"]], 
            zoom_start=st.session_state.coordenadas_mapa["zoom"]
        )
        
        if st.session_state.coordenadas_mapa["nombre"] != "Barcelona":
            folium.Marker(
                [st.session_state.coordenadas_mapa["lat"], st.session_state.coordenadas_mapa["lon"]],
                popup=st.session_state.coordenadas_mapa["nombre"],
                tooltip=st.session_state.coordenadas_mapa["nombre"],
                icon=folium.Icon(color="red", icon="cloud")
            ).add_to(m)
            
        st_folium(m, width="100%", height=500, key="mapa_barcelona_interactiu")