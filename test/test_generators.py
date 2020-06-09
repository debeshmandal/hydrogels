#!/usr/bin/env python
"""
Pytest script for testing the generators folder
"""

def test_polymers():
    import hydrogels.generators.polymers as polymers
    # create linear polymer and print positions
    print(polymers.LinearPolymer('test', 5).dataframe)
    return

if __name__ == "__main__":
    test_polymers()