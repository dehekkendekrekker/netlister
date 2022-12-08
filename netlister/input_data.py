from netlister.registry import RegistryMixin
from loguru import logger
import json

class InputData(RegistryMixin):
    # data
    # top

    '''
    Determines the top-level module in the verilog hierarchy
    '''
    def get_top_module_type(self):
        for type, mod in self.data['modules'].items():
            if 'top' in mod['attributes']:
                return type

        # If it can't find a module marked as 'top', fail
        logger.error("Could not find top module. Maybe add 'hierarchy -top <modulname>' to your yosys script.")
        quit()

    def get_module_for_type(self, type):
        if type not in self.data["modules"]:
            logger.error("Could not find module {} in input data")
            quit

        return self.data["modules"][type]




    def load(self, path):
        logger.info("Loading input data from {}", path)
        with open(path) as f:
            self.data = json.load(f)







    




        
        
