#!/usr/bin/env python
"""
Objects for handling commonly used high-level readdy systems
"""
import typing

import numpy as np
import pandas as pd
import readdy

from readdy.api.reaction_diffusion_system import ReactionDiffusionSystem

class AbstractSystem(ReactionDiffusionSystem):
    """
    Wrapper for a ReaDDy system
    """
    def __init__(self, box):
        super(box)