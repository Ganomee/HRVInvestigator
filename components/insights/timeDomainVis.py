# import all necessary libraries
import numpy as np
import param
import panel as pn
from components.insights.shared import InsightsWindowSelector, InsightsTab
import holoviews as hv
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource


class InsightsTimeDomainTab(InsightsTab):
    domainStatsVis = param.Parameter(default=None, precedence=-1)
    domainVis = param.Parameter(default=None, precedence=-1)

    def __init__(self, fileSelectorRef, windowSelectorRef, data_history, **params):
        super(InsightsTimeDomainTab, self).__init__(
            fileSelectorRef, windowSelectorRef, data_history, **params)
        self.domainStatsVis = InsightsTimeDomainStats(
            self.activeDataObj, self.windowSelectorRef)
        self.domainVis = InsightsTimeDomainVis(
            self.activeDataObj, self.windowSelectorRef)

    @param.depends('windowSelectorRef.window', 'fileSelectorRef.options')
    def getRender(self):
        return pn.Row(self.domainStatsVis.getRender(self.activeDataObj, self.windowSelectorRef.window) if self.domainStatsVis is not None else None,
                      self.domainVis.getRender(
            self.activeDataObj, self.windowSelectorRef.window) if self.domainVis is not None else None
        )


class InsightsTimeDomainStats(param.Parameterized):
    meanRR = param.Number(default=None, precedence=1)
    SDNN = param.Number(default=None, precedence=1)
    Mean_HR = param.Number(default=None, precedence=1)
    STD_HR = param.Number(default=None, precedence=1)
    MinHR = param.Number(default=None, precedence=1)
    MaxHR = param.Number(default=None, precedence=1)
    RMSDD = param.Number(default=None, precedence=1)

    def __init__(self, dataObjRef, windowRef, **params):
        super(InsightsTimeDomainStats, self).__init__(**params)

    def updateParams(self, dataObj, window):
        # check if data object is not none or window is not none
        if dataObj is not None and "peaks" in dataObj.features and window is not None and "sfreq" in dataObj.features:
            # get the data
            data = dataObj.features["peaks"]
            freq = dataObj.features["sfreq"]
            # create a mask that filters for data larger than the first elem of window and smaller than the second elem of window
            mask = (data >= window[0]) & (data <= window[1])
            # apply that mask to the data
            data = np.unique(data[mask])
            # compute the stats
            data = np.diff(data)/freq
            self.meanRR = np.mean(data)
            self.SDNN = np.std(data)
            self.Mean_HR = 60000/self.meanRR
            self.STD_HR = 60000/self.SDNN
            self.MinHR = 60000/np.max(data)
            self.MaxHR = 60000/np.min(data)
            self.RMSDD = np.sqrt(np.mean(np.square(np.diff(data))))
        else:
            # set info to none
            self.meanRR = None
            self.SDNN = None
            self.Mean_HR = None
            self.STD_HR = None
            self.MinHR = None
            self.MaxHR = None
            self.RMSDD = None

    def getRender(self, dataObj, window):
        self.updateParams(dataObj, window)
        # check if data is not none
        if self.meanRR is None:
            # then return a message with peak detection info unavailable
            return pn.Column(pn.pane.Markdown("## Time Domain Stats"), pn.pane.Markdown("No peak data available"))
        # return a tabulated panel with the stats
        return pn.Param(self, parameters=['meanRR', 'SDNN', 'Mean_HR', 'STD_HR', 'MinHR', 'MaxHR', 'RMSDD'], show_name=False, widgets={'meanRR': {'type': pn.widgets.StaticText, 'readonly': True},
                                                                                                                                       'SDNN': {'type': pn.widgets.StaticText, 'readonly': True},
                                                                                                                                       'Mean_HR': {'type': pn.widgets.StaticText, 'readonly': True},
                                                                                                                                       'STD_HR': {'type': pn.widgets.StaticText, 'readonly': True},
                                                                                                                                       'MinHR': {'type': pn.widgets.StaticText, 'readonly': True},
                                                                                                                                       'MaxHR': {'type': pn.widgets.StaticText, 'readonly': True},
                                                                                                                                       'RMSDD': {'type': pn.widgets.StaticText, 'readonly': True}})


class InsightsTimeDomainVis(param.Parameterized):

    def __init__(self, dataObjRef, windowRef, **params):
        super(InsightsTimeDomainVis, self).__init__(**params)

    def getRender(self, dataObj, window):
        # return a message that no visualizations are available if dataObj has no feature peaks

        if dataObj is None or "peaks" not in dataObj.features:
            return pn.Column(pn.pane.Markdown("## Time Domain Visualizations"), pn.pane.Markdown("No peak data available"))
        if "sfreq" not in dataObj.features:
            return pn.Column(pn.pane.Markdown("## Time Domain Visualizations"), pn.pane.Markdown("No sampling frequency available"))

        # get the data
        peaks = dataObj.features["peaks"]
        # create a mask that filters for data larger than the first elem of window and smaller than the second elem of window
        mask = (peaks >= window[0]) & (peaks <= window[1])
        # apply that mask to the data
        peaks = peaks[mask]

        # caclculate the distance between peaks
        distances = np.unique(np.diff(peaks))
        # multiply with frequency to get the distance in seconds
        distances = distances/dataObj.features["sfreq"]

        hist, edges = np.histogram(distances, density=True, bins=50)

        bins = pd.DataFrame(
            {'left': edges[:-1], 'right': edges[1:], 'top': hist})
        bins = ColumnDataSource(bins)

        p = figure(plot_height=400, plot_width=400, title='Histogram',
                   tools="save", background_fill_color="#fafafa")
        p.quad(bottom=0, top='top', left='left', right='right',
               source=bins, fill_color="navy", line_color="white", alpha=0.5)
        bokehPane = pn.pane.Bokeh(p)
        # return the histogram
        return pn.Column(pn.pane.Markdown("## Time Domain Visualizations"), bokehPane)
