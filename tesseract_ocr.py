from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from subprocess import CREATE_NO_WINDOW
import os
import pandas as pd
import cv2
import numpy as np
import pytesseract
from PIL import ImageFont, Image, ImageDraw
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\tesseract.exe'
# from base64 import b64decode
# import subprocess

class tesseractOCR():
    def __init__(self, d, lnt, s, l, o):
        self.font = r'../assets/font/calibri.ttf'
        lens = lnt
        medic = d
        sia = s
        loc = l
        olho = o

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        chrome_service = ChromeService(ChromeDriverManager().install())
        chrome_service.creation_flags = CREATE_NO_WINDOW
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("detach", True)
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        driver.get('https://calc.apacrs.org/toric_calculator20/Toric%20Calculator.aspx')

        img = cv2.imread('C:/img.jpg')

        # Convert image to grey scale
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = img_grey.shape
        # Converting grey image to binary image by Thresholding
        threshold = cv2.threshold(img_grey, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        aligned_img_threshold = cv2.resize(threshold, (width // 2, height // 2))

        # Copy of input image
        img_cp = img.copy()
        img_cp = cv2.resize(img_cp, (width // 2, height // 2))

        # Get coordinate position of all entities from entity_coordinate code
        entity_roi_od = [
            [(209, 70), (892, 124), 'MainContent_PatientName'],
            [(243, 168), (389, 194), 'MainContent_PatientNo'],
            [(159, 730), (219, 752), 'MainContent_AxLength'],
            [(160, 754), (219, 777), 'MainContent_OpticalACD'],
            [(160, 778), (219, 801), 'MainContent_LensThickness'],
            [(160, 800), (220, 823), 'MainContent_WTW'],
            [(460, 824), (521, 846), 'MainContent_MeasuredK'],
            [(592, 821), (625, 846), 'MainContent_MeasuredAxis'],
            [(460, 848), (521, 874), 'MainContent_MeasuredK0'],
            [(594, 848), (624, 873), 'MainContent_MeasuredAxis0']
        ]
        entity_roi_os = [
            [(209, 70), (892, 124), 'MainContent_PatientName'],
            [(243, 168), (389, 194), 'MainContent_PatientNo'],
            [(690, 729), (752, 754), 'MainContent_AxLength'],
            [(694, 752), (751, 777), 'MainContent_OpticalACD'],
            [(692, 776), (752, 800), 'MainContent_LensThickness'],
            [(692, 800), (752, 822), 'MainContent_WTW'],
            [(992, 822), (1054, 848), 'MainContent_MeasuredK'],
            [(1121, 819), (1158, 846), 'MainContent_MeasuredAxis'],
            [(992, 848), (1054, 871), 'MainContent_MeasuredK0'],
            [(1120, 846), (1158, 871), 'MainContent_MeasuredAxis0']
        ]

        aligned_img_show = img_cp.copy()
        aligned_img_mask = np.zeros_like(aligned_img_show)

        entity_name = []
        entity_value = []

        radioOD = driver.find_element(By.ID, ('MainContent_Rad1'))
        radioOS = driver.find_element(By.ID, ('MainContent_Rad2'))

        if olho == '1':
            radioOD.click()
            entity_roi = entity_roi_od
        else:
            radioOS.click()
            entity_roi = entity_roi_os

        for roi in entity_roi:
            top_left_x = roi[0][0]
            top_left_y = roi[0][1]
            bottom_right_x = roi[1][0]
            bottom_right_y = roi[1][1]

            cv2.rectangle(aligned_img_mask, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), cv2.FILLED)
            aligned_img_show = cv2.addWeighted(aligned_img_show, 0.99, aligned_img_mask, 0.1, 0)

            # Crop the specific required portion of entire image
            img_cropped = aligned_img_threshold[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

            # configuring parameters for tesseract
            custom_config = r'--oem 3 --psm 6'

            # Providing cropped image as input to the OCR
            ocr_output = pytesseract.image_to_string(img_cropped, config=custom_config, lang='eng')
            # Remove unwanted extra line gaps between sentences
            cleaned_output = os.linesep.join([s for s in ocr_output.splitlines() if s])

            # Write extracted entity value in red color on the form
            # cv2.putText(img_cp, f'{cleaned_output}', (top_left_x, top_left_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # img_cp = self.__write_text(f'{cleaned_output}', top_left_x, top_left_y, img_cp)

            # Store OCR output in list
            entity_name.append(roi[2])
            entity_value.append(cleaned_output.upper())

        img_co = cv2.resize(aligned_img_show, (1080, 1900))
        cv2.imshow('Image', img_co)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Store OCR output in dataframe
        df = pd.DataFrame()
        df['Entity_Name'] = entity_name
        df['Entity_Value'] = entity_value

        # Move last name to the end
        df.loc[0, "Entity_Value"] = ' '.join(reversed(df.loc[0, "Entity_Value"].split(', ')))

        # Replace comma to dot
        df["Entity_Value"] = df["Entity_Value"].str.replace(',', '.')

        for i in range(0, len(df)):
            text_input = driver.find_element(By.ID, f'{df.loc[i, "Entity_Name"]}')
            text_input.send_keys(df.loc[i, "Entity_Value"])
    
        lentes = Select(driver.find_element(By.ID, "MainContent_IOLModel"))
        lentes.select_by_value(lens)

        inSia = driver.find_element(By.ID, "MainContent_DoctorName")
        inSia.send_keys(medic)

        inSia = driver.find_element(By.ID, "MainContent_InducedCyl")
        inSia.send_keys(Keys.CONTROL + 'a')
        inSia.send_keys(sia)
        inLoc = driver.find_element(By.ID, "MainContent_IncisionAxis")
        inLoc.send_keys(Keys.CONTROL + 'a')
        inLoc.send_keys(loc)

        driver.find_element(By.ID, "MainContent_Button1").click()

        # pdf = b64decode(driver.print_page())
        # with open(r"C:\Users\ti\Desktop\python_print_page.pdf", 'wb') as f:
        #     f.write(pdf)

        # driver.find_element(By.ID, "A2").click()
        # cv2.imshow('Image', img_cp)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def __write_text(self, text, x, y, img, text_size=12):
        font_type = ImageFont.truetype(self.font, text_size)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x, y - text_size), text, font=font_type, fill=(0, 0, 255))
        img = np.array(img_pil)
        return img
