import scm.pyzacros as pz


def test_Species():
    print("---------------------------------------------------")
    print(">>> Testing Species class")
    print("---------------------------------------------------")

    # Adsorbed specie
    myAdsorbedSpecies = pz.Species("H2*", denticity=1)
    print(myAdsorbedSpecies)

    output = str(myAdsorbedSpecies)
    expectedOutput = "H2*"
    assert( output == expectedOutput )

    # Gas specie
    myGasSpecies = pz.Species("H2", gas_energy=0.0)
    print(myGasSpecies)

    output = str(myGasSpecies)
    expectedOutput = "H2"
    assert( output == expectedOutput )

    # Free adsorption site
    myAdsorptionFreeSite = pz.Species("*")
    print(myAdsorptionFreeSite)

    output = str(myAdsorptionFreeSite)
    expectedOutput = "*"
    assert( output == expectedOutput )
