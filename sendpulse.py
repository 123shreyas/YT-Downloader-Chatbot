import json
import base64
import requests

class SendpulseAPI:
    def __init__(self, user_id, secret, storage_file):
        self.user_id = user_id
        self.secret = secret
        self.token_url = "https://api.sendpulse.com/oauth/access_token"
        self.api_url = "https://api.sendpulse.com"
        self.storage_file = storage_file
        self.token = self.load_token()

    def load_token(self):
        try:
            with open(self.storage_file, 'r') as f:
                token = json.load(f)
                return token
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_new_token()

    def save_token(self, token):
        with open(self.storage_file, 'w') as f:
            json.dump(token, f)

    def get_new_token(self):
        credentials = {
            'grant_type': 'client_credentials',
            'client_id': self.user_id,
            'client_secret': self.secret
        }
        response = requests.post(self.token_url, data=credentials)
        response.raise_for_status()
        token = response.json()
        self.save_token(token)
        return token

    def make_request(self, method, endpoint, data=None):
        if not self.token:
            self.token = self.get_new_token()
        headers = {
            'Authorization': f'Bearer {self.token["access_token"]}',
            'Content-Type': 'application/json'
        }
        url = f'{self.api_url}{endpoint}'
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def smtp_send_mail(self, email):
        endpoint = '/smtp/emails'
        return self.make_request('POST', endpoint, email)
