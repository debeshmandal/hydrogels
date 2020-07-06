import pytest 
@pytest.mark.skip
def test_LennardJonesGel_generation():
    from hydrogels.generators.gels import LennardJonesGel
    gel = LennardJonesGel()
    return