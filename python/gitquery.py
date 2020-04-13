from requests import exceptions, request

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

    @property
    def headers(self):
        default_headers = dict(
            Authorization=f"token {self.github_token}",
        )
        return {
            **default_headers,
            **self.additional_headers
        }

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

    def iterator(self):
        pass
