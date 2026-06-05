# 🤖 Assistent de Piezòmetres i Pous - Barcelona

Aquest projecte és un **agent de dades intel·ligent** que utilitza Intel·ligència Artificial per respondre preguntes en llenguatge natural sobre el catàleg de pous i piezòmetres de la ciutat de Barcelona.

## 🛠️ Tecnologies utilitzades

* **Python** (Pandas per a la gestió i cerca de dades en el CSV)
* **LangChain** (per crear l'arquitectura de l'agent i la memòria)
* **Groq API** (Model `llama-3.1` com a motor de text)
* **Visual Studio Code** (Entorn de desenvolupament integrat amb entorns virtuals `venv`)
* **GitHub Copilot** (Asstistent de IA utilitzat per a la generació i optimització del codi)

## 🧠 Millores de la branca `dev`
* **Memòria de conversa:** L'assistent recorda el context i les preguntes anteriors.
* **Integració amb Google Maps:** Si li demanes veure un pou al mapa, l'assistent obrirà automàticament el teu navegador Chrome en la ubicació exacta.
* **Cerca exacta per CSV:** L'agent creua les teves peticions (Ex: "abre pozo 5") directament amb la columna `Codi_Estacio_ACA`, extreu la latitud/longitud d'aquest fitxer i mapifica el resultat.
* **Memòria de conversa:** L'assistent recorda el context i les preguntes anteriors.
* **Integració amb Google Maps:** Obre automàticament el navegador Chrome en la ubicació exacta del pou detectat.


## 🚀 Com executar el projecte per primera vegada

<<<<<<< HEAD
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
=======
### 1. Clonar el repositori
```bash
git clone <url-del-teu-repositori>
cd bcn-piezometres-ai

2. Crear i activar l'entorn virtual
Bash
python3 -m venv env
source env/bin/activate

3. Instal·lar les dependències d'un sol cop
(Això instal·larà de forma automàtica Pandas, LangChain, Groq, Dotenv i Tabulate amb les versions correctes).

Bash
pip install -r requirements.txt

4. Configurar les credencials
Crea un fitxer anomenat .env a l'arrel del projecte i afegeix la teva clau de Groq:

Plaintext
GROQ_API_KEY=la_teva_clau_aquí

5. Executar l'aplicació
Bash
python app.py
>>>>>>> dev
