"""
Views for Application level healthcheck
"""

import datetime
import logging

import celery
import redis
from django.conf import settings
from django.http import JsonResponse
from kombu.utils.url import _parse_url as parse_redis_url
from psycopg2 import connect, OperationalError
from rest_framework import status as status_codes

log = logging.getLogger(__name__)

UP = "up"
DOWN = "down"
NO_CONFIG = "no config found"
TIMEOUT_SECONDS = 5


def get_pg_info():
    """
    Check PostgreSQL connection.
    """
    try:
        conf = settings.DATABASES['default']
        database = conf["NAME"]
        user = conf["USER"]
        host = conf["HOST"]
        port = conf["PORT"]
        password = conf["PASSWORD"]
    except (AttributeError, KeyError):
        log.error("No PostgreSQL connection info found in settings.")
        return {"status": NO_CONFIG}
    except TypeError:
        return {"status": DOWN}
    log.debug("got past getting conf")
    try:
        start = datetime.datetime.now()
        connection = connect(
            database=database, user=user, host=host,
            port=port, password=password, connect_timeout=TIMEOUT_SECONDS,
        )
        log.debug("at end of context manager")
        micro = (datetime.datetime.now() - start).microseconds
        connection.close()
    except (OperationalError, KeyError):
        log.error("Invalid PostgreSQL connection info in settings: %s", conf)
        return {"status": DOWN}
    log.debug("got to end of postgres check successfully")
    return {"status": UP, "response_microseconds": micro}


def get_redis_info():
    """
    Check Redis connection.
    """
    try:
        url = settings.BROKER_URL
        _, host, port, _, password, db, _ = parse_redis_url(url)
    except AttributeError:
        log.error("No valid Redis connection info found in settings.")
        return {"status": NO_CONFIG}

    start = datetime.datetime.now()
    try:
        rdb = redis.StrictRedis(
            host=host, port=port, db=db,
            password=password, socket_timeout=TIMEOUT_SECONDS,
        )
        info = rdb.info()
    except (redis.ConnectionError, TypeError) as ex:
        log.error("Error making Redis connection: %s", ex.args)
        return {"status": DOWN}
    except redis.ResponseError as ex:
        log.error("Bad Redis response: %s", ex.args)
        return {"status": DOWN, "message": "auth error"}
    micro = (datetime.datetime.now() - start).microseconds
    del rdb  # the redis package does not support Redis's QUIT.
    ret = {
        "status": UP, "response_microseconds": micro,
    }
    fields = ("uptime_in_seconds", "used_memory", "used_memory_peak")
    ret.update({x: info[x] for x in fields})
    return ret


def get_celery_info():
    """
    Check celery availability
    """
    start = datetime.datetime.now()
    try:
        insp = celery.task.control.inspect()
        celery_stats = insp.stats()
        if not celery_stats:
            log.error("No running Celery workers were found.")
            return {"status": DOWN, "message": "No running Celery workers"}
    except IOError as exp:
        log.error("Error connecting to the backend: %s", exp)
        return {"status": DOWN, "message": "Error connecting to the backend"}
    return {"status": UP, "response_microseconds": (datetime.datetime.now() - start).microseconds}


def status(request):  # pylint: disable=unused-argument
    """
    Status view
    """
    def create_response(data, status_code):
        """
        helper function to create a response
        """
        resp = JsonResponse(data)
        resp.status_code = status_code
        return resp

    if request.GET.get("token", "") != settings.STATUS_TOKEN:
        return create_response(
            {'error': 'token_error'},
            status_codes.HTTP_400_BAD_REQUEST
        )
    info = {}

    log.debug("Getting postgres status")
    info["postgresql"] = get_pg_info()

    log.debug("Getting redis status")
    info["redis"] = get_redis_info()

    log.debug("Getting celery status")
    info["celery"] = get_celery_info()

    code = status_codes.HTTP_200_OK
    for key in info:
        if info[key]["status"] == DOWN:
            code = status_codes.HTTP_503_SERVICE_UNAVAILABLE
            break
    return create_response(info, code)
