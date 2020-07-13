# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk16", 0, Pins("P11"), IOStandard("LVCMOS33")),

    ("user_led", 0, Pins("F15"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("E16"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("E15"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("D16"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("C16"), IOStandard("LVCMOS33")),
    ("user_led", 5, Pins("C15"), IOStandard("LVCMOS33")),
    ("user_led", 6, Pins("B16"), IOStandard("LVCMOS33")),
    ("user_led", 7, Pins("B15"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("R1"), IOStandard("LVCMOS33")),
        Subsignal("rx", Pins("T2"), IOStandard("LVCMOS33"))
    ),

    # PMOD 3
    ("usb", 0,
        Subsignal("d_p", Pins("D4")),
        Subsignal("d_n", Pins("C6")),
        Subsignal("pullup", Pins("B7 C7")),
        IOStandard("LVCMOS33")
    ),


    # Built-in #1
    # cs="A9", clk="B9", mosi="B10", miso="A10", wp="A11", hold="B8",
    ("spiram", 0,
        Subsignal("cs_n", Pins("A9"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("B10"), IOStandard("LVCMOS33")), # io0
        Subsignal("miso", Pins("A10"), IOStandard("LVCMOS33")), # io1
        Subsignal("clk",  Pins("B9"), IOStandard("LVCMOS33")),
        
        Subsignal("wp",   Pins("A11"), IOStandard("LVCMOS33")), # io2
        Subsignal("hold", Pins("B8"), IOStandard("LVCMOS33")), # io3
    ),
    ("spiram4x", 0,
        Subsignal("cs_n", Pins("A9"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("B9"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("B10 A10 A11 B8"), IOStandard("LVCMOS33")),
    ),

    # Built-in #2
    # cs="A2", clk="A4", mosi="A5", miso="B3", wp="B4", hold="A3",
    ("spiram", 1,
        Subsignal("cs_n", Pins("A2"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("A5"), IOStandard("LVCMOS33")), # io0
        Subsignal("miso", Pins("B3"), IOStandard("LVCMOS33")), # io1
        Subsignal("clk",  Pins("A4"), IOStandard("LVCMOS33")),
        
        Subsignal("wp",   Pins("B4"), IOStandard("LVCMOS33")), # io2
        Subsignal("hold", Pins("A3"), IOStandard("LVCMOS33")), # io3
    ),
    ("spiram4x", 1,
        Subsignal("cs_n", Pins("A2"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("A4"), IOStandard("LVCMOS33")),
        Subsignal("dq",   Pins("A5 B3 B4 A3"), IOStandard("LVCMOS33")),
    ),

]

# Platform -----------------------------------------------------------------------------------------
class ApolloProgrammer():
    needs_bitreverse = False

    def load_bitstream(self, bitstream_file):
        """ Programs the board using the Apollo firmware """

        from luna.apollo import ApolloDebugger
        from luna.apollo.ecp5 import ECP5_JTAGProgrammer

        # Create our connection to the debug module.
        debugger = ApolloDebugger()

        print(bitstream_file)
        bitstream = bytearray(open(bitstream_file, "rb").read())

        with debugger.jtag as jtag:
            programmer = ECP5_JTAGProgrammer(jtag)
            programmer.configure(bitstream)


class Platform(LatticePlatform):
    default_clk_name   = "clk16"
    default_clk_period = 1e9/16e6
    spiflash_clock_div = 2

    def __init__(self, device="LFE5U-12F", **kwargs):
        LatticePlatform.__init__(self, device + "-8BG256", _io, **kwargs)

    def create_programmer(self):
        return ApolloProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk16", loose=True), 1e9/16e6)
