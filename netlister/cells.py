from netlister.functions import abort
import netlister.modules as modules
from netlister.registry import RegistryMixin
from loguru import logger
from prettytable import PrettyTable
from netlister.input_data import CellTemplate

from netlister.traits import HasParent

class CellFactory(RegistryMixin):
    def create(self, cell_templates : list):
        cell_instances = []
        cell_template : CellTemplate
        for cell_template in cell_templates:
            cell_instances.append(self.__create(cell_template))

        return cell_instances

    def __create(self, cell_template : CellTemplate):
        if cell_template.is_device:
            cell = CDevice()
        else:
            cell = CModule()

        cell.type = cell_template.type
        cell.name = cell_template.label
        cell.connections = cell_template.connections
        cell.set_module(self.module_factory.create_from_cell(cell))

        return cell

class Cell(HasParent):
    module : "modules.Module"
    parent : "modules.Module"
    connections : dict
    name : str

    def set_module(self, module : "modules.Module"):
        self.module = module

    def debug_info(self):
        t = PrettyTable(["property", "value"])
        t.align="l"
        t.add_row(["class", "CELL"])
        t.add_row(["parent_module", self.parent])
        t.add_row(["child_module", self.module])
        t.add_row(['type', type(self)])
        t.add_row(['connections', "\n".join(["%s: %s" % (key, value) for key,value in self.connections.items()])])
    
        return t

    def connect(self):
        self.__update_parent_nets()
        if not self.parent.parent:
            return None
        self.parent.parent.connect()
        

    def __update_parent_nets(self):
        for label, nets in self.connections.items():
            for idx, net_nr in enumerate(nets):
                if idx not in self.module.net_list[label]:
                    continue

                net = self.module.net_list[label][idx]
                self.parent.update_ports_and_internal_nets(net_nr, net)



class CModule(Cell):
    def __str__(self) -> str:
        return "CMOD"
    

class CDevice(Cell):
    def __str__(self) -> str:
        return "CDEV"

