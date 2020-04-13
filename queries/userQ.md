
```json
query ($query: String!, $type: SearchType!, $first: Int!) {
  search(query: $query, type: $type, first: $first, after: "Y3Vyc29yOjEy") {
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
                  collaborators {
                    totalCount
                  }
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
    repositoryCount
  }
}
```

```json
{
  "type":"USER",
  "query":"location:usa repos:>0",
  "first":2
}
```