class Token:
    def __init__(self, tokenType, value):
        self.tokenType = tokenType
        self.value = value

    def getToken(self):
        return (self.tokenType,self.value)

    def getType(self):
        return self.tokenType
    def getValue(self):
        return self.value