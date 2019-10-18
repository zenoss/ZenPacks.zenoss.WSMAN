##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012-2018, all rights reserved.
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

from twisted.internet import defer

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin

from ZenPacks.zenoss.WSMAN.utils import addLocalLibPath

addLocalLibPath()

import txwsman


def create_enum_info(className, wql=None, namespace=None):
    return txwsman.util.create_enum_info(className, wql, namespace)


class WSMANPlugin(PythonPlugin):

    deviceProperties = PythonPlugin.deviceProperties + (
        'zWSMANPort',
        'zWSMANUsername',
        'zWSMANPassword',
        'zWSMANUseSSL',
        'zWSMANMaxObjectCount',
        )

    wsman_queries = {}

    def client(self, conn_info):
        '''
        Return a WSMAN Collect Client
        '''
        return txwsman.enumerate.create_wsman_client(conn_info)

    def conn_info(self, device):
        '''
        Return a ConnectionInfo given device.
        '''

        hostname = device.manageIp
        username = device.zWSMANUsername
        auth_type = 'basic'
        password = device.zWSMANPassword
        scheme = 'https' if device.zWSMANUseSSL is True else 'http'
        port = int(device.zWSMANPort)
        connectiontype = 'Keep-Alive'
        keytab = ''

        return txwsman.util.ConnectionInfo(
            hostname,
            auth_type,
            username,
            password,
            scheme,
            port,
            connectiontype,
            keytab)

    @defer.inlineCallbacks
    def collect(self, device, log):
        '''
        Collect results of the class' queries list.

        This method should be overridden
        if more complex collection is required.
        '''

        if not device.zWSMANUseSSL:
            log.warning("SSL not enabled for %s", device.id)
            self._eventService.sendEvent({
                'device': device.id,
                'eventKey': "{}|{}".format(device.id, 'wsmanCollectSsl'),
                'eventClassKey': 'wsmanCollect',
                'severity': ZenEventClasses.Warning,
                'summary': 'WSMAN: SSL not enabled',
                'message': 'SSL not enabled for {}'.format(device.id),
            })
        else:
            self._eventService.sendEvent({
                'device': device.id,
                'eventKey': "{}|{}".format(device.id, 'wsmanCollectSsl'),
                'eventClassKey': 'wsmanCollect',
                'severity': ZenEventClasses.Clear,
                'summary': 'WSMAN: SSL enabled',
            })

        conn_info = self.conn_info(device)
        client = self.client(conn_info)

        enum_infos = map(
            create_enum_info,
            self.wsman_queries,
            self.wsman_queries.values())

        results = {}

        for enum_info in enum_infos:
            try:
                results[enum_info.className] = yield client.enumerate(
                    enum_info.className,
                    wql=enum_info.wql,
                    namespace=enum_info.namespace,
                    maxelements=device.zWSMANMaxObjectCount)
            except txwsman.util.RequestError as e:
                if 'unauthorized' in e.message:
                    raise
                else:
                    log.error(
                        "%s, %s class name returned error: %s",
                        device.id, enum_info.className, e.message)
                    continue

        defer.returnValue(results)
