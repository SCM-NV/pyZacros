import scm.pyzacros as pz
import scm.pyzacros.utils


def test_Mechanism():
    print("---------------------------------------------------")
    print(">>> Testing Mechanism class")
    print("---------------------------------------------------")

    s0 = pz.Species("*", 1)  # Empty adsorption site
    s1 = pz.Species("H*", 1)  # H adsorbed with dentation 1
    s2 = pz.Species("H2*", 1)  # H2 adsorbed with dentation 1
    s3 = pz.Species("H2*", 2)  # H2 adsorbed with dentation 2

    myReaction1 = pz.ElementaryReaction(
        site_types=("f", "f"),
        neighboring=[(0, 1)],
        initial=[s1, s1],
        final=[s2, s0],
        reversible=True,
        pre_expon=1e13,
        pe_ratio=0.676,
        activation_energy=0.2,
    )

    myReaction2 = pz.ElementaryReaction(
        site_types=("f", "f"),
        neighboring=[(0, 1)],
        initial=[s3, s3],
        final=[s2, s0],
        reversible=True,
        pre_expon=1e13,
        pe_ratio=0.676,
        activation_energy=0.2,
    )

    myMechanism = pz.Mechanism()
    myMechanism.append(myReaction1)
    myMechanism.append(myReaction2)

    print(myMechanism)

    output = str(myMechanism)

    expectedOutput = """\
mechanism

reversible_step H2*1f*2f<->H*1fH*2f;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_reversible_step

reversible_step H2*1fH2*1f<->H2*1f*2f;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 H2* 1
    1 H2* 2
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_reversible_step

end_mechanism\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)
