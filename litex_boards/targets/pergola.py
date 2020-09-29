#!/usr/bin/env python3

# This file is Copyright (c) 2018-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2018 David Shah <dave@ds0.me>
# License: BSD

import os
import argparse
import sys

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import pergola

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.spi_ram import SpiRam

from litedram import modules as litedram_modules
from litedram.phy import GENSDRPHY

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys    = ClockDomain()

        # # #

        # Clk / Rst
        clk16 = platform.request("clk16")

        # PLL
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk16, 16e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)

        # TODO: Does not build with this enabled
        # self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, device="LFE5U-12F", toolchain="trellis",
        sys_clk_freq=int(50e6), **kwargs):

        platform = pergola.Platform(device=device, toolchain=toolchain)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on Pergola",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Leds -------------------------------------------------------------------------------------
        self.submodules.leds = LedChaser(
            pads         = platform.request_all("user_led"),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

        # PSRAM

        psram_size = int((64/8)*1024*1024)

        self.add_csr("main_ram")
        self.submodules.main_ram = SpiRam(
            platform.request("spiram4x", 0),
            dummy=6,
            div=platform.spiflash_clock_div,
            endianness="little")
        self.register_mem("main_ram", self.mem_map["main_ram"],
            self.main_ram.bus, psram_size)

        self.mem_map["extra_ram1"] = self.mem_map["main_ram"] + psram_size
        self.add_csr("extra_ram1")
        self.submodules.extra_ram1 = SpiRam(
            platform.request("spiram4x", 1),
            dummy=6,
            div=platform.spiflash_clock_div,
            endianness="little")
        self.register_mem("extra_ram1", self.mem_map["extra_ram1"],
            self.extra_ram1.bus, psram_size)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Pergola")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    parser.add_argument("--toolchain", default="trellis", help="Gateware toolchain to use, trellis (default) or diamond")
    parser.add_argument("--device", dest="device", default="LFE5U-12F", help="FPGA device, Pergola is populated with a LFE5U-12F by default")
    parser.add_argument("--sys-clk-freq", default=50e6, help="System clock frequency (default=50MHz)")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        device=args.device,
        toolchain=args.toolchain,
        sys_clk_freq=int(float(args.sys_clk_freq)),
        **soc_core_argdict(args))

    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()
