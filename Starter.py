import re
import subprocess

import Token
import Parser
#list of all keywords
keywords = ["START_PROGRAM","END_PROGRAM", "START_SUB", "END_SUB", "GOSUB", "CODE", "IF",
            "THEN", "ELSE", "END_IF", "WHILE", "DO", "END_WHILE", "INT", "STRING", "PRINT", "INPUT_INT", "INPUT_STRING" ]

#list of all symbols
symbols = {"softOpen": r"\(", "softClose": r"\)", "hardOpen": r"\[", "hardClose": r"\]",
           "quote": r'"', "semi": r";", "assignment": r"(:=)", "colon": r":", "multOp": r"[*/]",
           "addOp": r"[+-]", "compOp": r"<|>|=<|=>|=|!="
           }

keywordPattern = r"\b(" + "|".join(keywords) + r")\b" #combining the keywords separated by a '|'
symbolPattern = r"|".join(symbols.values()) #combining the symbols separatec by a '|'
numberPattern = r"(-?[1-9][0-9]*|0)" #regular expression rule for number
stringPattern = r'"[a-zA-Z0-9 -]*"' #regular expression rule for string
labelPattern = r"\b[a-zA-Z][a-zA-Z0-9]*\b" #regular expression rule for label
tokenPattern = r"|".join([keywordPattern, stringPattern, numberPattern, symbolPattern, labelPattern]) #combining all possible tokens separated by a '|'

def tokenize(filePath):
    #opens the AMB file and reads it and sets code equal to its contents
    with open(filePath, "r") as f:
        code = f.read()

    tokens = []
    last = 0

    #finds all matches in code that match a tokenPattern
    for match in re.finditer(tokenPattern, code):
        if match.start() > last: #checks to see if there are symbols inbetween last match and current match
            wrongArray = []
            #loops through space between last match and current match and adds everything to wrongArray
            for i in range(last,match.start()):
                wrongArray.append(code[i])
            wrong = ''.join(wrongArray) #joins everything from wrongArray
            if not wrong.isspace(): #checks to make sure it is not just white space
                print("Unrecognized token : "+ wrong.strip())

        value = match.group()

        #check to see what category match fell in
        if re.match(stringPattern, value):
            tokentype = "string"
        elif re.match(keywordPattern, value):
            tokentype = "keyword"
        elif re.match(numberPattern, value):
            tokentype = "number"
        elif re.match(symbolPattern, value):
            #loops through all symbols in symbols and assigns symbol to the symbol
            #and assigns pattern to the regex
            #sets the tokenType to be what the symbol actually is (i.e. hardOpen, addOp, ect)
            for symbol, pattern in symbols.items():
                if re.fullmatch(pattern, value):
                    tokentype = symbol
                    break
        elif re.match(labelPattern, value):
            tokentype = "label"

        #adds toekns to token list and sets last match to the current match
        tokens.append(Token.Token(tokentype,value))
        last = match.end()

    #checks for any unrecognized characters after the last match is found
    #raises error if not white space
    if last < len(code):
        wrongArray = []
        for i in range(last, len(code)):
            wrongArray.append(code[i])
        wrong = ''.join(wrongArray)
        if not wrong.isspace():
            print("Unrecognized token : " + wrong.strip())

    return tokens



def test_tokenizer():
    tokens = tokenize("test.amb")
    count = 0
    for token in tokens:
        print((str(count) + ": " + token.getType()) + ", " + token.getValue())
        count+=1


#test_tokenizer()



def testParser():
    tokens = tokenize("test.amb")
    parser = Parser.Parser(tokens)
    try:
        parseTree = parser.parse()
        pythonCode = parseTree.generateCode()
        with open("generatedPy.py", "w") as f:
            f.write(pythonCode)
        print("File has been created titled 'generatedPy.py' that has working AMB code.")
    except Parser.ExpectedSymbol as e:
        print(f"Parse Error: {e}")

testParser()




