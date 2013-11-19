##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from twisted.internet.error import ConnectionRefusedError, TimeoutError


def addLocalLibPath():
    """
    Helper to add the ZenPack's lib directory to PYTHONPATH.
    """
    import os
    import site

    site.addsitedir(os.path.join(os.path.dirname(__file__), 'lib'))

def result_errmsg(result):
    """Return a useful error message string given a twisted errBack result."""
    try:

        if result.type == ConnectionRefusedError:
            return 'connection refused. Check IP and zWSMANPort'
        elif result.type == TimeoutError:
            return 'connection timeout. Check IP and zWSMANPort'
        elif result.type == NameError:
            return 'Invalid CIM Class.  Class not found.'
#        elif result.type == CIMError:
#            if '401' in result.value.args[1]:
#                return 'login failed. Check zWSMANUsername and zWSMANPassword'
#            else:
#                return result.value.args[1]
        else:
            return result.getErrorMessage()
    except AttributeError:
        pass

    return str(result)
