import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os

class CUFScraper:
    """
    A web scraper for extracting pediatric doctor information from the CUF hospital website.
    Uses Playwright for interaction and requests + BeautifulSoup for scraping detail pages.
    """

    def __init__(self, page):
        """
        Initialize the CUFScraper with a Playwright page instance.
        """
        self.page = page
        self.base_url = "https://www.cuf.pt/medicos"
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    def wait_for_element_value(self, selector, target_text, timeout=10000):
        """
        Waits for a specific selector to match a target inner text.
        """
        start = time.time()
        while True:
            try:
                el = self.page.query_selector(selector)
                if el:
                    current_text = el.inner_text().strip()
                    if current_text == target_text:
                        return True
            except:
                pass

            if (time.time() - start) * 1000 > timeout:
                raise TimeoutError(f"Timeout waiting for {selector} to have text '{target_text}'")
            time.sleep(0.1)

    def apply_pediatrics_filter(self):
        """
        Navigate to the CUF doctors page and apply a filter for 'pediatria'.
        """
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("networkidle")

        # Accept cookies
        self.page.click("button#onetrust-accept-btn-handler", timeout=3000)

        # Search for 'pediatria'
        self.page.click(".text-search-placeholder")
        time.sleep(1)
        self.page.fill(".text-search-placeholder", "pediatria")
        time.sleep(1)
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def collect_doctor_links(self):
        """
        Iterate through all paginated results and collect all doctor profile URLs.

        Returns:
            list: A list of full URLs to doctor detail pages.
        """
        doctor_links = []
        page = 1

        while True:
            print(f"🔎 Collecting links on page {page}...")
            self.page.wait_for_selector("text=Limpar filtros")
            self.page.query_selector_all("div.container-info-doctors")

            cards = self.page.query_selector_all("div.container-info-doctors a[href]")
            for card in cards:
                href = card.get_attribute("href")
                if href and href.startswith("/medicos/"):
                    full_url = f"https://www.cuf.pt{href}"
                    doctor_links.append(full_url)

            # Check for next page
            next_button = self.page.query_selector("a[rel=next]")
            if next_button:
                next_button.click()
                page += 1
                self.page.wait_for_load_state("networkidle")
                self.wait_for_element_value("a[title='Página atual']", str(page))
            else:
                break

        print(f"✅ Total doctor links collected: {len(doctor_links)}")
        print(len(doctor_links))
        return list(set(doctor_links))  # Ensure uniqueness

    def scrape_doctor_details(self, urls):
        """
        Given a list of doctor URLs, fetch and parse each detail page.

        Args:
            urls (list): List of full URLs to doctor detail pages.

        Returns:
            list: List of dictionaries with doctor data.
        """
        doctors = []

        for i, url in enumerate(urls, 1):
            try:
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, "html.parser")

                name = soup.select_one("h1").get_text(strip=True)

                area = "N/A"
                label = soup.find(string="Áreas de Diferenciação")
                if label:
                    area = label.find_next("div").get_text(strip=True)

                unit_divs = soup.select("div.field--name-field-sites .field--item")
                units = [u.get_text(strip=True) for u in unit_divs] if unit_divs else ["N/A"]

                doctors.append({
                    "name": name,
                    "area_diferenciacao": area,
                    "unit": " | ".join(units)
                })

                print(f"✅ [{i}/{len(urls)}] Scraped: {name}")

            except Exception as e:
                print(f"❌ Error parsing {url}: {e}")

        return doctors

    def save_doctors_data(self, doctors, filename="output/doctors_data"):
        """
        Save doctor data to both CSV and Excel formats in the 'output/' directory.
        """
        os.makedirs("output", exist_ok=True)
        df = pd.DataFrame(doctors)

        csv_path = f"{filename}.csv"
        xlsx_path = f"{filename}.xlsx"

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df.to_excel(xlsx_path, index=False)

        print(f"📁 Data saved to:\n  - {csv_path}\n  - {xlsx_path}")
