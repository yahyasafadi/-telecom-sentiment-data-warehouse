import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time, os

def scrape_reviews(url: str, num: int, ville: str, operateur: str, driver) -> list:
    print(f"Chargement : {url}")
    driver.get(url)
    time.sleep(5)
    
    try:
        driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Avis') or .//div[text()='Avis']]").click()
        time.sleep(3)
        
        scrollable_div = driver.execute_script("let a=document.querySelectorAll('div.jJc9Ad'); return a[a.length-1].closest('.m6QErb[tabindex=\"-1\"]');")
        for _ in range(30):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2.5)
    except: return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    reviews = []
    for block in soup.find_all("div", class_="jJc9Ad"):
        name = block.find("div", class_="d4r55")
        comment = block.find("span", class_="wiI7pd")
        date = block.find("span", class_="rsqaWe")
        if name:
            reviews.append({
                "num_agence": num, "Ville": ville, "Name": name.text.strip(),
                "Comment": comment.text.strip() if comment else "Aucun texte",
                "Date": date.text.strip() if date else "N/A"
            })
    return reviews

def extract_reviews_for_operator(operateur: str):
    print(f"--- Extraction des avis pour {operateur} ---")
    csv_path = f"data/raw/{operateur}/data_agences.csv"
    if not os.path.exists(csv_path): return
    
    df_agences = pd.read_csv(csv_path)
    driver = uc.Chrome(version_main=147)
    
    all_reviews = []
    for _, row in df_agences.iterrows():
        all_reviews.extend(scrape_reviews(row["url"], row["num_agence"], row["ville"], operateur, driver))
    
    driver.quit()
    if all_reviews:
        df = pd.DataFrame(all_reviews).drop_duplicates(subset=["Name", "Comment"])
        df.to_csv(f"data/raw/{operateur}/reviews.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    for op in ["IAM", "INWI", "Orange"]:
        extract_reviews_for_operator(op)
