import sys
from WebScrapper.scrapper import Scrappers
from Configs.selenium_config import driver

def main(business_name, location):
    print("\n<== EXTRACTION STARTED ==>\n")
    scrapper = Scrappers()
    
    scrapper.scrape(business_name, location)
    
    print("\n<== EXTRACTION COMPLETED ==>\n")
    driver.close()

if __name__ == "__main__":
    business_name = sys.argv[1]  # Get business name from command line
    location = sys.argv[2]  # Get location from command line
    main(business_name, location)
