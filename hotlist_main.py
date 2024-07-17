import os
import re
import pandas as pd
from playwright.sync_api import Page, sync_playwright
import time,warnings
import threading,asyncio
import requests 
from PIL import Image
 
warnings.simplefilter("ignore", category=UserWarning)

class Hotlist:
    def __init__(self):
        self.page = None
        self.base_url = "https://onlyhotlist.in/"
        self.Hotlist_url = "https://onlyhotlist.in/index.php"
        
    def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        This function is used to display the progress bar

        Args:
            iteration (int): iteration number
            total (int): total number
            prefix (str): prefix string
            suffix (str): suffix string
            decimals (int): number of decimals
            length (int): length of the progress bar
            fill (str): fill character
            printEnd (str): print end character

        Returns:
            None
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)

        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        if iteration == total: 
            print(flush=True)
            
    
    def navigate_to_Hotlist(self, current_page: int = 1):
        """
        This function is used to navigate to the Hotlist page

        Returns:
            True: If the function is successful
            Exception: If the function is unsuccessful
        """
        successfull_navigation = False
        while not successfull_navigation:
            try:
                self.page.goto(f"{self.Hotlist_url}?page={current_page}")
                retry_count = 0
                while self.page.locator('[alt="C2C Hotlist"]').all() == []:
                    time.sleep(1)
                    if retry_count == 5:
                        self.page.reload()
                        print("Not Fully Loaded, Reloading the page")
                        retry_count = 0
                successfull_navigation = True
            except Exception as e:
                return e.__str__()
        
    
    def download_image(self, image_url: str, file_name: str):
        """
        This function is used to download the image
        
        Args:
            image_url (str): Image URL
            file_name (str): File name
            
        Returns:
            file_name (str): path of the downloaded image
        """
        
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        file_download = False
        while not file_download:
            try:
                data = requests.get(image_url).content
                f = open(file_name, 'wb')
                f.write(data) 
                f.close()
                file_download = True
            except Exception as e:
                pass
         
        return file_name
            
    def scrape_Hotlist_data(self, page: Page):
        """
        This function is used to scrape the Hotlist site for data
        
        Args:
            page (Page): Page object
            
        Returns:
            scraped_data (dict): Dictionary of scraped data
        """
        self.navigate_to_Hotlist(1)
        #scrolling to the bottom of the page
        scroll = False
        while not scroll:
            try:
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(1)
                if page.locator('//ul[@class="pagination pagination-sm justify-content-center"]/li').all_inner_texts() != []:
                    scroll = True
                else:
                    time.sleep(1)
                    scroll = False
            except Exception as e:
                pass
        
        list_of_pages = page.locator('//ul[@class="pagination pagination-sm justify-content-center"]/li').all_inner_texts()
        last_page = max([int(page) for page in list_of_pages if page.isdigit()])
        data = page.locator('[data-aos="zoom-out"]').all()
        scraped_data = []
        current_page = 1
        while current_page < last_page + 1:
            self.navigate_to_Hotlist(current_page)
            get_target_data = False
            while not get_target_data:
                try:
                    target_data = page.locator('[data-aos="zoom-out"]').all()
                    if target_data != []:
                        get_target_data = True
                    else:
                        time.sleep(1)
                        get_target_data = False
                except Exception as e:
                    pass
            index = 0
            for data in target_data:
                get_vendor_data = False
                while not get_vendor_data:
                    try:
                        vender_data = data.locator('div[class="card"]').locator('div').locator('ul').locator('li').all_inner_texts()
                        if vender_data != []:
                            get_vendor_data = True
                        else:
                            time.sleep(1)
                            get_vendor_data = False
                    except Exception as e:
                        pass
                    
                thread_list = []
                for vendor in vender_data:
                    get_vendor_data = False
                    while not get_vendor_data:
                        try:
                            if "Vendor Name:" in vendor:
                                vendor_name = vendor.split(":")[1]
                            if "Vendor Number:" in vendor:
                                vendor_code = vendor.split(":")[1]
                            if "Vendor Email:" in vendor:
                                vendor_email = vendor.split(":")[1]
                            if "uploaded on:" in vendor:
                                vendor_date = vendor.split(":")[1]
                            get_vendor_data = True
                        except Exception as e:
                            pass
                        
                get_download_image = False
                while not get_download_image:
                    try:
                        download_image = data.locator('div[class="card"]').locator('a').locator('img').get_attribute("src")
                        download_image_src = self.base_url + download_image
                        file_name = download_image_src.split("/")[-1]
                        file_name = file_name.split(".")[0]
                        file_name = f"{file_name} ({vendor_email}_{vendor_date}).jpg"
                        current_path = os.path.dirname(os.path.abspath(__file__))
                        file_path = os.path.join(current_path, "downloads", f"Page No-{current_page}")
                        os.makedirs(file_path, exist_ok=True)
                        file_name = os.path.join(file_path, file_name)
                        thread = threading.Thread(target=self.download_image, args=(download_image_src, file_name))
                        thread.start()
                        thread_list.append(thread)
                        get_download_image = True
                    except Exception as e:
                        pass
                    finally:
                        if len(thread_list) >= len(target_data):
                            for thread in thread_list:
                                thread.join()
                            get_download_image = True
                    
                
                data_dict = {
                    "Vendor Name": vendor_name,
                    "Vendor Code": vendor_code,
                    "Vendor Email": vendor_email,
                    "Vendor Data Uploaded On": vendor_date,
                    "Download Image": file_name
                }
                scraped_data.append(data_dict)
                
                self.progress_bar(index, len(target_data), prefix = f'Page-{current_page}-Progress:', suffix = 'Complete', length = 70, printEnd = "\r")
                
                index += 1
            current_page += 1
        return scraped_data
        
    def save_to_excel(self):
        """
        This function is used to save the Hotlist datas to an excel file
        
        Returns:
            None
        """
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_path, "Hotlist Data")
        os.makedirs(file_path, exist_ok=True)
        file_name = os.path.join(file_path, "Hotlist Data.xlsx")
        all_df = pd.DataFrame()
        data = self.scrape_Hotlist_data(self.page)
        for index, data in enumerate(data):
            df = pd.DataFrame(data, index=[index])
            all_df = pd.concat([all_df, df], axis=0)
        all_df.to_excel(file_name, index=False)
        print(f"Data saved to {file_name}")
    
    def remove_all_jpg_files(self):
        """
        This function is used to remove all the jpg files
        
        Returns:
            None
        """
        current_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_path, "downloads")
        for folder in os.listdir(file_path):
            folder_path = os.path.join(file_path, folder)
            for file in os.listdir(folder_path):
                if file.endswith(".jpg"):
                    os.remove(os.path.join(folder_path, file))
            os.rmdir(folder_path)
        print("All JPG files removed")
        
    def run(self):
        """
        This function is used to run the Hotlist script
        
        Returns:
            None
        """
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch_persistent_context(user_data_dir="Hotlist Data", headless=False, args=["--start-maximized"],downloads_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads"),accept_downloads=True)
            page = browser.pages[0]
            self.page = page
            self.save_to_excel()
        
if __name__ == "__main__":
    
    Hotlist = Hotlist()
    Hotlist.remove_all_jpg_files()
    Hotlist.run()
    
        
        