"""A system that runs the enzymatic degradation reactions
"""
from .. import System

class EnzymaticDegradation(System):
    def __init__(self, box: list):
        super().__init__(box)

    def configure_potentials(self):
        return

    def add_enzyme(self):
        return

    def add_payload(self):
        return