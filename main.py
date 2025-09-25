from user_auth import UserAuth
from profile_management import ProfileManagement
from rate_limiter import RateLimiter
import os
import json
import time
from selenium import webdriver
from decouple import config

token_file = 'token.json'
email = config("EMAIL")
password = config("PASSWORD")
base_url = 'https://api.multilogin.com'

def main():
    auth = UserAuth(base_url, email, password, token_file)
    pm = ProfileManagement(auth)
    options = webdriver.ChromeOptions()
    limiter = RateLimiter(max_requests=5, period=10)


    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            tokens = json.load(f)
        if tokens["token_expiration"] > time.time():
            # reuse saved tokens
            auth.access_token = tokens["access_token"]
            auth.refresh_token = tokens["refresh_token"]
            auth.token_expiration = tokens["token_expiration"]
        else:
            # expired → refresh or re-login
            tokens = auth.login()
            with open(token_file, "w") as f:
                json.dump(tokens, f)
    else:
        # first run → login
        tokens = auth.login()
        with open(token_file, "w") as f:
            json.dump(tokens, f)

    with limiter.limit():
        folders = pm.get_folders()
    folder_id = folders[0].get("folder_id")

    with limiter.limit():
        profile_list = pm.get_profiles(folder_id)

    if len(profile_list) == 0:
        with limiter.limit():
            pm.create_basic_profile('test', folder_id)
    profile_id = profile_list[0].get("profile_id")  
      
    print(f"folder id: {folder_id}")
    print(f"profile id: {profile_id}")
    print(len(profile_list))
    
    with limiter.limit():
        port = pm.start_profile(profile_id, folder_id)

    try:
        selenium_url = f'http://127.0.0.1:{port}'
        driver = webdriver.Remote(command_executor=selenium_url, options=options)
        driver.get('https://www.wine-searcher.com')
        driver.quit()
    except Exception as e:
        print(f"Error: {e}")
        
main()