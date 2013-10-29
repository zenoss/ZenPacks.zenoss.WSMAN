"""
Process transport based on subprocess

@copyright: 2010-2012
@author: Joseph Tallieu <joseph_tallieu@dell.com>
@author: Vijay Halaharvi <vijay_halaharvi@dell.com>
@organization: Dell Inc. - PG Validation
@license: GNU LGLP v2.1
"""
#    This file is part of WSManAPI.
#
#    WSManAPI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 2.1 of the License, or
#    (at your option) any later version.
#
#    WSManAPI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with WSManAPI.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import time
import logging

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import DNSLookupError
from twisted.web.client import getPage
from twisted.web.error import Error as HTTPError
from .. import Transport

log = logging.getLogger("WSMAN.transport")

class ZAPIError(Exception):
    pass

class Twisted(Transport):
    """
    Twisted based transport
    """

    def __init__(self):
        """
        Constructor for the twisted transport
        """

        # Base class
        super(Twisted, self).__init__()

        self.id = 'twisted'


    @inlineCallbacks
    def execute(self, command):
        """
        Execute the command and return the output.

        @param command: The command constructed by the provider.
        @type command: String

        @return: The output from the command execution
        @rtype: String
        """
        start = time.time()
        try:
            log.debug("Requesting %s" % body)
            result = yield getPage( self.url, method='POST', headers=headers, postdata=xml(body))
            log.debug("Received '%s'" % result)
        except Exception, ex:
            if isinstance(ex, DNSLookupError):
                raise ZAPIError('%s cannot be resolved' % self.base_url)
            elif isinstance(ex, HTTPError):
                if int(ex.status) == 401:
                    raise ZAPIError(
                        'Invalid credentials. Check zCommandUsername and '
                        'zCommandPassword.')
                else:
                    raise ZAPIError(ex)
            else:
                raise ZAPIError(ex) 



        duration = time.time() - start
        output = result
        log.info("Command Completed in %0.3f s" % duration, extra={'command': command, 'output': output, 'duration':duration})
        returnValue(output)

