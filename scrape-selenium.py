#!/usr/bin/python3

import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import traceback


CLOSEDVCSVFILE = "violations.csv"
OPENVCSVFILE = "open_violations.csv"

closed_csvfields = ['Violation Number', 'Violation Date', 'School Code', 'Route#', 'Hearing Date', 'Violation Code', 'Status', 'LDDA$', 'Entry Date', 'Field Trip', 'Violation Status', 'Type of Service',
                    'Type of Vehicle', 'School Name', 'School Address', 'Session', 'Session Time', 'Telephone', 'Vendor Name', 'Vendor Code', 'Vehicle Number', 'Case#', 'Description', 'Detailed Status'] # 24

open_csvfields = ['Violation Number', 'Violation Date', 'School Code', 'Route#', 'Hearing Date', 'Hearing Time', 'Entry Date', 'Field Trip', 'Violation Status', 'Type of Service',
                  'Type of Vehicle', 'School Name', 'School Address', 'Session', 'Session Time', 'Telephone', 'Vendor Name', 'Vendor Code', 'Vehicle Number', 'Case#', 'Violation Code', 'Description'] # 22


def login(driver):
    login_input = driver.find_element(By.ID, "ContentPlaceHolder1_Login1_Login1_UserName")
    pw_input = driver.find_element(By.ID, "ContentPlaceHolder1_Login1_Login1_Password")
    login_button = driver.find_element(By.ID, "ContentPlaceHolder1_Login1_Login1_LoginButton")
    login_input.send_keys("NT")
    pw_input.send_keys("Welcome@1")
    login_button.click()


def logout(driver):
    driver.find_element(By.XPATH, "/html/body/form/table/tbody/tr/td/div[1]/ul/li[6]/a").click()


def clean_field(txt):
    if txt is None:
        return ""
    return txt.text.strip().replace(',', ' ')


def closed_violation_details(entry, driver):
    row = []
    data = entry.find_all("td")
    vnum = int(data[0].a.text.strip())
    row.append(vnum)
    driver.get("https://www.opt-osfns.org/OPT/VENDORS/VIOLATION/print_violation.aspx?VioNumber=" + str(vnum))
    row.append(clean_field(data[1]))
    row.append(clean_field(data[2]))
    row.append(clean_field(data[3]))
    row.append(clean_field(data[4]))
    # inner table
    if len(data) >= 12:
        row.append(clean_field(data[9]))
        row.append(clean_field(data[10]))
        row.append(clean_field(data[11]))
    else:
        row.append("")
        row.append("")
        row.append("")
    # Details page
    table = driver.find_element(By.ID, "ContentPlaceHolder1_pnlviolation")
    table = BeautifulSoup(table.get_attribute("innerHTML"), "html.parser")
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblvioentrydt")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblFieldTrip")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblStatus")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblServiceType")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVehicleType")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSchool")))
    # row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSNumber")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSAddress")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblsession")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSessionTime")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblTelephone")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVenName")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVenCode")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVehNumber")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblcaseno")))
    # Details page bottom table first row only
    # row.append(clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblVioCode_0")))
    desc = clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblVioDesc_0")) + '\n' + clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblQuestion_0")) + \
        '\n' + clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblAnswer_0")) + '\n' + clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblComments_0"))
    row.append(desc)
    row.append(clean_field(table.select(
        "#ContentPlaceHolder1_gvViolations > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(3)")[0]))
    print("V#", vnum, end='\r', flush=True)
    return row

def open_violation_details(entry, driver):
    row = []
    data = entry.find_all("td")
    vnum = int(data[0].a.text.strip())
    driver.get("https://www.opt-osfns.org/OPT/VENDORS/VIOLATION/print_violation.aspx?VioNumber=" + str(vnum))
    row.append(vnum)
    row.append(clean_field(data[1]))
    row.append(clean_field(data[2]))
    row.append(clean_field(data[3]))
    row.append(clean_field(data[4]))
    row.append(clean_field(data[5]))
    # Details page
    table = driver.find_element(By.ID, "ContentPlaceHolder1_pnlviolation")
    table = BeautifulSoup(table.get_attribute("innerHTML"), "html.parser")
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblvioentrydt")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblFieldTrip")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblStatus")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblServiceType")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVehicleType")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSchool")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSAddress")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblsession")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblSessionTime")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblTelephone")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVenName")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVenCode")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblVehNumber")))
    row.append(clean_field(table.find(id="ContentPlaceHolder1_lblcaseno")))
    # Details page bottom table first row only
    row.append(clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblVioCode_0")))
    desc = clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblVioDesc_0")) + '\n' + clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblQuestion_0")) + \
        '\n' + clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblAnswer_0")) + '\n' + clean_field(table.find(id="ContentPlaceHolder1_gvViolations_lblComments_0"))
    row.append(desc)
    print("V#", vnum, end='\r', flush=True)
    return row

# main
try:
    #### Start connection ####
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.add_argument('-headless')
    fireFoxOptions.accept_insecure_certs = True
    # browser = webdriver.Firefox(
    #     executable_path="./drivers/geckodriver_linux64", options=fireFoxOptions)
    ffservice=Service("./drivers/geckodriver_linux64")
    browser = webdriver.Firefox(service=ffservice, options=fireFoxOptions)

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # browser = webdriver.Chrome('chromedriver', options=chrome_options)

    browser.get("https://www.opt-osfns.org/OPT/VENDORS/VIOLATION/Login.aspx")

    # Login
    print("Logging in...")
    login(browser)
    # input("If there is an SSL error, please resolve it and press any key to continue...")
    browser.implicitly_wait(20)

    # Get Open and Closed Violations tables
    vtable = browser.find_element(By.ID, 'ContentPlaceHolder1_dgrOpenVios')
    opentable = BeautifulSoup(vtable.get_attribute("innerHTML"), "html.parser")
    vtable = browser.find_element(By.ID, "ContentPlaceHolder1_dgrClosedVios")
    closedtable = BeautifulSoup(vtable.get_attribute("innerHTML"), "html.parser")

    #### Open Violations ####
    # print("Processing Open Violations...")
    # openvnums=0
    # with open(OPENVCSVFILE, 'w') as f:
    #     vcsv = csv.writer(f)
    #     vcsv.writerow(open_csvfields)
    #     print("csv fields: ", len(open_csvfields))
    #     for entry in opentable.find_all("tr"):
    #         if entry.find("a") is not None:
    #             vcsv.writerow(open_violation_details(entry, browser))
    #             openvnums += 1
    # print("%d open violations saved to" % openvnums, OPENVCSVFILE)

    #### Closed Violations ####
    print("Processing Closed Violations...")
    # Open and read csv
    oldvnums = []
    try:
        with open(CLOSEDVCSVFILE, 'r') as f:
            vcsv = csv.reader(f)
            fields = next(vcsv)
            if fields == closed_csvfields:
                print('Read CSV: %d fields' % len(fields))
            else:
                raise Exception(
                    "CSV fields mismatch. Please provide a different/empty CSV file.")
            for row in vcsv:
                oldvnums.append(int(row[0]))
    except FileNotFoundError:  # create csv file
        with open(CLOSEDVCSVFILE, 'w') as f:
            vcsv = csv.writer(f)
            vcsv.writerow(closed_csvfields)
            print("Created csv: %d fields" % len(closed_csvfields))
    oldvnums = set(oldvnums)
    print("%d entries read from csv" % len(oldvnums))

    # Gather Closed Violations on webpage
    currvnums = []
    for row in closedtable.find_all('a', class_='myhyperlink'):
        currvnums.append(int(row.text))
    currvnums = set(currvnums)
    print("%d entries found on webpage" % len(currvnums))

    # Find and write new entries
    newvnums = currvnums - oldvnums
    print("**** %d new entries identified ****" % len(newvnums))
    with open(CLOSEDVCSVFILE, 'a') as f:
        vcsv = csv.writer(f)
        for entry in closedtable.find_all("tr"):
            if entry.find("a") is not None and int(entry.find('a').text) in newvnums:
                vcsv.writerow(closed_violation_details(entry, browser))

    # Logout
    print("Logging out...          ")
    logout(browser)
except:
    traceback.print_exc()
finally:
    browser.quit()
    print("Operation Finished.")
