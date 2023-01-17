import param


class DataHistoryItem(param.Parameterized):
    # TODO think about iof this can be constant
    data = param.Parameter(allow_None=False)
    # Contains all features created by pipelines
    features = param.Dict(default={})
    # holds the outputs of the ML models run on the features
    mlRuns = param.Dict(default={})
    name = param.String(allow_None=False)
    predecessor = param.String(allow_None=True)

    @param.depends('data', 'features', 'name', 'mlRuns')
    def updateHistory(self):
        print("updateHistory")
        if main_ecg_history is not None:
            main_ecg_history.history = main_ecg_history.history

    def getID(self):
        return self.name

    def getSaveDict(self):
        """Returns a dictionary used for pickeling
        Returns:
            {dict}: a dictionary containing all the major data of the DataHistoryItem
        """
        return {"data": list(self.data), "features": dict(self.features), "mlRuns": dict(self.mlRuns), "name": str(self.name), "predecessor": str(self.predecessor)}

    def loadFromDict(self, loadedDict):
        """Loads and replaces Data from a given dict.
        Used for pickeling and replacing

        Args:
            loadedDict (_type_): _description_
        """
        if "data" in loadedDict:
            self.data = loadedDict["data"]
        if "features" in loadedDict:
            self.features = loadedDict["features"]
        if "mlRuns" in loadedDict:
            self.mlRuns = loadedDict["mlRuns"]
        if "name" in loadedDict:
            self.name = loadedDict["name"]
        if "predecessor" in loadedDict:
            self.predecessor = loadedDict["predecessor"]

    def updateFromDict(self, loadedDict):
        if "data" in loadedDict and not (loadedDict["data"] is None or loadDict["data"] == []):
            self.data = loadedDict["data"]
        if "features" in loadedDict and loadedDict["features"] is not None:
            # For each feature in the dict, check if it is already in the features dict and replace otherwise add
            for key in loadedDict["features"]:
                if key not in self.features:
                    self.features[key] = loadedDict["features"][key]
                else:
                    self.features.update({key: loadedDict["features"][key]})
        # For each mlRun in the dict, check if it is already in the mlRuns dict and replace otherwise add
        if "mlRuns" in loadedDict and loadedDict["mlRuns"] is not None:
            for key in loadedDict["mlRuns"]:
                if key in self.mlRuns:
                    self.mlRuns[key] = loadedDict["mlRuns"][key]
                else:
                    self.mlRuns.update({key: loadedDict["mlRuns"][key]})
        # update the name and predecessor if given

        if "predecessor" in loadedDict:
            self.predecessor = loadedDict["predecessor"]
        else:
            self.name

        if "name" in loadedDict:
            self.name = loadedDict["name"]
        else:
            self.name = self.name + "#"


class DataHistoryList(param.Parameterized):
    current = param.ClassSelector(DataHistoryItem, allow_None=True)
    history = param.List(class_=DataHistoryItem, allow_None=True, default=[])

    def addNew(self, dataHistoryItem):
        # check if dataHistory Item has a data
        if dataHistoryItem.data is None:
            raise Exception("DataHistoryItem has no data")
        # check if dataHistory Item has a name, other wise give it default name
        if dataHistoryItem.name is None:
            dataHistoryItem.name = "Item#"+str(len(self.history))
        # check if the name is already in the history, if so add a number to the end
        if dataHistoryItem.name in [x.name for x in self.history]:
            dataHistoryItem.name = dataHistoryItem.name + \
                "#" + str(len(self.history))
        self.history.append(dataHistoryItem)
        self.history = self.history  # hack to trigger change events
        self.current = self.history[-1]
        return self.current

    def addNewFromDict(self, inDict):
        if "name" in inDict and inDict["name"] in [x.name for x in self.history]:
            inDict["name"] = inDict["name"] + "#" + str(len(self.history))
        historyItem = DataHistoryItem(data=[], name="")
        print(historyItem)
        historyItem.loadFromDict(inDict)
        print(historyItem)
        return self.addNew(historyItem)

    def addNewToExisting(self, id, data, features, runs):
        dataElem = self.getHistoryFromID(id)
        isCurrent = dataElem == self.current
        if runs is None:
            runs = {}
        if data is not None and (dataElem.features is not None or dataElem.mlRuns != {}):
            self.addNewFromDict({"data": data, "features": features, "mlRuns": runs,
                                "name": dataElem.name, "predecessor": dataElem.name})
            return

        if features is not None and (dataElem.mlRuns != {}):
            self.addNew({"data": dataElem.data, "features": features,
                        "mlRuns": runs, "name": dataElem.name, "predecessor": dataElem.name})
            return

        # replace data
        dataElem.updateFromDict(
            {"data": data, "features": features, "mlRuns": runs})
        # update current if only updated
        if isCurrent:
            self.current = dataElem
        return dataElem

    def setActive(self, id):
        print("setActive" + str(id))
        self.current = self.getHistoryFromID(id)

    def getHistoryFromID(self, id):
        name = id
        return [x for x in self.history if x.name == name][0] if [x for x in self.history if x.name == name] != [] else None
