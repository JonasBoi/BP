# Bakalářská práce - FIT VUT

## **Strojové učení pro odpovídání na otázky v přirozeném jazyce**

**Student**: Jonáš Sasín (xsasin05)\
**Vedoucí práce**: doc. RNDr. Pavel Smrž, Ph.D.

"Navrhněte a realizujte systém, který s využitím existujících implementací dokáže\
odpovídat na otázky nad českou Wikipedií, případně nad doplňkovými zdroji informací."

### Potřebné Python knihovny

Testováno pro verzi Pythonu 3.6.9 (server) a 3.7.10 (experimenty)

Potřebné knihovny jsou uvedeny v souboru /web_server/requirements.txt nebo\
v Jupyter notebooku /notebooks/question_answering.ipynb .\
(Pro experimenty v notebooku je potřeba více knihoven, než pro spuštění serveru.)\
Pro jejich instalaci je tedy možné použít příkaz

* pip3 install -r requirements.txt

Důvod instalace starší verze Tensorflow: knihovna deeppavlov, přesněji model používaný\
pro NER má zastaralé závislosti, které to vyžadují.\
Demonstrační aplikace běží na adrese http://r2d2.fit.vutbr.cz/.cs

**Knihovny:** torch, sentencepiece, transformers, wikipedia, rank_bm25,\
corpy, tensorflow, deeppavlov, Flask, scipy

### Spuštění serveru pro demo-aplikaci

V adresáři web_server použít příkaz:

* python3 server.py

Server se spouští defaultně na localhost a portu 4321.\
Pro úpravu (spuštění na jiném portu/hostname) je potřeba přepsat konfiguraci v souboru server.py

Při prvním spuštění je potřeba stáhnout deeppavlov NER model.\
Pro vyhnutí se stahování je potřeba v souboru QA_responder.py, metodě **init**() přepsat parametr\
pro inicializaci Retrieveru na *download_ner_model=False*. Ve stejné metodě je nastavena cesta k datům\
potřebným pro běh aplikace. Ty je v případě potřeby možné také přepsat.\
Schémata formátů JSON jsou v adresáři /app/api a je v nich možno případně upravit defaultní konfiguraci.

pozn.: Při spuštění serveru bude načtení modelu pro NER vypisovat spoustu warningů, které lze ignorovat a jsou způsobeny out-dated závislostmi modelu.

### Experimenty v notebooku

Přiloženy jsou také notebooky pro trénink modelů, ty jsou z větší části vypůjčeny z notebooků Huggingface.\
Pro trénink jsou přiloženy také skripty pro knihovnu datasets, které načtou českou verzi squad 1.1 a 2.0.

V notebooku question_answering.ipynb by měly být komentáře dostačující pro zopakování většiny experimentů.\
Do běhového prostředí je potřeba doinstalovat knihovny a stáhnout soubory, nebo k nim nastavit adekvátní cestu\
(k souborům, z nichž většina je v adresáři data).

### Odevzdané soubory

/benchmarks

* human_eval_200 - odpovědi, které byly vyhodnoceny ručně
* quarter_sqad_experiments - porovnání všech variant na čtvrtině datasetu
* whole_sqad_evaluation - vyhodnocení nejlepšího systému

/data

* albert_squad_finetuned - natrénovaný albert model (1.1)
* albert_squad2_finetuned - natrénovaný albert model (2.0)
* mbert_finetuned_czech_squad - natrénovaný mbert model (1.1)
* mbert_finetuned_czech_squad2 - natrénovaný mbert model (2.0)
* sqad_processed.json - otázky a odpovědi datasetu sqad bez ano/ne
* abstracts_index.pkl - index abstraktů pro načtení modulem pickle
* wiki_abstracts_processed - zpracované abstrakty pro tvorbu indexu
* wiki_titles - soubor s titulky článku

/notebooks

* question_answering.ipynb
  * experimenty a vyhodnocení modelu, zpracování dat
* mbert_czech_squad_fine-tuning.ipynb
  * natrénování vícejazyčného modelu bert
* albert_squad_fine-tuning.ipynb
  * natrénování anglického modelu albert
* czech_squad.py a czech_squad2.py
  * skripty pro knihovnu huggingface - datasets pro načtení českého překladu squad 1.1/2.0

/source_tex

* soubory latexu pro překlad odevzdaného pdf - lze přeložit pomocí příkazu make

/web_server

* server.py
* requirements.txt
* /app
  * /api - json schémata
  * **init.py**
  * app.py - inicializace Flask serveru
  * routes.py - dostupné služby serveru
  * reader.py
  * retriever.py
  * QA_responder - třída pro inicializaci systému pro odpovídání

poster.pdf - plakát prezentující výsledky\
README.md - tento soubor\
thesis.pdf - práce v pdf pro odevzdání do wis\
thesis_print.pdf - práce určená pro tisk