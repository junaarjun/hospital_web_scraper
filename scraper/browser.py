from playwright.sync_api import sync_playwright

class BrowserManager:
    def __init__(self, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def close(self):
        self.browser.close()
        self.playwright.stop()

    def get_page(self):
        return self.page
