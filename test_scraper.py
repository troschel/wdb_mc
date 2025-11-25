import pytest
from bs4 import BeautifulSoup

# Import helper functions from your scraper
from wdb_mc_scraper import clean_quota


# ------------------------------
# Helper for testing title logic
# ------------------------------
def extract_title_from_soup(html):
    """
    Fake title extractor that uses BeautifulSoup instead of Selenium.
    Helps test logic without a browser.
    """
    soup = BeautifulSoup(html, "html.parser")

    if soup.select_one(".header-title h2"):
        return soup.select_one(".header-title h2").text.strip()

    if soup.select_one(".header-title h1"):
        return soup.select_one(".header-title h1").text.strip()

    if soup.select_one("h1"):
        return soup.select_one("h1").text.strip()

    return None


# --------------------------------------------------------
# TEST 1 — scraper initializes
# --------------------------------------------------------
def test_scraper_initializes():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    assert driver is not None

    driver.quit()


# --------------------------------------------------------
# TEST 2 — title extraction fallback works
# --------------------------------------------------------
def test_extract_title():
    html = """
    <article>
        <div class="header-title"><h2>Software Developer</h2></div>
    </article>
    """
    assert extract_title_from_soup(html) == "Software Developer"


# --------------------------------------------------------
# TEST 3 — missing title handled gracefully
# --------------------------------------------------------
def test_extract_title_missing():
    html = "<article></article>"
    assert extract_title_from_soup(html) is None


# --------------------------------------------------------
# TEST 4 — clean quota input
# --------------------------------------------------------
def test_clean_quota():
    assert clean_quota("80%") == "80"
    assert clean_quota("80-100%") == "80-100"
    assert clean_quota(None) is None
