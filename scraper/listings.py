from config.settings import LISTINGS_URL, APARTMENT_TYPE_FILTER, LOGIN_URL
from dotenv import load_dotenv
import os
import csv
from datetime import datetime
from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
load_dotenv()


def scrape_listings():
    """
    Log into SSSB, scrape available apartment listings, extract queue information,
    and append the results to `storage/apartments.csv`.

    This function uses Selenium to authenticate to the SSSB portal using credentials
    stored in environment variables. After logging in, it retrieves the user's current
    credit days, navigates to the apartment listings page, applies filtering,
    loads all available apartments, and extracts structured details from each listing.
    Results are appended to a persistent CSV, creating a longitudinal dataset.

    Steps Performed
    ---------------
    1. Load login credentials from environment variables.
    2. Launch a Chrome WebDriver instance and authenticate.
    3. Parse the logged-in dashboard to extract the user's credit days.
    4. Navigate to the apartment listings page and apply apartment-type filters.
    5. Wait for listings to load and parse the final HTML with BeautifulSoup.
    6. For each apartment:
        - Extract attribute headers and values
        - Clean rent amounts and queue-day formats
        - Capture title, address, consultation date, and credit days
    7. Append structured results to `storage/apartments.csv`.
       The header row is written only if the file is new or empty.

    Output File
    -----------
    storage/apartments.csv : CSV
        A cumulative dataset of apartment listings across all scrapes.
        Fields include:
            - Area
            - Living space
            - Rent
            - Moving in
            - Queue days
            - Floor
            - Title
            - Address
            - ConsultationDate
            - CreditDays

    Notes
    -----
    - Queue days strings like '787 (14st)' are cleaned to retain only the numeric value.
    - Rent values have non-breaking spaces removed.
    - ConsultationDate is stored as a YYYY-MM-DD string.
    - The function must be run in an environment where Selenium and ChromeDriver are available.

    Returns
    -------
    None
        Writes data to CSV as a side effect.
    """
        
    # Load credentials from environment variables
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # visible browser

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    driver.get(LOGIN_URL)

    wait.until(EC.presence_of_element_located((By.NAME, "log")))
    driver.find_element(By.NAME, "log").send_keys(USERNAME)
    driver.find_element(By.NAME, "pwd").send_keys(PASSWORD)  # change ID if needed
    driver.find_element(By.XPATH, "//button[text()='Log in']").click()


    # recover my queuing days for the day of consulting

    soup = BeautifulSoup(driver.page_source, "lxml")
    membership_div = soup.find("div", {"data-widget": "koerochprenumerationer@STD"})
    credit_days = membership_div.find("strong").get_text(strip=True)# go to listings

    driver.get(LISTINGS_URL)

    # filter by apartment type if needed

    if APARTMENT_TYPE_FILTER != "All":
        select = wait.until(EC.presence_of_element_located((By.ID, "oboTyper")))
        for option in select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == APARTMENT_TYPE_FILTER:
                option.click()
                break

    wait = WebDriverWait(driver, 15)  # wait up to 15 seconds

    # Wait until the search button is clickable, then click it
    search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn.Sok")))
    search_button.click()




    # list appartments and their details

    # wait for apartments to load
    wait.until(EC.presence_of_element_located((By.ID, "apartmentList")))


    # Parse the html of the rendered page

    soup = BeautifulSoup(driver.page_source, "lxml")

    # Find the container with all apartments
    apartment_list = soup.find("div", id="apartmentList")
    apartments = apartment_list.find_all("div", class_="appartment row")

    all_apartments = []
    consultation_date = datetime.now().strftime("%Y-%m-%d")  
    # iterate over apartments and extract details

    for apt in apartments:
        # Extract headers and corresponding data
        headers = [li.get_text(strip=True).rstrip(':') for li in apt.select(".apt-details-headers li")]
        data = [li.get_text(strip=True) for li in apt.select(".apt-details-data li")]
        data = [x for x in data if x != ''] # remove empty entry because of structure
        data[2] = data[2].replace('\xa0', '')  # Clean up non-breaking spaces in rent
        data[4] = int(re.sub(r"\s*\(.*\)", "",data[4]))  # Keep only queueing days number

        # Convert to dict
        apartment_info = dict(zip(headers, data))
        
        # Optionally, add title and address
        title_elem = apt.select_one(".apt-title a")
        apartment_info["Title"] = title_elem.get_text(strip=True) if title_elem else ""
        
        address_elem = apt.select_one(".apt-address")
        apartment_info["Address"] = address_elem.get_text(strip=True) if address_elem else ""
        
        apartment_info["ConsultationDate"] = consultation_date
        apartment_info["CreditDays"] = credit_days
        all_apartments.append(apartment_info)


    # save in csv

    filename = "storage/apartments.csv"

    # Make sure there is at least one apartment
    if all_apartments:
        # Get all keys (columns) from the first dict
        fieldnames = all_apartments[0].keys()
        
        # Check if the file exists and is empty
        file_exists = os.path.exists(filename)
        write_header = not file_exists or os.path.getsize(filename) == 0

        with open(filename, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()  # write column headers only if file is new/empty
            for apt in all_apartments:
                writer.writerow(apt)
