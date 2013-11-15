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

from twisted.internet import defer

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin

from ZenPacks.zenoss.WSMAN.utils import addLocalLibPath

addLocalLibPath()

import txwsman

class WSMANPlugin(PythonPlugin):

    deviceProperties = PythonPlugin.deviceProperties + (
        'zWSMANPort',
        'zWSMANUsername',
        'zWSMANPassword',
        'zWSMANUseSSL',
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
        scheme = 'https' if device.zWSMANUseSSL == True else 'http'
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


    def create_enum_info(self, className, wql=None, namespace=None):
        return txwsman.util.create_enum_info(className, wql, namespace)

    @defer.inlineCallbacks
    def collect(self, device, log):
        '''
        Collect results of the class' queries list.
        
        This method should be overridden if more complex collection is required.
        '''

        conn_info = self.conn_info(device)
        client = self.client(conn_info)
        
        try:
            results = yield client.do_enumerate( map(self.create_enum_info, self.wsman_queries, self.wsman_queries.values()))
            import pdb;pdb.set_trace()

        except txwsman.util.RequestError as e:
            log.error(e[0])
            raise


        defer.returnValue(results)

        '''
        if not self.wql_queries:
            pass
    
        try:
            pass
        except Exception as e:
            log.error(e[0])
            raise

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
        '''

    def check_results(self, results, device, log):
        """Check results for errors."""

        # If all results are failures we have a problem to report.
        if len(results) and True not in set(x[0] for x in results):
            log.error('%s WSMAN: %s', device.id, result_errmsg(results[0][1]))

            #This will allow for an event to be created by the device class.
            results = "ERROR", result_errmsg(results[0][1])

            return results

        return results
