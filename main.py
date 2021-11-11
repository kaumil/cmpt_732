import configparser
import os
import json
import gzip
import pickle
import uuid
import asyncio
from pathlib import Path
from api.scraping.scrapers import CADORSPageScrapper, CADORSQueryScrapper


def main(scraping_config):
    print("Starting to scrape the occurance links of all CADORS incidents")

    # getting occurances
    query_scrapper = CADORSQueryScrapper(scraping_config)
    asyncio.run(query_scrapper.scrape_occurances())

    print("Completed scrapping occurance urls.")

    print("Starting to scrape page data.")

    Path(scraping_config["page_data_output_folder"]).mkdir(parents=True, exist_ok=True)
    cnt = 0

    for file in os.listdir(scraping_config["occurances_output_folder"]):
        # for file in fnames:
        with open(
            os.path.join(scraping_config["occurances_output_folder"], str(file)), "rb"
        ) as f:
            occurances = pickle.load(f)
            file_data = []
            for occurance in occurances:
                print(cnt)
                obj = CADORSPageScrapper(url=occurance, config=scraping_config)
                file_data.append(obj.scrape_data())
                cnt += 1

            json_str = json.dumps(file_data) + "\n"
            json_bytes = json_str.encode("utf-8")

            with gzip.open(
                os.path.join(
                    scraping_config["page_data_output_folder"], str(uuid.uuid4())
                ),
                "w",
            ) as fout:
                fout.write(json_bytes)

    print("Completed scraping all page data")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    scraping_config = dict(config.items("scraping"))

    main(scraping_config)
