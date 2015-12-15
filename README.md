# CCXCon
[![Build Status](https://travis-ci.org/mitodl/ccxcon.svg)](https://travis-ci.org/mitodl/ccxcon)

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)


CCXCon is a simple API serves as an interface between edX running instances and different MIT apps.

At a high level, it takes information from multiple edX backends, and
produces a single data stream. Going the other way, it takes data
along this same single data stream and will route it to the correct
edX backend.

Implements the APIs as described here http://docs.ccxcon.apiary.io/

## Setup

You can run the entire project through docker.

```
pip install docker-compose
docker-compose up
```

From there, you can visit the minimal web-ui at
https://localhost.daplie.com:8077/ (which proxies back to localhost,
but has valid certificates).

## Tests

You can run the tests via the command `docker-compose run web tox`.


## Authorization

To be authorized to make requests to CCXCon, you use OAuth2. OAuth2
clients can be made in the django-admin. If you're doing
server-to-server oauth (edX and teachers' portal cases), you'll want
to create a user representing them, and an oauth app tied to that
user. The Authorization type should be "Client Credentials". You can
read more about that in the
[OAuth2 spec](https://tools.ietf.org/html/rfc6749#section-4.4).
