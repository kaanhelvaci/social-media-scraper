from playwright.sync_api import sync_playwright
import time
import pandas as pd
import re

text_list = []

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
user_name = "" # Bu alana kullanıcı adı gelir.
password = ""  # Bu alana parola gelir.

def find_keys(data, key_to_find):
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_to_find:
                if (isinstance(value, str) and not url_pattern.search(value)) or isinstance(value, int):
                    results.append(value)
            elif isinstance(value, (dict, list)):
                results.extend(find_keys(value, key_to_find))

    elif isinstance(data, list):
        for item in data:
            results.extend(find_keys(item, key_to_find))

    return results

def scroll():

    def check_json(response):
        if "UserTweets" in response.url:
            json_body = response.json()
            text = find_keys(json_body,"full_text")
            text_list.extend(text)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size(
            {"width":1200, "height":1000}
        )
        page.goto("") # Bu alana URL gelir.
        time.sleep(3)
        page.wait_for_load_state("networkidle")
        page.click('span:text("Giriş yap")')
        time.sleep(3)
        page.fill('input[name="text"]', user_name)
        time.sleep(3)
        page.click('span:text("İleri")')
        time.sleep(3)
        page.fill('input[name="password"]', password)
        time.sleep(3)
        try:
            page.wait_for_selector("#LoginForm_Login_Button", state="visible", timeout=10000)
            button = page.query_selector("#LoginForm_Login_Button")
            button.click()
        except Exception as e:
            print("Buton görünür değil veya tıklanamadı:", e)
            print("Lütfen butona manuel olarak tıklayın.")
        page.wait_for_timeout(15000)
        time.sleep(3)
        
        page.on("response", lambda response: check_json(response))
        for x in range(1,50):
            page.keyboard.press("End")
            time.sleep(3)
        time.sleep(5)
        browser.close()

def main():
    scroll()
    df = pd.DataFrame(text_list, columns=["Tweet"])
    df.to_excel("data.xlsx", index=False)

if __name__ == "__main__":
    main()
