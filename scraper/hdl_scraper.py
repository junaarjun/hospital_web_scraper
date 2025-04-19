import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

class HDLScraper:
    """
    A scraper for extracting doctor information from Hospital da Luz's website
    using Playwright for interaction and BeautifulSoup for parsing.
    """

    def __init__(self, page):
        """
        Initialize the scraper with a Playwright page object.
        """
        self.page = page
        self.base_url = "https://www.hospitaldaluz.pt"
        self.search_url = f"{self.base_url}/pt/encontre-um-medico"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.session = requests.Session()
        self.cookies = {}
        self.num_pages = 0

    def apply_speciality_filters(self):
        """
        Apply filters for pediatric specialties using Playwright,
        then extract the filtered URL and session cookies.
        """
        self.page.goto(self.search_url)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Accept cookies popup if it appears
        try:
            self.page.click("button.button.outline.small", timeout=3000)
        except:
            pass

        # Type "pediatria" in the "Especialidades" filter input
        self.page.click("//h3[contains(text(),'Especialidades')]/ancestor::div[@class='form-field filter-options-wrapper filter-header-wrapper']//input")
        self.page.fill("//h3[contains(text(),'Especialidades')]/ancestor::div[@class='form-field filter-options-wrapper filter-header-wrapper']//input", "pediatria")
        time.sleep(1)

        # Click the required specialty checkboxes
        filters = ["Neuropediatria", "Pediatria", "Pediatria-do-Desenvolvimento"]
        for spec in filters:
            self.page.click(f"label[for={spec}]")
            time.sleep(0.5)

        # Wait until results are fully loaded
        self.page.wait_for_selector("img.loading-icon", state="detached", timeout=10000)
        self.page.wait_for_selector(".medic-card", timeout=10000)

        # Capture the filtered URL
        current_url = self.page.url
        print(f"📌 Filtered URL: {current_url}")

        # Extract the number of pages from pagination element
        self.num_pages = self.page.locator("nav.search-pagination li:nth-last-child(2) a").inner_text()

        # Extract cookies from the browser context
        context = self.page.context
        cookies = context.cookies()
        self.cookies = {cookie['name']: cookie['value'] for cookie in cookies}

        return current_url

    def extract_doctor_list_and_details(self, filtered_url):
        """
        Scrape all doctor cards and follow each card's link
        to extract detailed doctor information.
        """
        doctors_data = []

        for page_num in range(1, int(self.num_pages) + 1):
            page_url = f"{filtered_url}?page={page_num}"
            print(f"🔄 Fetching page {page_num}: {page_url}")

            self.page.goto(page_url)
            self.page.wait_for_selector(".medic-card", timeout=10000)
            time.sleep(1)

            html = self.page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".medic-card")

            if not cards:
                print("⚠️ No .medic-card elements found on this page.")
                break

            for card in cards:
                link = card.find("a", href=True)
                if link:
                    detail_url = self.base_url + link['href']
                    doctor_data = self.extract_doctor_detail(detail_url)
                    if doctor_data:
                        doctors_data.append(doctor_data)
                        print(f"✅ Successfully fetched data for {doctor_data['name']}")

        return doctors_data

    def extract_doctor_detail(self, url):
        """
        Visit the doctor's detail page and extract their information.
        """
        try:
            self.page.goto(url)
            self.page.wait_for_selector("h2.medic-name", timeout=10000)

            html = self.page.content()
            soup = BeautifulSoup(html, "html.parser")

            name = soup.select_one("h2.medic-name").get_text(strip=True)

            units = soup.select("p.medic-hospitals a")
            unit_list = [u.get_text(strip=True) for u in units] if units else ["N/A"]

            ordem = soup.select_one("p.medic-order span")
            ordem_num = ordem.get_text(strip=True) if ordem else "N/A"

            specialties = soup.select("ul.medic-specialities-list li")
            specialty_list = [s.get_text(strip=True) for s in specialties] if specialties else ["N/A"]

            return {
                "name": name,
                "unit": " | ".join(unit_list),
                "order_serial_number": ordem_num,
                "specialty": " | ".join(specialty_list)
            }

        except Exception as e:
            print(f"❌ Failed to fetch data from {url} - {e}")
            return None

    def save_doctors_data(self, data, filename="hdl_doctors_data"):
        """
        Save scraped doctor data to both CSV and Excel formats.
        """
        print("💾 Saving data...")
        df = pd.DataFrame(data)

        # Ensure output directory exists
        import os
        os.makedirs("output", exist_ok=True)

        df.to_csv(f"{filename}.csv", index=False, encoding="utf-8-sig")
        df.to_excel(f"{filename}.xlsx", index=False)
        print(f"✅ Data saved as '{filename}.csv' and '{filename}.xlsx' in 'output/' folder")
