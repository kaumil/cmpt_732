import configparser
import os
import json
import time
import shutil
import logging
import uuid
import time

from pathlib import Path
from api.scraping.scrapers import CADORSPageScrapper, CADORSQueryScrapper

URL_SCRAPING_FINISHED = True
OCCURENCE_COUNTER_START = 0

def scrape_urls(scraping_config):
    print("Starting to scrape the occurance links of all CADORS incidents")

    # getting occurances
    query_scrapper = CADORSQueryScrapper(scraping_config)
    query_scrapper.scrape_occurances()

    print("Completed scrapping occurance urls.")


def scrape_occurences(scraping_config):
    Path(scraping_config["page_data_output_folder"]).mkdir(parents=True, exist_ok=True)
    Path(scraping_config["scraped_occurances_folder"]).mkdir(parents=True, exist_ok=True
                                                             )
    cnt = OCCURENCE_COUNTER_START
    
    print("Starting to scrape page data.")

    for file in os.listdir(scraping_config["occurances_output_folder"]):
        # for file in fnames:
        file_data = []
        src = os.path.join(scraping_config["occurances_output_folder"], str(file))
        dest = os.path.join(scraping_config["scraped_occurances_folder"], str(file))
        with open(
            src,
            "r",
        ) as f:
            occurances = json.load(f)  # new logic

            for occurance in occurances:
                
                try:
                    obj = CADORSPageScrapper(url=occurance, config=scraping_config)
                    file_data.append(obj.scrape_data())
                    cnt += 1
                    print('\n', '>>> Processed record #', cnt)
                    
                except Exception as e:
                    print('>>>>>>> ERROR: COULD NOT PROCESS RECORD #', cnt, str(e))
                    logging.error(str(e))
                    time.sleep(5)
                    

        print("Moving file")
        shutil.move(src=src, dst=dest)
        time.sleep(10)

        json_str = json.dumps(file_data)
        # json_bytes = json_str.encode("utf-8")

        with open(
            os.path.join(
                scraping_config["page_data_output_folder"],
                str(uuid.uuid4()) + ".json",
            ),
            "w",
        ) as f:
            f.write(json_str)

    print("Completed scraping all page data")


def main(scraping_config):
    if not URL_SCRAPING_FINISHED:
        scrape_urls(scraping_config)
    scrape_occurences(scraping_config)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    scraping_config = dict(config.items("scraping"))
    logging.basicConfig(filename='log.txt', encoding='utf-8', level=logging.ERROR)

    main(scraping_config)
    