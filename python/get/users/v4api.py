import argparse
import getopt,sys
import logging
import jsonlines
from datetime import datetime,timezone
import time
from dateutil.parser import parse
from requests import exceptions
import traceback

sys.path.append('../..')
from gitquery import GitHubQuery

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='query-{}.log'.format(datetime.now().strftime('%Y-%m-%d')),
                    level=logging.DEBUG)

class USER_QUERY(GitHubQuery):
    QUERY = """
            query ($query: String!, $type: SearchType!, $first: Int!, $after: String) {
              rateLimit(dryRun: false) {
                remaining
                cost
                limit
                nodeCount
                resetAt
              }
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
                      following(first: 10) {
                        totalCount
                        nodes {
                          id
                        }
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
                      followers(first: 10) {
                        totalCount
                        nodes {
                          id
                        }
                      }
                      organizations(first: 10) {
                        totalCount
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
                              pushedAt
                            }
                          }
                        }
                      }
                      contributionsCollection {
                        totalRepositoryContributions(excludeFirst: false)
                        startedAt
                        contributionCalendar {
                          totalContributions
                          months {
                            totalWeeks
                            year
                            name
                            firstDay
                          }
                          weeks {
                            firstDay
                            contributionDays {
                              weekday
                              date
                              contributionCount
                            }
                          }
                        }
                        contributionYears
                        hasActivityInThePast
                        hasAnyContributions
                        totalCommitContributions
                        totalIssueContributions(excludeFirst: false, excludePopular: false)
                        totalPullRequestContributions
                        totalPullRequestReviewContributions
                        totalRepositoriesWithContributedCommits
                        totalRepositoriesWithContributedIssues
                        totalRepositoriesWithContributedPullRequestReviews
                        totalRepositoriesWithContributedPullRequests
                      }
                      watching {
                        totalCount
                      }
                      hovercard {
                        contexts {
                          message
                          octicon
                          ... on OrganizationTeamsHovercardContext {
                            __typename
                            totalTeamCount
                            message
                            octicon
                          }
                          ... on OrganizationsHovercardContext {
                            __typename
                            message
                            octicon
                            totalOrganizationCount
                          }
                        }
                      }
                      pinnedRepositories {
                        totalCount
                      }
                      pinnableItems(first: 10) {
                        totalCount
                        nodes {
                          ... on Repository {
                            id
                            name
                          }
                        }
                      }
                    }
                  }
                  cursor
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
"""
    FIRST=2
    BACKOFF=1
    QUERY_PARAMS = dict(type='USER',
                        query='location:usa repos:>0 created:>2005-01-01',
                        first=FIRST,
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
        self.cursorf = None
        self.lastcursor = None

    def setCursor(self,cursorfile):
        try:
            with open(cursorfile, 'r') as f:
                self.lastcursor = f.readlines()[-1].strip()
        except FileNotFoundError:
            pass

        if self.lastcursor:
            self.query_params['after'] = self.lastcursor

        self.cursorf = open(cursorfile, 'a')

    def sleepsome(self, sleept):
        time.sleep(sleept)

    def check_ratelimit(self, response):
        '''
        see
        https://developer.github.com/v4/guides/resource-limitations/
        https://developer.github.com/v4/object/ratelimit/
        https://developer.github.com/v3/search/#rate-limit

        :param response:
        :return:
        '''
        #the number of points remaining in the current rate limit window.
        remaining = response["data"]["rateLimit"]["remaining"]

        #point cost for the current call that counts against the rate limit
        cost = response["data"]["rateLimit"]["cost"]

        #maximum number of points the client is permitted to consume in a 60-minute window.
        limit = response["data"]["rateLimit"]["limit"]

        nodeCount = response["data"]["rateLimit"]["nodeCount"]

        #the time at which the current rate limit window resets in UTC epoch seconds.
        resetAt = parse(response["data"]["rateLimit"]["resetAt"])

        if remaining <= USER_QUERY.FIRST:
            now = datetime.now(timezone.utc).replace(microsecond=0)
            logging.info('reached {} limit. SLeeping until {}'.format(limit, resetAt))
            self.sleepsome((resetAt - now).total_seconds())
            logging.info('resuming crawling')

        return resetAt,remaining,cost,limit,nodeCount

    #Y3Vyc29yOjEy
    def iterator(self,datafile):
        generator = self.generator()
        hasNextPage = True
        totalParsed,retries,errors,total=0,0,0,0
        with jsonlines.open(datafile, mode='a') as jsonfile:
            while hasNextPage:
                try:
                    response = next(generator)

                    if response and "data" not in response:
                        USER_QUERY.QUERY_PARAMS.FIRST = USER_QUERY.QUERY_PARAMS.FIRST - USER_QUERY.QUERY_PARAMS.BACKOFF
                        retries += 1

                    if response and "error" in response:
                        errors += 1

                    if response and "data" in response and "error" not in response:
                        resetAt, remaining, cost, limit, nodeCount = self.check_ratelimit(response)
                        endCursor = str(response["data"]["search"]["pageInfo"]["endCursor"])
                        self.query_params['after'] = endCursor
                        self.cursorf.write(endCursor+'\n')
                        self.cursorf.flush()
                        hasNextPage = bool(response["data"]["search"]["pageInfo"]["hasNextPage"])
                        for edge in response["data"]["search"]["edges"]:
                            jsonfile.write(edge['node'])
                            totalParsed +=1

                        if total==0:
                            total = int(response["data"]["search"]["userCount"])
                        sys.stdout.write('\r{}/{} [{:.2f}%] errors: {} retries: {}'.format(totalParsed,total,(totalParsed/total*100),errors,retries))
                        sys.stdout.flush()
                        logging.info('{}/{} [errors: {}, retries: {}] remaining: {} limit:{} cost: {} nodecount: {}'.format(
                            totalParsed,total,errors,retries,remaining,limit,cost,nodeCount))

                except exceptions.HTTPError:
                    errors+=1
                except Exception as err:
                    errors+=1

        self.cursorf.close()
        print('\nFinished: {}'.format(totalParsed))


def main():
    """
    python v4api.py --token <TOKEN>
    """
    try:
        parser = argparse.ArgumentParser(description='Queries GitHub through the GitGraphQL API for all users')
        parser.add_argument("--token", type=str, help="configs")
        parser.add_argument("--disc", type=str, default='data.jsonl', help="configs")
        parser.add_argument("--cursor", type=str, default='cursor.txt', help="configs")
        args = parser.parse_args()
        logging.info('Starting User Query')

        q = USER_QUERY(github_token=args.token)
        q.setCursor(args.cursor)
        q.iterator(datafile=args.disc)

    except getopt.GetoptError:
        sys.exit(2)

    logging.info('Finished')


if __name__ == '__main__':
    main()

