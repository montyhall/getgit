# getgit

[V3 APIs](https://developer.github.com/v3/)

[v4 GraphQL](https://api.github.com/graphql)

To get all schemas in graphQL [see introspection](https://graphql.github.io/learn/introspection/)

https://medium.com/vlgunarathne/introduction-to-github-graphql-api-423ebbab75f9

```bash
{
  __schema {
    types {
      name
    }
  }
}
```

and then to get details of an object
```bash
{
  __type(name: "Organization") {
    name
    description
    fields {
      name
      description
      type {
        name
        kind
        ofType {
          name
          kind
        }
      }
    }
  }
}
```

# APIs

## Organizations

[see docs](https://developer.github.com/v3/orgs/)

### List all organizations

Lists all organizations, in the order that they were created on GitHub.

```bash
curl -i -XGET https://api.github.com/organizations?since=1
```

{
  __type(name: "Organization") {
    name
    fields {
      name
    }
  }
}

organization(login: $org) {
      repositories(
        first: 50
        after: $cursor
        orderBy: { field: PUSHED_AT, direction: DESC }
      ) {
        totalCount
        pageInfo {
          endCursor
          __typename
        }
        edges {
          cursor
          node {
            name
            descriptionHTML
            license
            stargazers(first: 50) {
              totalCount
            }
            repositoryTopics(first: 20) {
              edges {
                node {
                  topic {
                    name
                  }
                }
              }
            }
            forkCount
            isFork
            createdAt
            updatedAt
            pushedAt
            homepageUrl
            url
            primaryLanguage {
              name
              color
            }
            collaborators(first: 50, affiliation: DIRECT) {
              edges {
                node {
                  name
                  login
                  avatarUrl
                }
              }
            }
          }
        }
      }
    }


### get an organization [v4 api](https://developer.github.com/v4/object/organization/)

```bash
curl -i -XGET https://api.github.com/orgs/github
```

## Repos

[see docs](https://developer.github.com/v3/repos/)

```bash
rsp <- curl -i -XGET https://api.github.com/organizations?since=1

foreach uname <- 'login' in rsp

    curl -i -XGET https://api.github.com/users/uname/repos
    
    curl -i -XGET https://api.github.com/orgs/github/repos
```

### list All public repos

[see docs](https://developer.github.com/v3/repos/#list-all-public-repositories)

```bash
curl -i -XGET https://api.github.com/repositories?since=1
```

### get a repo

[see docs](https://developer.github.com/v3/repos/#Get)

GET /repos/:owner/:repo

e.g.

```bash
curl -i -XGET https://api.github.com/repos/collectiveidea/imap_authenticatable
```

### All topics of a repo

[see doc](https://developer.github.com/v3/repos/#list-all-topics-for-a-repository)

GET /repos/:owner/:repo/topics

e.g.

```bash
curl -i -XGET https://api.github.com/repos/collectiveidea/imap_authenticatable/topics
```

### list contributors

[see docs](https://developer.github.com/v3/repos/#list-contributors)

GET /repos/:owner/:repo/contributors

e.g.

```bash
curl -i -XGET https://api.github.com/repos/collectiveidea/imap_authenticatable/contributors
```

# Third party APIs

[AGitHub](https://github.com/mozilla/agithub)