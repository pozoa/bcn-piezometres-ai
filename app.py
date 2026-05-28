import os
import pandas as pd
from dotenv import load_dotenv
# Cambiamos el conector de OpenAI por el de Groq
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Cargar variables de entorno del archivo .env
load_dotenv()

def iniciar_asistente_ia(archivo_csv):
    try:
        df = pd.read_csv(archivo_csv)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

    # Configurar el modelo de IA Gratuito de Groq (Llama 3 es inteligentísimo)
    # Forzamos la lectura de la API Key desde el archivo .env usando os.getenv
    llm = ChatGroq(
        model="llama-3.1-8b-instant",  # <-- Cambiamos este nombre aquí
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # Crear el agente que conectará la IA con tu CSV
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True, 
        agent_type="tool-calling", # Tipo de agente optimizado para Groq
        allow_dangerous_code=True 
    )
    return agent

if __name__ == "__main__":
    archivo = "piezometres_equipaments.csv"
    
    print("🤖 Inicializando el Asistente de IA GRATUITO con Groq...")
    asistente = iniciar_asistente_ia(archivo)
    
    if asistente:
        print("\n✅ ¡Asistente listo y GRATIS! Ya puedes preguntar sobre los pozos de Barcelona.")
        print("Escribe 'salir' para terminar.\n")
        
        while True:
            pregunta = input("Pregunta a tus datos: ")
            if pregunta.lower() == 'salir':
                print("¡Hasta luego!")
                break
                
            if pregunta.strip() == "":
                continue
                
            try:
                # El agente procesa la pregunta
                respuesta = asistente.invoke({"input": pregunta})
                print(f"\n🤖 IA (Groq): {respuesta['output']}\n")
            except Exception as e:
                print(f"\n❌ Error al procesar: {e}\n")