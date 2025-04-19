from scraper.browser import BrowserManager
from scraper.cuf_scraper import CUFScraper
from scraper.hdl_scraper import HDLScraper
import pandas as pd
import time


def run_cuf_scraper():
    """
    Runs the CUF scraper in a separate browser context.
    """
    browser = BrowserManager(headless=False)
    page = browser.get_page()

    cuf = CUFScraper(page)
    cuf.apply_pediatrics_filter()
    links = cuf.collect_doctor_links()
    cuf_data = cuf.scrape_doctor_details(links)
    cuf.save_doctors_data(cuf_data, filename="output/cuf_doctors_data")

    browser.close()
    print("✅ CUF Scraper finished.\n")


def run_hdl_scraper():
    """
    Runs the HDL scraper in a separate browser context.
    """
    browser = BrowserManager(headless=False)
    page = browser.get_page()

    hdl = HDLScraper(page)
    filtered_url = hdl.apply_speciality_filters()
    hdl_data = hdl.extract_doctor_list_and_details(filtered_url)
    hdl.save_doctors_data(hdl_data, filename="output/hdl_doctors_data")

    browser.close()
    print("✅ HDL Scraper finished.\n")


def merge_outputs_to_excel(cuf_file="output/cuf_doctors_data.xlsx",
                           hdl_file="output/hdl_doctors_data.xlsx",
                           output_file="output/all_doctors_combined.xlsx"):
    """
    Merge CUF and HDL doctor data into a single Excel file with separate sheets.

    Args:
        cuf_file (str): Path to CUF Excel file.
        hdl_file (str): Path to HDL Excel file.
        output_file (str): Path for the combined Excel output file.
    """
    try:
        print("📚 Merging CUF and HDL data into one Excel file...")
        cuf_df = pd.read_excel(cuf_file)
        hdl_df = pd.read_excel(hdl_file)

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            cuf_df.to_excel(writer, sheet_name="CUF", index=False)
            hdl_df.to_excel(writer, sheet_name="HDL", index=False)

        print(f"✅ Combined file saved at: {output_file}\n")
    except Exception as e:
        print(f"❌ Failed to merge files: {e}")


def main():
    """
    Run CUF and HDL scrapers serially (one after another),
    and merge the results into one Excel file.
    """
    # Run CUF Scraper first
    # print("🏁 Starting CUF Scraper...\n")
    # run_cuf_scraper()

    # # Run HDL Scraper after CUF is finished
    # print("🏁 Starting HDL Scraper...\n")
    # run_hdl_scraper()

    # # After both scrapers finish, merge the results into one Excel file
    # time.sleep(2)  # Short delay to ensure files are saved before merging
    merge_outputs_to_excel()


if __name__ == "__main__":
    main()
