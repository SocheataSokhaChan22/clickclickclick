import requests as re
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from bs4 import BeautifulSoup
import pandas as pd
import feature_extraction as fe
import os
import logging
from datetime import datetime

disable_warnings(InsecureRequestWarning)

# Setup logging
logging.basicConfig(filename='phishing_data_update.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch the latest phishing URLs from Phishtank
def fetch_phishtank_data(url):
    try:
        response = re.get(url)
        if response.status_code == 200:
            logging.info("Successfully fetched data from Phishtank.")
            return response.json()
        else:
            logging.error(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except re.exceptions.RequestException as e:
        logging.error(f"Exception occurred while fetching data: {e}")
        return None

# Function to scrape the content of the URL and convert it to a structured form
def create_structured_data(url_list):
    data_list = []
    for i, url in enumerate(url_list):
        try:
            response = re.get(url, verify=False, timeout=4)
            if response.status_code != 200:
                logging.warning(f"{i}. HTTP connection was not successful for the URL: {url}")
            else:
                soup = BeautifulSoup(response.content, "html.parser")
                vector = fe.create_vector(soup)
                vector.append(url)
                data_list.append(vector)
        except re.exceptions.RequestException as e:
            logging.error(f"{i} --> {e}")
            continue
    return data_list

# Check if the CSV file exists and create it if it doesn't
csv_file = "structured_data_phishing.csv"
if not os.path.isfile(csv_file):
    columns = [
        'has_title', 'has_input', 'has_button', 'has_image', 'has_submit', 'has_link',
        'has_password', 'has_email_input', 'has_hidden_element', 'has_audio', 'has_video',
        'number_of_inputs', 'number_of_buttons', 'number_of_images', 'number_of_option',
        'number_of_list', 'number_of_th', 'number_of_tr', 'number_of_href', 'number_of_paragraph',
        'number_of_script', 'length_of_title', 'has_h1', 'has_h2', 'has_h3', 'length_of_text',
        'number_of_clickable_button', 'number_of_a', 'number_of_img', 'number_of_div',
        'number_of_figure', 'has_footer', 'has_form', 'has_text_area', 'has_iframe', 'has_text_input',
        'number_of_meta', 'has_nav', 'has_object', 'has_picture', 'number_of_sources', 'number_of_span',
        'number_of_table', 'URL', 'label'
    ]
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)
    logging.info("CSV file created with headers.")

# Fetch the latest phishing data from Phishtank
phishing_url = "http://data.phishtank.com/data/online-valid.json"
phishtank_data = fetch_phishtank_data(phishing_url)

if phishtank_data is not None:
    # Convert JSON data to DataFrame
    phishing_df = pd.json_normalize(phishtank_data)
    # Extract relevant fields and rename for consistency
    phishing_df = phishing_df[['url', 'verified', 'verification_time', 'online', 'target']]
    phishing_df.columns = ['URL', 'Verified', 'Verification_Time', 'Online', 'Target']
    # Filter for online and verified phishing URLs
    phishing_df = phishing_df[(phishing_df['Online'] == 'yes') & (phishing_df['Verified'] == 'yes')]
    # Convert Verification_Time to datetime
    phishing_df['Verification_Time'] = pd.to_datetime(phishing_df['Verification_Time'])

    # Retrieve only the "url" column and convert it to a list
    URL_list = phishing_df['URL'].to_list()

    # Restrict the URL count
    begin = 0
    end = 500  # Modify this range as needed
    collection_list = URL_list[begin:end]
else:
    logging.error("Failed to update the phishing dataset.")



