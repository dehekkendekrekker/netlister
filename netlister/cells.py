from netlister.functions import abort
import netlister.modules as modules
from netlister.registry import RegistryMixin
from loguru import logger

from netlister.traits import HasParent

class CellFactory(RegistryMixin):
    def create(self, cells_data):
        cells = []
        for name, cell_data in cells_data.items():
            data = self.cell_parser.parse(cell_data)
            cells.append(self.__create(name, data))

        return cells

    def __create(self, name, data):
        if data["is_device"]:
            cell = CDevice()
        else:
            cell = CModule()

        cell.type = data["type"]
        cell.name = name
        cell.connections = data["connections"]
        cell.set_module(self.module_factory.create_from_cell(cell))

        return cell

class Cell(HasParent):
    module : "modules.Module"
    def set_module(self, module : "modules.Module"):
        self.module = module
        module.set_parent(self)

class CModule(Cell):
    pass
    

class CDevice(Cell):
    pass

class CellParser(RegistryMixin):
    cell_factory : CellFactory

    def parse(self, cell_data):
        return {
            "is_device": self.__is_physical_cell(cell_data['attributes']),
            "type": cell_data['type'],
            "connections": cell_data['connections']
        }

    def __is_physical_cell(self, attributes):
        return "module_not_derived" not in attributes or bool(attributes['module_not_derived']) is not True

        

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


