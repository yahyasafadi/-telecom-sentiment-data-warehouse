import pandas as pd
import time, random, os
from selenium import webdriver
from selenium.webdriver.common.by import By

VILLES = [
    "Casablanca", "Rabat", "Marrakech", "Tanger", "Fès", "Agadir",
    "Kenitra", "Meknès", "Oujda", "Tetouan", "Safi", "El Jadida"
]

def extract_agencies_for_operator(operateur: str):
    print(f"--- Extraction des agences pour {operateur} ---")
    driver = webdriver.Chrome()
    driver.maximize_window()
    results = []

    for ville in VILLES:
        driver.get(f"https://www.google.com/maps/search/{operateur} {ville}")
        time.sleep(5)
        
        try:
            scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
            for _ in range(15):
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(2)
        except:
            pass

        agences = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        for agence in agences:
            try:
                driver.execute_script("arguments[0].click();", agence)
                time.sleep(random.uniform(2, 4))
                results.append({
                    "nom_agence": driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text,
                    "adresse": driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']").text,
                    "ville": ville,
                    "operateur": operateur,
                    "url": driver.current_url
                })
            except:
                continue

    driver.quit()
    
    out_dir = f"data/raw/{operateur}"
    os.makedirs(out_dir, exist_ok=True)
    df = pd.DataFrame(results).drop_duplicates(subset=["url"])
    df.to_csv(f"{out_dir}/data_agences.csv", index=False)
    print(f"Sauvegardé : {len(df)} agences pour {operateur}")

if __name__ == "__main__":
    for op in ["IAM", "INWI", "Orange"]:
        extract_agencies_for_operator(op)
