##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012-2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenModel.ZenPack import ZenPackBase
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory

# Categorize our zProperties.
ZPROPERTY_CATEGORY = 'WSMAN'

setzPropertyCategory('zWSMANPort', ZPROPERTY_CATEGORY)
setzPropertyCategory('zWSMANUsername', ZPROPERTY_CATEGORY)
setzPropertyCategory('zWSMANPassword', ZPROPERTY_CATEGORY)
setzPropertyCategory('zWSMANUseSSL', ZPROPERTY_CATEGORY)
setzPropertyCategory('zWSMANCollectionInterval', ZPROPERTY_CATEGORY)
setzPropertyCategory('zWSMANMaxObjectCount', ZPROPERTY_CATEGORY)


class ZenPack(ZenPackBase):
    """WSMAN ZenPack."""

    packZProperties = [
        ('zWSMANPort', 443, 'int'),
        ('zWSMANUsername', '', 'string'),
        ('zWSMANPassword', '', 'password'),
        ('zWSMANUseSSL', True, 'boolean'),
        ('zWSMANCollectionInterval', 300, 'int'),
        ('zWSMANMaxObjectCount', 50, 'int'),
        ]

    packZProperties_data = {
        'zWSMANPort': {
            'category': ZPROPERTY_CATEGORY,
            'label': 'WSMAN Port',
            'description': 'TCP port of remote WSMAN service.',
            'type': 'int',
        },
        'zWSMANUsername': {
            'category': ZPROPERTY_CATEGORY,
            'label': 'WSMAN Username',
            'description': 'Username for remote WSMAN service.',
            'type': 'string',
        },
        'zWSMANPassword': {
            'category': ZPROPERTY_CATEGORY,
            'label': 'WSMAN Password',
            'description': 'Password for remote WSMAN service.',
            'type': 'password',
        },
        'zWSMANUseSSL': {
            'category': ZPROPERTY_CATEGORY,
            'label': 'WSMAN SSL',
            'description': 'Use SSL for remote WSMAN service.',
            'type': 'boolean',
        },
        'zWSMANCollectionInterval': {
            'category': ZPROPERTY_CATEGORY,
            'label': 'WSMAN Datasource Collection Interval',
            'description': 'Default interval (in seconds) between WSMAN datasource collections.',
            'type': 'int',
        },
        'zWSMANMaxObjectCount': {
            'category': ZPROPERTY_CATEGORY,
            'label': 'WSMAN Max Objects per a Response',
            'description': 'Elements returned from the API per a request.',
            'type': 'int',
        },
    }
