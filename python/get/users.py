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
query ($query: String!, $type: SearchType!, $first: Int!, $after: Int!) {
  search(query: $query, type: $type, first: $first, after: $after) {
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

    def iterator(self,datafile):
        generator = self.generator()
        hasNextPage = True
        totalParsed,total=0,0
        with jsonlines.open(datafile, mode='w') as jsonfile:
            while hasNextPage:
                response = next(generator)
                endCursor = response["data"]["search"]["pageInfo"]["endCursor"]
                #self.query_params = dict(after=endCursor)
                hasNextPage = response["data"]["search"]["pageInfo"]["hasNextPage"]
                hasNextPage=False
                for edge in response["data"]["search"]["edges"]:
                    jsonfile.write(edge['node'])
                    totalParsed +=1

                if total==0:
                    total = int(response["data"]["search"]["userCount"])
                sys.stdout.write('\r{}/{} [{:.2f}%]'.format(totalParsed,total,(totalParsed/total*100)))
                sys.stdout.flush()
                logging.info('{}/{}'.format(totalParsed,total))
            print('\n')
def main():
    """
    python users.py --token 017cbe095f094a6f23c61f09dedeb7dd027c5862
    """
    try:
        parser = argparse.ArgumentParser(description='Queries GitHub through the GitGraphQL API for all users')
        parser.add_argument("--token", type=str, default='017cbe095f094a6f23c61f09dedeb7dd027c5862', help="configs")
        parser.add_argument("--disc", type=str, default='data.jsonl', help="configs")
        args = parser.parse_args()
        logging.info('Starting User Query')

        q = USER_QUERY(github_token=args.token)
        q.iterator(datafile=args.disc)

    except getopt.GetoptError:
        sys.exit(2)


if __name__ == '__main__':
    main()
