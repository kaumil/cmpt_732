import asyncio
import time
import uuid
import os
import pickle
from bs4 import BeautifulSoup
from .utils import Utils
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException


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
        self.occurance_url = None
        self.items_per_page = -1
        self.current_page = 1
        self.current_item = 0
        self.occurances = -1
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
        options.headless = True
        options.add_argument("--window-size=1920,1200")

        driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
        driver.get(self.base_url)

        # the logic of date ranges goes here

        search_btn = driver.find_element(By.ID, "btn_SearchTop")
        search_btn.click()

        wait = WebDriverWait(driver, 240)
        wait.until(
            lambda x: x.find_element(
                By.XPATH, "//*[contains(text(), ': Summary Results')]"
            )
        )

        driver.get(driver.current_url)

        occurance_element = driver.find_element(
            By.XPATH, "//div[@class='col-md-6 mrgn-bttm-md form-inline']"
        )
        occurance_text = occurance_element.text

        ids_per_page_element = driver.find_element(By.ID, "hidRecordsPerPage")

        return (
            driver,
            driver.current_url,
            int(Utils.get_numbers(occurance_text)[-1]),
            int(ids_per_page_element.get_attribute("value")),
        )

    async def scrape_occurances(self):
        """
        [
            Function to scrape page occurances on the page
        ]
        """
        (
            self.driver,
            self.occurance_url,
            self.occurances,
            self.items_per_page,
        ) = self._get_summary_results()

        while self.current_item <= self.occurances:
            # the scraping of all the occurances hasn't completed yet.

            element = self.driver.find_element(
                By.ID,
                "ContentPlaceHolder1_rpt_CADORS_hyp_CADORSNum_"
                + str(self.current_item),
            )
            self.urls.append(element.get_attribute("href"))

            self.current_item += 1

            if self.current_item == self.items_per_page:

                # only for local will have to change for lambda
                await self._write_occurances_files(self.urls)
                self.urls = []
                # End of page
                # Change url code goes here

                next_button = self.driver.find_element(By.ID, "btnNextTop")
                next_button.click()

                time.sleep(10)
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
                self.driver.get(self.driver.current_url)
                self.current_page += 1
                print(self.driver.current_url)
                self.current_item = 0

    async def _write_occurances_files(self, occurances: list):
        """
        Function to write all occurance urls to files

        Args:
            occurances (list): [List of all occurance urls for incidents]
        """
        print("Trying to print the occurances")
        with open(
            os.path.join(self.occurances_output_folder, str(uuid.uuid4())), "wb"
        ) as f:
            pickle.dump(occurances, f)


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

        (
            occurance_information_section,
            aircraft_information_section,
            occurance_summary,
        ) = panel_body.findAll(
            "section", attrs={"class": "mrgn-bttm-sm panel panel-primary"}
        )

        occurance_information_section_panel_body = occurance_information_section.find(
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

    async def _write_data(self):
        pass
