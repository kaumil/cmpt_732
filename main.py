from api.scraping.scrappers import CADORSQueryScrapper, CADORSPageScrapper
import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    scraping_config = dict(config.items("scraping"))
    print(scraping_config)

    # getting occurances
    query_scrapper = CADORSQueryScrapper(scraping_config)
    query_scrapper.scrape_occurances()

    # getting page information
    # driver code for PageScrapper
    url = "https://wwwapps.tc.gc.ca/saf-sec-sur/2/cadors-screaq/rd.aspx?cno%3d%26dtef%3d%26dtet%3d2021-10-24%26otp%3d-1%26ftop%3d%253e%253d%26ftno%3d0%26ijop%3d%253e%253d%26ijno%3d0%26olc%3d%26prv%3d-1%26rgn%3d-1%26tsbno%3d%26tsbi%3d-1%26arno%3d%26ocatno%3d%26ocatop%3d1%26oevtno%3d%26oevtop%3d1%26evtacoc%3d3%26fltno%3d%26fltr%3d-1%26cars%3d-1%26acat%3d-1%26nar%3d%26aiddl%3d-1%26aidxt%3d%26optdl%3d-1%26optcomt%3d%26optseq%3d%26optxt%3d%26opdlxt%3dResults%2bwill%2bappear%2bin%2bthis%2blist%26mkdl%3d-1%26mkxt%3d%26mdldl%3d-1%26mdlxt%3d%26cmkdl%3dC%26cmkxt%3d%26rt%3dQR%26hypl%3dy%26cnum%3d2021Q2922"
    obj = CADORSPageScrapper(url, config)
    obj.scrape_data()
    obj.page_data
