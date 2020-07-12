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

    def __init__(self, device="LFE5U-12F", **kwargs):
        LatticePlatform.__init__(self, device + "-8BG256", _io, **kwargs)

    def create_programmer(self):
        return ApolloProgrammer()

    def do_finalize(self, fragment):
        LatticePlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk16", loose=True), 1e9/16e6)
