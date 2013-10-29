##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""API interface to the PyWSMAN library.

WSMAN classes available
    EnumerateClassNames
    EnumerateClasses
    EnumerateInstances
    EnumerateInstanceNames

example:
    wbemQueries = {
        'ec':'root/emc',
        'ein':'root/emc:CIM_ManagedElement'
        }

You must also have the zWSMANPort, zWSMANUsername and zWSMANPassword properties
set to succesfully pull data.

"""

from twisted.internet import ssl, reactor
from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin

from ZenPacks.zenoss.WSMAN.utils import addLocalLibPath, result_errmsg

addLocalLibPath()

from pywbem.twisted_client import (
    EnumerateClassNames,
    EnumerateClasses,
    EnumerateInstanceNames,
    EnumerateInstances,
    )


class WSMANPlugin(PythonPlugin):

    deviceProperties = PythonPlugin.deviceProperties + (
        'zWSMANPort',
        'zWSMANUsername',
        'zWSMANPassword',
        'zWSMANUseSSL',
        )

    wbemQueries = {}

    def collect(self, device, log):
        if not device.manageIp:
            log.error('%s has no management IP address', device.id)

        if not device.zWSMANPort:
            log.error("zWSMANPort empty for %s", device.id)

        if not device.zWSMANUsername:
            log.error("zWSMANUsername empty for %s", device.id)

        if not device.zWSMANPassword:
            log.error("zWSMANPassword empty for %s", device.id)

        if not device.manageIp or \
            not device.zWSMANPort or \
            not device.zWSMANUsername or \
            not device.zWSMANPassword:
            return None

        deferreds = []

        for wbemnamespace, wbemclass in self.wbemQueries.items():
            namespaces = wbemnamespace.split(":")
            namespace = namespaces[0]
            if len(namespaces) > 1:
                classname = namespaces[1]

            userCreds = (device.zWSMANUsername, device.zWSMANPassword)

            if wbemclass == 'ec':
                wbemClass = EnumerateClasses(
                    userCreds, namespace=namespace)

            elif wbemclass == 'ecn':
                wbemClass = EnumerateClassNames(
                    userCreds, namespace=namespace)

            elif wbemclass == 'ei':
                wbemClass = EnumerateInstances(
                    userCreds, namespace=namespace, classname=classname)

            elif wbemclass == 'ein':
                wbemClass = EnumerateInstanceNames(
                    userCreds, namespace=namespace, classname=classname)

            else:
                log.warn('Incorrect class call %s', wbemclass)
                wbemClass = EnumerateClasses(userCreds,
                                             namespace=namespace)

            deferreds.append(wbemClass.deferred)

            if device.zWSMANUseSSL == True:
                reactor.connectSSL(
                    host=device.manageIp,
                    port=int(device.zWSMANPort),
                    factory=wbemClass,
                    contextFactory=ssl.ClientContextFactory())
            else:
                reactor.connectTCP(
                    host=device.manageIp,
                    port=int(device.zWSMANPort),
                    factory=wbemClass)

        # Execute the deferreds and return the results to the callback.
        d = DeferredList(deferreds, consumeErrors=True)
        d.addCallback(self.check_results, device, log)

        return d

    def check_results(self, results, device, log):
        """Check results for errors."""

        # If all results are failures we have a problem to report.
        if len(results) and True not in set(x[0] for x in results):
            log.error('%s WSMAN: %s', device.id, result_errmsg(results[0][1]))

            #This will allow for an event to be created by the device class.
            results = "ERROR", result_errmsg(results[0][1])

            return results

        return results
