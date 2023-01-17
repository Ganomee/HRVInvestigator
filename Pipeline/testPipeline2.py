import param


class testPipeline2(param.Parameterized):
    testInput = param.String(default='test')
    testWindowsize2 = param.Integer(default=10)

    def run(self, *events):
        print("doing calculations" + str(self.testWindowsize2))
        return self.testInput
