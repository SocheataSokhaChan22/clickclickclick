import requests as re
from bs4 import BeautifulSoup
import pandas as pd
import feature_extraction as fe
import os
import logging
from datetime import datetime

logging.basicConfig(filename='phishing_data_update.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Script started.")

def fetch_phishtank_data(url):
    try:
        response = re.get(url)
        response.raise_for_status()
        logging.info("Successfully fetched data from Phishtank.")
        return response.json()
    except re.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None

def create_structured_data(url_list):
    data_list = []
    for i, url in enumerate(url_list):
        try:
            response = re.get(url, verify=False, timeout=4)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                vector = fe.create_vector(soup)
                vector.append(url)
                data_list.append(vector)
            else:
                logging.warning(f"{i}. Failed to fetch URL: {url}")
        except re.RequestException as e:
            logging.error(f"{i} --> {e}")
            continue
    return data_list

csv_file = "structured_data_phishing.csv"
if not os.path.isfile(csv_file):
    columns = ['has_title', 'has_input', 'has_button', 'has_image', 'has_submit', 'has_link',
               'has_password', 'has_email_input', 'has_hidden_element', 'has_audio', 'has_video',
               'number_of_inputs', 'number_of_buttons', 'number_of_images', 'number_of_option',
               'number_of_list', 'number_of_th', 'number_of_tr', 'number_of_href', 'number_of_paragraph',
               'number_of_script', 'length_of_title', 'has_h1', 'has_h2', 'has_h3', 'length_of_text',
               'number_of_clickable_button', 'number_of_a', 'number_of_img', 'number_of_div',
               'number_of_figure', 'has_footer', 'has_form', 'has_text_area', 'has_iframe', 'has_text_input',
               'number_of_meta', 'has_nav', 'has_object', 'has_picture', 'number_of_sources', 'number_of_span',
               'number_of_table', 'URL', 'label']
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)
    logging.info("Created CSV file with headers.")

phishing_url = "http://data.phishtank.com/data/online-valid.json"
phishtank_data = fetch_phishtank_data(phishing_url)

if phishtank_data:
    phishing_df = pd.json_normalize(phishtank_data)
    phishing_df = phishing_df[['url', 'verified', 'verification_time', 'online', 'target']]
    phishing_df.columns = ['URL', 'Verified', 'Verification_Time', 'Online', 'Target']
    phishing_df = phishing_df[(phishing_df['Online'] == 'yes') & (phishing_df['Verified'] == 'yes')]
    phishing_df['Verification_Time'] = pd.to_datetime(phishing_df['Verification_Time'])
    URL_list = phishing_df['URL'].to_list()

    collection_list = URL_list[:500]  # Adjust range as needed
    structured_data = create_structured_data(collection_list)

    if structured_data:
        df_new = pd.DataFrame(structured_data, columns=columns[:-1] + ['URL'])
        df_new['label'] = 'phishing'
        df_old = pd.read_csv(csv_file)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined.to_csv(csv_file, index=False)
        logging.info("Structured data updated and saved.")
    else:
        logging.info("No new structured data to update.")
else:
    logging.error("Failed to update phishing data.")

logging.info("Script finished.")
logging.shutdown()
