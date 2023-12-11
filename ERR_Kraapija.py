import json
import time
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

# Klass artiklite kuupäeva objekti esindamiseks
class ArtikliKuupäevaObjekt:
    def __init__(self, kuupäev, artiklid=None):
        self.kuupäev = kuupäev
        self.artiklid = artiklid if artiklid is not None else []

    def lisa_artikkel(self, artikkel):
        self.artiklid.append(artikkel)

    def to_dict(self):
        return {'kuupäev': self.kuupäev, 'artiklid': self.artiklid}

# Funktsioon lingi elementide otsimiseks
def otsi_lingid(ülemElement):
    linkide_elemendid = ülemElement.find_elements(By.TAG_NAME, 'a')
    lingid = []
    
    for lingi_element in linkide_elemendid:
        try:
            href = lingi_element.get_attribute("href")
            lingid.append(href)
        except:
            print("Stale element encountered.")

    return lingid

# Funktsioon artiklite andmete väljavõtmiseks
def artiklite_andmete_väljavõte(hrefs):
    artiklite_andmed = []

    def päring_artiklile(href):
        try:
            # Tee päring artikli URL-ile
            vastus = requests.get(href, headers={"User-Agent": "Mozilla/5.0"})
            vastus.raise_for_status()

            # Kasuta BeautifulSoup andmete analüüsimiseks
            supp = BeautifulSoup(vastus.text, 'html.parser')

            # Võta artikli pealkiri
            artikli_päis = supp.find('h1').text.strip()

            # Võta artikli teksti elemendid
            teksti_elemendid = supp.find_all(class_="text")
            # Võta teksti elementide sisu listiks
            teksti_sisu_list = [element.get_text(separator='\n') for element in teksti_elemendid]
            # Ühenda teksti sisu
            artikli_sisu = '\n'.join(teksti_sisu_list)
            
            # Tagasta artikli andmed sõnena
            return {'päis': artikli_päis, 'sisu': artikli_sisu}
        except Exception as e:
            # Käitle erandeid ja lisa vead puuduvate elementide listi
            print(f"Viga {href} töödeldes: {e}")
            puuduvateElementidegaArtiklid.append(href)
            return None

    # Kasuta mitmiklõngade täitmiseks ThreadPoolExecutorit
    with ThreadPoolExecutor() as executor:
        artiklite_andmed = list(executor.map(päring_artiklile, hrefs))
        
    # Eemalda None-väärtustega artiklid
    artiklite_andmed = [artikkel for artikkel in artiklite_andmed if artikkel is not None]
    return artiklite_andmed

# Funktsioon JSON faili salvestamiseks
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

# Looge Chrome WebDriveri eksemplar
juht = webdriver.Chrome()

# Ava ERR uudiste veebileht
juht.get("https://www.err.ee/uudised")

# Leidke kuupäeva sisestamise sisestusväli
input_xpath = "/html/body/div[1]/div[4]/div/div[1]/div[1]/div[2]/input"
input_field = juht.find_element(By.XPATH, input_xpath)

# Puhasta sisestusväli ja sisesta soovitud alguskuupäev
input_field.clear()
desired_start_date = "01.01.2017"
input_field.send_keys(desired_start_date)
input_field.send_keys(Keys.RETURN)

# Leidke "Eelmine päev" nupp
eelmine_päeva_nupp = juht.find_element(By.XPATH, "//button[@class='btn round history-btn' and text()='Eelmine päev']")

# Initsialiseerige list artiklite objektide jaoks
artikliteObjektid = []

# List puuduvate elementidega artiklite jaoks
puuduvateElementidegaArtiklid = []

# Initsialiseerige sügavus
sügavus = 0

try:
    start_time = time.time()
    while eelmine_päeva_nupp.is_displayed():
        # Etapp 1: Kogu linkide andmed
        etapp1_start = time.time()
        eelmine_päeva_nupp.click()
        time.sleep(1)
        ülemElemendid = juht.find_elements(By.XPATH, "//*[@id=\"ng-app\"]/body/div[1]/div[4]/div/div[1]/div[3]")
        lingid = otsi_lingid(ülemElemendid[0])
        time.sleep(1)
        etapp1_end = time.time()

        # Etapp 2: Kogu artiklite andmed
        etapp2_start = time.time()
        kuupäev = juht.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div[1]/div[3]/h4").get_attribute("innerHTML")
        artiklite_sisud = artiklite_andmete_väljavõte(lingid)
        etapp2_end = time.time()

        # Etapp 3: Kogu artiklite objektid
        etapp3_start = time.time()
        artikliteObjektid.append(ArtikliKuupäevaObjekt(kuupäev, artiklite_sisud))
        etapp3_end = time.time()

        # Väljasta kuupäev ja etappide kestused
        print("\n" + kuupäev + "\n")
        sügavus += 1
        print(f"Etapp 1 kestus: {etapp1_end - etapp1_start} sekundit")
        print(f"Etapp 2 kestus: {etapp2_end - etapp2_start} sekundit")
        print(f"Etapp 3 kestus: {etapp3_end - etapp3_start}")
        if kuupäev == "01.01.2008":
            break
except:
    # Käitle üldine erand ja väljasta teade
    print("Programmil tekkis tõrge, salvestatakse kogutud andmed ning väljastatakse faili.")
finally:
    # Sulgege brauseriaken
    juht.quit()

    # Salvesta kogutud artiklite andmed JSON faili
    salvesta_jsoni(artikliteObjektid)

    # Arvuta ja väljasta koguaeg
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Koguaeg: {total_time} sekundit")
