import numpy as np
import param
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import mne
import sys
#import below
from components.dataStructure import DataHistoryList, DataHistoryItem


class sample(param.Parameterized):
    optionalArgument1 = param.Number(default=250)
    name = "sample"

    def set_vars(self, optionalArgument1):
        self.optionalArgument1 = optionalArgument1

    def run(self, data: DataHistoryItem, model_file):
        print("starting to evaluate model")
        # print(str(model_file))
        # create random data of length of original data (either 1 or 0)
        model_res = np.random.randint(2, size=len(data.data)).tolist()
        print("finished evaluating")

        return model_res
