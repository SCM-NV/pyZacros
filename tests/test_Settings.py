import pyzacros as pz
import pyzacros.utils


def test_Settings():
    print("---------------------------------------------------")
    print(">>> Testing Settings class")
    print("---------------------------------------------------")

    sett = pz.Settings()
    sett.random_seed = 71543
    sett.temperature = 380.0
    sett.pressure = 2.00
    sett.snapshots= ('time', 1e-5)
    sett.process_statistics = ('time', 1e-5)
    sett.species_numbers = ('time', 1e-5)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 1.0e+50
    sett.wall_time = 5000
    output = str(sett)

    print(output)

    expectedOutput = """\
random_seed          71543
temperature          380.0
pressure               2.0

snapshots                 on time       1e-05
process_statistics        on time       1e-05
species_numbers           on time       1e-05
event_report      off
max_steps         infinity
max_time          1e+50
wall_time         5000\
"""
    assert( pz.utils.compare( output, expectedOutput, 1e-3 ) )
