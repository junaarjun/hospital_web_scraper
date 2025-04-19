from scraper.browser import BrowserManager
from scraper.cuf_scraper import CUFScraper

def main():
    browser = BrowserManager(headless=True)
    page = browser.get_page()

    scraper = CUFScraper(page)
    scraper.apply_pediatrics_filter()
    doctors = scraper.extract_doctor_data()
    browser.close()

    scraper.save_doctors_data(doctors)

if __name__ == "__main__":
    main()
