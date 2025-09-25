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
host = 'http://127.0.0.1'

def main():
    auth = UserAuth(base_url, email, password, token_file)
    pm = ProfileManagement(auth)
    options = webdriver.ChromeOptions()
    limiter = RateLimiter(max_requests=2, period=10)


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

    if len(profile_list) < 4:
        for i in range(4 - len(profile_list)):
            with limiter.limit():
                pm.create_basic_profile('test', folder_id)
    profile_ids = [profile.get("profile_id") for profile in profile_list]  
      
    print(f"folder id: {folder_id}")
    print(f"profile id: {profile_ids}")
    print(len(profile_list))

    data_list = []
    for profile_id in profile_ids:
        with limiter.limit():
            port = pm.start_profile(profile_id, folder_id)
            print(port)
            selenium_url = f'{host}:{port}'
            driver = webdriver.Remote(command_executor=selenium_url, options=options)

            data = {
                "profile_id": profile_id,
                "port": port,
                "driver": driver
            }

            data_list.append(data)
    print(data_list)

    for data in data_list:
        with limiter.limit():
            driver = data.get("driver", None)
            try:
                driver.get("https://www.wine-searcher.com")
            except Exception as e:            
                print(f"Error opening url: {e}")

    for profile_id in profile_ids:
        with limiter.limit():
            pm.stop_profile(profile_id)
main()