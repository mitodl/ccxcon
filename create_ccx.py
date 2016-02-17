"""
Script to create a CCX using the CCXCon REST APIs
"""

import argparse
import sys

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

HTTP_201_CREATED = 201
CCXCON_TOKEN_URL = '/o/token/'
CCXCON_CREATE_CCX = '/api/v1/ccx/'


def parse_arguments():
    """
    Parsing arguments necessary to create the CCX
    """
    parser = argparse.ArgumentParser(description="Create a CCX using CCXCon")
    # Parameters for CCXCon information
    parser.add_argument('--ccxcon-url', dest='ccxconurl',
                        help="The CCXCon URL to be used", required=True)
    parser.add_argument('--client-id', dest='clientid',
                        help="The user's OAUTH ID", required=True)
    parser.add_argument('--client-secret', dest='clientsecret',
                        help="The user's OAUTH SECRET", required=True)
    # Parameters for creating the CCX
    parser.add_argument('--master-course', dest='mastercourse',
                        help="The master course UUID", required=True)
    parser.add_argument('--user-email', dest='useremail',
                        help="The coach email", required=True)
    parser.add_argument('--seats', type=int, dest='seats',
                        help="The number of seats for the CCX", required=True)
    parser.add_argument('--ccx-title', dest='ccxtitle',
                        help="The title for the CCX", required=True)
    parser.add_argument('--modules', dest='modules', nargs="*",
                        help="Course modules")
    # Parameters for the script
    parser.add_argument('--no-cert-verify', dest='certverify', action='store_false',
                        default=True, help="No SSL certificate verification")
    return parser.parse_args()


def _get_oauth_client(ccxcon_url, client_id, client_secret, cert_verify):
    """
    Function that creates an oauth client and fetches a token.
    """
    client = BackendApplicationClient(client_id=client_id)
    oauth_ccxcon = OAuth2Session(client=client)
    oauth_ccxcon.fetch_token(
        token_url="{}{}".format(ccxcon_url.rstrip('/'), CCXCON_TOKEN_URL),
        client_id=client_id,
        client_secret=client_secret,
        verify=cert_verify
    )
    return oauth_ccxcon


# pylint: disable=too-many-arguments
def create_ccx_through_ccxcon(ccxcon_url, client_id, client_secret,
                              master_course_uuid, user_email, seats, ccx_title,
                              course_modules=None, cert_verify=True):
    """
    Creates a CCX using the CCXCon
    """
    oauth_ccxcon = _get_oauth_client(ccxcon_url, client_id, client_secret, cert_verify)
    payload = {
        'master_course_id': master_course_uuid,
        'user_email': user_email,
        'total_seats': seats,
        'display_name': ccx_title,
    }
    if course_modules is not None:
        payload['course_modules'] = course_modules
    headers = {'content-type': 'application/json'}

    # make the POST request
    resp = oauth_ccxcon.post(
        url="{}{}".format(ccxcon_url.rstrip('/'), CCXCON_CREATE_CCX),
        json=payload,
        headers=headers,
        verify=cert_verify
    )
    # pylint: disable=superfluous-parens
    if resp.status_code != HTTP_201_CREATED:
        print('Server returned unexpected status code {}'.format(resp.status_code))
        sys.exit(1)
    print('CCX successfully created')


def main():
    """
    Entry point for the script
    """
    args = parse_arguments()

    create_ccx_through_ccxcon(
        args.ccxconurl,
        args.clientid,
        args.clientsecret,
        args.mastercourse,
        args.useremail,
        args.seats,
        args.ccxtitle,
        args.modules,
        args.certverify
    )


if __name__ == '__main__':
    main()
