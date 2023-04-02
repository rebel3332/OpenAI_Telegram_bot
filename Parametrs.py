class Parametrs():
    data = dict()

    def __init__(self, BD):
        self.data = BD.get_allparametrs()
