import os
import streamlit as st
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import feature_extraction as fe
import machine_learning
from streamlit_extras.let_it_rain import rain

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

if 'recently_checked_urls' not in st.session_state:
    st.session_state.recently_checked_urls = pd.DataFrame(columns=['URL', 'Status'])

st.image("frame.png", output_format='PNG')
st.title('ClickClickClick URL Identifier')
st.write('ClickClickClick URL Identifier helps you detect malicious links in emails, text messages, and other online content.')
st.subheader('Disclaimer')
st.write('Our tools are intended to help users identify potential phishing links or legitimate URLs. While we strive for accuracy, results may vary. We are not liable for any damages resulting from tool use. By using our services, you agree to these terms.')

def submit_url_to_urlscan(url, visibility='public'):
    headers = {'API-Key': '35c0f5ff-38a9-4c9c-8844-1c246ef7012d', 'Content-Type': 'application/json'}
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

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

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

def apply_color(status):
    return 'color: red' if status == 'SUSPICIOUS' else 'color: green'

st.subheader("Recently Checked URLs:")
recently_checked_table = st.session_state.recently_checked_urls.reset_index(drop=True)
st.table(recently_checked_table.style.map(lambda x: apply_color(x), subset=['Status']))

st.header("About ClickClickClick URL Identifier")
st.write('ClickClickClick URL Identifier is a tool developed by 3 junior students of the MIS department at Paragon International University.') 
st.write('Project Members:')
st.write('- Morita Chhea')
st.write('- Socheata Sokhachan')
st.write('- Sophy Do')        
st.write('ClickClickClick URL Identifier detects phishing and malicious websites using a machine-learning algorithm. The tool uses high-quality datasets containing features from various sources and phishing websites. The ClickClickClick URL Identifier uses a Random Forest machine learning model to identify potential phishing websites from features such as the URL, its domain, HTML content, and other heuristics.')
st.write('Report Issue: [ClickClickClick Tech Crew](mailto:ssokhachan@paragoniu.edu.kh)')
st.write('Privacy Policy: We respect your privacy and do not store or share any information entered in the ClickClickClick URL Identifier.')
st.write('Learn more about Phishing: [ClickClickClick Online awareness campaign](https://www.facebook.com/profile.php?id=61557960070679)')
