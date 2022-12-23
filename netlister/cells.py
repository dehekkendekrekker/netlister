from skidl import *
import skidl
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
        # loop through the label:{idx:net_nr} mapping
        # ex: "A": [ 12, 13, 14, 11, 15, 16, 17, 10, "0", "0", "0", "0", "0", "0", "0" ],
        for label, nets in self.connections.items():
            # Loop throug the {idx_netnr} mapping
            for idx, net_nr in enumerate(nets):
                # If the idx does not exist in the netlist, this means this net is not mapped
                # and the corresponding pin on the device will be treated as unconnected.
                if idx not in self.module.net_list[label]:
                    continue

                # Get the corresponding net of the child module. This is of class Net
                net = self.module.net_list[label][idx]

                if self.__is_logic_level(net_nr):
                    # The pin on position idx must be connected to logic high
                    self.__connect_net_to_logic_level(net_nr, net)

                    # The parent need not be updated, since we don't have as valid net_nr
                    continue
                   


                # This updates the nets of the parent
                self.parent.update_ports_and_internal_nets(net_nr, net)

    def __is_logic_level(self, input):
        return isinstance(input, str)

    def __connect_net_to_logic_level(self, net_nr, net : Net):
        if net_nr == "1":
            logger.info("Connecting net {} to logic-high", net)
            vcc = Net.fetch("VCC")
            net.connect(vcc)
        elif net_nr == "0":
            logger.info("Connecting net {} to logic-low", net)
            gnd = Net.fetch("GND")
            net.connect(gnd)
        else:
            logger.error("Unknown logic level {} for module {}", net_nr, self.type)
            quit()




class CModule(Cell):
    def __str__(self) -> str:
        return "CMOD"
    

class CDevice(Cell):
    def __str__(self) -> str:
        return "CDEV"

