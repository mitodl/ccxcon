Release Notes
=============

Version 0.2.0
-------------

- Added missing release_notes template files.
- Changed to ``django-server-status``.
- Added logging message for webhooks with non-200 responses.
- Removed ``dredd``, removed unused HTTP methods from API, added unit tests.
- Added generator script for life-like data.
- Implemented receiving JSON on ``create-ccx`` endpoint.
- Added support for course modules.
- Fixed ``requests`` installation.
- Added additional logging.
- Incoming requests send uuids, not course ids.
- Included the course/module's instance in webhook.
- disabled SSL being necessary for celery.
- Added status.
- Enabled ``redis`` in the web container.
- Made webhook fixes.
- Added API endpoint to create ccxs on edX.
- Now fetching module listing through course structure api.

Version 0.1.0
-------------

- Initial release
