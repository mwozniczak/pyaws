"""
Command-line Interface (CLI) Utilities Module

Module Functions:
    - get_os:
        Retrieve localhost os type, ancillary environment specifics
    - awscli_defaults:
        determine awscli config file locations on localhost
    - import_file_object:
        import text filesystem object and convert to object
    - export_json_object:
        write a json object to a filesystem object
    - read_local_config:
        parse local config file
    - config_init:
        Initializes config file where none exists
"""
import sys
import os
import json
import platform
import datetime
import logging
import inspect
from pygments import highlight, lexers, formatters
from pyaws.colors import Colors
from pyaws import __version__

# globals
MODULE_VERSION = '1.16'
logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


def debug_mode(header, data_object, debug=False, halt=False):
    """ debug output """
    if debug:
        print('\n  ' + str(header) + '\n')
        try:
            export_json_object(data_object)
        except Exception:
            print(data_object)
        if halt:
            sys.exit(0)
    return True


def awscli_defaults(os_type=None):
    """
    Summary:
        Parse, update local awscli config credentials
    Args:
        :user (str):  USERNAME, only required when run on windows os
    Returns:
        TYPE: dict object containing key, value pairs describing
        os information
    """

    try:
        if os_type is None:
            os_type = platform.system()

        if os_type == 'Linux':
            HOME = os.environ['HOME']
            awscli_credentials = HOME + '/.aws/credentials'
            awscli_config = HOME + '/.aws/config'
        elif os_type == 'Windows':
            username = os.getenv('username')
            awscli_credentials = 'C:\\Users\\' + username + '\\.aws\\credentials'
            awscli_config = 'C:\\Users\\' + username + '\\.aws\\config'
        elif os_type == 'Java':
            logger.warning('Unsupported OS. No information')
            HOME = os.environ['HOME']
            awscli_credentials = HOME + '/.aws/credentials'
            awscli_config = HOME + '/.aws/config'
        alt_credentials = os.getenv('AWS_SHARED_CREDENTIALS_FILE')
    except OSError as e:
        logger.exception(
            '%s: problem determining local os environment %s' %
            (inspect.stack()[0][3], str(e))
            )
        raise e
    return {
                'awscli_defaults': {
                    'awscli_credentials': awscli_credentials,
                    'awscli_config': awscli_config,
                    'alt_credentials': alt_credentials
                }
            }


def config_init(config_file, json_config_obj, config_dirname=None):
    """
    Summary:
        Creates local config from JSON seed template
    Args:
        :config_file (str): filesystem object containing json dict of config values
        :json_config_obj (json):  data to be written to config_file
        :config_dirname (str):  dir name containing config_file
    Returns:
        TYPE: bool, Success | Failure
    """
    HOME = os.environ['HOME']
    # client config dir
    if config_dirname:
        dir_path = HOME + '/' + config_dirname
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            os.chmod(dir_path, 0o755)
    else:
        dir_path = HOME
    # client config file
    r = export_json_object(
            dict_obj=json_config_obj,
            filename=dir_path + '/' + config_file
        )
    return r


def export_json_object(dict_obj, filename=None, logging=True):
    """
    Summary:
        exports object to block filesystem object

    Args:
        :dict_obj (dict): dictionary object
        :filename (str):  name of file to be exported (optional)

    Returns:
        True | False Boolean export status

    """
    try:
        if filename:
            try:
                with open(filename, 'w') as handle:
                    handle.write(json.dumps(dict_obj, indent=4, sort_keys=True))
                    logger.info(
                        '%s: Wrote %s to local filesystem location' %
                        (inspect.stack()[0][3], filename))
                handle.close()
            except TypeError as e:
                logger.warning(
                    '%s: object in dict not serializable: %s' %
                    (inspect.stack()[0][3], str(e)))
        else:
            json_str = json.dumps(dict_obj, indent=4, sort_keys=True)
            print(highlight(json_str, lexers.JsonLexer(), formatters.TerminalFormatter()).strip())
            if logging:
                logger.info('%s: successful export to stdout' % inspect.stack()[0][3])
            return True
    except OSError as e:
        logger.critical(
            '%s: export_file_object: error writing to %s to filesystem. Error: %s' %
            (inspect.stack()[0][3], filename, str(e)))
        return False
    if logging:
        logger.info('export_file_object: successful export to %s' % filename)
    return True


def get_os(detailed=False):
    """
    Summary:
        Retrieve local operating system environment characteristics
    Args:
        :user (str): USERNAME, only required when run on windows os
    Returns:
        TYPE: dict object containing key, value pairs describing
        os information
    """
    try:

        os_type = platform.system()

        if os_type == 'Linux':
            os_detail = platform.platform()
            distribution = platform.linux_distribution()[0]
            HOME = os.getenv('HOME')
            username = os.getenv('USER')
        elif os_type == 'Windows':
            os_detail = platform.platform()
            username = os.getenv('username') or os.getenv('USER')
            HOME = 'C:\\Users\\' + username
        else:
            logger.warning('Unsupported OS. No information')
            os_type = 'Java'
            os_detail = 'unknown'
            HOME = os.getenv('HOME')
            username = os.getenv('USER')

    except OSError as e:
        raise e
    except Exception as e:
        logger.exception(
            '%s: problem determining local os environment %s' %
            (inspect.stack()[0][3], str(e))
            )
    if detailed and os_type == 'Linux':
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'linux_distribution': distribution,
                'username': username,
                'HOME': HOME
            }
    elif detailed:
        return {
                'os_type': os_type,
                'os_detail': os_detail,
                'username': username,
                'HOME': HOME
            }
    return {'os_type': os_type}


def import_file_object(filename):
    """
    Summary:
        Imports block filesystem object
    Args:
        :filename (str): block filesystem object
    Returns:
        dictionary obj (valid json file), file data object
    """
    try:
        handle = open(filename, 'r')
        file_obj = handle.read()
        dict_obj = json.loads(file_obj)

    except OSError as e:
        logger.critical(
            'import_file_object: %s error opening %s' % (str(e), str(filename))
        )
        raise e
    except ValueError:
        logger.info(
            '%s: import_file_object: %s not json. file object returned' %
            (inspect.stack()[0][3], str(filename))
        )
        return file_obj    # reg file, not valid json
    return dict_obj


def json_integrity(baseline, suspect):
    """
    Summary:
        Validates baseline dict against suspect dict to ensure contain USERNAME
        k,v parameters.
    Args:
        baseline (dict): baseline json structure
        suspect (dict): json object validated against baseline structure
    Returns:
        Success (matches baseline) | Failure (no match), TYPE: bool
    """
    try:
        for k,v in baseline.items():
            for ks, vs in suspect.items():
                keys_baseline = set(v.keys())
                keys_suspect = set(vs.keys())
                intersect_keys = keys_baseline.intersection(keys_suspect)
                added = keys_baseline - keys_suspect
                rm = keys_suspect - keys_baseline
                logger.info('keys added: %s, keys removed %s' % (str(added), str(rm)))
                if keys_baseline != keys_suspect:
                    return False
    except KeyError as e:
        logger.info(
            'KeyError parsing pre-existing config (%s). Replacing config file' %
            str(e))
    return True


def json_integrity_multilevel(d1, d2):
    """ still under development """
    keys = [x for x in d2]
    for key in keys:
        d1_keys = set(d1.keys())
        d2_keys = set(d2.keys())
        intersect_keys = d1_keys.intersection(d2_keys)
        added = d1_keys - d2_keys
        removed = d2_keys - d1_keys
        modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
        same = set(o for o in intersect_keys if d1[o] == d2[o])
        if added == removed == set():
            d1_values = [x for x in d1.values()][0]
            print('d1_values: ' + str(d1_values))
            d2_values = [x for x in d2.values()][0]
            print('d2_values: ' + str(d2_values))
            length = len(d2_values)
            print('length = %d' % length)
            pdb.set_trace()
            if length > 1:
                d1 = d1_values.items()
                d2 = d2_values.items()
        else:
            return False
    return True


def read_local_config(cfg):
    """ Parses local config file for override values

    Args:
        :local_file (str):  filename of local config file

    Returns:
        dict object of values contained in local config file
    """
    try:
        if os.path.exists(cfg):
            config = import_file_object(cfg)
            return config
        else:
            logger.warning(
                '%s: local config file (%s) not found, cannot be read' %
                (inspect.stack()[0][3], str(cfg)))
    except OSError as e:
        logger.warning(
            'import_file_object: %s error opening %s' % (str(e), str(cfg))
        )
    return {}


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path
