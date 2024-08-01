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
    url = 'https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz'
    filename = 'geckodriver-v0.30.0-linux64.tar.gz'
    extract_path = './'

    # Download the file
    urllib.request.urlretrieve(url, filename)

    # Extract the tar file
    with tarfile.open(filename) as tar:
        tar.extractall(path=extract_path)

    # Make the driver executable
    os.chmod(os.path.join(extract_path, 'geckodriver'), 0o755)

    # Add to PATH
    os.environ["PATH"] += os.pathsep + extract_path

    # Clean up
    os.remove(filename)

_ = install_geckodriver()

def get_driver():
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Firefox(service=FirefoxService(), options=options)
    return driver

def fetch_html_structure(url):
    driver = get_driver()
    driver.get(url)
    
    # Use explicit wait to ensure the page loads
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
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
    driver = get_driver()
    driver.get(url)
    
    # Use explicit wait to ensure the element loads
    try:
        masthead_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((by, identifier)))
        masthead_image = masthead_element.screenshot_as_png
    except Exception as e:
        driver.quit()
        raise e
    
    driver.quit()
    
    image = Image.open(io.BytesIO(masthead_image))
    return image

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

# Instructions for deploying this script on Streamlit Cloud
st.write("""
## Instructions to deploy on Streamlit Cloud
1. Create a new GitHub repository and upload this `app.py` file and `requirements.txt`.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in.
3. Click on 'New app' and link your GitHub repository.
4. Choose the branch and the main file (`app.py`) and click 'Deploy'.
5. Your app will be available at a unique URL provided by Streamlit Cloud.
""")
