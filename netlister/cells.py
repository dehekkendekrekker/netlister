from netlister.functions import abort
import netlister.modules as modules
from netlister.registry import RegistryMixin
from loguru import logger
from prettytable import PrettyTable

from netlister.traits import HasParent

class CellFactory(RegistryMixin):
    def create(self, cells_data):
        print(cells_data)
        cells = []
        for cell_template in cells_data:
            data = self.cell_parser.parse(cell_template)
            cells.append(self.__create(cell_template.label, data))

        return cells

    def __create(self, name, data):
        if data["is_device"]:
            cell = CDevice()
        else:
            cell = CModule()

        logger.warning("{}", cell)

        cell.type = data["type"]
        cell.name = name
        cell.connections = data["connections"]
        cell.set_module(self.module_factory.create_from_cell(cell))

        return cell

class Cell(HasParent):
    module : "modules.Module"
    parent : "modules.Module"

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

class CellParser(RegistryMixin):
    cell_factory : CellFactory

    def parse(self, cell_template):
        return {
            "is_device": self.__is_physical_cell(cell_template),
            "type": cell_template.type,
            "connections": cell_template.connections
        }

    # The cell is considered physcial if it is not marked as 'module_not_derived' or if it is marked as blackbox
    def __is_physical_cell(self, cell_template):
        if not self.input_data.has_module(cell_template.type):
            logger.warning("Module {} not found in input data. Treating as device", cell_template.type)
            return True

        module_template = self.input_data.get_module_for_type(cell_template.type)
        
        if module_template.is_blackbox():
            return True
        

        return False


        

    '''
    This adds a chip to the net list basd on the properties retrieved
    from the "devices":"name" property of the chipset file
    '''
    # def __parse_cell(self, cell):
    #     cell_type = cell["type"]
    #     cell_connections = cell["connections"]

    #     # Get KiCad properties for chip from chipset file
    #     # device, properties = self.get_chip_props(cell_type)
    #     device = self.chipset.module(cell_type).device
    #     device.add_to_netlist()
    #     device.connect(cell_connections)


