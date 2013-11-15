##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

PYTHON=$(shell which python)
HERE=$(PWD)
TXWSMAN_DIR=$(HERE)/src/txwsman
ZP_DIR=$(HERE)/ZenPacks/zenoss/WSMAN
LIB_DIR=$(ZP_DIR)/lib
BIN_DIR=$(ZP_DIR)/bin

default: egg

egg:
	# setup.py will call 'make build' before creating the egg
	python setup.py bdist_egg

# pipe operator means src/txwsman must exist (as opposed to being more recent)
build: | src/txwsman
	cd $(TXWSMAN_DIR); git checkout master; git pull
	rm -rf $(LIB_DIR)/txwsman
	mkdir -p $(LIB_DIR)/txwsman/request
	cp -r $(TXWSMAN_DIR)/txwsman/*.py $(LIB_DIR)/txwsman/
	cp -r $(TXWSMAN_DIR)/txwsman/request/*.xml $(LIB_DIR)/txwsman/request/
        
src:
	mkdir src

src/txwsman: src
	cd src; git clone https://github.com/zenoss/txwsman.git

clean:
	rm -rf lib build dist *.egg-info $(LIB_DIR)/txwsman src
