from netlister.registry import RegistryMixin, Registry
from loguru import logger
import json

class InputData(RegistryMixin):
    def __init__(self, registry: Registry) -> None:
        super().__init__(registry)

        self.modules = {}

    '''
    Determines the top-level module in the verilog hierarchy
    '''
    def get_top_module(self):
        for type, module in self.modules.items():
            if module.is_top():
                return module

        # If it can't find a module marked as 'top', fail
        logger.error("Could not find top module. Maybe add 'hierarchy -top <modulname>' to your yosys script.")
        quit()

    def get_module_for_type(self, type) -> "ModuleTemplate":
        if type not in self.modules:
            logger.error("Could not find module {} in input data", type)
            quit()

        return self.modules[type]


    def has_module(self, module):
        return module in self.modules


    def load(self, path):
        logger.info("Loading input data from {}", path)
        with open(path) as f:
            self.__parse(json.load(f))


    def __parse(self, data):
        for type, information in data['modules'].items():
            module = ModuleTemplate(type)

            module.set_attributes(information['attributes'])

            for label, portinfo in information['ports'].items():
                module.add_port(label, portinfo['bits'])

            for label, cellinfo in information['cells'].items():
                cell = CellTemplate(label)
                cell.type = cellinfo['type']
                cell.attributes = cellinfo['attributes']
                if 'port_directions' in cellinfo:
                    cell.port_directions = cellinfo['port_directions']
                cell.connections = cellinfo['connections']
                self.__determine__is_device(cell)
                module.add_cell(cell)

            for label, netnameinfo in information['netnames'].items():
                netname = NetName(label, netnameinfo['bits'])

            self.modules[type] = module

    def __determine__is_device(self, cell_template : "CellTemplate"):
        if not self.has_module(cell_template.type):
            logger.warning("Module {} not found in input data. Treating as device", cell_template.type)
            cell_template.is_device = True
            return

        module_template = self.get_module_for_type(cell_template.type)
        
        if module_template.is_blackbox():
            cell_template.is_device = True
            return
        
        cell_template.is_device = False
        return



class CellTemplate:
    attributes : dict
    port_directions : dict
    attributes : dict
    is_device : bool

    def __init__(self, label) -> None:
        self.label = label

        self.attributes = {}
        self.port_directions = {}
        self.attributes = {}
        self.is_device = None



class NetName:
    def __init__(self, label, bits) -> None:
        self.label = label
        self.bits = bits

       
    
        


class ModuleTemplate:
    def __init__(self, type) -> None:
        self.type = type
        self.ports = {}
        self.cells = []
        self.netnames = []
        self.attributes = {}

    def set_attributes(self, attributes):
        self.attributes = attributes

    def is_top(self):
        if "top" in self.attributes and self.attributes['top'] == "00000000000000000000000000000001":
            return True

        return False


    def is_blackbox(self):
        if 'blackbox' in self.attributes and self.attributes['blackbox'] == "00000000000000000000000000000001":
            return True

        return False

    def add_port(self, label, bits):
        self.ports[label] = bits

    def add_cell(self, cell):
        self.cells.append(cell)

    def add_netnames(self, netname):
        self.netnames.append(netname)








    




        
        
