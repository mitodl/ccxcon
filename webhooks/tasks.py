"""
Celery tasks.
"""
import hashlib
import hmac
import json
import logging

from django.apps import apps
from django.core.exceptions import FieldError
from django.utils.encoding import force_bytes
import requests
from requests.exceptions import RequestException

from ccxcon.celery import async
from webhooks.models import Webhook

log = logging.getLogger(__name__)


@async.task
def publish_webhook(model_str, lookup_field, lookup_value):
    """
    Publishes model updates to various services as defined by Webhook instances.

    Args:
        model_str (str): Model name in the format of "app.Model"
        lookup_field (str): Model field to use in lookup.
        lookup_value: Value to pass for model lookup.

    Returns:
        None
    """
    try:
        app, model_label = model_str.split('.')
    except ValueError:
        log.warning("Malformed model string for webhook serialization: %s",
                    model_str)
        raise

    try:
        model = apps.get_model(app, model_label)
    except LookupError:
        log.warning("Could not find the model %s for webhook publishing.",
                    model_str)
        raise

    try:
        instance = model.objects.get(**{lookup_field: lookup_value})
        if not hasattr(instance, 'to_webhook'):
            log.info("Not submitting %s:%s=%s to webhook. It does not support "
                     "serialization", type(instance), lookup_field,
                     lookup_value)
            return

        payload = {
            'action': 'update',
            'type': model_label,
            'payload': instance.to_webhook()
        }

    except model.DoesNotExist:
        # Send delete.
        payload = {
            'action': 'delete',
            'type': model_label,
            'payload': {
                lookup_field: lookup_value
            },
        }
    except model.MultipleObjectsReturned:
        log.warning("Webhook lookup by PK unsuccessful. Returned multiple on pk "
                    "lookup. <%s %s=%s>", model_str, lookup_field, lookup_value)
        raise
    except FieldError as e:
        log.error("Unknown lookup field when fetching model %s: %s", model, e)
        raise

    for wh in Webhook.active.all():
        try:
            j_payload = json.dumps(payload)
            signature = hmac.new(force_bytes(wh.secret), force_bytes(j_payload),
                                 hashlib.sha1).hexdigest()
            log.debug("Posting payload with signature %s. Payload: %s", signature, j_payload)
            # NOTE: Using the non-stringy version, given we're posting this as json.
            requests.post(wh.url, json=payload, headers={
                'X-CCXCon-Signature': signature
            })
        except RequestException as e:
            log.error("Failed to post to %s with payload %s due to error %s",
                      wh.url, j_payload, e)
