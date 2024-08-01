import streamlit as st
import os
import urllib.request
import tarfile
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
from bs4 import BeautifulSoup

@st.cache_resource
def install_geckodriver():
    st.write("Downloading and installing geckodriver...")
    url = 'https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz'
    filename = 'geckodriver-v0.34.0-linux64.tar.gz'
    extract_path = './'

    try:
        # Download the file
        urllib.request.urlretrieve(url, filename)
        st.write("Downloaded geckodriver.")

        # Extract the tar file
        with tarfile.open(filename) as tar:
            tar.extractall(path=extract_path)
        st.write("Extracted geckodriver.")

        # Make the driver executable
        os.chmod(os.path.join(extract_path, 'geckodriver'), 0o755)

        # Add to PATH
        os.environ["PATH"] += os.pathsep + extract_path

        # Clean up
        os.remove(filename)
        st.write("Geckodriver installation complete.")
    except Exception as e:
        st.write(f"An error occurred during geckodriver installation: {e}")

@st.cache_resource
def install_firefox():
    st.write("Downloading and installing Firefox...")
    url = 'https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US'
    filename = 'firefox-latest.tar.bz2'
    extract_path = './firefox/'

    try:
        # Download the file
        urllib.request.urlretrieve(url, filename)
        st.write("Downloaded Firefox.")

        # Extract the tar file
        with tarfile.open(filename, 'r:bz2') as tar:
            tar.extractall(path=extract_path)
        st.write("Extracted Firefox.")

        # Add to PATH
        os.environ["PATH"] += os.pathsep + os.path.join(extract_path, 'firefox')

        # Clean up
        os.remove(filename)
        st.write("Firefox installation complete.")
    except Exception as e:
        st.write(f"An error occurred during Firefox installation: {e}")

_ = install_geckodriver()
install_firefox()

def get_driver():
    st.write("Initializing the Firefox WebDriver...")
    try:
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Firefox(service=FirefoxService(), options=options)
        st.write("Firefox WebDriver initialized successfully.")
        return driver
    except Exception as e:
        st.write(f"An error occurred while initializing the Firefox WebDriver: {e}")
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
