import argparse
import getopt,sys
import logging
import jsonlines
from datetime import datetime

sys.path.append('..')
from gitquery import GitHubQuery

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='query-{}.log'.format(datetime.now().strftime('%Y-%m-%d')),
                    level=logging.DEBUG)

class USER_QUERY(GitHubQuery):
    QUERY = """
query ($query: String!, $type: SearchType!, $first: Int!) {
  search(query: $query, type: $type, first: $first) {
    userCount
    edges {
      node {
        ... on User {
          login
          name
          location
          email
          company
          createdAt
          databaseId
          following {
            totalCount
          }
          id
          isBountyHunter
          isCampusExpert
          isDeveloperProgramMember
          isEmployee
          isHireable
          isSiteAdmin
          isViewer
          projectsUrl
          updatedAt
          websiteUrl
          url
          bio
          followers {
            totalCount
          }
          organizations(first: 10) {
            totalCount
          }
          repositories(affiliations: OWNER, privacy: PUBLIC, first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
            totalDiskUsage
            totalCount
            nodes {
              createdAt
              description
              forkCount
              homepageUrl
              id
              isFork
              isPrivate
              isTemplate
              isMirror
              isLocked
              pushedAt
              watchers {
                totalCount
              }
              diskUsage
              forks {
                totalCount
              }
              hasWikiEnabled
              isArchived
              isDisabled
              issues {
                totalCount
              }
              licenseInfo {
                name
                id
              }
              name
              primaryLanguage {
                id
                name
              }
              pullRequests {
                totalCount
              }
              stargazers {
                totalCount
              }
            }
          }
          pinnedItems(first: 10) {
            totalCount
            edges {
              node {
                ... on Repository {
                  id
                  name
                  sshUrl
                  url
                  createdAt
                  databaseId
                  description
                  diskUsage
                  forkCount
                  homepageUrl
                  hasWikiEnabled
                  isArchived
                  isDisabled
                  isFork
                  isLocked
                  isMirror
                  isPrivate
                  isTemplate
                  issues {
                    totalCount
                  }
                  primaryLanguage {
                    id
                    name
                  }
                  stargazers {
                    totalCount
                  }
                  updatedAt
                  watchers {
                    totalCount
                  }
                }
              }
            }
          }
        }
      }
      cursor
      textMatches {
        fragment
        highlights {
          text
        }
        property
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""
    QUERY_PARAMS = dict(type='USER',
                        query='location:usa repos:>0',
                        first=5,
                        after=None)

    ADDITIONAL_HEADERS = dict(
        Accept="application/vnd.github.vixen-preview+json",
    )

    def __init__(self, github_token):
        super().__init__(
            github_token=github_token,
            query=USER_QUERY.QUERY,
            query_params=USER_QUERY.QUERY_PARAMS,
            additional_headers=USER_QUERY.ADDITIONAL_HEADERS
        )

    def iterator(self):
        generator = self.generator()
        hasNextPage = True
        users = []
        while hasNextPage:
            response = next(generator)
            #endCursor = response["data"]["organization"]["repositories"]["pageInfo"]["endCursor"]
            #self.query_params = dict(after=endCursor)
            #users.extend(response["data"]["organization"]["repositories"]["nodes"])
            users.extend(response)
            #hasNextPage = response["data"]["organization"]["repositories"]["pageInfo"]["hasNextPage"]
            hasNextPage=False
            yield response["data"]["search"]["edges"]
        #return (users)


def main():
    """
    python users.py --token 2df7b713b04fe8ff8f1d21f9eb6713936bd8033c
    """
    try:
        parser = argparse.ArgumentParser(description='Queries GitHub through the GitGraphQL API for all users')
        parser.add_argument("--token", type=str, default='2df7b713b04fe8ff8f1d21f9eb6713936bd8033c', help="configs")
        parser.add_argument("--disc", type=str, default='data.json', help="configs")
        args = parser.parse_args()
        logging.info('Starting User Query')

        q = USER_QUERY(github_token=args.token)

        with jsonlines.open(args.disc, mode='w') as writer:
            while q.iterator().hasnext():
                rsp = q.iterator()
                writer.write(rsp[0]['node'])

    except getopt.GetoptError:
        sys.exit(2)


if __name__ == '__main__':
    main()
