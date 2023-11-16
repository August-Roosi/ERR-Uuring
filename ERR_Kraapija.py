import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

class ArtikliKuupäevaObjekt:
    def __init__(self, kuupäev, artiklid=None):
        self.kuupäev = kuupäev
        self.artiklid = artiklid if artiklid is not None else []

    def lisa_artikkel(self, artikkel):
        self.artiklid.append(artikkel)

    def to_dict(self):
        return {'kuupäev': self.kuupäev, 'artiklid': self.artiklid}

def otsi_lingid():
    linkide_elemendid = ülemElement.find_elements(By.TAG_NAME, 'a')

    for lingi_element in linkide_elemendid:
        href = lingi_element.get_attribute("href")
        lingid.append(href)
        print("Lingi HREF:", href)

def artiklite_andmete_väljavõte(hrefs):
    artiklite_andmed = []

    for href in hrefs:
        try:
            vastus = requests.get(href)
            vastus.raise_for_status()  # Viska HTTPError halva vastuse korral

            supp = BeautifulSoup(vastus.text, 'html.parser')

            artikli_päis = supp.find('h1').text.strip()

            teksti_elemendid = supp.find_all(class_="text")
            teksti_sisu_list = [element.get_text(separator='\n') for element in teksti_elemendid]
            artikli_sisu = '\n'.join(teksti_sisu_list)

            artiklite_andmed.append(({'päis': artikli_päis, 'sisu': artikli_sisu}))
        except Exception as e:
            print(f"Viga {href} töödeldes: {e}")
            puuduvateElementidegaArtiklid.append(href)

    return artiklite_andmed

def salvesta_jsoni(artiklite_kuupäeva_objektid):
    andmed = {}

    for artiklite_kuupäeva_objekt in artiklite_kuupäeva_objektid:
        # Teisenda kuupäeva string datetime objektiks
        kuupäev_obj = datetime.strptime(artiklite_kuupäeva_objekt.kuupäev, "%d.%m.%Y")

        # Teisenda artiklite nimekiri JSON-i jaoks sobivamaks vorminguks
        vormindatud_artiklid = [{'päis': artikkel['päis'], 'sisu': artikkel['sisu']} for artikkel in artiklite_kuupäeva_objekt.artiklid]

        # Uuenda sõnaraamatut
        andmed.setdefault(str(kuupäev_obj.year), {}).setdefault(str(kuupäev_obj.month), {})[str(kuupäev_obj.day)] = vormindatud_artiklid

    # Teisenda sõnaraamat JSON stringiks
    json_andmed = json.dumps(andmed, indent=2, ensure_ascii=False)

    # Kirjuta JSON string faili
    failinimi = f"ERR_Artiklid.json"
    with open(failinimi, 'w', encoding="utf-8") as json_fail:
        json_fail.write(json_andmed)


juht = webdriver.Chrome()

juht.get("https://www.err.ee/uudised")

eelmine_päeva_nupp = juht.find_element(By.XPATH, "//button[@class='btn round history-btn' and text()='Eelmine päev']")
artikliteObjektid = []
puuduvateElementidegaArtiklid = []
sügavus = 0

while eelmine_päeva_nupp.is_displayed():
    eelmine_päeva_nupp.click()
    time.sleep(1)

    ülemElemendid = juht.find_elements(By.XPATH, "//*[@id=\"ng-app\"]/body/div[1]/div[4]/div/div[1]/div[3]")
    lingid = []

    for ülemElement in ülemElemendid:
        otsi_lingid()
        time.sleep(1)
        
    time.sleep(1)
    kuupäev = juht.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[1]/div[3]/h4").get_attribute("innerHTML")
    artiklite_sisud = artiklite_andmete_väljavõte(lingid)
    artikliteObjektid.append(ArtikliKuupäevaObjekt(kuupäev, artiklite_sisud))
    print("\n"+kuupäev+"\n")
    if (sügavus == 1):
        break
    sügavus += 1

salvesta_jsoni(artikliteObjektid)

juht.quit()
