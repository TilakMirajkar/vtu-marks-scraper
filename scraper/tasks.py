import os
import time
import pandas as pd
import pytesseract

from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver





def generate_usn_list(prefix_usn, suffix_usn):
    usn_list = []
    for part in suffix_usn.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            usn_list.extend(f"{prefix_usn}{str(num).zfill(3)}" for num in range(start, end + 1))
        else:
            usn_list.append(f"{prefix_usn}{str(int(part)).zfill(3)}")
    return usn_list



def initialize_webdriver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver


def process_and_save_data(soup_dict, is_reval):
    records = {}
    subject_codes = []  

    for id, soup in soup_dict.items():
        this_usn, this_name = id.split('+')
        sems_divs = soup.find_all('div', style="text-align:center;padding:5px;")
        first_sem_div = sems_divs[0]  # Get the first semester div
        sems_data = [first_sem_div.find_next_sibling('div')]

        student_record = {'USN': this_usn, 'Student Name': this_name}

        for marks_data in sems_data:
            rows = marks_data.find_all('div', class_='divTableRow')
            data = [[cell.text.strip() for cell in row.find_all('div', class_='divTableCell')] for row in rows]
            df_temp = pd.DataFrame(data[1:], columns=data[0])

            for _, row in df_temp.iterrows():
                subject_code = row['Subject Code']
                total_marks = row['Total']

                student_record[subject_code] = total_marks
                
                if subject_code not in subject_codes:  
                    subject_codes.append(subject_code) 

        records[id] = student_record

    columns = ['USN', 'Student Name'] + subject_codes
    final_df = pd.DataFrame(records.values(), columns=columns)

    header_row = ['USN', 'Student Name'] + subject_codes
    header_df = pd.DataFrame([header_row], columns=columns)

    final_df = pd.concat([header_df, final_df], ignore_index=True)
    final_df = final_df.drop_duplicates()
    final_df.reset_index(drop=True, inplace=True)
    final_df.drop(final_df.index[0], inplace=True)  
    return final_df





def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
    return df


def scrape_data(driver, usn_list):
    soup_dict = {}
    for usn in usn_list:
        while True:
            driver.find_element(By.NAME, 'lns').clear()
            driver.find_element(By.NAME, 'lns').send_keys(usn)

            captcha_image = driver.find_element(By.XPATH, '//*[@id="raj"]/div[2]/div[2]/img').screenshot_as_png
            pytesseract.pytesseract.tesseract_cmd = r'C:/Users/tilak/OneDrive/Desktop/FinalEduinsight/EduInsight/scraper/Tesseract-OCR/tesseract.exe'

            text = get_captcha_from_image(captcha_image)
            driver.find_element(By.NAME, 'captchacode').clear()
            driver.find_element(By.NAME, 'captchacode').send_keys(text)
            driver.find_element(By.ID, 'submit').click()

            try:
                WebDriverWait(driver, 1).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert_text = alert.text
                alert.accept()

                if 'University Seat Number is not available or Invalid..!' in alert_text:
                    break

                print(f"Captcha failed for USN {usn}. Retrying...")

            except:
                print(f"Captcha succeeded for USN {usn}.")
                soup = BeautifulSoup(driver.page_source, 'lxml')
                student_usn = soup.find_all('td')[1].text.split(':')[1].strip().upper()
                student_name = soup.find_all('td')[3].text.split(':')[1].strip()
                key = f'{student_usn}+{student_name}'
                soup_dict[key] = soup
                driver.back()
                break

        time.sleep(2)

    return soup_dict


def get_captcha_from_image(target_image):

    pixel_range = [(i, i, i) for i in range(102, 130)]
    image_data = BytesIO(target_image)
    image = Image.open(image_data)
    width, height = image.size
    image.convert("RGB")
    white_image = Image.new("RGB", (width, height), "white")

    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            if pixel in pixel_range:
                white_image.putpixel((x, y), pixel)

    text = pytesseract.image_to_string(white_image, config='--psm 7 --oem 1').strip()

    if len(text) < 6:
        text = text.ljust(6, 'A')
    elif len(text) > 6:
        text = text[:6]

    return text


def download_excel(df, sem):
    output = BytesIO()
    name = f'{sem}th Sem Results'
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=name)
    
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Results.xlsx"'  # Filename for download

    return response
