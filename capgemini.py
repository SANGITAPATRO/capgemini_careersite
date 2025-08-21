import time
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import datetime
from datetime import datetime

# URL to scrape
url = "https://www.capgemini.com/careers/join-capgemini/job-search/?size=15"

# Output file
CSV_FILE = f'capgemini_opening{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--start-maximized')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Data storage
# Capgemin
jobs = []

def accept_cookies(driver):
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept']"))
        )
        accept_button.click()
        print("Clicked 'Accept' button by text.")
    except:
        print("'Accept' button not found or already closed.")

def get_all_jobs():
    print("🚀 Launching browser...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        accept_cookies(driver)

        # Keep clicking Load More until it's gone
        while True:
            try:
                load_more = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@class,'filters-more') and contains(@aria-label,'Load More')]")
                ))
                driver.execute_script("arguments[0].click();", load_more)
                print("🖱️ Clicked 'Load More'")
                time.sleep(2)
            except TimeoutException:
                print("✅ No more 'Load More' button.")
                break

        # After all jobs are loaded, get all job links
        jobs = driver.find_elements(By.XPATH, "//a[contains(@class,'joblink')]")
        jobs_url = [job.get_attribute("href") for job in jobs]
        print(f"🔍 Found total {len(jobs_url)} jobs")

        for job in jobs_url:
            time.sleep(2)
            driver.execute_script("window.open(arguments[0]);", job)
            driver.switch_to.window(driver.window_handles[-1])

            time.sleep(5)
            try:
                time.sleep(2)
                title_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'box-title')]")))
                title = title_element.text.strip()

                # Extract the details by label text
                date_posted = driver.find_element(By.XPATH, "//span[text()='Posted on']/following-sibling::span").text.strip()
                category = driver.find_element(By.XPATH, "//span[text()='Experience level']/following-sibling::span").text.strip()
                contract_type = driver.find_element(By.XPATH, "//span[text()='Contract type']/following-sibling::span").text.strip()
                location = driver.find_element(By.XPATH, "//span[text()='Location']/following-sibling::span").text.strip()
                description = driver.find_element(By.XPATH,"//section[@class='section section--job-info']").text.strip()

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(5)

                # Append data
                job_entry = {
                    "ob_title": title,
                    "date_posted": date_posted,
                    "description": description,
                    "employment_type":  contract_type,
                    "hiring_organization": "Capgemini",
                    "job_location": location,
                    "job_url": job,
                    "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "company": "Capgemini",
                    "host_url": url,
                    # "category" : category
                }
                jobs.append(job_entry)
                # Capgemini_jobs["Job Title"].append(title)
                # Capgemini_jobs["Location"].append(location)
                # Capgemini_jobs["Category"].append(category)
                # Capgemini_jobs["Contract Type"].append(contract_type)
                # Capgemini_jobs["URL"].append(job)
                # Capgemini_jobs["Date Posted"].append(date_posted)

            except Exception as e:
                print(f"❌ Error parsing job: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    except Exception:
        print("🚨 Fatal error occurred!")
        traceback.print_exc()
    finally:
        driver.quit()
        print("🛑 Browser closed")

if __name__ == "__main__":
    get_all_jobs()
    pd.DataFrame(jobs).to_csv(CSV_FILE, index=False, encoding='utf-8')
    print(f"✅ Data saved to {CSV_FILE}")
