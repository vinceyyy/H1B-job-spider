import undetected_chromedriver as uc
import json
import time
from bs4 import BeautifulSoup

# setup
with open("secrets.json") as s:
    j = json.load(s)
    username = j["linkedin"]["username"]
    password = j["linkedin"]["password"]
browser = uc.Chrome()

# Open login page
browser.get("https://linkedin.com")

# Enter login info:
elementID = browser.find_element_by_id("session_key")
elementID.send_keys(username)
elementID = browser.find_element_by_id("session_password")
elementID.send_keys(password)
elementID.submit()

job = "H1B Marketing Analyst"


# Go to job search page
browser.get("https://www.linkedin.com/jobs/?showJobAlertsModal=false")
jobID = browser.find_element_by_class_name("jobs-search-box__text-input")
jobID.send_keys(job)
browser.find_element_by_css_selector("[type=submit]").click()
time.sleep(1)

# Add filters
# date posted
browser.find_element_by_css_selector(
    "[aria-label='Date Posted filter. Clicking this button displays all Date Posted filter options.']"
).click()
browser.find_element_by_css_selector("[aria-label='Filter by Past Month']").click()
browser.find_element_by_css_selector(
    "[aria-label='Apply selected filter and show results']"
).click()

# Load more
last_height = browser.execute_script("return document.body.scrollHeight")
for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)
    new_height = browser.execute_script("return document.body.scrollHeight")
    last_height = new_height


# Get page source code
src = browser.page_source
soup = BeautifulSoup(src, "lxml")
# Strip text from source code
results = (
    soup.find("small", {"class": "display-flex t-12 t-black--light t-normal"})
    .get_text()
    .strip()
    .split()[0]
)
results = int(results.replace(",", ""))
print(results)
