import param


class aatestPipeline(param.Parameterized):
    testInput = param.String(default='test')
    testWindowsize = param.Integer(default=10)

    def run(self, *events):
        print("doing calculations" + str(self.testWindowsize))
        return self.testInput
