import streamlit as st
import os
import urllib.request
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
from bs4 import BeautifulSoup

@st.cache_resource
def install_chromium():
    st.write("Downloading and setting up Chromium and ChromeDriver...")

    # Paths for Chromium and ChromeDriver
    chromium_url = 'https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/818858/chrome-linux.zip'
    chromedriver_url = 'https://chromedriver.storage.googleapis.com/87.0.4280.88/chromedriver_linux64.zip'
    chromium_path = './chrome-linux'
    chromedriver_path = './chromedriver'

    # Download and extract Chromium
    urllib.request.urlretrieve(chromium_url, 'chrome-linux.zip')
    with zipfile.ZipFile('chrome-linux.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    os.chmod(f"{chromium_path}/chrome", 0o755)

    # Download and extract ChromeDriver
    urllib.request.urlretrieve(chromedriver_url, 'chromedriver_linux64.zip')
    with zipfile.ZipFile('chromedriver_linux64.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    os.chmod(f"{chromedriver_path}", 0o755)

    # Clean up
    os.remove('chrome-linux.zip')
    os.remove('chromedriver_linux64.zip')

    # Add to PATH
    os.environ["PATH"] += os.pathsep + os.path.abspath(chromium_path)
    os.environ["PATH"] += os.pathsep + os.path.abspath('.')

    st.write("Chromium and ChromeDriver setup complete.")

install_chromium()

def get_driver():
    st.write("Initializing the Chrome WebDriver...")
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = os.path.abspath('./chrome-linux/chrome')
        driver = webdriver.Chrome(service=ChromeService(os.path.abspath('./chromedriver')), options=options)
        st.write("Chrome WebDriver initialized successfully.")
        return driver
    except Exception as e:
        st.write(f"An error occurred while initializing the Chrome WebDriver: {e}")
        raise e

def fetch_html_structure(url):
    st.write(f"Fetching HTML structure for URL: {url}")
    try:
        driver = get_driver()
        driver.get(url)
        
        # Use explicit wait to ensure the page loads
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        st.write("Page loaded successfully.")
        
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, 'html.parser')
        tags = [tag.name for tag in soup.find_all()]
        unique_tags = set(tags)
        st.write("Fetched HTML structure successfully.")
        return unique_tags
    except Exception as e:
        st.write(f"An error occurred while fetching HTML structure: {e}")
        raise e

def capture_masthead(url, identifier, by=By.TAG_NAME):
    st.write(f"Capturing masthead for URL: {url} using identifier: {identifier}")
    try:
        driver = get_driver()
        driver.get(url)
        
        # Use explicit wait to ensure the element loads
        masthead_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((by, identifier)))
        masthead_image = masthead_element.screenshot_as_png
        st.write("Masthead captured successfully.")
        
        driver.quit()
        
        image = Image.open(io.BytesIO(masthead_image))
        return image
    except Exception as e:
        st.write(f"An error occurred while capturing the masthead: {e}")
        raise e

# Streamlit app
st.title("Website Masthead Capture")

# Input URL
url = st.text_input("Enter the URL of the website:")

if url:
    st.write("Fetching information from:", url)
    try:
        with st.echo():
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
            with st.echo():
                masthead_img = capture_masthead(url, identifier, by=by_map[identifier_type])
            st.image(masthead_img, caption='Captured Masthead')
    except Exception as e:
        st.error(f"An error occurred: {e}")
