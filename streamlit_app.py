import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
from bs4 import BeautifulSoup

# Streamlit app
st.title("Website Masthead Capture")

# Input URL
url = st.text_input("Enter the URL of the website:")

def fetch_html_structure(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1280, 720)  # Set the browser window size
    driver.get(url)
    
    # Use explicit wait to ensure the page loads
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    except Exception as e:
        driver.quit()
        raise e
    
    page_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    tags = [tag.name for tag in soup.find_all()]
    unique_tags = set(tags)
    return unique_tags

def capture_masthead(url, identifier, by=By.TAG_NAME):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1280, 720)  # Set the browser window size
    driver.get(url)
    
    # Use explicit wait to ensure the element loads
    try:
        masthead_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, identifier)))
        masthead_image = masthead_element.screenshot_as_png
    except Exception as e:
        driver.quit()
        raise e
    
    driver.quit()
    
    image = Image.open(io.BytesIO(masthead_image))
    return image

if url:
    st.write("Fetching information from:", url)
    try:
        tags = fetch_html_structure(url)
        st.write("HTML Tags found on the page:", tags)
        
        identifier = st.text_input("Enter the identifier (e.g., tag name, id, or class) to capture the masthead:")
        identifier_type = st.selectbox("Select the type of identifier:", ["Tag Name", "ID", "Class Name"])
        
        by_map = {
            "Tag Name": By.TAG_NAME,
            "ID": By.ID,
            "Class Name": By.CLASS_NAME
        }
        
        if identifier:
            masthead_img = capture_masthead(url, identifier, by=by_map[identifier_type])
            st.image(masthead_img, caption='Captured Masthead')
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Instructions for deploying this script on Streamlit Cloud
st.write("""
## Instructions to deploy on Streamlit Cloud
1. Create a new GitHub repository and upload this `app.py` file and `requirements.txt`.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in.
3. Click on 'New app' and link your GitHub repository.
4. Choose the branch and the main file (`app.py`) and click 'Deploy'.
5. Your app will be available at a unique URL provided by Streamlit Cloud.
""")
