#!/usr/bin/env python3
import json
import os
import requests
import time
import yaml

### Resource:
## https://www.grace-dev.com/python-apis/strava-api/

def write_token(token, token_fp):
    with open(token_fp, 'w') as outfile:
        json.dump(token, outfile)

def read_token(token_fp):
    with open(token_fp, 'r') as token_file:
        token = json.load(token_file)
    return token

def gen_auth_token(client_id, client_secret, redirect_url, token_fp):
    request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                                      f'&response_type=code&redirect_uri={redirect_url}' \
                                      f'&approval_prompt=force' \
                                      f'&scope=profile:read_all,activity:read_all'

    # User prompt showing the Authorization URL and asks for the code
    print('Click here:', request_url)
    print('Please authorize the app and copy&paste below the generated code!')
    print('P.S: you can find the code in the URL')
    code = input('Insert the code from the url: ')
    token = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                                               data={'client_id': client_id,
                                                             'client_secret': client_secret,
                                                             'code': code,
                                                             'grant_type': 'authorization_code'}, verify=False)

    write_token(token.json(), token_fp)

def refresh_auth_token(client_id, client_secret, token_fp, token):
    token = requests.post(url='https://www.strava.com/api/v3/oauth/token',
                                    data={'client_id': client_id,
                                    'client_secret': client_secret,
                                    'grant_type': 'refresh_token',
                                    'refresh_token': token['refresh_token']}, verify=False)
    write_token(token.json(), token_fp)

def main():
    with open('config.yml', 'r') as ymlfile:
        config_yml = yaml.safe_load(ymlfile)
    client_id = config_yml['strava']['client_id']
    client_secret = config_yml['strava']['client_secret']
    redirect_url = config_yml['strava']['redirect_url']
    token_fp = config_yml["strava"]["token_fp"]
    if not os.path.exists(token_fp):
        gen_auth_token(client_id, client_secret, redirect_url, token_fp)

    token = read_token(token_fp)
    if token['expires_at'] < time.time():
        refresh_auth_token(client_id, client_secret, token_fp, token)

main()
