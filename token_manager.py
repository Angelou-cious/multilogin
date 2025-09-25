import os, time, json
from user_auth import UserAuth

class TokenManager:
    def __init__(self, auth: UserAuth, token_file: str = "token.json"):
        self.auth = auth
        self.token_file = token_file

    def load_tokens(self):

        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as token:
                return json.load(token)

        return None
    
    def save_tokens(self, tokens):
        with open(self.token_file, "w") as token:
            json.dump(tokens, token)

    def get_tokens(self):
        tokens = self.load_tokens()

        if tokens and tokens["token_expiration"] > time.time():
            self.auth.access_token = tokens["access_token"]
            self.auth.refresh_token = tokens["refresh_token"]
            self.auth.token_expiration = tokens["token_expiration"]
        else:
            tokens = self.auth.login()
            self.save_tokens(tokens)

        return tokens