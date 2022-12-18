from netlister.registry import RegistryMixin, Registry
from netlister.functions import abort
from skidl import *
import skidl
from loguru import logger
from prettytable import PrettyTable
import json
from netlister.modules import Device

from netlister.traits import HasParent

class NetList(RegistryMixin):
    def __init__(self, registry: Registry) -> None:
        super().__init__(registry)

    def create(self):
        logger.info("Creating netlist")
        self.__create_power_gnd()
        self.__enum_devices()
        self.__show_paths()
        self.__create_nets()

        # self.__show_debug_infos()
        
        
        # self[0]=self.GND  # Not sure about this
        # self[1]=self.VCC  # Not about this either
        # for name, net in self.input_data.top['netnames'].items():
        #     for net_nr in net['bits']:
        #         if not net_nr in self:
        #             self[net_nr] = skidl.Net(net_nr)

    def __create_power_gnd(self):
        vcc = Net("VCC")
        vcc.drive = skidl.POWER
        gnd = Net("GND")
        gnd.drive = skidl.POWER



    def __enum_devices(self):
        for device in self.modules.devices():
            logger.info("{}", device)

    def __show_paths(self):
        print("=== Paths from device to top module ===")
        for device in self.modules.devices():
            self.__show_path(device)

    def __show_path(self, device):
        path_elements = []
        parent: HasParent
        parent = device
        while parent is not None:
            path_elements.append(str(parent))
            parent = parent.get_parent()

        output = "->".join(path_elements)
        print(output)


    def __show_debug_infos(self, idx = None):
        print("=== DEBUG INFO ===")
        if idx is not None:
            self.__show_debug_info(self.modules.devices()[idx])
        else:
            for device in self.modules.devices():
                self.__show_debug_info(device)

    def __show_debug_info(self, device):
        path_elements = []
        parent: HasParent
        parent = device
        while parent is not None:
            path_elements.append(str(parent.debug_info()))
            parent = parent.get_parent()

        output = "\n============\n".join(path_elements)
        print(output)

    def __create_nets(self):
        device : Device
        for device in self.modules.devices():
            device.create_nets()


    

    def build(self, root):
        skidl.ERC()
        skidl.generate_netlist(file_ = "%s.net" % root)
    


    def display(self):
        t = PrettyTable()
        t.align("l")
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
