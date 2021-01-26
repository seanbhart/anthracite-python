import logging
import requests


def reddit_auth() -> dict:
    print("REDDIT")
    base_url = 'https://www.reddit.com/'
    data = {'grant_type': 'password', 'username': "TJ279", 'password': "EmptyBookIguanaBlue$05"}
    auth = requests.auth.HTTPBasicAuth("CRnYWjFI8ekzYg", "eWGBThJ8G-kBpJmyK0loM0uPcKOaKw")
    r = requests.post(base_url + 'api/v1/access_token',
                      data=data,
                      headers={'user-agent': 'anthracite by TJ279'},
                      auth=auth)
    d = r.json()
    return d


def reddit_profile():
    auth = reddit_auth()
    token = 'bearer ' + auth['access_token']
    base_url = 'https://oauth.reddit.com'
    headers = {'Authorization': token, 'User-Agent': 'anthracite by TJ279'}
    response = requests.get(base_url + '/api/v1/me', headers=headers)
    if response.status_code == 200:
        print(response.json()['name'], response.json()['comment_karma'])


def reddit():
    auth = reddit_auth()
    token = 'bearer ' + auth['access_token']
    base_url = 'https://oauth.reddit.com'
    headers = {'Authorization': token, 'User-Agent': 'anthracite by TJ279'}
    payload = {'t': 'day', 'limit': 5}
    response = requests.get(base_url + '/r/wallstreetbets/top', headers=headers, params=payload)
    if response.status_code == 200:
        json = response.json()
        link_ids = []
        if 'data' in json:
            if 'children' in json['data']:
                for c in json['data']['children']:
                    id = c['kind'] + "_" + c['data']['id']
                    link_ids.append(id)

        print(link_ids)
        # joined_string = ",".join(link_ids)
        payload = {'id': link_ids}
        response = requests.get(base_url + '/r/wallstreetbets/api/info', headers=headers, params=payload)
        print(response.json())