import uuid
import os
import json
from bs4 import BeautifulSoup
from .utils import Utils
from pathlib import Path
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class CADORSQueryScrapper:
    def __init__(self, config: dict):
        """
        [
            Class to fetch page urls from the search page
        ]

        Args:
            config ([dict]): [Configuration path to provide configuration details]
        """
        self.driver = None
        self.options = {}
        self.occurance_url = None
        self.items_per_page = -1
        self.current_page = int(config["url_scrape_start"])
        self.current_item = 0
        self.occurances = -1
        self.current_batch = 1
        self.url_scrape_limit = int(config["url_scrape_limit"])
        self.batch_size = int(config["batch_size"])
        self.base_url = config["base_url"] + config["query_page_extension"]
        self.driver_path = config["driver_path"]
        self.occurances_output_folder = config["occurances_output_folder"]

        # checking if output folder exists else creating one
        Path(config["occurances_output_folder"]).mkdir(parents=True, exist_ok=True)

        self.urls = []

    def _get_summary_results(self):
        """
        [
            Function to get summary results after searching
        ]

        Returns:
            [tuple]: [
                (
                    driver -> Driver of the particular web page
                    driver.current_url -> Current url of the driver
                    int(Utils.get_numbers(occurance_text)[-1]) -> Get number of occurances on the page
                    int(ids_per_page_element.get_attribute("value")) -> Get number of ids per page
                )
            ]
        """
        options = Options()
        options.headless = False
        options.add_argument("--window-size=1920,1200")

        driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
        driver.get(self.base_url)

        # the logic of date ranges goes here

        search_btn = driver.find_element(By.ID, "btn_SearchTop")
        search_btn.click()

        wait = WebDriverWait(driver, 240)
        # print("Waiting to get Summary results....")
        wait.until(
            lambda x: x.find_element(
                By.XPATH, "//*[contains(text(), ': Summary Results')]"
            )
        )

        occurance_element = driver.find_element(
            By.XPATH, "//div[@class='col-md-6 mrgn-bttm-md form-inline']"
        )
        occurance_text = occurance_element.text

        ids_per_page_element = driver.find_element(By.ID, "hidRecordsPerPage")

        input_top = driver.find_element(By.ID, "txtTopPageNumber")
        driver.execute_script("arguments[0].value=''", input_top)
        input_top.send_keys(str(self.current_page))
        go_btn = driver.find_element(By.ID, "btnGoToPage")
        go_btn.click()
        # print(driver.current_url)

        return (
            driver,
            options,
            driver.current_url,
            int(Utils.get_numbers(occurance_text)[-1]),
            15
            # int(ids_per_page_element.get_attribute("value")),
        )

    def scrape_occurances(self):
        """
        [
            Function to scrape page occurances on the page
        ]
        """
        (
            self.driver,
            self.options,
            self.occurance_url,
            self.occurances,
            self.items_per_page,
        ) = self._get_summary_results()

        while self.current_page <= self.occurances:
            # the scraping of all the occurances hasn't completed yet.

            element = self.driver.find_element(
                By.ID,
                "ContentPlaceHolder1_rpt_CADORS_hyp_CADORSNum_"
                + str(self.current_item),
            )
            self.urls.append(element.get_attribute("href"))

            self.current_item += 1
            # print(f"URLS fetched: {self.urls[-1]}")
            # print(self.current_item)

            if self.current_item == self.items_per_page:
                # End of page

                # writing it to files
                if self.current_batch == self.batch_size:
                    # print("Printing the occurances")
                    self._write_occurances_files(self.urls)
                    self.urls = []
                    self.current_batch = 0

                print("CURRENT PAGE: ", self.current_page)
                if self.current_page == self.url_scrape_limit:
                    if self.urls:
                        self._write_occurances_files(self.urls)
                    break

                next_button = self.driver.find_element(By.ID, "btnNextTop")
                # print("Clicking the next button")
                next_button.click()

                wait = WebDriverWait(self.driver, 240)
                wait.until(
                    lambda x: int(
                        Utils.get_numbers(
                            x.find_element(
                                By.XPATH,
                                "//div[@class='col-md-6 mrgn-bttm-md form-inline']",
                            ).text
                        )[0]
                    )
                    == self.current_page + 1
                )
                self.current_page += 1
                self.current_batch += 1
                self.current_item = 0

    def _write_occurances_files(self, occurances: list):
        """
        Function to write all occurance urls to files

        Args:
            occurances (list): [List of all occurance urls for incidents]
        """
        # print("Trying to print the occurances")
        with open(
            os.path.join(self.occurances_output_folder, str(uuid.uuid4()) + ".json"),
            "w",
        ) as f:
            json.dump(occurances, f)


class CADORSPageScrapper:
    def __init__(self, url: str, config: dict) -> None:
        """
        [
            Class to scrape information of a particular page
        ]
        Args:
            url ([str]): [Url of the page to scrape information from]
            config ([dict]): [Configuration path to provide configuration details]
        """
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")

        driver = webdriver.Chrome(
            executable_path=config["driver_path"], options=options
        )
        driver.get(url)

        self.driver = driver
        self.url = url
        self.items_parsed = 0
        self.page_data = {}

    def scrape_data(self):
        """
        Function to scrape data from the page
        """

        cadors_report_soup = BeautifulSoup(self.driver.page_source, "html5lib")
        primary_panel_body = cadors_report_soup.find(
            "section", attrs={"class": "mrgn-bttm-sm panel panel-primary"}
        )

        record_no = int(
            Utils.get_numbers(
                primary_panel_body.find(
                    "header", attrs={"class": "text-danger"}
                ).getText()
            )[0]
        )
        self.page_data["record_no"] = record_no

        # fetching the main panel body
        panel_body = primary_panel_body.find("div", attrs={"class": "panel-body"})

        # fetching CADORS Number and Occurance Category
        cadors_row = panel_body.find("div", attrs={"class": "row"})
        (
            cadors_number_txt,
            cadors_number_val,
            occurance_category_txt,
            occurance_category_val,
        ) = cadors_row.findAll("div", attrs={"class": "col-md-3 mrgn-bttm-sm"})

        cadors_number_val = Utils.clean_text(cadors_number_val.text)
        occurance_category_val = Utils.clean_text(occurance_category_val.text)

        temp = panel_body.find("div", attrs={"class": "row"})
        t = 0
        for ele in temp.findAll("div", attrs={"class": "col-md-3 mrgn-bttm-sm"}):
            x = ele.text
            x = re.sub(" +", " ", x)
            x = x.strip()
            t += 1
            if t == 2:
                cador_no = x
            if t==4:
                occat=[]
                for li in ele.find('ul'):
                    ltxt = li.text
                    ltxt = re.sub(" +", " ", ltxt)
                    ltxt = ltxt.strip()
                    # print(ltxt,len(ltxt))
                    if len(ltxt)!=0:
                        occat.append(ltxt)
                
        self.page_data["CADORS Number"] = cador_no
        self.page_data['Occurrence Category']= occat
        self.page_data['Occurrence Summary']=[]
        
        
        for ele in panel_body.findAll(
            "section", attrs={"class": "mrgn-bttm-sm panel panel-primary"}
        ):
            head = ele.find("div", attrs={"class": "well well-sm"}).text
            res = re.sub(" +", " ", head)
            res = res.strip()
            # print('\n',res,len(res),'\n')
            if res == "Occurrence Information":
                occurance_information_section_panel_body = ele.find(
                    "div", attrs={"class": "panel-body"}
                )
                key, val = None, None
                cnt = 0

                for row in occurance_information_section_panel_body.findAll(
                    "div", attrs={"class": "row"}
                ):

                    items = row.findAll(
                        "div", class_=["col-md-3 mrgn-bttm-md", "col-md-4 mrgn-bttm-md"]
                    )

                    for item in items:
                        if cnt % 2 == 0:
                            key = Utils.clean_text(item.text)

                        else:
                            val = Utils.clean_text(item.text)

                            self.page_data[key] = val
                        cnt += 1
                        occurance_event_info = occurance_information_section_panel_body.find(
                    "section", attrs={"class": "mrgn-bttm-sm panel panel-primary bullet_left_15px"}
                )
                        # print(occurance_event_info)
                occ_event=[]
                if occurance_event_info.find("ul") is not None:
                    for li in occurance_event_info.find("ul"):
                        ltxt = li.text
                        ltxt = re.sub(" +", " ", ltxt)
                        ltxt = ltxt.strip()
                        if len(ltxt)!=0:
                            occ_event.append(ltxt)
                self.page_data['Occurrence Event Information'] = occ_event
            elif res == "Occurrence Summary":
                a = ele.findAll("div", attrs={"class": "col-md-3 mrgn-bttm-md"})
                for i in a:
                    x = i.text
                    x = re.sub(" +", " ", x)
                    x = x.strip()
                    if x != "Date Entered:" and x != "Narrative:":
                        date = x
                        break
                b = ele.find(
                    "div", attrs={"class": "col-md-8 mrgn-bttm-md width-670px"}
                ).text
                b = re.sub(" +", " ", b)
                summary = b.strip()
                # print('\n','Date:\n',date,'--',len(date),'\n','Summary:\n',summary,'--',len(summary),'\n')
                # os_g.append({"Date": date, "Summary": summary})
                self.page_data["Occurrence Summary"].append({"Date": date, "Summary": summary})
            elif res=='Aircraft Information':
                air_info_single={}
                aircraft_information_section_panel_body = ele.find(
                    "div", attrs={"class": "panel-body"}
                )                          
                key, val = None, None
                for row in aircraft_information_section_panel_body.findAll(
                    "div", attrs={"class": "row"}
                ):
                    items = row.findAll(
                        "div", class_=["col-md-3 mrgn-bttm-md", "col-md-4 mrgn-bttm-md"]
                    )               
                    cnt=0
                    for item in items:
                        if cnt % 2 == 0:
                            key = Utils.clean_text(item.text)
                            air_info_single[key]=[]
                        cnt += 1
                    
                for row in aircraft_information_section_panel_body.findAll(
                    "div", attrs={"class": "row"}
                ):
                    items = row.findAll(
                        "div", class_=["col-md-3 mrgn-bttm-md", "col-md-4 mrgn-bttm-md"]
                    )               
                    cnt=0
                    for item in items:
                        if cnt % 2 == 0:
                            key = Utils.clean_text(item.text)
                        elif cnt % 2 != 0:
                            val = Utils.clean_text(item.text)
                            # print(val)
                            air_info_single[key].append(val)
                        cnt += 1
                        
                air_info_single['Aircraft Event Information']=[]                 
                aircraft_event_info = aircraft_information_section_panel_body.findAll(
                    "section", attrs={"class": "mrgn-bttm-sm panel panel-primary bullet_left_15px"}
                ) 
                for airevent in aircraft_event_info:
                    print(airevent)
                    aircraft_event=[]
                    if airevent.find("ul") is not None:
                        for li in airevent.find("ul"):
                            ltxt = li.text
                            ltxt = re.sub(" +", " ", ltxt)
                            ltxt = ltxt.strip()
                            if len(ltxt)!=0:
                                aircraft_event.append(ltxt)
                    air_info_single['Aircraft Event Information'].append(aircraft_event)
                            
                self.page_data['Aircraft Information']=air_info_single
        return self.page_data
