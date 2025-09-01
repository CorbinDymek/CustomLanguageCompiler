class AMBNode:
    def __init__(self, nodeType, value=None):
        self.nodeType = nodeType
        self.value = value
        self.children = []

    def addChild(self, child):
        self.children.append(child)

    def printTree(self, indent=0):
        output = ""
        for i in range(indent):
            output += "  "
        output += self.nodeType
        if self.value is not None:
            output += ", " + str(self.value)
        for child in self.children:
            output = output + "\n" + child.printTree(indent + 1)
        return output

    def __str__(self):
        return self.printTree()

    def generateCode(self, indent=0, label=None):
        output = ""
        indentString = "    " * indent

        if self.nodeType == "Program":
            for child in self.children:
                output += child.generateCode(0)
            output += "main()"
            return output

        #handles variables both integers and strings
        elif self.nodeType == "Variable":
            typeNode = self.children[0]
            labelNode = self.children[1]
            if typeNode.value == "INT":
                output += indentString + labelNode.value + " = 0\n" #initializes int
            elif typeNode.value == "STRING":
                output += indentString + labelNode.value + ' = ""\n' #initialized string
            return output

        #handles arrays - both integers and strings
        elif self.nodeType == "ArrayVariable":
            typeNode = self.children[0]
            labelNode = self.children[2]
            sizeNode = self.children[4]
            if typeNode.value == "INT":
                output += indentString + labelNode.value + " = [0] * " + sizeNode.value + "\n" #creates int array of certain size
            elif typeNode.value == "STRING":
                output += indentString + labelNode.value + " = [''] * " + sizeNode.value + "\n" #creates string array of certain size
            return output

        #creates functions out of sublist
        elif self.nodeType == "SubList":
            labelNode = self.children[1]
            output += indentString + "def " + labelNode.value + "():\n" #defines function
            for child in self.children[3:]:
                if (child.nodeType != "keyword" or child.value != "END_SUB"):
                    output += child.generateCode(indent+1)
            return output + "\n"

        #creates a function call from goSub
        elif self.nodeType == "GoSub":
            labelNode = self.children[1]
            output += indentString + labelNode.value + "()\n" #calls function
            return output

        #handles printing in python
        elif self.nodeType == "Print":
            expNode = self.children[2]
            expCode = expNode.generateCode(0).strip()
            output += indentString + "print(" + expCode + ")\n"
            return output

        #handles variable/array names aka lineLabel
        elif self.nodeType == "LineLabel":
            if len(self.children) > 1:
                labelVal = self.children[0].value
                output += self.children[1].generateCode(indent, label = labelVal)
            return output

        #Handles expressions and creates assingment using "=" in python
        elif self.nodeType == "Assignment":
            if len(self.children) >= 5 and self.children[0].value == "[": #array
                indexNode = self.children[1]
                expNode = self.children[4]
                indexCode = indexNode.generateCode(0).strip()
                expCode = expNode.generateCode(0).strip()
                output += indentString + label + "[" + indexCode + "] = " + expCode + "\n" #assigns array element
            else:  #regular assignment not array
                expNode = self.children[1]
                expCode = expNode.generateCode(0).strip()
                output += indentString + label + " = " + expCode + "\n" #assigns variable
            return output

        #handles loops by turning comparison values from AMB into python operations
        elif self.nodeType == "Loop":
            exp1Node = self.children[1]
            compNode = self.children[2]
            exp2Node = self.children[3]
            exp1Code = exp1Node.generateCode(0).strip()
            exp2Code = exp2Node.generateCode(0).strip()
            comparrisonValues = {"<": "<", ">": ">", "=<": "<=", "=>": ">=", "=": "==", "!=": "!="}
            comparrisonOp = comparrisonValues.get(compNode.value, compNode.value)
            output += indentString + "while " + exp1Code + " " + comparrisonOp + " " + exp2Code + ":\n" #starts while loop
            for child in self.children[5:]:
                if child.nodeType != "keyword" or child.value != "END_WHILE":
                    output += child.generateCode(indent + 1)
            return output

        #handles creation of if-else statements by converting AMB operations into python operations
        elif self.nodeType == "Condition":
            exp1Node = self.children[1]
            compNode = self.children[2]
            exp2Node = self.children[3]
            exp1Code = exp1Node.generateCode(0).strip()
            exp2Code = exp2Node.generateCode(0).strip()
            comparrisonValues = {"<": "<", ">": ">", "=<": "<=", "=>": ">=", "=": "==", "!=": "!="}
            comparrisonOp = comparrisonValues.get(compNode.value, compNode.value)
            output += indentString + "if " + exp1Code + " " + comparrisonOp + " " + exp2Code + ":\n" #starts if statement
            for child in self.children[5:]:
                if child.nodeType == "keyword" and child.value == "ELSE":
                    output += indentString + "else:\n" #starts else statement
                elif child.nodeType != "keyword" or child.value != "END_IF":
                    output += child.generateCode(indent + 1)
            return output

        #handles mathematical expressions and creates them in python
        elif self.nodeType == "Expression":
            if len(self.children) == 1:
                output += self.children[0].generateCode(0)

            else:
                result = self.children[0].generateCode(0).strip()
                i = 1
                while i < len(self.children):
                    op = self.children[i].value
                    nextTerm = self.children[i + 1].generateCode(0).strip()
                    result = result + " " + op + " " + nextTerm
                    i += 2  #skips op and term
                output += result
            return output

        #handles "[" and "(" such as array assignment or complex expressions
        elif self.nodeType == "Term":
            if len(self.children) == 1:
                output += self.children[0].generateCode(0)
            elif len(self.children) >= 3 and self.children[1].nodeType == "hardOpen":
                label = self.children[0].generateCode(0).strip()
                index = self.children[2].generateCode(0).strip()
                output += label + "[" + index + "]" #access array element
            elif len(self.children) >= 3 and self.children[0].nodeType == "softOpen":
                result = self.children[1].generateCode(0).strip()
                output += "(" + result + ")"
                i = 3 #skips softclose
                while i + 1 < len(self.children):
                    op = self.children[i].value
                    nextFactor = self.children[i + 1].generateCode(0).strip()
                    output += " " + op + " " + nextFactor
                    i += 2
            else:
                result = self.children[0].generateCode(0).strip()
                i = 1
                while (i+1 < len(self.children)):
                    op = self.children[i].value
                    nextFactor = self.children[i + 1].generateCode(0).strip()
                    result +=  " " + str(op) + " " + nextFactor
                    i += 2  #Skips op and term
                output += result
            return output


        elif self.nodeType == "label":
            output += str(self.value)
            return output

        elif self.nodeType == "number":
            output += str(self.value)
            return output

        elif self.nodeType == "string":
            output += self.value
            return output
        #handles inputs in AMB and gets them working in python
        elif self.nodeType == "keyword" and self.value in ["INPUT_INT", "INPUT_STRING"]:
            if self.value == "INPUT_INT":
                output += "int(input())" #integer input
            else:
                output += "input()" #string input
            return output

        #if criteria not met in previous function, this allows program to continue and not crash
        elif self.nodeType in ["keyword", "semi", "softOpen", "softClose", "hardOpen", "hardClose", "colon",
                               "assignment", "addOp", "multOp", "compOp"]:
            return ""

        else:
            output += indentString + "node: " + self.nodeType + "\n"
            return output
