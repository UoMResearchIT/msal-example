import json
from typing import Union, List
import os
import atexit
from pathlib import Path

import requests
import msal
import yaml


def main():
    """Get an API authentication token and use it to make a sample request to the Microsoft Graph
    API."""
    config = get_config()
    token_cache = get_token_cache("cache.bin")

    access_token = get_access_token(config["client_id"], token_cache, config["token_scope"])

    access_graph_api(access_token)


def get_config():
    config_path = Path("config.yaml")
    if config_path.exists():
        with open('config.yaml') as input_file:
            config = yaml.safe_load(input_file)
        if "client_id" not in config:
            raise KeyError("'config.yaml' must contain a 'client_id' key.")
        if "token_scope" not in config:
            raise KeyError("'config.yaml' must contain a 'token_scope' key.")
        return config
    else:
        raise FileNotFoundError("Could not find 'config.yaml'.")


def get_token_cache(cache_name: str) -> msal.SerializableTokenCache:
    """Attempt to load a TokenCache from a file. If the file does not exist then return an empty
    TokenCache."""
    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_name):
        cache.deserialize(open(cache_name, "r").read())
    return cache


def get_access_token(client_id: str, token_cache: Union[None, msal.SerializableTokenCache],
                     token_scope: List[str]) -> str:
    """Get an API access token using the Microsoft Authentication Library. First try to get a
    token silently using a local token cache. If this doesn't work use the device flow workflow
    to get a token."""
    app = msal.PublicClientApplication(client_id,
                                       authority="https://login.microsoftonline.com/common",
                                       token_cache=token_cache)

    # Register token cache to be saved on program exit.
    atexit.register(lambda: open("cache.bin", "w").write(token_cache.serialize()))

    token = get_token_from_cache(app, token_scope)
    if token:
        return token
    else:
        return get_token_by_device_flow(app, token_scope)


def get_token_from_cache(app: msal.PublicClientApplication,
                         token_scope: List[str]) -> Union[str, None]:
    """Try to get an API access token from a local cache. If the access token is expired
     a refresh token will automatically be used to get a new access token. If the refresh token
     is expired then the user will have to reauthenticate."""
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(token_scope, account=accounts[0])
        # Method returns None if no token can be acquired
        if result and "access_token" in result:
            return result["access_token"]
        else:
            return None


def get_token_by_device_flow(app: msal.PublicClientApplication, token_scope: List[str]) -> str:
    flow = app.initiate_device_flow(scopes=token_scope)
    if "user_code" not in flow:
        raise ValueError("Fail to create device flow. Err: %s" % json.dumps(flow, indent=4))
    print(flow["message"])
    print("Program execution will continue automatically after authentication.")

    # This function polls every 5 seconds to see if the user has completed the authentication
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result["access_token"]
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        raise ValueError()


def access_graph_api(access_token: str):
    """Example of calling graph API using the access token"""
    profile_data = requests.get("https://graph.microsoft.com/v1.0/me",
                                headers={'Authorization': 'Bearer ' + access_token}).json()
    print("Graph API call result: %s" % json.dumps(profile_data, indent=2))


if __name__ == "__main__":
    main()
