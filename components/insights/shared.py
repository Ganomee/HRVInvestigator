import param
import panel as pn
import numpy as np
from param.parameterized import bothmethod
from components.dataStructure import DataHistoryList, DataHistoryItem


class InsightsFileSelector(param.Parameterized):

    dataHistory = param.ClassSelector(
        DataHistoryList, allow_None=True, precedence=-1)
    options = param.Selector(default=None,
                             objects=[None],
                             allow_None=True, check_on_set=False)

    def __init__(self, data_history, **params):
        super().__init__(**params)
        self.dataHistory = data_history
        self.updateOptions()
        # install proper watcher on dataHistory
        self.dataHistory.param.watch(self.updateOptions, "history")

    # @param.depends('main_ecg_history.history', watch=True)
    def updateOptions(self, *events):
        self.param['options'].objects = [None] + \
            [elem.name for elem in self.dataHistory.history]

    def getRender(self):
        return pn.Param(self, parameters=["options"], widgets={
                        "options": {"widget_type": pn.widgets.Select, "name": ""}}, name="Select Source")


class InsightsWindowSelector(param.Parameterized):
    window = param.Range(default=(0, 1), bounds=(
        0, 1), precedence=1, instantiate=True, per_instance=True)
    fileSelectorRef = param.Parameter(
        default=None, precedence=-1, instantiate=True, per_instance=True)
    windowSelector = pn.widgets.EditableRangeSlider(name="Select Window", start=0, end=1,
                                                    value_throttled=(0, 1), step=1, instantiate=True, per_instance=True)
    dataHistory = param.ClassSelector(
        DataHistoryList, allow_None=True, precedence=-1, instantiate=True, per_instance=True)

    def __init__(self, fileSelector, data_history,  **params):
        super(InsightsWindowSelector, self).__init__(**params)
        # create a binding that updates the window when the windowSelector is changed
        self.fileSelectorRef = fileSelector
        self.windowSelector = pn.widgets.EditableRangeSlider(name="Select Window", start=0, end=1,
                                                             value_throttled=(0, 1), step=1, instantiate=True, per_instance=True)
        self.windowSelector.param.watch(self.updateWindow, ['value_throttled'])
        self.param.watch(self.updateSliderBounds, 'window', onlychanged=False)
        self.dataHistory = data_history

    @bothmethod
    def updateSliderBounds(self, *events):
        """Updates the bounds of the slider based on the param representation of window"""
        print("called updatedSliderBounds")
        print(*events)
        # get current values of the slider
        start = self.windowSelector.value[0]
        end = self.windowSelector.value[1]
        # get target bounds of the param window
        target_start = self.param.window.bounds[0]
        target_end = self.param.window.bounds[1]
        # if setting bounds would violate the currrent values update them first
        if start < target_start:
            start = target_start
        if end > target_end:
            end = target_end
        self.windowSelector.value = (start, end)
        # now update the bounds of the slider
        self.windowSelector.start = target_start
        self.windowSelector.end = target_end

    def updateWindow(self, *events):
        """Updates the param window based on the value of the windowSelector"""
        print("called updatedWindow")
        winState = self.param['window'].readonly
        # disable readonly
        self.param['window'].readonly = False
        self.window = self.windowSelector.value_throttled
        # re-enable readonly
        self.param['window'].readonly = winState

    @param.depends('fileSelectorRef.options', watch=True, on_init=True)
    def updateWindowBounds(self, *events):
        """Updates the bounds of the window based on the selected file"""
        print("called updatedWindowBounds")
        if self.fileSelectorRef is not None and self.fileSelectorRef.options is not None:
            # get data from history
            dataElem = self.dataHistory.getHistoryFromID(
                self.fileSelectorRef.options)
            if dataElem is not None:
                self.param['window'].readonly = False
                self.param['window'].bounds = (0, len(dataElem.data))
                self.window = (0, len(dataElem.data))
                self.param.trigger('window')
        else:
            self.param['window'].readonly = False
            self.param['window'].bounds = (0, 1)
            self.window = (0, 1)
            self.param.trigger('window')
            self.param['window'].readonly = True

    @param.depends('fileSelectorRef.options', watch=False)
    def getRender(self):
        return self.windowSelector


class InsightsTab(param.Parameterized):
    """Abstract class for the individual insights tabs"""
    fileSelectorRef = param.Parameter(default=None, precedence=-1)
    windowSelectorRef = param.Parameter(default=None, precedence=-1)
    # a parameter of DataHistory  Item
    activeDataObj = param.Parameter(default=None, precedence=-1)
    # elem of type DataHistoryList
    dataHistory = param.ClassSelector(class_=DataHistoryList, precedence=-1)

    def __init__(self, fileSelectorRef, windowSelectorRef, data_history, **params):
        super(InsightsTab, self).__init__(**params)
        self.fileSelectorRef = fileSelectorRef
        self.windowSelectorRef = windowSelectorRef
        self.dataHistory = data_history
        # install watcher for fileSelector
        self.dataHistory.param.watch(
            self.updateDataObj, "history", onlychanged=False)

    # update the active data object ,so that the active data can be handed down to child components
    @param.depends('fileSelectorRef.options', watch=True, on_init=True)
    def updateDataObj(self, *events):
        if self.fileSelectorRef is not None and self.fileSelectorRef.options is not None:
            self.activeDataObj = self.dataHistory.getHistoryFromID(
                self.fileSelectorRef.options)

        else:
            # update the active data objSect to None using panel .update
            self.activeDataObj = None

    @param.depends('fileSelectorRef.options', 'windowSelectorRef.window', watch=True, on_init=True)
    def getRender(self, *events):
        # To be implemented in child class likely contains stats and visualizations
        return pn.Column()
