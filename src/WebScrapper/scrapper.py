import re
import time
import traceback
import json  # Ensure you import json for saving the data
import requests
from bs4 import BeautifulSoup
from Configs.selenium_config import driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin
import csv
import os  # Make sure to import the os module

class Scrappers:
    def scrape(self, industry_name, location):
        try:
            print("\n[LOG] - LOADING ITEMS\n")
            scrapeDetail = ScrapeDetails()
            query = f'{industry_name} in {location}' if industry_name and location else f'{industry_name} {location}'
            driver.get(f'https://www.google.com/maps/search/{query}')

            # Initialize the count variable
            count = 0

            scrollableTable = driver.find_element(
                By.CSS_SELECTOR, "#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd")

            while True:
                scrollableTable.send_keys(Keys.END)  # MAX - 120 Items
                if driver.find_elements(By.CSS_SELECTOR, "#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd.QjC7t > div.m6QErb.tLjsW.eKbjU > div > p > span > span"):
                    if driver.find_elements(
                            By.CSS_SELECTOR, "#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.RiRi5e.Hk4XGb.Yt0HSb > div > button"):
                        driver.find_element(
                            By.CSS_SELECTOR, "#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div.RiRi5e.Hk4XGb.Yt0HSb > div > button").click()
                    break
            print("\n[LOG] - ITEMS LOADED\n")
            soup = BeautifulSoup(driver.page_source, 'lxml')
            res = soup.select("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div:not(.TFQHme):not(.m6QErb) > div > a")
            links = [link.attrs['href'] for link in res]
            print(f'{len(links)} ITEMS FOUND')
            result = []

            print("\n[LOG] - EXTRACTING DATA \n")
            for link in links:
                if count == 5:
                    break
                driver.get(link)
                print(f"\n[LOG] -  VISITING : {link[0:25]}... \n")
                content = driver.page_source
                soup = BeautifulSoup(content, 'lxml')
                print("\n[LOG] - SOURCE PAGE EXTRACTED\n")
                business_data = scrapeDetail.scrape_data(soup)
                # business_data["google_map_link"] = link
                business_data["email"] = scrapeDetail.scrape_email(business_data["Website"]) if business_data["Website"] != 'null' else 'null'
                business_data["status"] = "null"
                print("\n[LOG] - DETAILS EXTRACTED\n")
                result.append(business_data)
                # store.insertOne([
                #     list(business_data.values())
                # ]) - uncomment this to add data to the google sheet on each iteration
                count += 1

            print("\n[LOG] - DATASET LOADED\n")
            # with open('business_data.json', 'w', encoding='utf-8') as f:
            #     json.dump(result, f, ensure_ascii=False, indent=4)
            
            csv_file_path = f"{industry_name}.csv"

            # Ensure the file doesn't exist yet and is being created
            if not os.path.exists(csv_file_path):
                print(f"File '{csv_file_path}' does not exist, creating it now...")

            # Get the keys (headers) from the first dictionary in the result
            keys = result[0].keys()

            # Write the data to the CSV file
            try:
                with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    
                    # Write the header (column names)
                    writer.writeheader()
                    
                    # Write the rows of data
                    writer.writerows(result)
                
                print(f"Data has been successfully written to '{csv_file_path}'")
                
            except Exception as e:
                print(f"An error occurred: {e}")
            print("\n[LOG] - EXTRACTION COMPLETED\n")
        except Exception as e:
            print(f"[ERROR] - An error occurred: {e}")
            traceback.print_exc()
            time.sleep(3)


class ScrapeDetails:
    def scrape_data(self, soup):
        try:
            print("\n[LOG] - EXTRACTING DETAILS\n")
            business_data = {
                "BusinessName": "null",
                "Address": "null",
                "PhoneNumber": "null",
                "Website": "null",
                "Category": "null",
            }
            base_selector = 9
            for i in range(7, 10):
                if len(soup.select(f'#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({i}) > div')) > 1:
                    base_selector = i
                    break
            length = soup.select(f'#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div')
            name_selector = soup.select("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div:nth-child(1) > h1")
            category_selector = soup.select("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div.LBgpqf > div > div:nth-child(2) > span > span > button")
            ratings_selector = soup.select("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div.LBgpqf > div > div.fontBodyMedium.dmRWX > div.F7nice > span:nth-child(1) > span:nth-child(1)")
            reviews_selector = soup.select("#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div.LBgpqf > div > div.fontBodyMedium.dmRWX > div.F7nice > span:nth-child(2) > span > span")
            business_data["BusinessName"] = name_selector[0].text if name_selector else "null"
            print(f"\n[LOG] - Name: {business_data['BusinessName']}\n")

            # Extract phone number
            phone_button = soup.find('button', {'aria-label': lambda x: x and x.startswith('Phone:')})
            business_data["PhoneNumber"] = phone_button['aria-label'].split('Phone: ')[-1] if phone_button else 'null'

            # Extract address
            address_button = soup.find('button', {'aria-label': lambda x: x and x.startswith('Address:')})
            business_data["Address"] = address_button['aria-label'].split('Address: ')[-1] if address_button else 'null'

            # Extract website
            website_link = soup.find('a', {'aria-label': lambda x: x and x.startswith('Website:')})
            business_data["Website"] = website_link['href'] if website_link else 'null'

            # for i in range(3, len(length)):
            #     src_link = None
            #     if soup.select(f'#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div.cXHGnc > div > img'):
            #         src_link = soup.select(f'#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div.cXHGnc > div > img')[0].attrs['src']
            #     elif soup.select(f'#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > a > div > div.cXHGnc > div > img'):
            #         src_link = soup.select(f'#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > a > div > div.cXHGnc > div > img')[0].attrs['src']
            #     if src_link:
            #         print("HEREEEEEEEEEEEEEEEEEEEEEE")
            #         if src_link == "//www.gstatic.com/images/icons/material/system_gm/2x/place_gm_blue_24dp.png":
            #             print("[LOG] - ADDRESS Found")
            #             business_data["Address"] = soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div:nth-child(2) > div")[0].text if soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div:nth-child(2)") else soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > a > div > div:nth-child(2) > div")[0].text
            #         elif src_link == "//www.gstatic.com/images/icons/material/system_gm/2x/public_gm_blue_24dp.png":
            #             print("[LOG] - WEBSITE FOUND")
            #             business_data["Website"] = soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div:nth-child(2) > div")[0].text if soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div:nth-child(2)") else soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > a > div > div:nth-child(2) > div")[0].text
            #         elif src_link == "//www.gstatic.com/images/icons/material/system_gm/2x/phone_gm_blue_24dp.png":
            #             print("[LOG] - PHONE NUMBER FOUND")
            #             business_data["PhoneNumber"] = soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div:nth-child(2) > div")[0].text if soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > button > div > div:nth-child(2)") else soup.select(f"#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child({base_selector}) > div:nth-child({i}) > a > div > div:nth-child(2) > div")[0].text

            business_data["Category"] = category_selector[0].text if category_selector else "null"
            # business_data["Rating"] = ratings_selector[0].text if ratings_selector else "null"
            # business_data["ReviewCount"] = reviews_selector[0].text[1:-1] if reviews_selector else "null"
            return business_data
        except Exception as error:
            print(f"[ERROR] - An error occurred: {error}")
            return None

    def scrape_email(self, url):
        try:
            # Ensure the URL is correctly formatted
            if not url.startswith('http://') and not url.startswith('https://'):
                url = f"https://{url}"

            print(f"\n[LOG] - EXTRACTING EMAIL ADDRESS FROM {url}\n")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find emails on the main page
            emails = self.extract_emails(soup)

            # If no email found, try to crawl for contact pages
            if not emails:
                contact_page_url = self.find_contact_page(soup, url)
                if contact_page_url:
                    print(f"[LOG] - Crawling Contact Page: {contact_page_url}")
                    response = requests.get(contact_page_url, timeout=10)
                    contact_soup = BeautifulSoup(response.content, 'lxml')
                    emails = self.extract_emails(contact_soup)

            if emails:
                result = re.sub(r'\d', '', emails[0])  # Remove digits from the email address
                print(f"\n[LOG] - EMAIL FOUND : {result}")
                return result
            else:
                print(f'[LOG] - EMAIL NOT FOUND')
                return 'null'
                
        except requests.RequestException as error:
            print(f"[ERROR] - Request error: {error}")
            return 'null'
        except Exception as error:
            print(f"[ERROR] - An unexpected error occurred: {error}")
            return 'null'

    def extract_emails(self, soup):
        """Extract emails from a page using both regex and mailto links."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        
        # Find emails in plain text
        emails = re.findall(email_pattern, soup.text)

        # Find emails in mailto links
        for mailto_link in soup.select('a[href^=mailto]'):
            mailto_email = mailto_link['href'].replace('mailto:', '').strip()
            if re.match(email_pattern, mailto_email):
                emails.append(mailto_email)
        
        return list(set(emails))  # Remove duplicates

    def find_contact_page(self, soup, base_url):
        """Find potential contact pages by looking for common 'Contact Us' links."""
        possible_keywords = ['contact', 'お問い合わせ', 'support', 'help', 'faq', 'お問い合わせ']
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.text.lower()

            # Check if the href or text contains contact-related keywords
            if any(keyword in href for keyword in possible_keywords) or any(keyword in text for keyword in possible_keywords):
                contact_url = urljoin(base_url, link['href'])  # Resolve relative URLs
                return contact_url
        
        return None
