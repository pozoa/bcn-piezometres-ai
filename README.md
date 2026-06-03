# 🤖 Assistent de Piezòmetres i Pous - Barcelona

Aquest projecte és un **agent de dades intel·ligent** que utilitza Intel·ligència Artificial per respondre preguntes en llenguatge natural sobre el catàleg de pous i piezòmetres de la ciutat de Barcelona.

## 🛠️ Tecnologies utilitzades
* **Python** (Pandas per a la gestió de dades)
* **LangChain** (per crear l'agent de dades)
* **Groq API** (Model `llama-3.1`)

## 🧠 Millores de la branca `dev`
* **Memòria de conversa:** L'assistent recorda el context i les preguntes anteriors.
* **Integració amb Google Maps:** Si li demanes veure un pou al mapa, l'assistent obrirà automàticament el teu navegador Chrome en la ubicació exacta.

## 🚀 Com executar el projecte per primera vegada

1. **Clonar el repositori:**
   ```bash
        git clone <url-del-teu-repositori>
        cd bcn-piezometres-ai

2. **Crear i activar l'entorn virtual**
        python3 -m venv env
        source env/bin/activate

3. Instal·lar les dependències d'un sol cop:
(Això instal·larà de forma automàtica Pandas, LangChain, Groq, Dotenv i Tabulate amb les versions correctes).
        pip install -r requirements.txt

4. Configurar les credencials:
Crea un fitxer .env a l'arrel del projecte i afegeix la teva clau de Groq:
    Plaintext
        GROQ_API_KEY=la_teva_clau_aquí

5.  Executar l'aplicació:
        Bash
        python app.py