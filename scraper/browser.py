from playwright.sync_api import sync_playwright


class BrowserManager:
    """
    BrowserManager is a wrapper for initializing and managing a Playwright browser,
    designed to be safe for multithreaded execution.

    Each instance creates its own Playwright, browser, context, and page to ensure
    thread isolation.

    Attributes:
        playwright: The Playwright instance.
        browser: The launched browser instance.
        context: The browser context (similar to a browser profile).
        page: The page object for navigation and interaction.
    """

    def __init__(self, headless=True):
        """
        Initialize the browser, context, and page.

        Args:
            headless (bool): Whether to run the browser in headless mode.
        """
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def get_page(self):
        """
        Returns the Playwright Page object for interacting with websites.

        Returns:
            Page: The current browser page.
        """
        return self.page

    def close(self):
        """
        Closes the browser and stops the Playwright instance.
        """
        self.browser.close()
        self.playwright.stop()
