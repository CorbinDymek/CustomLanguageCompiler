from enum import nonmember
from unittest import expectedFailure

import Token
import AMBNode
class ExpectedSymbol(Exception):
    pass

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.currentToken = 0

    def getCur(self):
        if self.currentToken < len(self.tokens):
            return self.tokens[self.currentToken]
        return None

    def consume(self, node, expectedType=None, expectedValue=None):
        cur = self.getCur()
        if cur is None:
            raise ExpectedSymbol("Reached the end of the input")
        if expectedType and cur.getType() != expectedType:
            raise ExpectedSymbol("Was expecting "+ cur.getType() +" type at pos "+ str(self.currentToken) + " but got " + cur.getType())
        if expectedValue and cur.getValue() != expectedValue:
            raise ExpectedSymbol("Was expecting a different value, got "+ cur.getValue() + " but expected " + expectedValue + ": at token " + str(self.currentToken))

        self.currentToken += 1
        node.addChild(AMBNode.AMBNode(cur.getType(), cur.getValue()))
        return True

    def parse(self):
        root = AMBNode.AMBNode("Program")
        self.program(root)
        return root

    def program(self, node):
        self.consume(node, expectedValue="START_PROGRAM")
        self.variableList(node)

    def variableList(self, node):
        cur = self.getCur()
        if cur and (cur.getValue() == "INT" or cur.getValue() == "STRING" or cur.getValue() == "["):
            self.variable(node)
            self.variableList(node)
        elif cur and cur.getValue() == "CODE":
            self.consume(node, expectedValue="CODE")
            self.subList(node)
        else:
            raise ExpectedSymbol("Expected INT, STRING, or CODE: " + str(self.currentToken))

    def variable(self, node):
        cur = self.getCur()
        if cur and (cur.getValue() == "INT" or cur.getValue() == "STRING"):
            variableNode = AMBNode.AMBNode("Variable")
            self.consume(variableNode, expectedValue=cur.getValue())
            self.consume(variableNode, expectedType="label")
            self.consume(variableNode, expectedValue=";")
            node.addChild(variableNode)
        elif cur and cur.getValue() == "[":
            self.consume(node, expectedValue="[")
            self.arrayVariable(node)
        else:
            raise ExpectedSymbol("Expected INT, STRING, or '['")


    def arrayVariable(self,node):
        varNode = AMBNode.AMBNode("ArrayVariable")
        cur = self.getCur()
        if cur and (cur.getValue() == "INT" or cur.getValue() == "STRING"):
            self.consume(varNode, expectedValue=cur.getValue())
            self.consume(varNode, expectedValue="]")
            self.consume(varNode, expectedType="label")
            self.consume(varNode, expectedValue="[")
            self.consume(varNode, expectedType="number")
            self.consume(varNode, expectedValue="]")
            self.consume(varNode, expectedValue=";")
            node.addChild(varNode)
        else:
            raise ExpectedSymbol("Expected INT or STRING at token " + str(self.currentToken) + " but got " + cur.getValue())

    def subList(self,node):
        cur = self.getCur()
        if cur and cur.getValue() == "START_SUB":
            subNode = AMBNode.AMBNode("SubList")
            self.consume(subNode, expectedValue="START_SUB")
            self.consume(subNode, expectedType="label")
            self.consume(subNode, expectedValue=":")
            self.codeList(subNode)
            node.addChild(subNode)
            self.subList(node)
        elif cur and cur.getValue() == "END_PROGRAM":
            self.consume(node, expectedValue="END_PROGRAM")
        else:
            raise ExpectedSymbol("Expected START_SUB or END_PROGRAM")

    def codeList(self,node):
        cur = self.getCur()
        if cur and cur.getValue() == "END_SUB":
            self.consume(node, expectedValue="END_SUB")
        else:
            self.codeLine(node)
            self.codeList(node)

    def codeLine(self,node):
        cur = self.getCur()
        # if cur and cur.getType() == "label":
        #     self.lineLabel(node)
        if cur and cur.getValue() == "IF":
            self.condition(node)
        elif cur and cur.getValue() == "WHILE":
            self.loop(node)
        elif cur and cur.getValue() == "PRINT":
            printNode = AMBNode.AMBNode("Print")
            self.consume(printNode, expectedValue="PRINT")
            self.consume(printNode, expectedValue="(")
            self.expression(printNode)
            self.consume(printNode, expectedValue=")")
            self.consume(printNode, expectedValue=";")
            node.addChild(printNode)
        elif cur and cur.getValue() == "GOSUB":
            goSubNode = AMBNode.AMBNode("GoSub")
            self.consume(goSubNode, expectedValue="GOSUB")
            self.consume(goSubNode, expectedType="label")
            self.consume(goSubNode, expectedValue=";")
            node.addChild(goSubNode)
        else:
            #raise ExpectedSymbol("Expected label, condition, loop, PRINT, or GOSUB at pos " + str(self.currentToken) + " but got " + cur.getValue())
            self.lineLabel(node)

    def lineLabel(self,node):
        lineLabelNode = AMBNode.AMBNode("LineLabel")
        self.consume(lineLabelNode, expectedType="label")
        self.assignment(lineLabelNode)
        node.addChild(lineLabelNode)

    def assignment(self,node):
        assignNode = AMBNode.AMBNode("Assignment")
        cur = self.getCur()
        if cur and cur.getValue() == "[":
            self.consume(assignNode, expectedValue="[")
            next = self.getCur()
            if next and (next.getType() == "number" or next.getType() == "label"):
                self.consume(assignNode, expectedType=next.getType())
                self.consume(assignNode, expectedValue="]")
                self.consume(assignNode, expectedValue=":=")
                self.expressionOrInput(assignNode)
                self.consume(assignNode, expectedValue=";")
        else:
            self.consume(assignNode, expectedValue=":=")
            self.expressionOrInput(assignNode)
            self.consume(assignNode, expectedValue=";")

        node.addChild(assignNode)

    def condition(self, node):
        conditionNode = AMBNode.AMBNode("Condition")
        self.consume(conditionNode, expectedValue="IF")
        self.expression(conditionNode)
        self.consume(conditionNode, expectedType="compOp")
        self.expression(conditionNode)
        self.consume(conditionNode, expectedValue="THEN")
        self.thenCodeList(conditionNode)
        node.addChild(conditionNode)

    def thenCodeList(self,node):
        cur = self.getCur()
        if cur and cur.getValue() == "ELSE":
            self.consume(node, expectedValue="ELSE")
            self.elseCodeList(node)
        elif cur and cur.getValue() == "END_IF":
            self.consume(node, expectedValue="END_IF")
        else:
            self.codeLine(node)
            self.thenCodeList(node)

    def elseCodeList(self, node):
        cur = self.getCur()
        if cur and cur.getValue() == "END_IF":
            self.consume(node, expectedValue="END_IF")
        else:
            self.codeLine(node)
            self.elseCodeList(node)

    def loop(self, node):
        loopNode = AMBNode.AMBNode("Loop")
        self.consume(loopNode, expectedValue="WHILE")
        self.expression(loopNode)
        self.consume(loopNode, expectedType="compOp")
        self.expression(loopNode)
        self.consume(loopNode, expectedValue="DO")
        self.whileCodeList(loopNode)
        node.addChild(loopNode)

    def whileCodeList(self,node):
        cur = self.getCur()
        if cur and cur.getValue() == "END_WHILE":
            self.consume(node, expectedValue="END_WHILE")
        else:
            self.codeLine(node)
            self.whileCodeList(node)

    def expressionOrInput(self, node):
        cur = self.getCur()
        if cur and cur.getValue() == "INPUT_INT":
            self.consume(node, expectedValue="INPUT_INT")
        elif cur and cur.getValue() == "INPUT_STRING":
            self.consume(node, expectedValue="INPUT_STRING")
        else:
            self.expression(node)

    def expression(self,node):
        expNode = AMBNode.AMBNode("Expression")
        self.term(expNode)
        self.termTail(expNode)
        node.addChild(expNode)

    def termTail(self,node):
        cur = self.getCur()
        if cur and (cur.getValue() == "+" or cur.getValue() == "-"):
            self.consume(node, expectedValue=cur.getValue())
            self.term(node)
            self.termTail(node)

    def term(self, node):
        termNode = AMBNode.AMBNode("Term")
        self.factor(termNode)
        self.factorTail(termNode)
        node.addChild(termNode)

    def factorTail(self,node):
        cur = self.getCur()
        if cur and (cur.getValue() == "*" or cur.getValue() == "/"):
            self.consume(node, expectedValue=cur.getValue())
            self.factor(node)
            self.factorTail(node)

    def factor(self,node):
        cur = self.getCur()
        if cur and cur.getValue() == "(":
            self.consume(node, expectedValue="(")
            self.expression(node)
            self.consume(node, expectedValue=")")
        elif cur and cur.getType() == "number":
            self.consume(node, expectedType="number")
        elif cur and cur.getType() == "string":
            self.consume(node, expectedType="string")
        elif cur and cur.getType() == "label":
            self.consume(node, expectedType="label")
            self.possibleArray(node)
        else:
            raise ExpectedSymbol("Expected '(', number, characterString, or label at pos " + str(self.currentToken) + " " + cur.getValue())

    def possibleArray(self,node):
        cur = self.getCur()
        if cur and cur.getValue() == "[":
            self.consume(node, expectedValue="[")
            self.arrayNumberOrLabel(node)

    def arrayNumberOrLabel(self,node):
        cur = self.getCur()
        if cur and (cur.getType() == "number" or cur.getType() == "label"):
            self.consume(node, expectedType=cur.getType())
            self.consume(node, expectedValue="]")
        else:
            raise ExpectedSymbol("Expected number or label")




