from requests import exceptions, request
import pytz

# see https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad
class GitHubQuery(object):
    BASE_URL = "https://api.github.com/graphql"

    def __init__(
            self,
            github_token=None,
            query=None,
            query_params=None,
            additional_headers=None
    ):
        self.github_token = github_token
        self.query = query
        self.query_params = query_params or dict()
        self.additional_headers = additional_headers or dict()
        self.timezone = pytz.timezone('UTC')

    @property
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}",
        )
        return {
            **default_headers,
            **self.additional_headers
        }

    # https://github.com/graphql-python/graphene-django/blob/dbd3957a9f622573b2b106546f3accc48f5d5b41/graphene_django/views.py#L161-L163
    def generator(self):
        while True:
            try:
                yield request(
                    'post',
                    GitHubQuery.BASE_URL,
                    headers=self.headers,
                    json={"query":self.query,"variables":self.query_params}
                ).json()
            except exceptions.HTTPError as http_err:
                raise http_err
            except Exception as err:
                raise err

    def iterator2(self):
        pass
