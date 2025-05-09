import ssl
import pandas as pd
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Set the SSL context to avoid SSL errors
ssl._create_default_https_context = ssl._create_unverified_context

# Dictionary to map categories to their corresponding codes
category_code_mapping = {
    'architecture': 'ARCH',
    'city': 'CITIES',
    'clothing': 'CLOTH',
    'dance and music and visual arts': 'DANCE',
    'food and drink': 'FOOD',
    'nature': 'NATUR',
    'people and action': 'PEOPLE',
    'religion and festival': 'RELIG',
    'utensil and tool': 'TOOLS'
}

# Dictionary to map countries to their corresponding codes
country_code_mapping = {
    'Korea': 'KOR',
    'China': 'CHN',
    'Nigeria': 'NGA',
    'India': 'IND',
    'Mexico': 'MEX',
    'Poland': 'POL',
    'Jordan': 'JOR',
    'Egypt': 'EGY',
    'France': 'FRA',
    'United States': 'US'
}

# -------------------- Function to scroll to the bottom of the page -------------------- 
def scroll_to_bottom(driver, SCROLL_PAUSE_TIME):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            try:
                driver.find_element(By.CSS_SELECTOR, ".mye4qd").click()
                print("🔄 'Load more' button clicked")
            except:
                print("⏹ No more scrolling available")
                break
        last_height = new_height

#-------------------- Function to search and collect images -------------------- 
def search_and_collect_images(country, category, driver, MAX_IMAGES=100):
    searchKey = f"{country} {category}"
    image_urls = []
    collected_images = 0
    cnt = 0

    driver.get("https://www.google.co.kr/imghp?hl=en&tab=wi&authuser=0&ogbl")
    elem = driver.find_element(By.NAME, "q")
    elem.send_keys(searchKey)
    elem.send_keys(Keys.RETURN)
    print(f"🔍 Search keyword: {searchKey}")
    time.sleep(1)
    while collected_images < MAX_IMAGES:
        time.sleep(1)
        scroll_to_bottom(driver, SCROLL_PAUSE_TIME=1)
        images = driver.find_elements(By.CSS_SELECTOR, ".ob5Hkd")
        print(f"🖼️ Start collecting images (Total {len(images)} images found)")

        for image in images:
            cnt += 1
            if collected_images >= MAX_IMAGES:
                break
            try:
                image.click()
                time.sleep(2)
                imgUrl = driver.find_element(
                    By.XPATH,
                    '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]').get_attribute("src")
                print(f'{cnt}th : {imgUrl}')
                if imgUrl and imgUrl not in image_urls:
                    image_urls.append(imgUrl)
                    collected_images += 1
            except Exception as e:
                print(f"❌ Failed to download image: {e}")
                pass
            time.sleep(1)
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".pnid")
            next_button.click()
            print("➡️ Moving to the next page")
        except Exception as e:
            print("⏹ No more pages available")
            break

    return image_urls

#-------------------- Function to save the collected image URLs to a CSV file --------------------
def save_to_csv(country, category, image_urls):
    category_code = category_code_mapping[category]
    country_code = country_code_mapping[country]
    df = pd.DataFrame({
        "category_code": category_code,
        "country_code": country_code,
        "image_url": image_urls,
        "created_at": [pd.Timestamp.now().isoformat()] * len(image_urls),
        "isEnglish": True,
    })

    # output_file_path = f'{country}/{category.replace(" ", "_")}/gcsd_{country}_{category.replace(" ", "_")}.csv'
    output_file_path = f'./gscd/{country.lower()}/{category}.csv'
    df.to_csv(output_file_path, index=False)
    print(f"✅ {output_file_path} file saved successfully")

#-------------------- Main function to execute the image search and collection for multiple countries and categories
def main():
    countries = ["France", "China", "Nigeria", "India", "Mexico","Poland","United States","Jordan"]
    categories = [
        "architecture",
        "city",
        "clothing",
        "dance and music and visual arts",
        "food and drink",
        "nature",
        "people and action",
        "religion and festival",
        "utensil and tool"
    ]

    driver = webdriver.Chrome()

    try:
        for country in countries:
            for category in categories:
                image_urls = search_and_collect_images(country, category, driver)
                save_to_csv(country, category, image_urls)
    finally:
        print("🚪 Closing browser")
        driver.close()

if __name__ == "__main__":
    main()