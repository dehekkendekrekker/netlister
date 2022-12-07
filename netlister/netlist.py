from netlister.registry import RegistryMixin, Registry
from netlister.functions import abort
from skidl import *
import skidl
from loguru import logger
from prettytable import PrettyTable
import json

class NetList(RegistryMixin, dict):
    def __init__(self, registry: Registry) -> None:
        super().__init__(registry)

        self.VCC = skidl.Net('VCC')
        self.VCC.drive = skidl.POWER
        self.GND = skidl.Net('GND')
        self.GND.drive = skidl.POWER

    def create(self):
        logger.info("Creating netlist")
        self[0]=self.GND  # Not sure about this
        self[1]=self.VCC  # Not about this either
        for name, net in self.input_data.top['netnames'].items():
            for net_nr in net['bits']:
                if not net_nr in self:
                    self[net_nr] = skidl.Net(net_nr)

    def build(self, root):
        skidl.ERC()
        skidl.generate_netlist(file_ = "%s.net" % root)
    


    def display(self):
        t = PrettyTable()
        t.title = "NETLIST"
        t.align ="l"
        t.field_names = ['nr', 'name']
        for key, value in self.items():
            t.add_row([key, value.name])
        print(t)
        
    def get_net(self, net_nr):
        if net_nr not in self:
            abort("Netnr %s does not exist in netlist" % net_nr)
        return self[net_nr]
