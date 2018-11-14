__author__ = 'peyman-tsiq'

import pandas as pd
import argparse
import requests
import json

LIST_REPO_EP='https://api.github.com/repositories'
README_EP='https://api.github.com/repos/{}/readme?ref=master'

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='test DataEng search API')
    argparser.add_argument('-bp',"--bookpath", type=str, default='../../../data/attune/Attune+Locations.csv', help="path to attune book")
    args = argparser.parse_args()

    headers = {'Accept': 'application/vnd.github.v3.json'}

    import base64

    rsp = requests.get(LIST_REPO_EP)
    repos = json.loads(rsp.text)

    for repo in repos:
        print('*' * 100)
        owner_repo_pair = repo['full_name']
        print(owner_repo_pair)
        print(README_EP.format(owner_repo_pair))

        rsp = requests.get(README_EP.format(owner_repo_pair),headers=headers)

        readme = json.loads(rsp.text)
        if 'content' in readme:
            readme['content'] = base64.b64decode(readme['content'])
        print(readme)


