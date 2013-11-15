
from ZenPacks.zenoss.WSMAN.modeler.WSMANPlugin import WSMANPlugin

class CPUs(WSMANPlugin):
     compname = 'hw'
     relname = 'cpus'
     modname = 'Products.Zenmodel.Cpu.Cpu'

     wsman_queries = {'DCIM_ComputerSystem': '' }

     def process(self, device, results, log):
         log.info("Modeler %s Processing data for device %s",
             self.name(), device.id)


         import pdb;pdb.set_trace()


