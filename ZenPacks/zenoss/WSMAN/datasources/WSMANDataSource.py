##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
log = logging.getLogger('zen.WSMAN')

import calendar

from twisted.internet import reactor, ssl

from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.Utils import prepId
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourcePlugin

from ZenPacks.zenoss.WSMAN.utils import addLocalLibPath, result_errmsg

addLocalLibPath()
from txwsman import util as txwsman_util
from txwsman import enumerate as txwsman_enumerate

def string_to_lines(string):
    if isinstance(string, (list, tuple)):
        return string
    elif hasattr(string, 'splitlines'):
        return string.splitlines()

    return None


class WSMANDataSource(PythonDataSource):
    """Datasource used to capture datapoints from WSMAN providers."""

    ZENPACKID = 'ZenPacks.zenoss.WSMAN'

    sourcetypes = ('WSMAN',)
    sourcetype = sourcetypes[0]

    plugin_classname = 'ZenPacks.zenoss.WSMAN.datasources.WSMANDataSource.WSMANDataSourcePlugin'

    namespace = 'root/dcim'
    query_language = 'WQL'  # hard-coded for now.
    query = ''
    CIMClass = ''
    result_component_key = ''
    result_component_value = ''
    result_timestamp_key = ''

    _properties = PythonDataSource._properties + (
        {'id': 'namespace', 'type': 'string'},
        {'id': 'query_language', 'type': 'string'},
        {'id': 'query', 'type': 'string'},
        {'id': 'CIMCLass', 'type': 'string'},
        {'id': 'result_component_key', 'type': 'string'},
        {'id': 'result_component_value', 'type': 'string'},
        {'id': 'result_timestamp_key', 'type': 'string'},
        )


class IWSMANDataSourceInfo(IRRDDataSourceInfo):
    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))

    namespace = schema.TextLine(
        group=_t('WSMAN'),
        title=_t('Namespace'))

    CIMClass = schema.Text(
        group=_t(u'WSMAN'),
        title=_t('CIM Class'))

    query = schema.Text(
        group=_t(u'WSMAN'),
        title=_t('Query'),
        xtype='twocolumntextarea')

    result_component_key = schema.TextLine(
        group=_t(u'WSMAN Results'),
        title=_t(u'Result Component Key'))

    result_component_value = schema.TextLine(
        group=_t(u'WSMAN Results'),
        title=_t(u'Result Component Value'))

    result_timestamp_key = schema.TextLine(
        group=_t(u'WSMAN Results'),
        title=_t(u'Result Timestamp Key'))


class WSMANDataSourceInfo(RRDDataSourceInfo):
    implements(IWSMANDataSourceInfo)
    adapts(WSMANDataSource)

    testable = False

    cycletime = ProxyProperty('cycletime')

    namespace = ProxyProperty('namespace')
    CIMClass = ProxyProperty('CIMClass')
    query = ProxyProperty('query')
    result_component_key = ProxyProperty('result_component_key')
    result_component_value = ProxyProperty('result_component_value')
    result_timestamp_key = ProxyProperty('result_timestamp_key')


class WSMANDataSourcePlugin(PythonDataSourcePlugin):
    proxy_attributes = (
        'zWSMANPort', 'zWSMANUsername', 'zWSMANPassword', 'zWSMANUseSSL',
        )

    @classmethod
    def config_key(cls, datasource, context):
        params = cls.params(datasource, context)
        return (
            context.device().id,
            datasource.getCycleTime(context),
            datasource.rrdTemplate().id,
            datasource.id,
            datasource.plugin_classname,
            params.get('namespace'),
            params.get('query_language'),
            params.get('CIMClass'),
            params.get('query'),
            )

    @classmethod
    def params(cls, datasource, context):
        params = {}

        params['namespace'] = datasource.talesEval(
            datasource.namespace, context)

        params['query_language'] = datasource.query_language

        params['query'] = datasource.talesEval(
            ' '.join(string_to_lines(datasource.query)), context)

        params['CIMClass'] = datasource.talesEval(
            ' '.join(string_to_lines(datasource.CIMClass)), context)

        params['result_component_key'] = datasource.talesEval(
            datasource.result_component_key, context)

        params['result_component_value'] = datasource.talesEval(
            datasource.result_component_value, context)

        params['result_timestamp_key'] = datasource.talesEval(
            datasource.result_timestamp_key, context)

        return params

    def collect(self, config):

        ds0 = config.datasources[0]
        def conn_info(datasource, config):
            ip = config.manageIp
            username = datasource.zWSMANUsername
            password = datasource.zWSMANPassword
            auth_type = 'basic'
            scheme = 'https' if datasource.zWSMANUseSSL == True else 'http'
            port = int(datasource.zWSMANPort)
            connectiontype = 'Keep-Alive'
            keytab = ''
            return txwsman_util.ConnectionInfo(
                      ip,
                      auth_type,
                      username,
                      password,
                      scheme,
                      port,
                      connectiontype,
                      keytab)

        def client(conn_info):
            return txwsman_enumerate.create_wsman_client(conn_info)

        def create_enum_info(className, wql=None, namespace=None):
            return txwsman_util.create_enum_info(className, wql, namespace)

        connInfo = conn_info(ds0, config)
        remote_client = client(connInfo)
        enumInfo = create_enum_info(ds0.params['CIMClass'], ds0.params['query'], ds0.params['namespace'])

        # Do Enumerate expects an array of enumInfo objects
        d = remote_client.do_enumerate([enumInfo])
        return d

    def onSuccess(self, results, config):
        data = self.new_data()

        # drop the dictionary key as its unneeded here.  We will only ever
        # have one class
        results = results.values()[0]

        if not isinstance(results, list):
            results = [results]

        # Convert datasources to a dictionary with result_component_value as
        # the key. This allows us to avoid an inner loop below.
        datasources = dict(
            (x.params.get('result_component_value', ''), x) \
                for x in config.datasources)

        result_component_key = \
            config.datasources[0].params['result_component_key']

        for result in results:
            if result_component_key:
                datasource = datasources.get(result[result_component_key])

                if not datasource:
                    continue

            else:
                datasource = config.datasources[0]

            if result_component_key and hasattr(result, result_component_key):
                result_component_value = datasource.params.get(
                    'result_component_value')

                if result_component_value != result[result_component_key]:
                    continue
            if datasource.component:
                component_id = prepId(datasource.component)
            else:
                component_id = None

            # Determine the timestamp that the value was collected.
            result_timestamp_key = datasource.params.get(
                'result_timestamp_key')

            timestamp = None

            if result_timestamp_key and result_timestamp_key in result:
                cim_date = result[result_timestamp_key]
                timestamp = calendar.timegm(cim_date.datetime.utctimetuple())

            if not timestamp:
                timestamp = 'N'

            for datapoint in datasource.points:
                if hasattr(result, datapoint.id):
                    data['values'][component_id][datapoint.id] = \
                        (getattr(result, datapoint.id), timestamp)


        data['events'].append({
            'eventClassKey': 'wsmanCollectionSuccess',
            'eventKey': 'wsmanCollection',
            'summary': 'WSMAN: successful collection',
            'device': config.id,
            })
        return data

    def onError(self, result, config):
        errmsg = 'WSMAN: %s' % result_errmsg(result)

        log.error('%s %s', config.id, errmsg)

        data = self.new_data()
        data['events'].append({
            'eventClassKey': 'wsmanCollectionError',
            'eventKey': 'wsmanCollection',
            'summary': errmsg,
            'device': config.id,
            })

        return data
