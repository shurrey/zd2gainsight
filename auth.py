
from cachetools import TTLCache
import requests

import config

class AuthController():
    target_url = ''
    def __init__(self):
        
        self.domain = config.config['gdh_domain']
        self.client_id = config.config['gdh_client_id']
        self.client_secret = config.config['gdh_client_secret']
        
        self.cache = None

    def getKey(self):
        return self.key

    def getSecret(self):
        return self.secret
    
    def gdh_auth(self):
   
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "write read"
        }

        response = requests.post(f"{self.domain}/oauth2/token", data=body, headers=headers)

        if response.ok:
            auth_json = response.json()
            return auth_json['access_token'], auth_json['expires_in']
        else:
            print(f"GDH_AUTH: error getting token {response.text}")
            return None,None


    def set_token(self):
        
        if self.cache is not None:
            try:
                token = self.cache['token']

                return
            
            except KeyError:

                pass

        token, expires_in = self.gdh_auth()

        self.cache = TTLCache(maxsize=1, ttl=expires_in)
        self.cache['token'] = token
        
    def get_token(self):
        
        try:
            token = self.cache['token']
            return token
        except KeyError:
            print(f"GET TOKEN KeyError {KeyError.with_traceback()}")
            self.set_token()

            return self.cache['token']
        except Exception:
            print(f"GET TOKEN Exception {Exception.with_traceback()}")