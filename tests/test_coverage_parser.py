from modeling.coverage_parser import parse_line


def test_parse_line():
    line1 = "C 'f/nscratch/vighneshiyer/cov-proxy-model/rocket-chip/emulator/generated-src/freechips.rocketchip.system.DefaultRV32Config.behav_srams.vl129n3pagev_line/tag_array_0_extoblockS129-130hTOP.TestHarness.ldut.tile_prci_domain.tile_reset_domain_tile.frontend.icache.tag_array.tag_array_0_ext' 160132"
    line2 = "C 'f/nscratch/vighneshiyer/cov-proxy-model/rocket-chip/emulator/generated-src/freechips.rocketchip.system.DefaultRV32Config.vl935n14pagev_branch/TLXbaroifS935-936hTOP.TestHarness.ldut.subsystem_sbus.system_bus_xbar' 160122"
    line3 = "C 'f/nscratch/vighneshiyer/cov-proxy-model/rocket-chip/emulator/generated-src/freechips.rocketchip.system.DefaultRV32Config.vl935n15pagev_branch/TLXbaroelsehTOP.TestHarness.ldut.subsystem_sbus.system_bus_xbar' 0"

    p1 = parse_line(line1)
    assert p1 == (
        "/nscratch/vighneshiyer/cov-proxy-model/rocket-chip/emulator/generated-src/freechips.rocketchip.system.DefaultRV32Config.behav_srams.v",
        129,
        "tag_array_0_ext",
        "block",
        "TOP.TestHarness.ldut.tile_prci_domain.tile_reset_domain_tile.frontend.icache.tag_array.tag_array_0_ext",
        160132
    )

    p2 = parse_line(line2)
    assert p2 == (
        "/nscratch/vighneshiyer/cov-proxy-model/rocket-chip/emulator/generated-src/freechips.rocketchip.system.DefaultRV32Config.v",
        935,
        "TLXbar",
        "if",
        "TOP.TestHarness.ldut.subsystem_sbus.system_bus_xbar",
        160122
    )

    p3 = parse_line(line3)
    assert p3 == (
        "/nscratch/vighneshiyer/cov-proxy-model/rocket-chip/emulator/generated-src/freechips.rocketchip.system.DefaultRV32Config.v",
        935,
        "TLXbar",
        "else",
        "TOP.TestHarness.ldut.subsystem_sbus.system_bus_xbar",
        0
    )
