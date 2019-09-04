# getgit

# APIs

## Organizations

see https://developer.github.com/v3/orgs/

### List all organizations

Lists all organizations, in the order that they were created on GitHub.

curl -i -XGET https://api.github.com/organizations?since=1

### get an organization

curl -i -XGET https://api.github.com/orgs/github

## Repos

see https://developer.github.com/v3/repos/


rsp <- curl -i -XGET https://api.github.com/organizations?since=1

then 

foreach uname <- 'login' in rsp
    curl -i -XGET https://api.github.com/users/uname/repos
    curl -i -XGET https://api.github.com/orgs/github/repos


### list All public repos

see https://developer.github.com/v3/repos/#list-all-public-repositories

curl -i -XGET https://api.github.com/repositories?since=1

### get a repo

see https://developer.github.com/v3/repos/#Get

GET /repos/:owner/:repo

e.g.

curl -i -XGET https://api.github.com/repos/collectiveidea/imap_authenticatable

### All topics of a repo

see https://developer.github.com/v3/repos/#list-all-topics-for-a-repository

GET /repos/:owner/:repo/topics

e.g.

curl -i -XGET https://api.github.com/repos/collectiveidea/imap_authenticatable/topics

### list contributors

see https://developer.github.com/v3/repos/#list-contributors

GET /repos/:owner/:repo/contributors

e.g.

curl -i -XGET https://api.github.com/repos/collectiveidea/imap_authenticatable/contributors