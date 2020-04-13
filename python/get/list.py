__author__ = 'peyman'

from redis import Redis
from rq import Queue
import argparse
import requests
import json
import base64

#curl -i -XGET https://api.github.com/organizations?since=1\&access_token=2df7b713b04fe8ff8f1d21f9eb6713936bd8033c

class OrgsGetter():
    def __init__(self):
        self.LIST_REPO_EP='https://api.github.com/repositories'
        self.README_EP='https://api.github.com/repos/{}/readme?ref=master'
        self.apikey='2df7b713b04fe8ff8f1d21f9eb6713936bd8033c'

        self.headers = {'Accept': 'application/vnd.github.v3.json',
                        'Authorization':self.apikey}

    def get_repos(self,url):
        rsp = requests.get(self.README_EP.format(owner_repo_pair), headers=self.headers)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Get Orgs in Github')
    argparser.add_argument('-bp',"--bookpath", type=str, default='../../../data/attune/Attune+Locations.csv', help="path to attune book")
    args = argparser.parse_args()

    headers = {'Accept': 'application/vnd.github.v3.json',
               'Authorization': }


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
        


37600000