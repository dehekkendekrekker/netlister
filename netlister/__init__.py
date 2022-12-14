from argparse import ArgumentParser
from netlister.registry import Registry
from netlister.input_data import InputData
from netlister.chipset import ChipSet
from netlister.netlist import NetList
from netlister.cells import CellFactory
from netlister.modules import ModuleFactory, ModuleList
import os

def run():
    parser = ArgumentParser(description="Turn YoSys json output into a KiCAD netlist")
    parser.add_argument("--input", required=True, help="JSON input file")
    parser.add_argument("--output", required=True, help="Defines the root of the output files (eg, name without extension)")
    parser.add_argument("--chipset", required=False, default=os.path.dirname(__file__) + "/chipsets/7400.json")
    args  = parser.parse_args()


    registry = Registry()
    registry.add("modules", ModuleList())
    registry.add("input_data", InputData(registry))
    registry.add("chipset", ChipSet(registry))
    registry.add("netlist", NetList(registry))
    registry.add("cell_factory", CellFactory(registry))
    registry.add("module_factory", ModuleFactory(registry))
    

    

    registry.input_data.load(args.input)
    registry.chipset.load(args.chipset)
    registry.module_factory.start()
    

    registry.netlist.create()
    registry.netlist.build(args.output)