#!/usr/bin/env python3

import argparse
import os
import sys
import json
import inspect
from pygments import highlight, lexers, formatters
import boto3
from pyaws import logd, __version__
from botocore.exceptions import ClientError
from pyaws.core.session import authenticated, boto3_session
from pyaws.core.script_utils import stdout_message, export_json_object

try:
    from pyaws.core.oscodes_unix import exit_codes
except Exception:
    from pyaws.core.oscodes_win import exit_codes    # non-specific os-safe codes

# globals
logger = logd.getLogger(__version__)
VALID_AMI_TYPES = ('amazonlinux1', 'amazonlinux2', 'redhat', 'ubuntu14.04', 'ubuntu16.04')
VALID_FORMATS = ('json', 'text')
DEFAULT_REGION = os.environ['AWS_DEFAULT_REGION']


def get_regions(profile):
    """ Return list of all regions """
    try:

        client = boto3_session(service='ec2', profile=profile)

    except ClientError as e:
        logger.exception('%s: Boto error while retrieving regions (%s)' %
            (inspect.stack()[0][3], str(e)))
        raise e
    return [x['RegionName'] for x in client.describe_regions()['Regions']]


def amazonlinux1(profile, region=None, detailed=False, debug=False):
    """
    Return latest current amazonlinux v1 AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)

    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'amzn-ami-hvm-2018.??.?.2018????-x86_64-gp2'
                        ]
                    }
                ])
            metadata[region] = r['Images'][0]
            amis[region] = r['Images'][0]['ImageId']
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def amazonlinux2(profile, region=None, detailed=False, debug=False):
    """
    Return latest current amazonlinux v2 AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)

    # retrieve ami for each region in list
    for region in regions:
        try:
            if not profile:
                profile = 'default'
            client = boto3_session(service='ec2', region=region, profile=profile)

            r = client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'amzn2-ami-hvm-????.??.?.2018????.?-x86_64-gp2',
                            'amzn2-ami-hvm-????.??.?.2018????-x86_64-gp2'
                        ]
                    }
                ])
            metadata[region] = r['Images'][0]
            amis[region] = r['Images'][0]['ImageId']
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def redhat(profile, region=None, detailed=False, debug=False):
    """
    Return latest current amazonlinux v1 AMI for each region
    Args:
        :profile (str): profile_name
        :region (str): if supplied as parameter, only the ami for the single
        region specified is returned
    Returns:
        amis, TYPE: list:  container for metadata dict for most current instance in region
    """
    amis, metadata = {}, {}
    if region:
        regions = [region]
    else:
        regions = get_regions(profile=profile)

    # retrieve ami for each region in list
    for region in regions:
        try:
            client = boto3_session(service='ec2', region=region, profile=profile)
            r = client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [

                        ]
                    }
                ])
            metadata[region] = r['Images'][0]
            amis[region] = r['Images'][0]['ImageId']
        except ClientError as e:
            logger.exception(
                '%s: Boto error while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            continue
        except Exception as e:
            logger.exception(
                '%s: Unknown Exception occured while retrieving AMI data (%s)' %
                (inspect.stack()[0][3], str(e)))
            raise e
    if detailed:
        return metadata
    return amis


def main(profile, imagetype, format, filename=''):
    """
    Summary:
        Calls appropriate module function to identify the latest current amazon machine
        image for the specified OS type
    Returns:
        json (dict) | text (str)
    """
    if imagetype in ('amazonlinux1', 'aml1'):
        latest = amazonlinux1(profile=profile, debug=debug)
    elif image in ('amazonlinux2', 'aml2'):
        latest = amazonlinux2(profile=profile, debug=debug)

    # return appropriate response format
    if format == 'json' and not filename:
        export_json_object(dict_obj=latest)
        sys.exit(exit_codes['EX_OK']['Code'])

    elif format == 'json' and filename:
        export_json_object(dict_obj=latest, filename=filename)
        sys.exit(exit_codes['EX_OK']['Code'])

    elif format == 'text' and not filename:
        print('{}'.format(latest)


def options(parser, help_menu=True):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default", required=False, help="type (default: %(default)s)")
    parser.add_argument("-i", "--image", nargs='?', type=str, choices=VALID_AMI_TYPES, required=False)
    parser.add_argument("-f", "--format", nargs='?', default='json', type=str, choices=VALID_FORMATS, required=False)
    parser.add_argument("-n", "--filename", nargs='?', default='', type=str, required=False)
    parser.add_argument("-d", "--debug", dest='debug', default=False, action='store_true', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    #parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def init_cli():
    """ Collect parameters and call main """
    try:
        parser = argparse.ArgumentParser(add_help=True)
        args = options(parser)
    except Exception as e:
        #help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_MISC']['Code'])

    if debug:
        print('profile is: ' + args.profile)
        print('image type: ' + args.image)
        print('format: ' + args.format)
        print('filename: ' + args.filename)
        print('debug flag: %b', str(args.debug))

    if len(sys.argv) == 1:
        #help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif authenticated(profile=args.profile):
        # execute ami operation
        if args.image:
            main(
                    profile=args.profile, imagetype=args.image,
                    format=args.format, filename=args.filename
                )
        else:
            stdout_message(
                    f'Image type must be one of: {VALID_AMI_TYPES}'
                    prefix='INFO'
                )
            sys.exit(exit_codes['E_DEPENDENCY']['Code'])
    else:
        stdout_message(
            'Authenication Failed to AWS Account for user %s' % profile,
            prefix='AUTH',
            severity='WARNING'
            )
        sys.exit(exit_codes['E_AUTHFAIL']['Code'])

    failure = """ : Check of runtime parameters failed for unknown reason.
    Please ensure local awscli is configured. Then run keyconfig to
    configure keyup runtime parameters.   Exiting. Code: """
    logger.warning(failure + 'Exit. Code: %s' % sys.exit(exit_codes['E_MISC']['Code']))
    print(failure)


if __name__ == '__main__':
    sys.exit(init_cli())
