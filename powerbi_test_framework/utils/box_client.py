import requests
from powerbi_test_framework.utils import logger
from powerbi_test_framework.utils.config import BOX_ACCESS_TOKEN, BOX_REFRESH_TOKEN, BOX_REQUEST_URL, BOX_UPLOAD_URL, BOX_REFRESH_TOKEN_URL, BOX_CLIENT_ID, BOX_CLIENT_SECRET,\
BOX_FOLDER_ID, LIST_FOLDER_URL
import os

class BoxClient:
    def __init__(self):
        self.access_token = BOX_ACCESS_TOKEN
        self.base_url = BOX_REQUEST_URL

    def make_request(self, method, url, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.status_code == 401:  # Unauthorized, possibly token expired
            self.access_token = self.get_refresh_token(BOX_REFRESH_TOKEN, BOX_CLIENT_ID, BOX_CLIENT_SECRET)
            print("Refreshed access token:", self.access_token)
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_refresh_token(self, refresh_token, client_id, client_secret):
        url = BOX_REFRESH_TOKEN_URL
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = self.make_request('POST', url, data=data)
        print("Obtained new access token from Box.", response)
        return response['access_token']
    
    def update_file(self, file_id, file_path):
        url = f"{self.base_url}files/{file_id}"
        print(f"Updating file ID {file_id} in Box with new content from {file_path}")
        
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            print(f"File not found: {abs_path}")
            return None

        with open(abs_path, 'rb') as file_content:
            files = {
                'file': (abs_path, file_content)
            }
            response = self.make_request('PUT', url, files=files)

        return response

    def upload_file(self, file_path, folder_id=BOX_FOLDER_ID):
        file_name = os.path.basename(file_path)

        file_id = self.list_folder(file_name)  # Check if file already exists

        if file_id:
            print(f"File {file_name} already exists in Box with ID {file_id}. Updating the file.")
            self.update_file(file_id, file_path)
            return file_id
        
        url = BOX_UPLOAD_URL
        print(f"Uploading file {file_path} to Box folder ID {folder_id}")
           
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            print(f"File not found: {abs_path}")
            return None

        with open(abs_path, 'rb') as file_content:
            files = {
                'file': (abs_path, file_content),
                'parent_id': (None, folder_id)
            }
            response = self.make_request('POST', url, files=files)

        return response


    def list_folder(self, file_name):
        print(f"Searching for file {file_name} in Box.")
        url = LIST_FOLDER_URL
        params = {
            'fields': 'name,id',
            'limit': 1000
        }
        response = self.make_request('GET', url, params=params)
        print("****************sdf",response)
        print(f"Searched for file {file_name} in Box. Found {response.get('total_count', 0)} items.")
        file_id = [data.get("id", None) for data in response['entries'] if data['name'] == file_name]
        if not file_id:
            return None
        if isinstance(file_id, list):
            file_id = file_id[0]
        return file_id