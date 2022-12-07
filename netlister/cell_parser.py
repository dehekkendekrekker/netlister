from skidl import *
import skidl
from netlister.registry import RegistryMixin
from netlister.functions import abort

class CellParser(RegistryMixin):
    def parse_cells(self):
        for cell in self.input_data.top["cells"].values():
            self.parse_cell(cell)

    '''
    This adds a chip to the net list basd on the properties retrieved
    from the "devices":"name" property of the chipset file
    '''
    def parse_cell(self, cell):
        cell_type = cell["type"]
        cell_connections = cell["connections"]

        # Get KiCad properties for chip from chipset file
        # device, properties = self.get_chip_props(cell_type)
        device = self.chipset.module(cell_type).device
        device.add_to_netlist()
        device.connect(cell_connections)


    


    
