# Bakalářská práce - FIT VUT
## **Strojové učení pro odpovídání na otázky v přirozeném jazyce**

**Student**: Jonáš Sasín (xsasin05)  
**Vedoucí práce**: doc. RNDr. Pavel Smrž, Ph.D.  

"Navrhněte a realizujte systém, který s využitím existujících implementací dokáže  
odpovídat na otázky nad českou wikipedií, případně nad doplňkovými zdroji informací."

### Potřebné Python knihovny
Potřebné knihovny jsou uvedeny v souboru /web_server/requirements.txt nebo  
v Jupyter notebooku /notebooks/question_answering.ipynb .  
(Pro experimenty v notebooku je potřeba více knihoven, než pro spuštění serveru.)  

### Spuštění serveru pro demo-aplikaci
V adresáři web_server použít příkaz:
 * python3 server.py 

Server se spouští defaultně na localhost a portu 4321.  
Pro úpravu (spuštění na jiném portu/hostname) je potřeba přepsat konfiguraci v souboru server.py  


Při prvním spuštění je potřeba stáhnout deeppavlov NER model.  
Pro vyhnutí se stahování je potřeba v souboru QA_responder.py, metodě __init__() přepsat parametr  
pro inicializaci Retrieveru na *download_ner_mode=False*. Ve stejné metodě je nastavena cesta k datům  
potřebným pro běh aplikace. Ty je v případě potřeby možné také přepsat.


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
 * czech-morfflex-morphodita - soubory pro analyzátor morphodita
 * abstracts_index.pkl - index abstraktů pro načtení přes pickle
 * wiki_abstracts_processed - zpracované abstrakty pro tvorbu indexu
 * wiki_titles - soubor s titulky článku 

/notebooks
 * question_answering.ipynb 
 * mbert_czech_squad_fine-tuning.ipynb 
 * albert_squad_fine-tuning.ipynb
 * czech_squad.py
 * czech_squad2.py

/source_tex
 * soubory latexu pro překlad odevzdaného pdf

/web_server
 * server.py
 * requirements.txt
 * /app
   - /api - json schémata
   - __init.py__
   - app.py - inicializace Flask serveru
   - routes.py - dostupné služby serveru 
   - reader.py
   - retriever.py
   - QA_responder - třída pro inicializaci systému pro odpovídání

poster.pdf - plakát prezentující výsledky  
README - tento soubor   
thesis.pdf - práce v pdf pro odevzdání do wis  
thesis_print.pdf - práce určená pro tisk  




