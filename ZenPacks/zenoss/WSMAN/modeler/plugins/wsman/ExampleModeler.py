
from ZenPacks.zenoss.WSMAN.modeler.WSMANPlugin import WSMANPlugin

class ExampleModeler(WSMANPlugin):
     compname = 'hw'
     relname = 'cpus'
     modname = 'Products.Zenmodel.Cpu.Cpu'

     #wsman_queries = {'DCIM_ComputerSystem': '',
     #                 'CIM_Component': '' }
     wsman_queries = {'DCIM_VirtualDiskView': '' ,
                      'DCIM_CPUView': '' ,
                      'DCIM_MemoryView': '' ,
                      'DCIM_FanView': '' ,
                      'DCIM_iDRACCardView': '' ,
                      'DCIM_PCIDeviceView': '' ,
                      'DCIM_VideoView': '' ,
                      'DCIM_ControllerView': '' ,
                      'DCIM_BIOSEnumeration': '' ,
                      'DCIM_SystemView': '' ,
                      'DCIM_VFlashView': '' ,
                      'DCIM_NICView': '' }

     def process(self, device, results, log):
         log.info("Modeler %s Processing data for device %s",
             self.name(), device.id)
         log.info("Example accessing a results metric: %s" % results[0][0].BusNumber)

         rm = self.relMap()
         rm.append(self.objectMap({
              'id': self.prepId(results[0][0].BusNumber)}))

         return rm



