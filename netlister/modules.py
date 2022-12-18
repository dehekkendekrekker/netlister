from skidl import *
import skidl
import netlister.cells as cells
from netlister.functions import abort
from netlister.registry import RegistryMixin
from netlister.traits import HasParent
from netlister.input_data import InputData
from netlister.input_data import ModuleTemplate

from loguru import logger
from prettytable import PrettyTable
import re

class ModuleAbstract(HasParent):
    type : str
    _ports: dict
    net_list : dict

    def __init__(self,type) -> None:
        super().__init__()
        self.type = type
        self._ports = {}
        self._ports_nets_lut = {}
        self.net_list = {}
        
        

    def set_ports(self, ports):
        bits : dict
        for label, bits in ports.items():
            self._ports[label] = bits.copy()
            self.net_list[label] = {}
        self.__update_internal_nets_lut()

    # Updates the lookup table to find the port:position of a netnr
    def __update_internal_nets_lut(self):
        for port, net_nrs in self._ports.items():
            for idx, net_nr in enumerate(net_nrs):
                self._ports_nets_lut[net_nr] = (port, idx)


    


    def debug_info(self):
        t = PrettyTable(["property", "value"])
        t.align='l'
        t.add_row(["parent", "%s->%s" % (self.get_parent(), self.get_parent().parent.type if self.get_parent() else None)])
        t.add_row(["type", self.type])
        t.add_row(["ports", "\n".join(["%s: %s" % (key, value) for key, value in self._ports.items()])])
        t.add_row(["net list", "============================"])
        self.__debug_info_net_list(t)

        return t

    def __debug_info_net_list(self, t : PrettyTable):
        for label, net_dict in self.net_list.items():
            t.add_row(["", "%s: {" % label])
            for position, net in net_dict.items():
                t.add_row(["","   %s: %s" % (position, net)])
            t.add_row(["", "}"])




    
class Module(ModuleAbstract):
    cells : list
    internal_nets : dict

    def __init__(self, type) -> None:
        super().__init__(type)
        self.cells = []
        self.internal_nets = {}
        self.__internal_nets_lut = {}

    def set_internal_nets(self, nets):
        for net in nets:
            self.internal_nets[net.label] = net.bits
        self.__update_internal_nets_lut()

    def __update_internal_nets_lut(self):
        for port, net_nrs in self.internal_nets.items():
            for idx, net_nr in enumerate(net_nrs):
                self.__internal_nets_lut[net_nr] = (port, idx)

    def update_ports_and_internal_nets(self, net_nr, net):
        self.__update_net_list(self._ports_nets_lut, net_nr, net)
        self.__update_net_list(self.__internal_nets_lut, net_nr, net)
        

    def __get_net(self, label, position) -> Net:
        return self.net_list[label][position]

    def __has_net(self, label, position):
        return position in self.net_list[label]

    def __set_net(self, port, position, net):
        self.net_list[port][position] = net


    def __update_net_list(self, lut, net_nr,net):
        if not net_nr in lut:
            # The net number should exist in the internal nets
            return

        port, position = lut[net_nr]
        if self.__has_net(port, position) and self.__get_net(port, position) == net:
            # The position already has the supplied net.
            # The system will try to re-add the net, since it will do multiple passes
            # To update this module, as the submodules/devices are updated
            return

        if self.__has_net(port, position) and self.__get_net(port, position) != net:
            # In this case, the system tries to update a port position with net,
            # but one already exists. This means that these nets should be merged.
            logger.info("Merging net {} at position {}:{} with {}", self.__get_net(port, position), port, position, net)
            self.__get_net(port, position).connect(net)
            return
            

        self.__set_net(port, position, net)
            


    def add_cells(self, cells):
        cell : HasParent
        for cell in cells:
            self.cells.append(cell)
            cell.set_parent(self)


    def __str__(self) -> str:
        return "MOD:%s" % self.type

    def debug_info(self):
        t = super().debug_info()
        t.add_row(["class", "MODULE"])
        t.add_row(["cells", "\n".join(["%s->%s" % (str(x),x.module.type) for x in self.cells])])
        return t

class Device(ModuleAbstract):
    pins: dict
    part: skidl.Part
    kicad_library: str
    footprint : str

    def __init__(self, type) -> None:
        super().__init__(type)

    def create_nets(self):
        self.__create_part()
        self.__create_signal_nets()
        self.__connect_signal_pins()
        self.__connect_power_pins()
        self.__handle_unconnected_pins()
        self.__connect_parent()

    def __create_part(self):
        logger.info("Creating part {}:{}", self.type, self.footprint)
        self.part = skidl.Part(self.kicad_library, self.type, footprint=self.footprint, tool_version="kicad_v6")

    def __create_signal_nets(self):
        for label, nets in self.parent.connections.items():
            for idx, value in enumerate(nets):
                self.net_list[label][idx] = Net()

    def __connect_signal_pins(self):
        for label, nets in self.net_list.items():
            for idx, net in nets.items():
                net: Net
                pin_nr = self._ports[label][idx]
                logger.info("Connecting {}:{} to net {}", self.part.name, pin_nr, net)
                net.connect(self.part[pin_nr])

    def __connect_power_pins(self):
        vcc = Net.fetch("VCC")
        gnd = Net.fetch("GND")

        for idx, pin_nr in self._ports["VCC"].items():
            logger.info("Connecting {}:{} to VCC", self.part.name, pin_nr, vcc)
            vcc.connect(self.part[pin_nr])
            self.net_list["VCC"][idx] = vcc

        for idx, pin_nr in self._ports["GND"].items():
            logger.info("Connecting {}:{} to GND", self.part.name, pin_nr, gnd)
            gnd.connect(self.part[pin_nr])
            self.net_list["GND"][idx] = gnd
            

    def __handle_unconnected_pins(self):
        for pin in self.part.get_pins():
            if not pin.is_connected():
                if pin.func == Pin.types.INPUT:
                    logger.warning("Pin {}:{} is not connected, connecting to GND", self.part.name, pin)
                    pin += Net.fetch("GND")
                elif pin.func == Pin.types.OUTPUT:
                    logger.warning("Pin {}:{} is not connected, marking as NC", self.part.name, pin)
                    pin += NC
                else:
                    abort("Unkown pin type: %s" % pin.func)

    def __connect_parent(self):
        self.parent.connect()


    def __str__(self) -> str:
        return "DEV:%s" % self.type

    def debug_info(self):
        t = super().debug_info()
        t.add_row(["class", "DEVICE"])
        t.add_row(["pins", "\n".join(["%s: %s" % (key, value) for key,value in self.pins.items()])])
        return t






class ModuleFactory(RegistryMixin):
    cell_factory : "CellFactory"
    input_data : "InputData"

    def start(self):
        top_module_template = self.input_data.get_top_module()
        return self.__create_module(top_module_template)
    
    def create_from_cell(self, parent_cell : "cells.Cell"):
        
        if isinstance(parent_cell, cells.CDevice):
            module = self.__create_device(parent_cell)
        if isinstance(parent_cell, cells.CModule):
            module = self.__create_module(parent_cell)

        module.set_parent(parent_cell)
        self.modules.add(module)
        return module

    def __create_module(self, parent_cell : "cells.Cell"):
        module_template = self.input_data.get_module_for_type(parent_cell.type)
        module = Module(parent_cell.type)
        module.set_ports(module_template.ports)
        module.set_internal_nets(module_template.netnames)
        cells = self.cell_factory.create(module_template.cells)
        module.add_cells(cells)
        return module

    def __create_device(self, parent_cell : "cells.Cell"):
        device_template = self.chipset.get_device_template_for_module(parent_cell.type)
        device = Device(device_template.type)
        device.kicad_library = device_template.kicad_library
        device.footprint = device_template.footprint
        device.set_ports(device_template.ports)
        return device

class ModuleList(list):
    def __init__(self):
        super().__init__()

        self.devices_idxs = []
        self.modules_idxs = []

    def add(self, item : ModuleAbstract):
        if isinstance(item, Device):
            self.__add_device(item)
        if isinstance(item, Module):
            self.__add_module(item)

    def __add_device(self,device:Device):
        self.append(device)
        self.devices_idxs.append(self.index(device))

    def __add_module(self, module:Module):
        self.append(module)
        self.modules_idxs.append(self.index(module))

    def devices(self):
        retlist = []
        for idx in self.devices_idxs:
            retlist.append(self[idx])

        return retlist

