import os
import pandas as pd
import webbrowser  # LIBRERÍA NATIVA PARA ABRIR EL NAVEGADOR
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

# Cargar variables de entorno del archivo .env
load_dotenv()

# Arxiu de dades global
ARCHIVO_CSV = "piezometres_equipaments.csv"

try:
    # Carreguem el DataFrame globalment perquè tant l'agent com la Tool puguin accedir-hi
    df_global = pd.read_csv(ARCHIVO_CSV)
except Exception as e:
    print(f"❌ Error crític al carregar el fitxer de dades: {e}")
    df_global = None


# 1. DEFINIMOS LA NUEVA HERRAMIENTA PERSONALIZADA MEJORADA
@tool
def obrir_mapa_per_codi_aca(codi_aca: str) -> str:
    """
    Obre el navegador web amb Google Maps a la ubicació exacta del pou utilitzant el seu codi 'Codi_Estacio_ACA'.
    S'ha d'utilitzar SEMPRE que l'usuari demani obrir, veure, localitzar o mostrar un pou o piezòmetre específic al mapa (Ex: 'abre pozo 5', 'veure el pou 22').
    L'argument ha de ser el codi numèric o de text que correspon a la columna Codi_Estacio_ACA.
    """
    if df_global is None:
        return "Error: La base de dades de pous no està disponible."
    
    try:
        # Netegem l'input per evitar espais en blanc i extreure només el text net
        codi_cercat = str(codi_aca).strip()
        
        # Si la IA envia text com "pozo 5", intentem extreure només el número o la referència neta
        if "pozo" in codi_cercat.lower():
            codi_cercat = codi_cercat.lower().replace("pozo", "").strip()
        if "pou" in codi_cercat.lower():
            codi_cercat = codi_cercat.lower().replace("pou", "").strip()

        # Busquem exactament la fila a la columna corresponent convertint a text per seguretat
        fila = df_global[df_global['Codi_Estacio_ACA'].astype(str).str.strip() == codi_cercat]
        
        # Si no es troba exactament pel codi, fem una cerca parcial (per si de cas)
        if fila.empty:
            fila = df_global[df_global['Codi_Estacio_ACA'].astype(str).str.contains(codi_cercat, case=False, na=False)]
            
        if fila.empty:
            return f"No s'ha trobat cap pou o estació que coincideixi amb el codi Codi_Estacio_ACA: '{codi_cercat}' dins del CSV."
        
        # Extraiem les coordenades de la primera fila que coincideixi
        latitud = fila.iloc[0]['Latitud']
        longitud = fila.iloc[0]['Longitud']
        nom_estacio = fila.iloc[0].get('Nom_Estacio', codi_cercat)
        
        # Construïm la URL pública de Google Maps amb les coordenades reals extretes del CSV
        url = f"http://maps.google.com/?q={latitud},{longitud}"
        
        # Obrim el navegador web predeterminat
        webbrowser.open(url)
        
        return f"S'ha obert correctament Google Maps per al pou {nom_estacio} (Codi ACA: {codi_cercat}) a les coordenades: {latitud}, {longitud}."
    except Exception as e:
        return f"No s'ha pogut obrir el navegador o processar les dades: {e}"


def iniciar_asistente_ia():
    if df_global is None:
        return None

    # Configurar el modelo de IA Gratuito de Groq
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    # PASSEM LA NOVA EINA AL VECTOR D'extra_tools I CONFIGUREM EL PREFIX AGÈNTIC
    agent = create_pandas_dataframe_agent(
        llm,
        df_global,
        verbose=True, 
        agent_type="tool-calling", 
        allow_dangerous_code=True,
        extra_tools=[obrir_mapa_per_codi_aca], # <-- Li donem el nou poder basat en el CSV
        prefix=(
            "Ets un assistent expert i un agent de dades per als pous de Barcelona. Respon sempre en català de forma educada i clara. "
            "Totes les teves respostes han d'estar basades estrictament en la informació que trobis al fitxer CSV. "
            "Si l'usuari et demana veure, obrir o mostrar un pou al mapa (Ex: 'abre pozo 5'), primer identifica quin és el seu "
            "identificador a la columna 'Codi_Estacio_ACA' de la taula. Un cop el tinguis, crida immediatament a l'eina "
            "'obrir_mapa_per_codi_aca' passant-li únicament aquest codi com a paràmetre. No intentis obrir el mapa pel teu compte ni inventis coordenades."
        )
    )
    return agent

if __name__ == "__main__":
    print("🤖 Inicialitzant l'Agent d'IA amb Cerca de Mapes per CSV...")
    asistente = iniciar_asistente_ia()
    
    if asistente:
        print("\n✅ Agent d'IA Actiu! Ara respondrà basant-se en les dades del teu CSV.")
        print("Prova ordres com: 'abre el pozo 5', 'on està el pou amb codi 12?' o demana estadístiques de les columnes.")
        print("Escriu 'salir' per acabar el xat.\n")
        
        historial_conversacion = []
        
        while True:
            pregunta = input("Pregunta a teves dades: ")
            if pregunta.lower() == 'salir':
                print("Fins aviat!")
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
                print(f"\n❌ Error al processar la petició: {e}\n")