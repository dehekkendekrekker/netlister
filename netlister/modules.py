import netlister.cells as cells
from netlister.registry import RegistryMixin
from netlister.traits import HasParent
from loguru import logger

class ModuleAbstract(HasParent):
    def __init__(self, type, parent) -> None:
        self.type = type
        self.set_parent(parent)
        self.cells = []
        self.ports = {}
        self.net_lut = {}


    def add_cells(self, cells):
        cell : HasParent
        for cell in cells:
            self.cells.append(cell)
            cell.set_parent(self)

    def add_port(self, label, net_nrs):
        self.ports[label] = net_nrs
        self.__update_net_lut()
        

    # Updates the lookup table to find the port:position of a netnr
    def __update_net_lut(self):
        for port, net_nrs in self.ports.items():
            for idx, net_nr in enumerate(net_nrs):
                self.net_lut[net_nr] = (port, idx)


    def set_net(self, net_nr, net):
        port, position = self.net_lut[net_nr]
        self.ports[port][position] = net

    
class Module(ModuleAbstract):
    pass




class ModuleFactory(RegistryMixin):
    module_parser : "ModuleParser"

    def create(self, type, parent):
        return self.__create_module(type, parent)

    def create_from_cell(self, cell : "cells.Cell"):
        if isinstance(cell, cells.CDevice):
            return self.device_factory.create(cell)
        if isinstance(cell, cells.CModule):
            return self.__create_module(cell.type, cell)

    def __create_module(self, type, parent):
        module = Module(type, parent)
        self.module_parser.hydrate(module)


        

        return module




class ModuleParser(RegistryMixin):
    module_factory : ModuleFactory
    def start(self):
        type = self.input_data.get_top_module_type()
        self.module_factory.create(type, None)
        
    def hydrate(self, module : Module):
        data = self.input_data.get_module_for_type(module.type)

        self.__parse_port(module, data['ports'])
        cells = self.registry.cell_factory.create(data['cells'])
        module.add_cells(cells)




    def __parse_port(self, module :Module, port_data):
        for label, data in port_data.items():
            module.add_port(label, data['bits'])
