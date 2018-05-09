##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from twisted.python.failure import Failure

from Products.ZenEvents import ZenEventClasses
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.WSMAN.datasources.WSMANDataSource import (
    WSMANDataSourcePlugin
)
from ZenPacks.zenoss.WSMAN.tests.utils import (
    load_pickle, Stub
)


class TestWSMANDataSourcePlugin(BaseTestCase):

    def setUp(self):
        self.plugin = WSMANDataSourcePlugin()
        self.results = load_pickle('wsman_plugin_results')

        component_ids = ['5000C5005EAE2971', '5000C5005EAD4635',
                         '5000C5005EAD3ED5', '5000C5005EAD5689',
                         '5000C5005EAD5C05', '5000C5005EADFF95']
        datasources = []
        for component in component_ids:
            datasource = Stub(
                component=component,
                eventClass='',
                params={'result_component_key': 'SASAddress',
                        'result_component_value': component},
                device='test_device',
                datasource='DiskSpace',
                cycletime=300,
                plugin_classname=(
                    'ZenPacks.zenoss.WSMAN.datasources.'
                    'WSMANDataSource.WSMANDataSourcePlugin'),
                points=[Stub(id='FreeSizeInBytes'), Stub(id='UsedSizeInBytes')]
            )
            datasources.append(datasource)
        self.config = Stub(datasources=datasources, id='test_device')

    def test_onSuccess(self):
        data = self.plugin.onSuccess(self.results, self.config)
        event = data['events'][0]

        self.assertEquals(len(data['values']), 6)
        self.assertEquals(len(data['events']), 1)
        self.assertEquals(event['severity'], ZenEventClasses.Clear)

        # plugin will return empty string as an eventClass, but it will be
        # transformed to '/Unknown'. So empty string is expected behaviour in
        # this case
        self.assertEquals(event['eventClass'], '')

    def test_onError(self):
        f = Failure(Exception('test_onError'))

        data = self.plugin.onError(f, self.config)
        event = data['events'][0]

        self.assertEquals(len(data['values']), 0)
        self.assertEquals(len(data['events']), 1)
        self.assertEquals(event['severity'], ZenEventClasses.Error)

        # plugin will return empty string as an eventClass, but it will be
        # transformed to '/Unknown'. So empty string is expected behaviour in
        # this case
        self.assertEquals(event['eventClass'], '')

    def test_onSuccess_event_class_defined(self):
        event_class = '/Status/UserDefined'
        self.config.datasources[0].eventClass = event_class
        data = self.plugin.onSuccess(self.results, self.config)
        event = data['events'][0]

        self.assertEquals(event['eventClass'], event_class)

    def test_onError_event_class_defined(self):
        event_class = '/Status/UserDefined'
        self.config.datasources[0].eventClass = event_class

        f = Failure(Exception('test_onError_event_class_defined'))
        data = self.plugin.onError(f, self.config)
        event = data['events'][0]

        self.assertEquals(event['eventClass'], event_class)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWSMANDataSourcePlugin))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
