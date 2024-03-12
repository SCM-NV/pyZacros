import scm.pyzacros as pz
import scm.pyzacros.utils


def test_Cluster():
    print("---------------------------------------------------")
    print(">>> Testing Cluster class")
    print("---------------------------------------------------")
    cluster = pz.Cluster(
        site_types=("f", "f"),
        neighboring=[(0, 1)],
        species=pz.SpeciesList([pz.Species("H*", 1), pz.Species("H*", 1)]),
        multiplicity=2,
        energy=0.1,
    )

    print(cluster)

    output = str(cluster)
    expectedOutput = """\
cluster H*1fH*2f:(0,1)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.100
end_cluster\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    cluster = pz.Cluster(
        site_types=("f", "f"),
        neighboring=[(0, 1)],
        species=[pz.Species("H2**"), pz.Species("H2**")],
        multiplicity=2,
        energy=0.1,
    )

    print(cluster)

    output = str(cluster)
    expectedOutput = """\
cluster H2**1fH2**1f:(0,1)
  sites 2
  neighboring 1-2
  lattice_state
    1 H2** 1
    1 H2** 2
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.100
end_cluster\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    cluster = pz.Cluster(
        site_types=("f", "g", "h", "i", "j"),
        neighboring=[(0, 1), (1, 2), (2, 3), (3, 0), (2, 4)],
        species=[pz.Species("CO2**"), pz.Species("*"), pz.Species("CO2**"), pz.Species("H*", 1), pz.Species("*")],
        entity_number=[0, 1, 0, 2, 3],
        multiplicity=1,
        energy=0.1,
        label="my_weird_cluster",
    )

    print(cluster)

    output = str(cluster)
    expectedOutput = """\
cluster my_weird_cluster
  sites 5
  neighboring 1-2 2-3 3-4 4-1 3-5
  lattice_state
    1 CO2** 1
    2 * 1
    1 CO2** 2
    3 H*  1
    4 *  1
  site_types f g h i j
  graph_multiplicity 1
  cluster_eng 0.100
end_cluster\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    cluster = pz.Cluster(
        site_types=("f", "g", "h", "i", "j"),
        neighboring=[(0, 1), (1, 2), (2, 3), (3, 0), (2, 4)],
        species=[pz.Species("CO2**"), pz.Species("*"), pz.Species("CO2**"), pz.Species("H*", 1), pz.Species("*")],
        multiplicity=1,
        energy=0.1,
        label="my_weird_cluster",
    )

    print(cluster)

    output = str(cluster)
    expectedOutput = """\
cluster my_weird_cluster
  sites 5
  neighboring 1-2 2-3 3-4 4-1 3-5
  lattice_state
    1 CO2** 1
    2 * 1
    1 CO2** 2
    3 H*  1
    4 *  1
  site_types f g h i j
  graph_multiplicity 1
  cluster_eng 0.100
end_cluster\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)
