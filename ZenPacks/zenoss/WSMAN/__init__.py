##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging

from Products.ZenModel.ZenPack import ZenPackBase
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory

LOG = logging.getLogger('zen.WSMAN')

# Categorize our zProperties.
setzPropertyCategory('zWSMANPort', 'WSMAN')
setzPropertyCategory('zWSMANUsername', 'WSMAN')
setzPropertyCategory('zWSMANPassword', 'WSMAN')
setzPropertyCategory('zWSMANUseSSL', 'WSMAN')
setzPropertyCategory('zWSMANCollectionInterval', 'WSMAN')


class ZenPack(ZenPackBase):
    """WSMAN ZenPack."""

    packZProperties = [
        ('zWSMANPort', '443', 'integer'),
        ('zWSMANUsername', '', 'string'),
        ('zWSMANPassword', '', 'password'),
        ('zWSMANUseSSL', True, 'boolean'),
        ('zWSMANCollectionInterval', '300', 'integer')
        ]

    packZProperties_data = {
        'zWSMANCollectionInterval': {
            'type': 'integer',
            'description': ('Defines, in seconds, the default collection '
                            'interval for WSMAN datasources.'),
            'label': 'WSMAN datasources collection interval'
        },
    }
