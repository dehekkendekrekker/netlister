from netlister.registry import RegistryMixin
from loguru import logger
import json

class InputData(RegistryMixin):
    # data
    # top

    '''
    Determines the top-level module in the verilog hierarchy
    '''
    def get_toplevel(self):
        for mod in self.data['modules'].values():
            if 'top' in mod['attributes']:
                return mod

        # If it can't find a module marked as 'top', fail
        logger.error("Could not find top module. Maybe add 'hierarchy -top <modulname>' to your yosys script.")
        quit()


    def load(self, path):
        logger.info("Loading input data from {}", path)
        with open(path) as f:
            self.data = json.load(f)
            self.top = self.get_toplevel()
