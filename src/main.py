from WebScrapper.scrapper import Scrappers 
from Configs.selenium_config import driver



def main():
    print("\n<=== MENU ===>\n1 - EXTRACT DATASET\n2 - SHOW DATASET\n3 - TRANSFER DATASET TO SHEET\n4 - GENERATE AND SEND PERSONALIZED EMAILS\n5 - PRODUCTION MODE (It'll do All 4 steps)\n0 - Exit the script \n<=== END ===>\n")
    scrapper = Scrappers()
    mode = 1

    try:
        if mode == 0:
            print("\n<== Terminated ==>\n")
            driver.close()
        elif mode == 1:
            print("\n<== EXTRACTION STARTED ==>\n")

            # business_name = input("Enter the Business Name: ")
            business_name = 'ドローン免許取得'
            location = input("Enter the Location: ")
            scrapper.scrape(business_name, location)
            
            print("\n<== EXTRACTED COMPLETED ==>\n")
            main()
        
        else:
            print("<== DEVELOPMENT MODE - STARTED ==>")
            
            print("<== DEVELOPMENT MODE - FINISHED ==>")
            main()
    except Exception as error:
        print(error)

main()
