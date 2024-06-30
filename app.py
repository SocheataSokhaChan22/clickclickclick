import os
import streamlit as st
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import feature_extraction as fe
from streamlit_extras.let_it_rain import rain
import pandas as pd
import machine_learning

# Set up Streamlit page configuration and custom CSS
st.set_page_config(
    page_title="ClickClickClick URL Identifier",
    page_icon="logo.png",
    layout="wide",
)

st.markdown("""
    <style>
    .stApp { background-color: #f9f9f9; color: #333; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div > div { border: 2px solid #E97451; }
    .stButton > button { background-color: #E97451; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Create a dataframe to store the recently checked URLs and their statuses
if 'recently_checked_urls' not in st.session_state:
    st.session_state.recently_checked_urls = pd.DataFrame(columns=['URL', 'Status'])

st.image("frame.png", output_format='PNG')
st.title('ClickClickClick URL Identifier')
st.write('ClickClickClick URL Identifier helps you detect malicious links in emails, text messages, and other online content.')
st.subheader('Disclaimer')
st.write('Our tools are intended to help users identify potential phishing links or legitimate URLs. While we strive for accuracy, results may vary. We are not liable for any damages resulting from tool use. By using our services, you agree to these terms.')

# Define the get_driver function without caching
def get_driver(width, height):
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument(f"--window-size={width}x{height}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(ChromeDriverManager().install(), port=0)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        st.error("Error initializing WebDriver. Please ensure Chrome is installed and up-to-date.")
        st.error(f"Details: {e}")
        return None

# Define the get_screenshot function
def get_screenshot(app_url, width, height):
    driver = get_driver(width, height)
    if not driver:
        return

    try:
        driver.get(app_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(2)
        driver.save_screenshot('screenshot.png')
    except Exception as e:
        st.error(f"Error capturing screenshot: {e}")
    finally:
        driver.quit()

# Define the submit_url_to_urlscan function
def submit_url_to_urlscan(url, visibility='public'):
    headers = {'API-Key': 'YOUR_API_KEY_HERE', 'Content-Type': 'application/json'}
    data = {"url": url, "visibility": visibility}
    response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, json=data)
    time.sleep(10)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to submit URL to urlscan.io. Status code: {response.status_code}")
        st.error(f"Response: {response.text}")
        return None

def example_safe():
    rain(
        emoji="💅",
        font_size=54,
        falling_speed=5,
        animation_length=5,
    )

def example_phishing():
    rain(
        emoji="💩",
        font_size=54,
        falling_speed=5,
        animation_length=5,
    )

width = 1920 
height = 1080

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Input URL form
with st.form("my_form"):
    app_url = st.text_input('Input URL here').rstrip('/')
    
    clickclickclick_submit = st.form_submit_button("Submit with ClickClickClick Technology Only")
    
    st.write("**Also Verify with urlscan.io**")
    st.write('We directly connect you to view information such as screenshot of the URL, domains, IPs, Autonomous System (AS) numbers, hashes, etc. We integrate the APIs of urlscan.io to provide more detailed information about the URL infrastructure in summary results.')
    visibility = st.selectbox("Select Scan Visibility", ["public", "unlisted", "private - Scan"])
    
    st.write("""
    - **Public:** The scan and its results will be publicly accessible.
    - **Unlisted:** The scan will not be listed publicly, but it can be accessed with a direct link.
    - **Private:** The scan and its results will only be accessible to you. Requires an API key with private scan privileges.
    """)

    urlscan_submit = st.form_submit_button("Submit with ClickClickClick Technology and Verify with urlscan.io")

    if clickclickclick_submit:
        if app_url:
            try:
                get_screenshot(app_url, width, height)
                st.session_state.submitted = True

                response = requests.get(app_url, verify=False, timeout=4)
                if response.status_code != 200:
                    st.error("We could not scan this website! This can happen for multiple reasons: The site could not be contacted (DNS or generic network issues), The site uses insecure TLS (weak ciphers e.g.), The site requires HTTP authentication.")
                else:
                    soup = BeautifulSoup(response.content, "html.parser")
                    vector = fe.create_vector(soup)
                    result = machine_learning.rf_model.predict([vector])
                    if result[0] == 0:
                        st.success("This website link is safe")
                        example_safe()
                    else:
                        st.warning("Attention! This website link is a potential PHISHING!")
                        example_phishing()
                    
                    status = "SUSPICIOUS" if result[0] == 1 else "LEGITIMATE"
                    st.session_state.recently_checked_urls = pd.concat([st.session_state.recently_checked_urls, pd.DataFrame({'URL': [app_url], 'Status': [status]})])

            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

    if urlscan_submit:
        if app_url:
            st.session_state.submitted = True
            try:
                st.info('Submitting URL to urlscan.io...')
                urlscan_response = submit_url_to_urlscan(app_url, visibility)
                if urlscan_response:
                    scan_id = urlscan_response['uuid']
                    st.success(f'Scan complete. View results at [URLScan website](https://urlscan.io/result/{scan_id}/)')
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

# Display screenshot result if submitted
if st.session_state.submitted and os.path.exists('screenshot.png'):
    st.image('screenshot.png', caption="Live Screenshot of the URL", use_column_width=True)

    with open("screenshot.png", "rb") as file:
        btn = st.download_button(
            label="Download image",
            data=file,
            file_name="screenshot.png",
            mime="image/png"
        )

def apply_color(status):
    return 'color: red' if status == 'SUSPICIOUS' else 'color: green'

st.subheader("Recently Checked URLs:")
recently_checked_table = st.session_state.recently_checked_urls.reset_index(drop=True)
st.table(recently_checked_table.style.applymap(lambda x: apply_color(x), subset=['Status']))

st.header("About ClickClickClick URL Identifier")
st.write('ClickClickClick URL Identifier is a tool developed by 3 junior students of the MIS department at Paragon International University.') 
st.write('Project Members:')
st.write('- Morita Chhea')
st.write('- Socheata Sokhachan')
st.write('- Sophy Do')        
st.write('ClickClickClick URL Identifier detects phishing and malicious websites using a machine-learning algorithm. The tool uses high-quality datasets containing features from various sources and phishing websites. The ClickClickClick URL Identifier uses a Random Forest machine learning model to identify potential phishing websites from features such as the URL, its domain, HTML content, and other heuristics.')
st.write('Contact us at: [customerservice@clickclickclick.com](mailto:ssokhachan@paragoniu.edu.kh)')
st.write('Privacy Policy: We respect your privacy and do not store or share any information entered in the ClickClickClick URL Identifier.')
