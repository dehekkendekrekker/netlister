from netlister.registry import RegistryMixin
from netlister.cells import Cell
from netlister.traits import HasParent
class DeviceList(list):
    pass


class Device(HasParent):
    pass

class DeviceFactory(RegistryMixin):
    def create(self, cell : "Cell"):
        device = Device()
        self.device_parser.hydrate(device, cell.type)
        return device


class DeviceParser(RegistryMixin):
    def hydrate(self, device  : Device, cell_type):
        data = self.chipset.data_for(cell_type)
        device.type = data['type']
        device.pins = data['properties']['pins']

