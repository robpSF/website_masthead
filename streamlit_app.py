import streamlit as st
import os
import subprocess
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
def install_dependencies():
    st.write("Installing Chromium and dependencies...")
    try:
        # Update package list and install chromium and necessary dependencies
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "chromium-browser"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "chromium-chromedriver"], check=True)
        st.write("Chromium and dependencies installed.")
    except Exception as e:
        st.write(f"An error occurred during installation: {e}")

install_dependencies()

def get_driver():
    st.write("Initializing the Chrome WebDriver...")
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(service=ChromeService("/usr/lib/chromium-browser/chromedriver"), options=options)
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
