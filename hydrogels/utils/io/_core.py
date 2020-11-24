import pandas as pd

class CoreReader:
    def __init__(self, data: pd.DataFrame):
        assert self.is_valid(data)
        self.data = data

    @staticmethod
    def is_valid(data: pd.DataFrame):
        return True
    
    @property
    def positions(self):
        return 

    @property
    def edges(self):
        return