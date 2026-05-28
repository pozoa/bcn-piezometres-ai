import os
import pandas as pd
import webbrowser  # <-- LIBRERÍA NATIVA PARA ABRIR EL NAVEGADOR
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.messages import AIMessage, HumanMessage
# IMPORTAMOS EL DECORADOR PARA CREAR HERRAMIENTAS
from langchain_core.tools import tool

# Cargar variables de entorno del archivo .env
load_dotenv()

# 1. DEFINIMOS LA NUEVA HERRAMIENTA PERSONALIZADA
@tool
def obrir_en_google_maps(latitud: float, longitud: float) -> str:
    """
    Obre el navegador web amb la ubicació exacta a Google Maps utilitzant la latitud i longitud proporcionades.
    Utilitza aquesta eina quan l'usuari demani explícitament 'veure', 'obrir' o 'mostrar' la ubicació d'un pou al mapa.
    """
    try:
        # Creamos la URL pública de Google Maps con las coordenadas
        url = f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"
        
        # Intentamos forzar la apertura específicamente en Chrome (opcional, si no, abrirá el predeterminado)
        # En la mayoría de sistemas Linux/Ubuntu, 'google-chrome' o el navegador por defecto funcionará directo:
        webbrowser.open(url)
        
        return f"S'ha obert correctament Google Maps amb les coordenades {latitud}, {longitud}."
    except Exception as e:
        return f"No s'ha pogut obrir el navegador: {e}"


def iniciar_asistente_ia(archivo_csv):
    try:
        df = pd.read_csv(archivo_csv)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

    # Configurar el modelo de IA Gratuito de Groq
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # PASSEM LA NOVA EINA AL VECTOR  D'extra_tools
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True, 
        agent_type="tool-calling", 
        allow_dangerous_code=True,
        extra_tools=[obrir_en_google_maps], # <-- AQUÍ LE DAMOS EL NUEVO PODER AL AGENTE
        prefix=(
            "Ets un assistent expert en els pous de Barcelona. Respon sempre en català de forma educada i clara. "
            "Si l'usuari et demana veure o mostrar un pou al mapa o al navegador, busca la seva latitud i longitud al DataFrame "
            "i executa l'eina 'obrir_en_google_maps'. No t'inventis les coordenades, usa les del fitxer."
        )
    )
    return agent

if __name__ == "__main__":
    archivo = "piezometres_equipaments.csv"
    
    print("🤖 Inicializando el Asistente de IA con Mapas Integrados...")
    asistente = iniciar_asistente_ia(archivo)
    
    if asistente:
        print("\n✅ ¡Asistente listo! Ahora puedes pedirle que te muestre los pozos en el mapa.")
        print("Ejemplo: 'Muéstrame en el mapa el pou con ID X' o 'Abre el mapa para el pozo de Sants'.")
        print("Escribe 'salir' para terminar.\n")
        
        historial_conversacion = []
        
        while True:
            pregunta = input("Pregunta a tus datos: ")
            if pregunta.lower() == 'salir':
                print("¡Hasta luego!")
                break
                
            if pregunta.strip() == "":
                continue
                
            try:
                respuesta = asistente.invoke({
                    "input": pregunta,
                    "chat_history": historial_conversacion
                })
                
                print(f"\n🤖 IA (Groq): {respuesta['output']}\n")
                
                historial_conversacion.append(HumanMessage(content=pregunta))
                historial_conversacion.append(AIMessage(content=respuesta['output']))
                
                if len(historial_conversacion) > 6:
                    historial_conversacion = historial_conversacion[-6:]
                    
            except Exception as e:
                print(f"\n❌ Error al procesar: {e}\n")