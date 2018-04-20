##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import os
import gzip
import pickle


def load_pickle(name):
    filename = '{}.pkl.gz'.format(name)
    path = os.path.join(os.path.dirname(__file__), 'data', filename)

    with gzip.open(path, 'rb') as f:
        return pickle.load(f)


class Stub(object):
    """
    Helper class that allows to access keyword-arguments, passed to init
    method as object's attributes.
    Example:
    >>> config = Stub(id='test_config',
    ...               datasources=[Stub(component='comp1'),
    ...                            Stub(component='comp2')])
    >>> print config.datasources[0].component
    comp1
    """
    def __init__(self, **props):
        self.__dict__ = props
