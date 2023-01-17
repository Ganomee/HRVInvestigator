# a panel Select widget with an auto update function if a value changes inside the MainHistoryParam,
# or its current selected value changes
from panel.widgets import Select
import panel as pn
from param.parameterized import bothmethod
from components.dataStructure import DataHistoryItem, DataHistoryList
import param


class ECGHistorySelector(param.Parameterized):

    ecg_history = param.ClassSelector(
        DataHistoryList, allow_None=True, precedence=-1)
    options_selector = Select(default=None,
                              options=[None],
                              allow_None=True, check_on_set=False)

    def __init__(self, ecg_history=None, label="Select Input", **params):
        super().__init__(**params)
        self.ecg_history = ecg_history or []
        self.label = label
        self.options_selector = Select(
            default=None, options=[None], name=self.label)
        self.update_active_history_item()
        self.ecg_history.param.watch(self.update_active_history_item, [
            'history'], onlychanged=False)
        self.ecg_history.param.watch(self.update_active_history_item, [
            'current'], onlychanged=False)

    @bothmethod
    def update_active_history_item(self, *events):
        self.options_selector.options = [
            elem.getID() for elem in self.ecg_history.history]

    def render(self):
        return self.options_selector


class ECGRunSelector(param.Parameterized):

    ecg_history = param.ClassSelector(
        DataHistoryList, allow_None=True, precedence=-1)
    ecg_file_selector_hook = param.Parameter(allow_None=True, precedence=-1)
    options_selector = Select(default=None,
                              options=[],
                              allow_None=True, check_on_set=False)

    def __init__(self, ecg_history=None, label="Select Input", hook=None, **params):
        super().__init__(**params)
        self.ecg_history = ecg_history or []
        self.label = label
        self.ecg_file_selector_hook = hook or None
        self.options_selector = Select(
            default=None, options=[None], name=self.label)
        self.update_active_history_item()
        self.ecg_history.param.watch(self.update_active_history_item, [
            'history'], onlychanged=True)
        self.ecg_history.param.watch(self.update_active_history_item, [
            'current'], onlychanged=False)
        self.ecg_file_selector_hook.param.watch(self.update_active_history_item, [
            'value'], onlychanged=False)

    @bothmethod
    def update_active_history_item(self, *events):
        if self.ecg_file_selector_hook is not None:
            # get the key names of the current selected item
            active_id = self.ecg_file_selector_hook.value
            active_obj = self.ecg_history.getHistoryFromID(active_id)
            runs = active_obj.mlRuns.keys()
            self.options_selector.options = [
                run for run in runs if run != 'truth']

        else:
            self.options_selector.options = []

    def render(self):
        return self.options_selector
