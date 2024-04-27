import regex
import argparse
import time

#
#                _---___
#           __  /       \
#          /  \ \       / __
#         /___| |______/ /  \
#          ___| |______ |   |
#         \   | |      \ \__/
#          \__/ /       \
#               \_    __/
#                  ~~~
#
#           KYLU PROJECT a1.7
#


class Node:
    def __init__(self, type, value, span, **embedded):
        self.type, self.val, self.span = type, value, span
        self.RoundingTolerance = 0.00001

        if self.type == "BOOL":
            if self.val == "True": self.val = True
            if self.val == "False": self.val = False

        #### all kylu calculations are performed on floats, try to convert values back to integers
        if self.type == "NUMBER":
            #### int(float()) is a workaround for converting floats represented as strings to integers, int("1.2") gives a ValueError
            val = float(self.val)
            self.val = round(val) if abs( round(val) - val ) < self.RoundingTolerance else val
            

        if 'a' in embedded: self.args = embedded['a']
        else: self.args = None
        if 'c' in embedded: self.contents = embedded['c']
        else: self.contents = None


    def __repr__(self):
        string = "<{}: {}{}{}>".format(
            self.type, 
            str(self.val) if self.val is not None else "",
            ", " + str(self.args) if self.args is not None else "",
            ", " + str(self.contents) if self.contents is not None else ""
        )
        return string
    
    
    def __eq__(self, other):
        if self.type != other.type: return False
        if self.val != other.val: return False
        if self.args != other.args: return False
        if self.contents != other.contents: return False
        return True



#### class will be created whenever an exception occurs during code processing
class ErrorHandler:
    def __init__(self, StartTime, ExitOnThrow):
        self.source = ""
        self.StartTime = StartTime
        self.ExitOnThrow = ExitOnThrow  #### determines if the program will be stopped when an error occurs
        self.CodeLookup = {
            "NULLREFERENCE": lambda data: f": REFERENCE '{data}' CANNOT BE RESOLVED",
            "INVALIDOPERATION": lambda data: f": OPERATION '{data[0]}' IS NOT SUPPORTED FOR TYPES {data[1]}" + f", {data[2]}" if len(data) > 2 else "",
            "UNEXPECTEDTYPE": lambda data: f": UNEXPECTED TYPE {data[0]}, EXPECTED TYPE {data[1]}",
            "FILENOTFOUND": lambda data: f": FILE '{data}' DOES NOT EXIST",
            "NOTCALLABLE": lambda data: f": OBJECT '{data}' IS NOT CALLABLE",
            "NOTITERABLE": lambda data: f": OBJECT '{data}' IS NOT ITERABLE",
            "NOTASSIGNABLE": lambda data: f": CANNOT ASSIGN VALUE TO OBJECT '{data}'",
            "INDEXERROR": lambda data: f": INDEX {data[0]} IS OUT OF RANGE FOR LIST {data[1]}",
            "ARGMISMATCH": lambda data: f": FUNCTION TAKES {data[0]} ARGUMENTS BUT {data[1]} WERE GIVEN",
            "INVALIDNAMESPACE": lambda data: ": TARGET NAMESPACE DOES NOT EXIST",
            "STOPITERATION": lambda data: ": CANNOT STOP ITERATION OUTSIDE LOOP",
            "RESETITERATION": lambda data: ": CANNOT RESET ITERATION OUTSIDE LOOP",
            "STOPFUNCTION": lambda data: ": CANNOT RETURN FROM FUNCTION OUTSIDE FUNCTION",
            "PYTHONERROR": lambda data: f": THE PYTHON INTERPRETER THREW AN EXCEPTION: {data}",
           
            "MISSINGSEPERATOR": lambda data: f": SEPERATOR '{data[0]}' IS REQUIRED BETWEEN '{data[1]}' AND '{data[2]}'",
            "UNMATCHEDPAREN": lambda data: f": PARENTHESIS OR BRACKET '{data}' WAS NEVER CLOSED",
            "INVALIDCHARACTER": lambda data: f": UNRECOGNIZED CHARACTER '{data}'",
            "MISSINGOPERAND": lambda data: f": BINARY OPERATION '{data}' IS MISSING AN OPERAND",
            "RESOLUTIONFAILURE": lambda data: f": FAILED TO RESOLVE SYNTAX ELEMENT: '{data[0]}', {data[1]}"
        }
        
    
    def SetSource(self, sourcefile): self.source = sourcefile


    def Throw(self, ErrorNode):
        if ErrorNode.val not in self.CodeLookup: print(f"UNRECOGNIZED ERROR CODE: {ErrorNode.val}")
        else: print(ErrorNode.val + self.CodeLookup[ErrorNode.val](ErrorNode.contents))
        
        if self.ExitOnThrow:
            print(f"\n[+] PROGRAM COMPLETED IN {time.time()-self.StartTime} SECONDS\n")
            try: input("PRESS [ENTER] TO VIEW STACKTRACE OR [CTRL+C] TO QUIT >")
            except KeyboardInterrupt: exit()
            
        for elem in ErrorNode.args:
            print(f"[!] {elem[0]} {elem[1]} --- {self.source[elem[0][0]:elem[0][1]]}")
        
        if self.ExitOnThrow: exit()
        return ErrorNode

########################################################################################################################
############# KYLU BUILTINS ############################################################################################
############################################################################################################
def listSub(a, b):
    a.remove(b)
    return a


def listAdd(a, b):
    a.append(b)
    return a


def product(iterable):
    result = 1
    for i in iterable: result *= i
    return result


#### CALCULATE THE DOT PRODUCT BETWEEN 2 VECTORS/MATRICES
def dot(a, b):
    height = len(a.args[0].args) if a.args[0].type == "LIST" else 1
    width = len(b.args) if b.args[0].type == "LIST" else 1
    #### a must have the same number of rows as b has columns
    if len(a.args[0].args) != len(b.args): return Node("NUMBER", 0, [])
    
    matrix = []
    for i in range(width):
        column = []
        for j in range(height):
            total = 0
            for elem in range(len(a.args)):
                rowElem = a.args[elem].args[i].val if a.args[elem].type == "LIST" else a.args[elem].val
                columnElem = b.args[j].args[elem].val if b.args[j].type == "LIST" else b.args[j].val
                total += rowElem * columnElem
            column.append(Node("NUMBER", total, ""))
        matrix.append(Node("LIST", "", [], a=column))
    
    return Node("LIST", "", [], a=matrix)  #### the resulting matrix will have dimensions [columns in a] x [rows in b]


#### FIND THE TRANSPOSE OF MATRIX OR VECTOR
def transpose(m):
    if m.type != "LIST": return Node("NUMBER", 0, [])
    if not m.args[0].args: return Node("NUMBER", 0, [])
    transposed = []
    for i in range(len(m.args[0].args)):
        transposed.append(Node("LIST", "", [], a=[m.args[j].args[i] for j in range(len(m.args))]))
    return Node("LIST", "", [], a=transposed)
            

#### FIND THE DETERMINANT OF A SQUARE MATRIX
def determinant(m):
    #### matrix must be square
    if len(m.args) != len(m.args[0].args): return Node("NUMBER", 0, [])
    if len(m.args) == 1: return m.args[0].args[0]
    #if len(m.args) == 2: return Node("NUMBER", m.args[0].args[0].val*m.args[1].args[1].val - m.args[0].args[1].val*m.args[1].args[0].val, [])
    total = 0
    for q in range(len(m.args)):
        subdet = determinant(Node("LIST", "", [], a=[Node("LIST", "", [], a=[m.args[i].args[j] for j in range(len(m.args)) if j != q]) for i in range(1, len(m.args))]))
        total += m.args[0].args[q].val * subdet.val * (2 * (q%2) - 1)
    return Node("NUMBER", total, [])


#### FIND THE ADJOINT OF A SQUARE MATRIX
def adjoint(m):
    adjugate = []
    for i in range(len(m.args)):
        column = []
        for j in range(len(m.args)):
            MatCofactor = Node("LIST", "", [], a=[Node("LIST", "", [], a=[m.args[eI].args[eJ] for eI in range(len(m.args)) if eI != i]) for eJ in range(len(m.args)) if eJ != j])
            ElemCofactor = determinant(MatCofactor).val
            column.append(Node("NUMBER", ElemCofactor * (2 * ((i+j)%2) - 1), []))
        adjugate.append(Node("LIST", "", [], a=column))
        
    result = Node("LIST", "", [], a=adjugate)
    return transpose(result)


#### FIND THE INVERSE OF A SQUARE MATRIX
def invert(m):
    det = determinant(m).val
    m = adjoint(m)
    inverse = []
    for i in range(len(m.args)):
        inverse.append(Node("LIST", "", [], a=[Node("NUMBER", m.args[i].args[j].val / det, []) for j in range(len(m.args))]))
    return Node("LIST", "", [], a=inverse)


#### RETURN ELEMENTS THAT 2 LISTS HAVE IN COMMON
def similar(a, b):
    if "LIST" not in [a.type, b.type]: return Node("ERROR", "INVALIDOPERATION", [], c=["ARRAYOPERATION", a.type, b.type])
    #### iterate over the shorter list
    match, other = (a, b) if len(a.args) < len(b.args) else (b, a)
    return Node("LIST", "", [], a=[each for each in match.args if each in other.args])


#### RETURN ELEMENTS THAT 2 LISTS DO NOT HAVE IN COMMON
def different(a, b):
    if "LIST" not in [a.type, b.type]: return Node("ERROR", "INVALIDOPERATION", [], c=["ARRAYOPERATION", a.type, b.type])
    #### iterate over the longer list to ensure all elements are checked
    match, other = (a, b) if len(a.args) > len(b.args) else (b, a)
    return Node("LIST", "", [], a=[each for each in match.args if each not in other.args])


def contains(item, array):
    if array.type != "LIST": return Node("ERROR", "INVALIDOPERATION", [], c=["ARRAYOPERATION", item.type, array.type])
    return Node("BOOL", item in array.args, [])


def toInt(number):
    try: num = int(number.val)
    except ValueError: return Node("ERROR", "INVALIDOPERATION", [], c=["TYPECONVERSION", "NUMBER", number.type])
    return Node("NUMBER", num, number.span)


def toString(literal):
    try: s = int(literal.val)
    except ValueError: return Node("ERROR", "INVALIDOPERATION", [], c=["TYPECONVERSION", "STRING", literal.type])
    return Node("NUMBER", s, literal.span)


def CurrentTime():
    return Node("NUMBER", time.time(), [])


#### RETURNS ALL ORDERED SETS BETWEEN 2 POINTS
def span(a, b, step=Node("NUMBER", 1, [])):
    if a.type == "NUMBER" and b.type == "NUMBER": return Node("LIST", "", [], a=[Node("NUMBER", i, []) for i in range(a.val, b.val, step.val)])
    
    if len(a.args) != len(b.args): return Node("NUMBER", 0, [])
    if len(a.args) == 1: return Node("LIST", "", [], a=[Node("NUMBER", i, []) for i in range(a.args[0].val, b.args[0].val, step.val)])

    result = []
    for i in range(a.args[0].val, b.args[0].val, step.val):
        for j in span(Node("LIST", "", [], a=a.args[1:]), Node("LIST", "", [], a=b.args[1:])).args:
            if j.type == "LIST": result.append(Node("LIST", "", [], a=[*j.args, Node("NUMBER", i, [])]))
            else: result.append(Node("LIST", "", [], a=[j, Node("NUMBER", i, [])]))
    return Node("LIST", "", [], a=result)


def write(*args):
    for arg in args:
        if arg.type == "STRING":
            replaceNewline = arg.val.replace("$n", "\n")
            arg = Node("STRING", replaceNewline, [])
        print(DECODE(arg), end="")
    return Node("VOID", "", [])


def prompt(prompt=Node("STRING", "", [])):
    string = input(DECODE(prompt))
    return Node("STRING", string, []) if string else Node("STRING", "", [])


def maximum(iterable):
    result = Node("NUMBER", 0, [])
    if iterable.type != "LIST": return Node("ERROR", "UNEXPECTEDTYPE", [], a=[], c=[iterable.type, "LIST"])
    for elem in iterable.args:
        if elem.type != "NUMBER": return Node("ERROR", "UNEXPECTEDTYPE", [], a=[], c=[elem.type, "NUMBER"])
        if elem.val > result.val: result = elem
        
    return result


def minimum(iterable):
    result = Node("NUMBER", 0, [])
    if iterable.type != "LIST": return Node("ERROR", "UNEXPECTEDTYPE", [], a=[], c=[iterable.type, "LIST"])
    for elem in iterable.args:
        if elem.type != "NUMBER": return Node("ERROR", "UNEXPECTEDTYPE", [], a=[], c=[elem.type, "NUMBER"])
        if elem.val < result.val: result = elem
        
    return result


#### unwrap AST for terminal output
def DECODE(tree):
    if tree.type in ["STRING", "NUMBER", "BOOL", "SYMBOL", "OPER"]: return tree.val
    elif tree.type == "ATTRIB": return tree.val.val
    elif tree.type == "LIST": return [DECODE(elem) for elem in tree.args]
    elif tree.type == "PAREN": return (DECODE(elem) for elem in tree.args)
    elif tree.type == "VOID": return "<void>"
    else: return tree


########################################################################################################################
############# PARSER: ANALYZE SYNTAX PATTERNS IN THE TOKENS ############################################################
############################################################################################################
class Parser:
    def __init__(self, code, StartTime, StopOnError):
        self.TokenRules = [
            [r"'[^']*'", "STRING"], [r'"[^"]*"', "STRING"], [r"(True|False)", "BOOL"],
            [r"[a-zA-Z][a-zA-Z0-9_]*", "SYMBOL"], [r"[0-9]+\.?[0-9]*", "NUMBER"], ["(void)", "VOID"],
            ["[\<\>\!]\=", "OPER"], ["\<\-[\=\<\>\+\-\*/\%\^]?", "OPER"], 
            ["\<[\!\:\+\^]\>", "OPER"], ["\<\![\:\+\^]\>", "OPER"], ["[\=\<\>\+\-\*/\%\^\:]", "OPER"],
            ["[^\s]", ""]
        ]
        self.priority = {
            "<=": 5, ">=": 5, "!=": 5, "<": 5, ">": 5, "=": 5,
            "<-+": 5, "<--": 5, "<-*": 5, "<-/": 5, "<-": 5,
            "+": 4, "-": 4, "*": 3, "/": 3, "%": 3, "^": 2, ":": 1,
            "<^>": 3, "<!^>": 3, "<+>": 4, "<!+>": 4, "<:>": 5, "<!:>": 5
        }
        self.SyntaxRules = {
            ("SYMBOL", "if"): self.IF, ("SYMBOL", "loop"): self.LOOP, ("SYMBOL", "obj"): self.OBJ, ("SYMBOL", "expect"): self.EXPECT,
            ("OPER", "-"): self.NEGNUM, ("OPER", "<!>"): self.NOT,
            ("", "@"): self.ATTRIB,("", "["): self.LIST, ("", "("): self.PAREN
        }
        self.idx = 0
        self.source = code + "$"
        self.TRACE = []  #### stores the current call stack for error tracing
        self.token = Node("", "", [0, 0])  #### placeholder so token isn't none when gettoken is first called
        
        self.ERRORHANDLER = ErrorHandler(StartTime, StopOnError)
        self.ERRORHANDLER.SetSource(self.source)
        self.GetToken()


    def __next__(self): return self.RunTransform()


    #### SCANNER EXTRACTS A SINGLE TOKEN FROM RAW TEXT WHEN CALLED
    def GetToken(self):
        self.idx = self.token.span[1]
        while 1:
            #### skip all space characters
            try:
                if self.source[self.idx] in [" ", "\n"]: self.idx += 1
                #### skip comments before searching for valid tokens
                elif (comment := regex.match(r"\?\?[^\n]*", self.source[self.idx:])) is not None: self.idx += len(comment.group(0))
                elif (comment := regex.match(r"\?\(.+\)\?", self.source[self.idx:])) is not None: self.idx += len(comment.group(0))
                else: break

            except IndexError: return Node("ERROR", "ENDOFFILE", [])  
            #### EOF will be handled differently depending on where GetToken was called from so it doesnt throw a unique error

        for rule in self.TokenRules:
            if (token := regex.match(rule[0], self.source[self.idx:])) is not None: break
        #### any kind of parse time error cannot be caught, it will halt the program immediately
        if token is None: return self.ERRORHANDLER.Throw(Node("ERROR", "INVALIDCHARACTER", [], a=self.TRACE, c=self.source[self.idx]) )
        
        value = token.group(0)[1:-1] if rule[1] == "STRING" else token.group(0)
        self.token = Node(rule[1], value, [self.idx, self.idx + len(token.group(0))])
        return self.token

###############################################################################
    def FIELD(self, start, stop, sep=None):
        if self.token.val != start: return
        if (t := self.GetToken()).type == "ERROR": return t
        tree = []
        while (self.token.val != stop):
            if (elem := self.RunTransform()).type == "ERROR":
                return self.ERRORHANDLER.Throw(Node("ERROR", "UNMATCHEDPAREN", [], a=self.TRACE, c=start)) if elem.val == "ENDOFFILE" else elem
            tree.append(elem)  #### parse each expression
            if sep:
                if self.token.val == stop: break
                if self.token.val != sep:
                    if (nextElement := self.RunTransform()).val == "ENDOFFILE": return self.ERRORHANDLER.Throw(Node("ERROR", "UNMATCHEDPAREN", [], a=self.TRACE, c=start))
                    else: return self.ERRORHANDLER.Throw(Node("ERROR", "MISSINGSEPERATOR", [], a=self.TRACE, c=[",", DECODE(tree[-1]), DECODE(nextElement)]))
                elif (t := self.GetToken()).type == "ERROR": return t
        if (t := self.GetToken()).type == "ERROR": return t
        return tree   


    #### CONSTRUCT ABSTRACT SYNTAX TREE FROM TOKEN STREAM WHEN CALLED
    def RunTransform(self):
        queue, stack = [], []
        while 1:
            #### expect operand 
            if self.token.type == "OPER" and self.token.val not in ["<!>", "-"]: #### unary operators have no left operand
                return self.ERRORHANDLER.Throw(Node("ERROR", "MISSINGOPERAND", [], a=self.TRACE, c=self.token.val))
            #### use syntax rules to extract syntax from token stream
            if (self.token.type, self.token.val) in self.SyntaxRules:
                self.TRACE.append([self.token.span, self.token.type])
                elem = self.SyntaxRules[(self.token.type, self.token.val)]()
                self.TRACE.pop()
                if elem.type == "ERROR": return elem
            else:
                elem = self.token
                if (t := self.GetToken()).type == "ERROR": return t
            #### all valid expressions are callable by default 
            if self.token.val == "(":
                if isinstance(args := self.FIELD("(", ")", ","), Node): return args
                elem = Node("CALL", "", [elem.span[0], self.idx], a=args, c=elem)

            #### expect operator
            queue.append(elem)
            if self.token.type != "OPER": break
           
            #### convert operator to postfix notation via shunting yard algorithm
            if not stack: stack.append(self.token)  #### add the first operator
            #### operators with higher precedence (lower number in self.priority) will be reduced into a tree first (last element on the stach)
            elif self.priority[self.token.val] < self.priority[stack[-1].val]: stack.append(self.token)
            #### operators with lower precedence (higher number) than the operator before them cannot be reduced before the previous operator
            #### so the previous operator must be reduced before the new one can be added
            elif self.priority[self.token.val] >= self.priority[stack[-1].val]:
                #### perform ShiftReduce to convert final 2 queue elements and last stack element to an operator node
                queue = queue[:-2] + [Node("OPEREXPR", stack[-1], [queue[-2].span[0], queue[-1].span[1]], a=[queue[-2], queue[-1]])]
                stack.pop()
                stack.append(self.token)

            operator = self.token.val
            if (t := self.GetToken()).type == "ERROR": return t
            if self.token.type in ["", "OPER"] and (self.token.type, self.token.val) not in self.SyntaxRules: return self.ERRORHANDLER.Throw(Node("ERROR", "MISSINGOPERAND", [], a=self.TRACE, c=operator))
            #### if the spot where the next operand should be has another operator or a misc character the operand must be missing
        
        #### reduce any remaining operators in reverse order (higher precedence operators will always be at the end of the stack)
        for operator in stack[::-1]:
            queue = queue[:-2] + [Node("OPEREXPR", operator, [queue[-2].span[0], queue[-1].span[1]], a=[queue[-2], queue[-1]])]
        return queue[0]


###############################################################################
    def IF(self):
        initIDX = self.idx
        pairs = []
        while self.token.val == "if":
            if (t := self.GetToken()).type == "ERROR": return t

            if isinstance(condition := self.FIELD("(", ")"), Node): return condition
            if len(condition) != 1: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["IF", "EXPRESSION REQUIRES 1 CONDITION IN THE FIRST FIELD"]))
            if isinstance(action := self.FIELD("{", "}"), Node): return action
            if len(action) == 0: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["IF", "ACTION IF TRUE BLOCK CANNOT BE EMPTY"]))
            pair = [*condition, action]

            if self.token.val == "{":  #### else statement
                if isinstance(elseStmnt := self.FIELD("{", "}"), Node): return elseStmnt
                if len(elseStmnt) == 0: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["IF", "ACTION IF FALSE BLOCK CANNOT BE EMPTY"]))
                pair.append(elseStmnt)
                pairs.append(pair)
                return Node("IF", Node("SYMBOL", "IF", []), [initIDX, self.idx], c=pairs)

            elif self.token.val == ",":  #### elif statement
                pairs.append(pair)
                if (t := self.GetToken()).type == "ERROR": return t

            else: return Node("IF", Node("SYMBOL", "IF", []), [initIDX, self.idx], c=pairs + [pair])


    def LOOP(self):
        initIDX = self.idx
        if (t := self.GetToken()).type == "ERROR": return t
        LoopType = self.token
        if (t := self.GetToken()).type == "ERROR": return t

        if LoopType.val == "iter":
            conditions = []
            while self.token.val == "(":
                if isinstance(iterator := self.FIELD("(", ")", ","), Node): return iterator
                if len(iterator) != 2: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["LOOP", "EXPRESSION REQUIRES 1 ITERATOR AND 1 INDEX IN THE FIRST FIELD"]))
                conditions.append(iterator)
       
        elif LoopType.val == "cond":
            if isinstance(conditions := self.FIELD("(", ")"), Node): return conditions
            if len(conditions) != 1: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["LOOP", "EXPRESSION REQUIRES 1 CONDITION IN THE FIRST FIELD"]))
            
        else: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["LOOP", f"INVALID LOOP TYPE {LoopType.val}"]))

        if isinstance(action := self.FIELD("{", "}"), Node): return action
        if len(action) == 0: return self.ERRORHANDLER.Throw(Node("ERROR", "RESOLUTIONFAILURE", [], a=self.TRACE, c=["LOOP", "REPEATED ACTION BLOCK CANNOT BE EMPTY"]))
        return Node("LOOP", LoopType, [initIDX, action[-1].span[1] + 1], a=conditions, c=action)


    def LIST(self):
        initIDX = self.idx
        if isinstance(args := self.FIELD("[", "]", ","), Node): return args
        return Node("LIST", "", [initIDX, self.idx], a=args)


    def PAREN(self):
        initIDX = self.idx
        if isinstance(args := self.FIELD("(", ")"), Node): return args
        return Node("PAREN", "", [initIDX, self.idx], a=args)


    def OBJ(self):
        initIDX = self.idx
        if (t := self.GetToken()).type == "ERROR": return t
        if isinstance(args := self.FIELD("(", ")", ","), Node): return args
        if isinstance(contents := self.FIELD("{", "}"), Node): return contents
        return Node("OBJECT", "", [initIDX, self.idx], a=args, c=contents)
    
    
    def EXPECT(self):
        initIDX = self.idx
        if (t := self.GetToken()).type == "ERROR": return t
        if isinstance(args := self.FIELD("(", ")", ","), Node): return args
        if isinstance(contents := self.FIELD("{", "}"), Node): return contents
        return Node("EXPECT", "", [initIDX, self.idx], a=args, c=contents)


    def ATTRIB(self):
        if (t := self.GetToken()).type == "ERROR": return t
        token = self.token
        if (t := self.GetToken()).type == "ERROR": return t
        return Node("ATTRIB", token, [token.span[0]-1, self.idx])

   
    def NEGNUM(self):
        if (t := self.GetToken()).type == "ERROR": return t
        token = self.token
        if (t := self.GetToken()).type == "ERROR": return t
        return Node("NUMBER", 0-float(token.val), [token.span[0]-1, token.span[1]])


    def NOT(self):
        if (t := self.GetToken()).type == "ERROR": return t
        elem = self.RunTransform()
        return Node("OPEREXPR", Node("OPER", "<!>", []), [elem.span[0]-3, self.idx], a=[elem, Node("BOOL", "", [])])



########################################################################################################################
############# INTERPRETER: RUN THE CODE ################################################################################
############################################################################################################
class Interpreter:
    def __init__(self, StartTime, StopOnError):
        self.EvalRules = {
            "IF": lambda tree: self.IF(tree),
            "LOOP": lambda tree: self.LOOP(tree),
            "PAREN": lambda tree: self.RUN(tree.args[0]),
            "CALL": lambda tree: self.CALL(tree),
            "OPEREXPR": lambda tree: self.OPER(tree),
            "ATTRIB": lambda tree: self.GETVAR(tree.val.val, -2),
            "SYMBOL": lambda tree: self.GETVAR(tree.val, -1),
            "LIST": lambda tree: Node("LIST", "", tree.span, a=[self.RUN(elem) for elem in tree.args]),
        }
        #### static methods that don't require access to other data in the interpreter
        self.STANDARDLIB = {
            "det": determinant, "dot": dot, "inverse": invert, "similar": similar, "different": different, "prompt": prompt,
            "write": write, "span": span, "in": contains, "toInt": toInt, "toString": toString, "CurrentTime": CurrentTime,
            "max": maximum, "min": minimum, "T": transpose, "adj": adjoint,
            
            "len": lambda tree: Node("NUMBER", len(DECODE(tree)), []),
            "out": lambda tree: Node("ERROR", "STOPFUNCTION", [], a=tuple(self.TRACE), c=[self.RUN(tree) if tree else Node("VOID", "", [])]),
            "stop": lambda: Node("ERROR", "STOPITERATION", [], a=tuple(self.TRACE)),
            "reset": lambda: Node("ERROR", "RESETITERATION", [], a=tuple(self.TRACE)),
            "Error": lambda *args: Node("ERROR", args[0].val, [], a=tuple(self.TRACE), c=[DECODE(arg) for arg in args[1:]])
        }
        self.MethodLookup = {
            "+": "ADD", "-": "SUBTRACT", 
            "*": "MULTIPLY",  "/": "DIVIDE",
            "%": "MODULUS", ">": "GREATER", "<": "LESS"
        }
        self.OperTable = {
            "+": {
                ("NUMBER", "NUMBER"): lambda a, b: Node("NUMBER", a.val + b.val, []),
                ("STRING", "STRING"): lambda a, b: Node("STRING", a.val + b.val, []),
                ("LIST", "STRING"): lambda a, b: Node("LIST", "", [], a=listAdd(a.args, b)),
                ("LIST", "NUMBER"): lambda a, b: Node("LIST", "", [], a=listAdd(a.args, b)),
                ("LIST", "LIST"): lambda a, b: Node("LIST", "", [], a=listAdd(a.args, b))
            },
            "-": {
                ("NUMBER", "NUMBER"): lambda a, b: Node("NUMBER", a.val - b.val, []),
                ("LIST", "STRING"): lambda a, b: Node("LIST", "", a.span, a=listSub(a.args, b)),
                ("LIST", "NUMBER"): lambda a, b: Node("LIST", "", a.span, a=listSub(a.args, b))
            },
            "*": {
                ("NUMBER", "NUMBER"): lambda a, b: Node("NUMBER", a.val * b.val, []),
                ("NUMBER", "STRING"): lambda a, b: Node("STRING", a.val * b.val, []),
            },
            "=": {
                ("NUMBER", "NUMBER"): lambda a, b: Node("BOOL", a.val == b.val, []),
                ("STRING", "STRING"): lambda a, b: Node("BOOL", a.val == b.val, []),
                ("LIST", "LIST"): lambda a, b: Node("BOOL", a.args == b.args, [])
            },
            "!=":{
                ("NUMBER", "NUMBER"): lambda a, b: Node("BOOL", a.val != b.val, []),
                ("STRING", "STRING"): lambda a, b: Node("BOOL", a.val != b.val, []),
                ("LIST", "LIST"): lambda a, b: Node("BOOL", a.args != b.args, []),
                ("BOOL", "BOOL"): lambda a, b: Node("BOOL", a.args != b.args, []),
            },
            "/": {("NUMBER", "NUMBER"): lambda a, b: Node("NUMBER", a.val / b.val, [])},
            "%": {("NUMBER", "NUMBER"): lambda a, b: Node("NUMBER", a.val % b.val, [])},
            "^": {("NUMBER", "NUMBER"): lambda a, b: Node("NUMBER", a.val ** b.val, [])},
            ">": {("NUMBER", "NUMBER"): lambda a, b: Node("BOOL", a.val > b.val, [])},
            "<": {("NUMBER", "NUMBER"): lambda a, b: Node("BOOL", a.val < b.val, [])},
            ">=": {("NUMBER", "NUMBER"): lambda a, b: Node("BOOL", a.val >= b.val, [])},
            "<=": {("NUMBER", "NUMBER"): lambda a, b: Node("BOOL", a.val <= b.val, [])},
            "<:>": {("BOOL", "BOOL"): lambda a, b: Node("BOOL", a.val or b.val, [])},
            "<+>":{("BOOL", "BOOL"): lambda a, b: Node("BOOL", a.val and b.val, [])},
            "<^>": {("BOOL", "BOOL"): lambda a, b: Node("BOOL", a.val ^ b.val, [])},
            "<!>": {("BOOL", "BOOL"): lambda a, b: Node("BOOL", not a.val, [])},
            "<!:>": {("BOOL", "BOOL"): lambda a, b: Node("BOOL", not (a.val or b.val), [])},
            "<!+>": {("BOOL", "BOOL"): lambda a, b: Node("BOOL", not (a.val and b.val), [])},
            "<!^>": {("BOOL", "BOOL"): lambda a, b: Node("BOOL", not (a.val ^ b.val), [])},
        }
        self.StartTime = StartTime
        self.StopOnError = StopOnError
        self.ERRORHANDLER = ErrorHandler(StartTime, StopOnError)
        self.TRACE = []
        
        self.IMPORTED = {}  #### stores each imported file as an object instance
        self.OBJECTTREE = [{}]  #### stores namespace tree data, each namespace is a map from var names to values


    def RUN(self, tree):
        if tree.type in self.EvalRules:
            self.TRACE.append([tree.span, tree.type])
            elem = self.EvalRules[tree.type](tree)
            self.TRACE.pop()
            return elem
        return tree


    def GETVAR(self, name, depth):
        #### tuples are immutable after creation, so they can't be passed to Node by reference
        if 0-depth > len(self.OBJECTTREE): return Node("ERROR", "INVALIDNAMESPACE", [], a=tuple(self.TRACE), c="")
        if name not in self.OBJECTTREE[depth]: return Node("ERROR", "NULLREFERENCE", [], a=tuple(self.TRACE), c=name)
        return self.OBJECTTREE[depth][name]
    
    
    def SETVAR(self, name, value, depth):
        if 0-depth > len(self.OBJECTTREE): return Node("ERROR", "INVALIDNAMESPACE", [], a=tuple(self.TRACE), c="")
        self.OBJECTTREE[depth].update({name: value})
        return value


    #### take in a list tree (array) and replace the element at the path (index) with the value (value)
    def update(self, array, value, index):
        new = array.args
        try:
            if index.type == "NUMBER": new[index.val] = value 
            if index.type == "LIST":
                if len(index.args) == 1: new[index.args[0].val] = value 
                else: new[index.args[0].val] = self.update(array.args[index.args[0].val], value, Node("LIST", "", [], a=index.args[1:]))
        except IndexError: return Node("ERROR", "INDEXERROR", [], a=tuple(self.TRACE), c=[index.args[0].val, DECODE(array)])
        return Node("LIST", "", array.span, a=new)

    
    #### unwrap nested get expression to find source list and list index to be replaced, then run self.update
    def updateFromTree(self, indexExpr, value, path):
        if indexExpr.type == "OPEREXPR": return self.updateFromTree(indexExpr.args[0], value, path + [self.RUN(indexExpr.args[1].args[0])])
        else: return self.update(self.RUN(indexExpr), value, Node("LIST", "", [], a=path[::-1]))


    ###########################################################################
    def OPER(self, tree):
        if tree.val.val == '<-':
            #### variables can only be initialized using symbols or the attribute operator
            if tree.args[0].type == "SYMBOL": return self.SETVAR(tree.args[0].val, self.RUN(tree.args[1]), -1)
            elif tree.args[0].type == "ATTRIB": return self.SETVAR(tree.args[0].val.val, self.RUN(tree.args[1]), -2)
            elif tree.args[0].type == "OPEREXPR":
                if tree.args[0].args[1].type == "LIST": return self.updateFromTree(tree.args[0], self.RUN(tree.args[1]), [])
                if tree.args[0].args[1].type == "SYMBOL": return self.GETVAR(tree.args[0].args[0].val, -1).update({tree.args[0].args[1].val: self.RUN(tree.args[1])})
            else: return Node("ERROR", "NOTASSIGNABLE", [], a=tuple(self.TRACE), c=tree.args[0])

        elif tree.val.val == ':':
            Object = self.RUN(tree.args[0])  #### get object to modify
            
            if tree.args[1].type == "EXPECT":
                #### run the code in the action block of the expect statement if the object's value matches the specified error type, otherwise return the object
                if Object.type == "ERROR" and Object.val == tree.args[1].args[0].val:
                    for line in tree.args[1].contents:
                        if (item := self.RUN(line)).type == "ERROR": break
                    return item
                else: return Object  #### statements can be chained to catch multiple error types
            
            elif Object.type == "ERROR": return Object
            
            elif tree.args[1].val == "type": return Node("STRING", tree.args[1].type, [])
            
            elif tree.args[1].type == "LIST":
                if len(tree.args[1].args) > 1:
                    #### take a set of elements (slice) from the source list including the stop index
                    try: newList = Object.args[self.RUN(tree.args[1].args[0]).val : self.RUN(tree.args[1].args[1]).val+1 : self.RUN(tree.args[1].args[2]).val]
                    except IndexError: return Node("ERROR", "INDEXERROR", [], a=tuple(self.TRACE), c=[tree.args[1].args[1].val, DECODE(Object)])
                    return Node("LIST", "", tree.span, a=newList)
                
                if (index := self.RUN(tree.args[1].args[0])).type != "NUMBER": return Node("ERROR", "UNEXPECTEDTYPE", [], a=tuple(self.TRACE), c=[index.type, "NUMBER"])
                try: return Object.args[index.val]
                except IndexError: return Node("ERROR", "INDEXERROR", [], a=tuple(self.TRACE), c=[tree.args[1].args[0].val, DECODE(Object)])
            
            elif tree.args[1].type == "CALL":
                if Object.type != "OBJINST": return Node("ERROR", "INVALIDOPERATION", [], a=tuple(self.TRACE), c=[tree.val.val, Object.type, tree.args[1].type])
                #### evaluate arguments and read into new namespace, extract target object, then load imported objects 
                self.OBJECTTREE.append({**{elem.val: self.RUN(elem) for elem in tree.args[1].args}, **Object.contents, **self.IMPORTED})
                result = self.CALL(tree.args[1]) #### evaluate function
                self.OBJECTTREE.pop()
                return result
            
            elif tree.args[1].type == "SYMBOL":
                if tree.args[1].val not in Object.contents: return Node("ERROR", "NULLREFERENCE", [], a=tuple(self.TRACE), c=tree.args[1].val)
                return Object.contents[tree.args[1].val]
            
            else: return Node("ERROR", "INVALIDOPERATION", [], a=tuple(self.TRACE), c=[tree.val.val, tree.args[0].type, tree.args[1].type])

        elif tree.val.val[:2] == '<-':
            val = self.BinOpExec(Node("OPEREXPR", Node("OPER", tree.val.val[2:], []), tree.span, a=tree.args))
            self.OPER(Node("OPEREXPR", Node("OPER", "<-", []), tree.span, a=[tree.args[0], val]))
            return val
        
        else: return self.BinOpExec(tree)


    def BinOpExec(self, tree):
        if (a := self.RUN(tree.args[0])).type == "ERROR": return a
        if (b := self.RUN(tree.args[1])).type == "ERROR": return b
        
        #### generate tree that would be parsed from a:OPERATION(b)
        if a.type == "OBJINST":
            return self.OPER(Node("OPEREXPR", Node("OPER", ":", []), [], a=[a, Node("CALL", "", [], a=b, c=self.CodeLookup[tree.val.val])]))  
        if b.type == "OBJINST":
            return self.OPER(Node("OPEREXPR", Node("OPER", ":", []), [], a=[b, Node("CALL", "", [], a=a, c=self.CodeLookup[tree.val.val])]))
        
        try: func = self.OperTable[tree.val.val][tuple(sorted((a.type, b.type)))]  #### get node template from lookup table
        except KeyError: return Node("ERROR", "INVALIDOPERATION", [], a=tuple(self.TRACE), c=[tree.val.val, a.type, b.type])
        
        try: return func(a, b)  #### run specified arithmetic/ logic operation and return the resulting node
        except Exception as e:
           print(f"WARNING: BINARY OPERATION: {tree.val.val} THREW AN UNCAUGHT EXCEPTION: {e}")
           return Node("ERROR", "PYTHONERROR", [], a=tuple(self.TRACE), c=e)


    def CALL(self, tree):
        #### Interpreter entry point for external static methods
        if str(tree.contents.val) in self.STANDARDLIB:  #### ensure self.STANDARDLIB is compared with a string
            funcArgs = []
            for arg in tree.args:  #### cancel function execution if an argument created an error
                if (ArgResult := self.RUN(arg)).type == "ERROR": return ArgResult
                else: funcArgs.append(ArgResult)
            
            try: return self.STANDARDLIB[tree.contents.val](*funcArgs)
            except Exception as e:
                print(f"WARNING: USER DEFINED FUNCTION: {tree.contents.val} THREW AN UNCAUGHT EXCEPTION: {e}")
                return Node("ERROR", "PYTHONERROR", [], a=tuple(self.TRACE), c=e)
            

        #### system builtin functions that require access to the parser/ other data in the interpreter
        elif str(tree.contents.val) == "ext":
            #### evaluate file and extract variable cache
            External = EVALFile(f"{tree.args[0].val}.kylu", self.StartTime)
            #### add file object to imported log and base namespace
            self.IMPORTED.update({tree.args[0].val: Node("OBJINST", "", [], c=External.OBJECTTREE[0])})
            self.SETVAR(tree.args[0].val, Node("OBJINST", "", [], c=External.OBJECTTREE[0]), 0)
            return Node("VOID", "", [])
            
        elif str(tree.contents.val) == "del":
            if tree.args[0].type == "SYMBOL":
                self.GETVAR(tree.args[0].val, -1)  #### confirm target object is valid, value not used in del operation
                del self.OBJECTTREE[-1][tree.args[0].val]
            if tree.args[0].type == "ATTRIB":
                self.GETVAR(tree.args[0].val.val, -2)
                del self.OBJECTTREE[-2][tree.args[0].val.val]
            return Node("VOID", "", [])

        elif str(tree.contents.val) == "monad":
            BindFunc = Parser("obj(func){ @val <- func(@val) out(@self(@val, @self)) }", time.time(), self.StopOnError).RunTransform()
            SelfObj = Parser("obj(val, self){ bind <- obj(func){@val <- func(@val) out(@self(@val, @self)) }}", time.time(), self.StopOnError).RunTransform()
            return Node("OBJINST", "", tree.span, c={"self": SelfObj, "val": tree.args[0], "bind": BindFunc})
        
        elif str(tree.contents.val) == "update":
            #### assign the updated list from self.update to the input list
            if (array := self.RUN(tree.args[0])).type != "LIST": return Node("ERROR", "UNEXPECTEDTYPE", [], a=tuple(self.TRACE), c=[array.type, "LIST"])
            if (index := self.RUN(tree.args[2])).type not in ["LIST", "NUMBER"]: return Node("ERROR", "UNEXPECTEDTYPE", [], a=tuple(self.TRACE), c=[index.type, "LIST or NUMBER"])
            if tree.args[0].type in ["SYMBOL", "ATTRIB"]: return self.update(array, self.RUN(tree.args[1]), index)
            return Node("VOID", "", [])
        
        elif str(tree.contents.val) == "filter":
            output = []
            for elem in tree.args[0].args:  #### if func(iter:[i]) returns True, add it to the output
                if(include := self.CALL(Node("CALL", "", [], a=[tree.args[0]], c=tree.args[1]))).type == "ERROR": return include
                if include.type != "BOOL": return Node("ERROR", "UNEXPECTEDTYPE", [], a=tuple(self.TRACE), c=[include.type, "BOOL"])
                if(include.val): output.append(elem)
            return Node("LIST", "", [], a=output)


        #### functions defined programmatically from within the source code
        if (func := self.RUN(tree.contents)).type == "ERROR": return func
        if func.type != "OBJECT": return Node("ERROR", "NOTCALLABLE", [], a=tuple(self.TRACE), c=DECODE(tree.contents))
        if len(func.args) != len(tree.args): return Node("ERROR", "ARGMISMATCH", [], a=tuple(self.TRACE), c=[len(func.args), len(tree.args)])
        
        #### build namespace from input arguments and tree object data, then load imported variables into namespace and import the function itself
        self.OBJECTTREE.append({**{func.args[arg].val: self.RUN(tree.args[arg]) for arg in range(len(func.args))}, **self.IMPORTED, DECODE(tree.contents): func})
        
        #### If a call to a sub object occurs inside another sub object
        #### the called object needs access to the properties of the outer object
        if tree.contents.type == "ATTRIB":
            currentNS = self.OBJECTTREE[-2]
            self.OBJECTTREE[-2] = self.OBJECTTREE[-3]
        #### evaluate function line by line until code ends or "out" function is called
        for line in func.contents:
            if (obj := self.RUN(line)).type == "ERROR":
                if obj.val == "STOPFUNCTION": obj = obj.contents[0]
                break
        else: obj = Node("OBJINST", "", [], c=self.OBJECTTREE[-1])
        
        if tree.contents.type == "ATTRIB": self.OBJECTTREE[-2] = currentNS
        self.OBJECTTREE.pop()
        return obj

    ###########################################################################
    def IF(self, tree):
        for IfStat in tree.contents:
            if (Cond := self.RUN(IfStat[0])).type == "ERROR": return Cond
            if Cond.type != "BOOL": return Node("ERROR", "UNEXPECTEDTYPE", [], a=tuple(self.TRACE), c=[Cond.type, "BOOL"])
    
            if Cond.val: targetField = IfStat[1]
            elif len(IfStat) == 3: targetField = IfStat[2]
            else: continue
            for line in targetField:
                if (item := self.RUN(line)).type == "ERROR": break
            return item

        else: return Node("VOID", "", [])


    def LOOP(self, tree):
        listComp = []
        if tree.val.val == "cond":
            if (CondType := self.RUN(tree.args[0])).type == "ERROR": return CondType
            if CondType.type != "BOOL": return Node("ERROR", "UNEXPECTEDTYPE", [], a=tuple(self.TRACE), c=[CondType.type, "BOOL"])
            
            while self.RUN(tree.args[0]).val:
                for line in tree.contents:
                    if (item := self.RUN(line)).type == "ERROR":
                        if item.val == "RESETITERATION": break
                        return Node("LIST", "", tree.span, a=listComp) if item.val == "STOPITERATION" else item
                    listComp.append(item)
            return Node("LIST", "", tree.span, a=listComp)
       
        if tree.val.val == "iter":
            if (Iterator := self.RUN(tree.args[0][1])).type == "ERROR": return Iterator
            if Iterator.type != "LIST": return Node("ERROR", "NOTITERABLE", [], a=tuple(self.TRACE), c=Iterator)
            
            for elem in Iterator.args:
                self.OBJECTTREE[-1].update({tree.args[0][0].val: elem})  #### update iterator value
                if len(tree.args) > 1:
                    listComp.append(self.LOOP(Node("LOOP", Node("SYMBOL", "iter", []), [], a=tree.args[1:], c=tree.contents)))
                else:
                    for line in tree.contents:  #### run each line in the contents of the loop
                        if (item := self.RUN(line)).type == "ERROR":
                            if item.val == "RESETITERATION": break
                            return Node("LIST", "", tree.span, a=listComp) if item.val == "STOPITERATION" else item
                        listComp.append(item)
            return Node("LIST", "", tree.span, a=listComp)


###############################################################################
def EVALFile(file, startTime):
        I = Interpreter(startTime, True)
        
        try: SOURCEFILE = open(file, 'r').read()
        except FileNotFoundError: I.ERRORHANDLER.Throw(Node("ERROR", "FILENOTFOUND", [], a=[], c=file))
        
        I.ERRORHANDLER.SetSource(SOURCEFILE)
        parser = Parser(SOURCEFILE, time.time(), True)
        try: 
            while parser.token.val != "$":
                if (tree := next(parser)).type == "ERROR": return tree
                if (result := I.RUN(tree)).type == "ERROR": I.ERRORHANDLER.Throw(result)
        except KeyboardInterrupt:
            print("\n[!] PROGRAM STOPPED")
            print(f"\n[+] PROGRAM: {file} COMPLETED IN {time.time()-startTime} SECONDS")
        return I


def Terminal():
    print(
    r"""
                                              _---___
                                         __  /       \
                                        /  \ \       / __
    KYLU PROJECT TERMINAL              /___| |______/ /  \
    release build alpha 1.7             ___| |______ |   |
                                       \   | |      \ \__/
    Azhaoli c2024                       \__/ /       \
                                             \_    __/
                                                ~~~
    """)
    StartTime = time.time()
    I = Interpreter(StartTime, False)
    while 1:
        try: code = input("\n(kylu)-> ")
        except KeyboardInterrupt:
            print("\n[!] PROGRAM STOPPED")
            exit()
        if code == "": continue
        if code == "/exit":
            print("\n[!] PROGRAM STOPPED")
            exit()
        if code == "/kyedit":
            append, code = "", ""
            while append != "/done":
                code = code + append
                append = input(">")  #### need to check for status command before input is added

        I.ERRORHANDLER.SetSource(code)
        if (tree := Parser(code, time.time(), False).RunTransform()).type == "ERROR": continue
        if (result := I.RUN(tree)).type == "ERROR": I.ERRORHANDLER.Throw(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interpreter for .kylu language files")
    parser.add_argument("--file", type=str, required=False, help="File to be read and executed")
    args = parser.parse_args()
    if not args.file: Terminal()
 
    EVALFile(args.file, time.time())
