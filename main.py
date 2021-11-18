import configparser
import os
import json
import time
import shutil
from pathlib import Path
import uuid

from api.scraping.scrapers import CADORSPageScrapper, CADORSQueryScrapper


def main(scraping_config):
    # print("Starting to scrape the occurance links of all CADORS incidents")

    # # getting occurances
    # query_scrapper = CADORSQueryScrapper(scraping_config)
    # query_scrapper.scrape_occurances()

    # print("Completed scrapping occurance urls.")

    # print("Starting to scrape page data.")

    # @gurashish start from over here....

    Path(scraping_config["page_data_output_folder"]).mkdir(parents=True, exist_ok=True)
    Path(scraping_config["scraped_occurances_folder"]).mkdir(
        parents=True, exist_ok=True
    )
    cnt = 0

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
                # print('GURDEBUG--------------')
                # print('occurence',occurance)
                obj = CADORSPageScrapper(url=occurance, config=scraping_config)
                file_data.append(obj.scrape_data())
                # print("\nGURdata\n", file_data)
                cnt += 1
                print(cnt)

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


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    scraping_config = dict(config.items("scraping"))

    main(scraping_config)
