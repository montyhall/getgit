#https://developer.github.com/v3/users/#get-all-users

import requests
import re
import os
import logging
import json
import argparse
import getopt,sys
from datetime import datetime,timezone
import jsonlines

"""
python implementation of Github V3 Search API for users 
https://api.github.com/search/users?q=location:usa
"""

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='search-{}.log'.format(datetime.now().strftime('%Y-%m-%d')),
                    level=logging.DEBUG)


class ResponseError(Exception):
    """Accessible attributes: error
        error (AttrDict): Parsed error response
    """
    def __init__(self, error):
        Exception.__init__(self, error)
        self.error = error

    def __str__(self):
        return json.dumps(self.error, indent=1)

class AttrDict(dict):
    """Attribute Dictionary (set and access attributes 'pythonically')"""
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError('no such attribute: %s' % name)

    def __setattr__(self, name, val):
        self[name] = val

def get_logger(name, level=None):
    """Returns logging handler based on name and level (stderr)
        name (str): name of logging handler
        level (str): see logging.LEVEL
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        stderr = logging.StreamHandler()
        stderr.setFormatter(logging.Formatter(
            '%(levelname)s [%(name)s]: %(message)s'))
        logger.addHandler(stderr)

        level = level if level else os.environ.get('OCTOHUB_LOGLEVEL', 'CRITICAL')
        logger.setLevel(getattr(logging, level))

    return logger

#log = get_logger('response')


def _get_content_type(response):
    """Parse response and return content-type"""
    try:
        content_type = response.headers['Content-Type']
        content_type = content_type.split(';', 1)[0]
    except KeyError:
        content_type = None

    return content_type


def _parse_link(header_link):
    """Parse header link and return AttrDict[rel].uri|params"""
    links = AttrDict()
    for s in header_link.split(','):
        link = AttrDict()

        m = re.match('<(.*)\?(.*)>', s.split(';')[0].strip())
        link.uri = m.groups()[0]
        link.params = {}
        for kv in m.groups()[1].split('&'):
            key, value = kv.split('=')
            link.params[key] = value

        m = re.match('rel="(.*)"', s.split(';')[1].strip())
        rel = m.groups()[0]

        links[rel] = link
        logging.debug('link-%s-page: %s' % (rel, link.params['page']))

    return links


def parse_element(el):
    """Parse el recursively, replacing dicts with AttrDicts representation"""
    if type(el) == dict:
        el_dict = AttrDict()
        for key, val in el.items():
            el_dict[key] = parse_element(val)

        return el_dict

    elif type(el) == list:
        el_list = []
        for l in el:
            el_list.append(parse_element(l))

        return el_list

    else:
        return el


def parse_response(response):
    """Parse request response object and raise exception on response error code
        response (requests.Response object):
        returns: requests.Response object, including:
            response.parsed (AttrDict)
            response.parsed_link (AttrDict)
            http://docs.python-requests.org/en/latest/api/#requests.Response
    """
    response.parsed = AttrDict()
    response.parsed_link = AttrDict()
    nextp, lastp = None, None

    if 'link' in response.headers.keys():
        response.parsed_link = _parse_link(response.headers['link'])
        nextp = response.parsed_link['next']['params']['page']
        lastp = response.parsed_link['last']['params']['page']
        #print(response.headers['link'])
        print('\nparsedLinks: {}'.format(response.parsed_link))

    headers = ['status', 'x-ratelimit-limit', 'x-ratelimit-remaining']
    for header in headers:
        if header in response.headers.keys():
            logging.info('%s: %s' % (header, response.headers[header]))

    if response.status_code not in (200, 201, 204):
        raise ResponseError(response)

    response.parsed = json.loads(response.text)

    return response,nextp,lastp


class Pager(object):
    def __init__(self, conn, uri, params, max_pages=0):
        """Iterator object handling pagination of Connection.send (method: GET)
            conn (octohub.Connection): Connection object
            uri (str): Request URI (e.g., /user/issues)
            params (dict): Parameters to include in request
            max_pages (int): Maximum amount of pages to get (0 for all)
        """
        self.conn = conn
        self.uri = uri
        self.params = params
        self.max_pages = max_pages
        self.count = 0
        self.next = None
        self.last = None

    def __iter__(self):
        while True:
            self.count += 1
            response,nextp,lastp = self.conn.send('GET', self.uri, self.params)
            yield response

            if nextp:
                self.next = nextp
            else:
                self.next += 1

            self.params['page'] = self.next

            if lastp:
                self.last = lastp

            if self.count == self.max_pages or self.count == self.last:
                break

            # if 'next' not in response.parsed_link.keys():
            #     break

            # Parsed link is absolute. Connection wants a relative link,
            # so remove protocol and GitHub endpoint for the pagination URI.
            # m = re.match(self.conn.endpoint + '(.*)', response.parsed_link.next.uri)
            # self.uri = m.groups()[0]
            # self.params = response.parsed_link.next.params
            #
            # print('count: {} max: {}'.format(self.count,self.max_pages))
            # print('next' in response.parsed_link.keys())

class Connection(object):
    def __init__(self, token=None):
        """OctoHub connection
            token (str): GitHub Token (anonymous if not provided)
        """
        __version__ = '0.1'
        __useragent__ = 'bubbs%s' % __version__
        self.endpoint = 'https://api.github.com'
        self.headers = {'User-Agent': __useragent__,
                        'Accept': 'application/vnd.github.v3+json'}
        self.currentLimit = 0
        self.totalcounts = 0
        if token:
            self.headers['Authorization'] = 'token %s' % token

    def throttle(self, response):
        """sleep to reset time
        see https://developer.github.com/v3/#rate-limiting
        """
        limit = int(response.headers['x-ratelimit-limit'])
        resetAt = int(response.headers['X-RateLimit-Reset'])
        now = datetime.now(timezone.utc).replace(microsecond=0)
        logging.info('reached {} limit. SLeeping until {}'.format(limit, resetAt))
        self.sleepsome((resetAt - now).total_seconds())
        logging.info('resuming crawling')

    def send(self, method, uri, params={}, data=None):
        """Prepare and send request
            method (str): Request HTTP method (e.g., GET, POST, DELETE, ...)
            uri (str): Request URI (e.g., /user/issues)
            params (dict): Parameters to include in request
            data (str | file type object): data to include in request
            returns: requests.Response object, including:
                response.parsed (AttrDict): parsed response when applicable
                response.parsed_link (AttrDict): parsed header link when applicable
                http://docs.python-requests.org/en/latest/api/#requests.Response
        """
        url = self.endpoint + uri
        kwargs = {'headers': self.headers, 'params': params, 'data': data}
        while True:
            try:
                response = requests.request(method, url, **kwargs)
                rsp,nextp,lastp = parse_response(response)
                self.totalcounts = rsp.parsed['total_count']
                bincomplete = bool(rsp.parsed['incomplete_results'])

                self.currentLimit = int(response.headers['x-ratelimit-remaining'])
                if self.currentLimit < 1:
                    self.throttle(response)

                return rsp, nextp, lastp
                break
            except ResponseError as e:
                if response.status_code == 403:
                    self.throttle(response)


def main():
    """
    https://api.github.com/search/users?q=location:usa
    python search.py --token <TOKEN>
    there are 52,594,054 users in total and 81226 in US as of this point
    """
    try:
        parser = argparse.ArgumentParser(description='Queries GitHub through the v3 API for all users')
        parser.add_argument("--token", type=str, help="configs")
        parser.add_argument("--disc", type=str, default='searchdata.jsonl', help="configs")

        args = parser.parse_args()
        logging.info('Starting User Search Query')

        conn = Connection(args.token)

        uri = '/search/users'

        with jsonlines.open(args.disc, mode='a') as jsonfile:
            pager = Pager(conn,uri,params={'q': 'location:usa','page':'1'},max_pages=0)
            for page in pager:
                for usr in page.parsed['items']:
                    jsonfile.write(usr)

    except getopt.GetoptError:
        sys.exit(2)

    logging.info('Finished')
    print('Done')

if __name__ == '__main__':
    main()
