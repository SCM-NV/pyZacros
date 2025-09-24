import random

import scm.pyzacros as pz


def test_InitialState():
    print("---------------------------------------------------")
    print(">>> Testing InitialState class")
    print("---------------------------------------------------")

    s0 = pz.Species("*", 1)  # Empty adsorption site
    s1 = pz.Species("H*", 1)  # H adsorbed with dentation 1
    s2 = pz.Species("H2**", 2)  # H2 adsorbed with dentation 2
    s3 = pz.Species("CO3***", 3)  # CO3 adsorbed with dentation 3

    lattice = pz.Lattice(
        cell_vectors=[[2.814, 0.000], [1.407, 2.437]],
        repeat_cell=[3, 3],
        site_types=["fcc", "hcp"],
        site_coordinates=[[0.33333, 0.33333], [0.66667, 0.66667]],
        neighboring_structure=[
            [(0, 0), pz.Lattice.NORTH],
            [(0, 0), pz.Lattice.EAST],
            [(0, 0), pz.Lattice.SOUTHEAST],
            [(1, 0), pz.Lattice.SELF],
            [(1, 0), pz.Lattice.EAST],
            [(1, 0), pz.Lattice.NORTH],
            [(1, 1), pz.Lattice.NORTH],
            [(1, 1), pz.Lattice.EAST],
            [(1, 1), pz.Lattice.SOUTHEAST],
        ],
    )

    lattice.plot(show_sites_ids=True, pause=2, close=True)
    initialState = pz.LatticeState(lattice, [s0, s1, s2])

    random.seed(10)
    initialState.fill_sites_random(site_name="fcc", species="H*", coverage=0.5)
    initialState.fill_sites_random(site_name=("fcc", "hcp"), species=s2, coverage=0.5)
    initialState.fill_site((0, 1), s2)
    initialState.fill_sites_random(site_name="hcp", species="H*", coverage=1.0)
    initialState.plot(pause=2, show_sites_ids=True, close=True)

    print(initialState)

    output = str(initialState)

    expectedOutput = """\
initial_state
  # species * H* H2**
  # species_numbers
  #   - *  0
  #   - H*  9
  #   - H2**  8
  seed_on_sites H2** 1 2
  seed_on_sites H* 3
  seed_on_sites H2** 4 9
  seed_on_sites H* 5
  seed_on_sites H* 6
  seed_on_sites H2** 8 13
  seed_on_sites H* 10
  seed_on_sites H* 11
  seed_on_sites H* 12
  seed_on_sites H* 14
  seed_on_sites H* 15
  seed_on_sites H2** 16 17
  seed_on_sites H* 18
end_initial_state\
"""
    assert output == expectedOutput

    initialState = pz.LatticeState(lattice, [s3])
    initialState.fill_sites_random(
        site_name=("fcc", "fcc", "fcc"), species=s3, coverage=0.1, neighboring=[[0, 1], [1, 2], [0, 2]]
    )
    initialState.fill_sites_random(site_name=("fcc", "fcc", "fcc"), species=s3, coverage=0.3)
    initialState.fill_site((12, 13, 14), s3)
    initialState.plot(pause=2, show_sites_ids=True, close=True)

    print(initialState)

    output = str(initialState)

    expectedOutput = """\
initial_state
  # species CO3***
  # species_numbers
  #   - CO3***  9
  seed_on_sites CO3*** 3 7 9
  seed_on_sites CO3*** 5 11 17
  seed_on_sites CO3*** 13 14 15
end_initial_state\
"""
    assert output == expectedOutput
