# 🤖 Agent Intel·ligent de Piezòmetres i Pous - Barcelona

Aquest projecte és un **agent de dades intel·ligent** que utilitza Intel·ligència Artificial per respondre preguntes en llenguatge natural i interactuar visualment amb el catàleg de pous i piezòmetres de la ciutat de Barcelona basant-se en les dades d'un fitxer CSV.

## 🛠️ Tecnologies i Entorn de treball

* **Python** (Pandas per a la gestió i cerca de dades en el CSV)
* **Streamlit** (Framework de Python utilitzat per crear la interfície web interactiva i el xat)
* **Folium / Streamlit-Folium** (Llibreries de mapes utilitzades per integrar la geolocalització en temps real dins de la web)
* **LangChain** (per crear l'arquitectura de l'agent i la memòria de la conversa)
* **Groq API** (Model `llama-3.1` com a motor de text gratuït d'alta velocitat)
* **Visual Studio Code** (Entorn de desenvolupament integrat amb entorns virtuals `venv`)
* **GitHub Copilot** (Assistent de IA utilitzat per a la generació i optimització del codi)

## 🧠 Millores de la branca `dev` (Versió Web App)

* **Interfície Gràfica Dual:** S'ha eliminat la terminal negra i s'ha creat una aplicació web moderna dividida en dues columnes: un xat estil ChatGPT a l'esquerra i un mapa interactiu a la dreta.
* **Mapa Interactiu Integrat:** El mapa de Folium està incrustat directament a la web. Quan demanes veure un pou (Ex: "abre pozo 5"), l'agent extreu la latitud/longitud del CSV de forma exacta a través de la columna `Codi_Estacio_ACA` i mou el mapa i el marcador automàticament.
* **Memòria de conversa:** L'assistent manté el fil de la conversa recordant les preguntes anteriors directament a la pantalla.

## 🚀 Com executar el projecte per primera vegada

### 1. Clonar el repositori
```bash
git clone <url-del-teu-repositori>
cd bcn-piezometres-ai

### 2. Crear i activar l'entorn virtual
Bash
python3 -m venv env
source env/bin/activate

3. Instal·lar les dependències d'un sol cop
(Això instal·larà de forma automàtica Pandas, Streamlit, Folium, LangChain, Groq i les llibreries del sistema).
Bash
pip install -r requirements.txt

4. Configurar les credencials
Crea un fitxer anomenat .env a l'arrel del projecte i afegeix la teva clau de Groq:
Plaintext
GROQ_API_KEY=la_teva_clau_aquí

5. Executar l'aplicació web
(IMPORTANT: Ja no s'utilitza 'python app.py'. El servidor de la interfície gràfica es llança mitjançant Streamlit).
Bash
streamlit run app.py