import csv
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ----------------------------------------------------------------------
#  SCRAPE SINGLE JOB DETAIL PAGE
# ----------------------------------------------------------------------
def scrape_job_detail(driver, url):
    """Scrape data from one job detail page."""

    driver.get(url)
    wait = WebDriverWait(driver, 10)

    article = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article.job-details"))
    )

    # ---- TITLE (robust: h2 or h1, depending on layout) ----
    try:
        title_el = article.find_element(By.CSS_SELECTOR, ".header-title h2")
    except Exception:
        try:
            title_el = article.find_element(By.CSS_SELECTOR, ".header-title h1")
        except Exception:
            # fallback: first h1 inside the article
            title_el = article.find_element(By.CSS_SELECTOR, "h1")

    title = title_el.text.strip()

    # ---- COMPANY ----
    try:
        company_el = article.find_element(By.CSS_SELECTOR, ".company-title")
        company = company_el.text.strip()
    except Exception:
        company = ""

    # ---- ATTRIBUTES FROM DATA-* (very stable) ----
    publishing_date = article.get_attribute("data-pub-date")
    quota = article.get_attribute("data-employment-grade")
    location = article.get_attribute("data-job-location")

    return {
        "title": title,
        "company": company,
        "publishing_date": publishing_date,
        "quota": quota,
        "location": location,
        "url": url,
    }


# ----------------------------------------------------------------------
#  GET TOTAL NUMBER OF PAGES
# ----------------------------------------------------------------------
def get_total_pages(driver):
    """
    Reads 'Seite X / Y' from the pagination and returns Y.
    If no pagination exists, returns 1.
    """

    try:
        elem = driver.find_element(By.CSS_SELECTOR, ".pagination .pages li")
        text = elem.text  # e.g. "Seite 1 / 100"
        m = re.search(r"Seite\s+\d+\s*/\s*(\d+)", text)
        if m:
            return int(m.group(1))
    except Exception:
        pass

    return 1


# ----------------------------------------------------------------------
#  SCRAPE ALL JOBS ON CURRENT PAGE (LIST VIEW)
# ----------------------------------------------------------------------
def collect_jobs_on_current_page(driver):
    """
    Collects (job_id, detail_url) pairs from the search results page
    without following links yet (avoids stale element issues).
    """

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.job-list-item")))

    job_elements = driver.find_elements(By.CSS_SELECTOR, "li.job-list-item")

    jobs_to_scrape = []
    for job in job_elements:
        job_id = job.get_attribute("data-job-id")
        detail_url = job.get_attribute("data-job-detail-url")

        # Some URLs are relative, prepend domain if needed
        if detail_url and not detail_url.startswith("http"):
            detail_url = "https://www.jobscout24.ch" + detail_url

        if job_id and detail_url:
            jobs_to_scrape.append((job_id, detail_url))

    return jobs_to_scrape


# ----------------------------------------------------------------------
#  SCRAPE ALL PAGES
# ----------------------------------------------------------------------
def scrape_all_jobs(base_url, max_pages=None, delay_between_jobs=0.3, delay_between_pages=1.0):
    """
    Scrapes all result pages starting from base_url.
    - max_pages: limit number of pages (None = all available)
    """

    options = Options()
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    all_results = []

    # --- First page: determine total_pages ---
    driver.get(base_url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.job-list-item")))
    total_pages = get_total_pages(driver)

    if max_pages is not None:
        total_pages = min(total_pages, max_pages)

    print(f"Detected {total_pages} pages of results.")

    # --- Loop over pages ---
    for page in range(1, total_pages + 1):
        if page == 1:
            page_url = base_url
        else:
            # subsequent pages use ?p=...
            if "?" in base_url:
                # if base_url already had params, we might want to be more careful;
                # for simple /de/jobs/ it's fine:
                page_url = re.sub(r"[?&]p=\d+", "", base_url)  # remove old p
                if "?" in page_url:
                    page_url += f"&p={page}"
                else:
                    page_url += f"?p={page}"
            else:
                page_url = f"{base_url}?p={page}"

        print(f"\n=== Page {page}/{total_pages} → {page_url} ===")
        driver.get(page_url)

        try:
            jobs_to_scrape = collect_jobs_on_current_page(driver)
        except Exception as e:
            print(f"Could not collect jobs on page {page}: {e}")
            continue

        print(f"Found {len(jobs_to_scrape)} jobs on this page.")

        # Scrape each job detail
        for job_id, job_url in jobs_to_scrape:
            print(f"  → Scraping job {job_id} ...")
            try:
                data = scrape_job_detail(driver, job_url)
                data["job_id"] = job_id
                all_results.append(data)
            except Exception as e:
                print(f"    Failed to scrape job {job_id}: {e}")

            time.sleep(delay_between_jobs)

        time.sleep(delay_between_pages)

    driver.quit()
    return all_results


# ----------------------------------------------------------------------
#  SAVE TO CSV
# ----------------------------------------------------------------------
def save_to_csv(data, filename="jobscout24_all_jobs.csv"):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} jobs to {filename}")


# ----------------------------------------------------------------------
#  MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    BASE_URL = "https://www.jobscout24.ch/de/jobs/"

    # Set max_pages=None for all, or e.g. max_pages=3 for testing
    jobs = scrape_all_jobs(BASE_URL, max_pages=None)

    save_to_csv(jobs, filename="datasets/jobscout24_all_jobs.csv")
