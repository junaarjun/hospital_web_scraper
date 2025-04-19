import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

class CUFScraper:
    def __init__(self, page):
        self.page = page
        self.base_url = "https://www.cuf.pt/medicos"
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    def wait_for_element_value(self, selector, target_text, timeout=10000):
        start = time.time()
        while True:
            try:
                el = self.page.query_selector(selector)
                if el:
                    current_text = el.inner_text().strip()
                    if current_text == target_text:
                        return False
            except:
                pass

            if (time.time() - start) * 1000 > timeout:
                raise TimeoutError(f"Timeout waiting for {selector} to have text '{target_text}'")
            time.sleep(0.1)


    def apply_pediatrics_filter(self):
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")
        self.page.click("button#onetrust-accept-btn-handler")
        self.page.click(".text-search-placeholder")
        time.sleep(1)
        self.page.fill(".text-search-placeholder", "pediatria")
        time.sleep(1)
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def extract_doctor_data(self):
        page = 1
        amount = 0
        doctors = []
        while True:
            self.page.wait_for_selector("text=Limpar filtros")
            cards = self.page.query_selector_all("div.container-info-doctors")

            for i in range(len(cards)):
                # Ambil ulang semua link setiap loop
                card_links = self.page.query_selector_all("div.container-info-doctors a[href]")
                detail_link = card_links[i].get_attribute("href")
                full_url = f"https://www.cuf.pt{detail_link}"

                try:
                    # Ambil halaman detail dengan requests
                    response = requests.get(full_url, headers=self.headers)
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Doctor's Name
                    name = soup.select_one("h1").get_text(strip=True)

                    # Area de Diferenciação
                    area = "N/A"
                    label = soup.find(string="Áreas de Diferenciação")
                    if label:
                        area = label.find_next("div").get_text(strip=True)

                    # Units
                    unit_divs = soup.select("div.field--name-field-sites .field--item")
                    units = [u.get_text(strip=True) for u in unit_divs] if unit_divs else ["N/A"]

                    doctors.append({
                        "name": name,
                        "area_diferenciacao": area,
                        "unit": "| ".join(units)
                    })
                    amount += 1
                    print(f"✅ {amount} data has bee scrapped")


                except Exception as e:
                    print("❌ Error parsing doctor:", e)

            # Cek apakah ada halaman berikutnya
            next_button = self.page.query_selector("a[rel=next]")
            if next_button:
                next_button.click()
                page += 1
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_selector(f"div.container-info-doctors a[href]:nth-of-type({i})", state="detached")
                self.wait_for_element_value("a[title='Página atual']", str(page))
            else:
                break

        return doctors
    
    def save_doctors_data(self, doctors, filename="doctors_data"):
        df = pd.DataFrame(doctors)

        # Simpan ke CSV
        df.to_csv(f"{filename}.csv", index=False, encoding="utf-8-sig")

        # Simpan ke XLSX
        df.to_excel(f"{filename}.xlsx", index=False)
        
        print(f"✅ Data berhasil disimpan ke '{filename}.csv' dan '{filename}.xlsx'")
