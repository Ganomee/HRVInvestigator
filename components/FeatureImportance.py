"""
Script for feature importance of a model using SHAP values using GradientExplainer.
Read more: https://shap-lrjball.readthedocs.io/en/latest/generated/shap.GradientExplainer.html
"""

import plotly.express as px
import plotly.io as pio
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/Users/shivam/Documents/GitHub/HRVInvestigator/components/monipy')
from monipy.models.Model import Model
from monipy.data.FeatureTable2 import FeatureTable
import shap
import numpy as np

#List of all the 30s, 60s and 120s window features
FEATURES = ['avg','sd','rmssd','rmssd_dt','skew','kurt','pnnx','nnx','triangular_index','quantile_25',
                'quantile_50','quantile_75','variance', 'csi','csim','cvi','sd1','sd2','csi_slope','csim_slope',
                'csi_filtered','csim_filtered','csi_filtered_slope','csim_filtered_slope','hr_diff','hr_diff_slope',
                'hr_diff_filtered','hr_diff_filtered_slope', 'ulf','vlf','lf','hf','lf_hf_ratio','total_power',
                'mf_hurst_max','mf_coef_left','mf_coef_center','mf_coef_right']
class FeatureImportance:
    """
    Constructor
    Parameter:
                model_directory : path to the model
                traindatapath : path to training data
                testdatapath: path to test data
    """
    def __init__(self, model_directory:str, traindatapath:str, testdatapath:str ):
        self.model = Model.load_by_path(model_directory)
        self.test_feattab = FeatureTable(testdatapath)
        self.train_feattab = FeatureTable(traindatapath)
    
        self.data = self.test_feattab.get_prediction_data(2)
        self.label = self.test_feattab.get_prediction_labels(2)

        self.data2 = self.train_feattab.get_prediction_data(2)
        self.label2 = self.train_feattab.get_prediction_labels(2)

        self.pred = self.model.predict(self.data) > 0.5
        self.from_saved = False
        self.shap_values = None

    def load_feature_importance(self, shap_values_path):
        
        self.shap_values = np.load(shap_values_path, allow_pickle=True)

    """
        Reformates the data by merging all 55sec windows into one continuous data to plot it later.
        Parameter:
                    data: the calculated SHAP values to be reformatted.
    """
    def reformat(self,data):
        all_feat = list()
        for feat in range(data.shape[2]):
            new_data = data[0,:,feat]
            for i in range(data.shape[0]):
                new_data = np.insert(new_data, -1, data[i,-1,feat])
            all_feat.append(new_data)
        return np.array(all_feat)

    """
        Trains the GradientExplainer on the train data and calculates the SHAP values for the test data.
    """
    def calculate_shap(self):
        shap.explainers._deep.deep_tf.op_handlers["AddV2"] = shap.explainers._deep.deep_tf.passthrough
        e = shap.GradientExplainer(self.model.model, self.data2)
        self.shap_values = e.shap_values(self.data[:300,:,:])

    """
        Plots the SHAP values over time for individual features. The background color marks the 55 seconds segments according 
        to the actual label (above; lightseagreen:true and orange:false) and predictions (below; green:true and yellow:false).

    """

    def plot_shap(self, file):
        if self.from_saved:
            fig = pio.read_json(file)
            print("Feature Importance Loaded From JSON File...")
        else:
            if self.shap_values is None:
                print("Error: SHAP values not loaded. Call load_feature_importance() to load the SHAP values first.")
                return None
            fig=px.line(self.reformat(self.shap_values[0]).T, labels={ '0' : "SHAP values", '1':"Time"})
            self.shap_values = pio.write_json(fig, file)

            for i in range(151):
                fig.add_shape(
                    type="rect",
                    x0=i,
                    x1=i+55,
                    y0=0,
                    y1=1.5,
                    layer="below",
                    fillcolor="LightSeaGreen" if self.label[i] else "Orange",
                    opacity=0.1 if self.label[i] else 0.01
                )
                fig.add_shape(
                    type="rect",
                    x0=i,
                    x1=i+55,
                    y0=0,
                    y1=-1,
                    layer="below",
                    fillcolor= "Green" if self.pred[i] else "Yellow",
                    opacity=0.1 if self.pred[i] else 0.01
                )
            fig.for_each_trace(lambda t: t.update(name = FEATURES[int(t.name)],
                                                legendgroup = FEATURES[int(t.name)],
                                                hovertemplate = t.hovertemplate.replace(t.name, FEATURES[int(t.name)])
                                                )
                            )
            fig.update_layout(
                title="SHAP Values of Features over Time ",
                xaxis_title="Time(seconds)",
                yaxis_title="SHAP Value",
                legend_title="Features",
            )
        return fig