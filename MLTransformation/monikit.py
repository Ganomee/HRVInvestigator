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

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/Users/shivam/Documents/GitHub/HRVInvestigator/components/monipy')
from monipy.models.Model import Model
from monipy.data.FeatureTable2 import FeatureTable

class monikit(param.Parameterized):
    optionalArgument1 = param.Number(default=250)
    name = "monikit"

    def set_vars(self, optionalArgument1):
        self.optionalArgument1 = optionalArgument1

    def run(self):
        print("starting to evaluate model")
        testdatapath="./DataArtifacts/"
        model_file = "./Models/monikit_model/"
        model = Model.load_by_path(model_file)
        test_feattab = FeatureTable(testdatapath)
        test_data = test_feattab.get_prediction_data(2)
        model_res = model.predict(test_data) > 0.5
        # model_res = self.reformat(model_res)
        # print(str(model_file))
        # create random data of length of original data (either 1 or 0)
        # model_res = np.random.randint(2, size=len(data.data)).tolist()
        print("finished evaluating")

        return model_res

    # def reformat(self, preds):
    #     for i in range(len(preds)):
    #         i *= 54
    #         for j in range(54):
    #             preds = np.insert(preds, i + j + 1, 0)
    #             i += 1
    #     return preds