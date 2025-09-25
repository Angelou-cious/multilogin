import requests
from user_auth import UserAuth
from typing import Dict, Any, Optional, List
from requests.exceptions import RequestException


class ProfileManagement:
    def __init__(self, user_auth: UserAuth):
        self.user_auth = user_auth

    def get_folders(self):
        url = f"{self.user_auth.base_url}/workspace/folders"
        headers = self.user_auth.get_auth_header()

        resp = requests.get(url=url, headers=headers)

        resp.raise_for_status()

        folders = resp.json().get("data")
        folders = folders.get("folders")
        results = []

        for folder in folders:
            name = folder.get("name")
            folder_id = folder.get("folder_id")
            
            profile = {
                "name": name,
                "folder_id": folder_id
            }

            results.append(profile)
        return results

    def create_folder(self, name: str, comment: str):

        url = f"{self.user_auth.base_url}/workspace/folder_create"
        headers = self.user_auth.get_auth_header()
        json = {"name": name, "comment": comment}
        resp = requests.post(url=url, headers=headers, json=json)

        resp.raise_for_status()

        return resp.text
    
    def create_profile(self, profile_data: Dict[str, Any], strict_mode: str = "false") -> Dict[str, Any]:
        if not self.user_auth.access_token:
            raise ValueError("You need to login first")

        url = f"{self.user_auth.base_url}/profile/create"
        headers = {
            'Authorization': f'Bearer {self.user_auth.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Strict-Mode': strict_mode,
        }
        
        try:
            response = requests.post(url=url, headers=headers, json=profile_data)
            response.raise_for_status()
            return response.json()
            
        except RequestException as e:
            print(f'Error creating profile: {e}')
            # Add this to see the actual error details:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"API Error Details: {error_detail}")
                except:
                    print(f"Response text: {e.response.text}")
            raise  # Re-raise to see the full error

    def create_basic_profile(self, name : str, folder_id : str, browser_type: str = 'mimic', os_type: str = 'windows', screen_width: int = 1366, screen_height: int = 768) -> Dict[str, Any]:

        profile_data = {
            "name": name,
            "browser_type": browser_type,
            "folder_id": folder_id,
            "os_type": os_type,
            "auto_update_core": True,
            "parameters": {
                "flags": {
                    "webrtc_masking": "mask",
                    "geolocation_popup": "allow",
                    "screen_masking": "custom"
                },
                "fingerprint": {
                    "screen": {
                        "width": screen_width,
                        "height": screen_height,
                        "pixel_ratio": 1.0
                    }

                }
                
            }
        }

        return self.create_profile(profile_data)

    def get_profile_summary(self, profile_id: str) -> str:

        url = f"{self.user_auth.base_url}/profile/summary"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.user_auth.access_token}',
        }
        
        params = {
            'meta_id': profile_id
        
        }

        try:

            response = requests.get(url=url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except RequestException as e:
            print(f'Error showing profile summary: {e}')

    def get_profiles(self, folder_id: str = "000d6955-183e-40ae-a31c-ad7b59ade856") -> List[Dict[str, Any]]:

        url = f"{self.user_auth.base_url}/profile/search"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.user_auth.access_token}',
        }
        json = {
            "search_text": "",
            "folder_id": folder_id,
            "limit":50,
            "offset": 0
        }

        response = requests.post(url=url, headers=headers, json=json)

        response.raise_for_status()

        profiles = response.json().get("data")
        profiles = profiles.get("profiles")

        try:
            results = []
            for profile in profiles:
                folder_id = profile.get("folder_id")
                profile_id = profile.get("id")

                data = {
                    "folder_id": folder_id,
                    "profile_id": profile_id
                }

                results.append(data)

            return results
        except Exception as e:
            print(f"Error getting profiles: {e}")

    def start_profile(self, profile_id: str, folder_id: str) -> Dict[str, Any]:
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.user_auth.access_token}",
        }

        url = (
            f"https://127.0.0.1:45001/api/v1/profile/f/{folder_id}/p/{profile_id}/start"
        )
        params = {"automation_type": "selenium"}

        try:
            response = requests.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()

            status = response.json().get("status")

            port = status.get("message")

            return port
        except requests.exceptions.RequestException as e:
            print(f"Error starting profile: {e}")

    def stop_profile(self, profile_id: str, host: str = "https://127.0.0.1", port: int = 45001):

        url = f"{host}:{port}/api/v1/profile/stop/p/{profile_id}"

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.user_auth.access_token}',
        }

        try:
            response = requests.get(url=url, headers=headers, verify=False)

            response.raise_for_status()

            return f'Profile {profile_id} stopped successfully'

        except RequestException as e:
            print(f'Error stopping profile: {e}')



    def delete_profiles(self, profile_ids: str, is_permanent: bool = True) -> str:

        url = f"{self.user_auth.base_url}/profile/remove"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Strict-Mode': "true",
            'Authorization': f'Bearer {self.user_auth.access_token}',
        }

        json = {
            "ids": [
                profile_ids
            ],
            "permanently": is_permanent
        }

        params = {
            "ids": profile_ids,
            "permanently": str(is_permanent).lower()
        }

        try:
            response = requests.post(url=url, headers=headers, json=json, params=params)

            response.raise_for_status()

            status = response.json().get("status")

            message = status.get("message")

            return message

        except RequestException as e:
            print(f'Error deleting profile: {e}')