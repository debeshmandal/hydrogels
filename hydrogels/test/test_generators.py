#!/usr/bin/env python
"""
Pytest script for testing the generators folder
"""

def test_polymers():
    import hydrogels.generators.polymers as polymers
    # create linear polymer and print positions
    polymers.LinearPolymer('test', 5).dataframe
    polymers.CrosslinkingPolymer('test', 5, 5).dataframe
    print(polymers.LinearPolymer('test', 5).edges)
    return

if __name__ == "__main__":
    test_polymers()