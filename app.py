import os
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
# IMPORTAMOS LAS HERRAMIENTAS DE MEMORIA CORRESPONDIENTES
from langchain_core.messages import AIMessage, HumanMessage

# Cargar variables de entorno del archivo .env
load_dotenv()

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

    # Crear el agente que conectará la IA con tu CSV.
    # Añadimos un prefijo para obligarle a hablar en catalán/castellano según prefieras y recordarle que use el historial.
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True, 
        agent_type="tool-calling", 
        allow_dangerous_code=True,
        prefix="Ets un assistent expert en els pous de Barcelona. Respon sempre en català de forma educada i clara."
    )
    return agent

if __name__ == "__main__":
    archivo = "piezometres_equipaments.csv"
    
    print("🤖 Inicializando el Asistente de IA GRATUITO con Groq y Memoria...")
    asistente = iniciar_asistente_ia(archivo)
    
    if asistente:
        print("\n✅ ¡Asistente listo y GRATIS! Ya puedes preguntar sobre los pozos de Barcelona.")
        print("Escribe 'salir' para terminar.\n")
        
        # MODIFICACIÓ DE PROVA EN LA BRANCA DEV: Creamos una lista para almacenar el historial de chat
        historial_conversacion = []
        
        while True:
            pregunta = input("Pregunta a tus datos: ")
            if pregunta.lower() == 'salir':
                print("¡Hasta luego!")
                break
                
            if pregunta.strip() == "":
                continue
                
            try:
                # El agente procesa la pregunta pasándole la entrada actual Y el historial acumulado
                respuesta = asistente.invoke({
                    "input": pregunta,
                    "chat_history": historial_conversacion
                })
                
                print(f"\n🤖 IA (Groq): {respuesta['output']}\n")
                
                # Guardamos la pregunta y la respuesta en el historial para la próxima iteración
                historial_conversacion.append(HumanMessage(content=pregunta))
                historial_conversacion.append(AIMessage(content=respuesta['output']))
                
                # Opcional: Para evitar que el historial sea gigante y ralentice la IA, 
                # podemos limitar el historial a las últimas 6 interacciones (3 preguntas y 3 respuestas)
                if len(historial_conversacion) > 6:
                    historial_conversacion = historial_conversacion[-6:]
                    
            except Exception as e:
                print(f"\n❌ Error al procesar: {e}\n")