__author__ = 'peyman-tsiq'

import pandas as pd
import argparse
import requests
import json

LIST_REPO='https://api.github.com/repositories'

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='test DataEng search API')
    argparser.add_argument('-bp',"--bookpath", type=str, default='../../../data/attune/Attune+Locations.csv', help="path to attune book")
    args = argparser.parse_args()

    # headers = {'content-type': 'application/json'}
    #
    # payload = {'businessName': contractor.insured_name,
    #            'address':contractor.street,
    #            'zip':contractor.zipcode,
    #            'city':contractor.city,
    #            'state':contractor.state}

    rsp = requests.get(LIST_REPO)
    jsonObj = json.loads(rsp.text)

    print(jsonObj)


