# CCXCon
[![Build Status](https://travis-ci.org/mitodl/ccxcon.svg)](https://travis-ci.org/mitodl/ccxcon)

CCXCon is a simple API serves as an interface between edX running instances and different MIT apps.

Implements the APIs as described here http://docs.ccxcon.apiary.io/

## Setup

You can run the entire project through docker.

```
pip install docker-compose
docker-compose up
```

From there, you can visit the minimal web-ui at http://localhost:8077/

## Tests

You can run the dredd API tests via the command `docker-compose up dredd`.
