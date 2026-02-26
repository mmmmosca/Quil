import sys

TOKENS = [
    "LCURLY",
    "RCURLY",
    "LSQUARE",
    "RSQUARE",
    "PLUS",
    "MINUS",
    "OUT_NUMBER",
    "OUT_CHAR",
    "INPUT",
    "ASSIGN",
    "EXIT",
    "BREAK_LOOP",
    "EOL",
    "NUMBER",
    "VAR"
]

class Lexer:
    def __init__(self, line):
        self.line = line
    
    def tokenize(self):
        tokens = []
        i = 0
        l = len(self.line)
        while i < l:
            if self.line[i] == "{":
                tokens.append(TOKENS[0])
                i += 1
            elif self.line[i] == "}":
                tokens.append(TOKENS[1])
                i += 1
            elif self.line[i] == "[":
                tokens.append(TOKENS[2])
                i += 1
            elif self.line[i] == "]":
                tokens.append(TOKENS[3])
                i += 1
            elif self.line[i] == "+":
                tokens.append(TOKENS[4])
                i += 1
            elif self.line[i] == "-":
                next = self.line[i+1]
                if next.isdigit():
                    negative_number = "-"
                    j = i+1
                    while j < l and self.line[j].isdigit():
                        negative_number += self.line[j]
                        j += 1
                    tokens.append({TOKENS[-2]: int(negative_number)})
                    i = j
                else:
                    tokens.append(TOKENS[5])
                    i += 1
            elif self.line[i] == "%":
                tokens.append(TOKENS[6])
                i += 1
            elif self.line[i] == "!":
                tokens.append(TOKENS[7])
                i += 1
            elif self.line[i] == "?":
                tokens.append(TOKENS[8])
                i += 1
            elif self.line[i] == "=":
                tokens.append(TOKENS[9])
                i += 1
            elif self.line[i] == ";":
                tokens.append(TOKENS[10])
                i += 1
            elif self.line[i] == "&":
                tokens.append(TOKENS[11])
                i += 1
            elif self.line[i].isdigit():
                j = i
                while j < l and self.line[j].isdigit():
                    j += 1
                tokens.append({TOKENS[-2]: int(self.line[i:j])})
                i = j
            elif self.line[i].isalpha() or self.line[i] == "_":
                j = i
                while j < l and (self.line[j].isalnum() or self.line[j] == "_"):
                    j += 1
                tokens.append({TOKENS[-1]: self.line[i:j]})
                i = j
            elif self.line[i].isspace():
                i += 1
            else: i += 1
        tokens.append(TOKENS[12])
        return tokens



class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.counter = 0
        self.vars = {}

    def _find_block_end(self, start, open_token, close_token):
        j = start + 1
        depth = 1
        l = len(self.tokens)
        while j < l and depth > 0:
            if self.tokens[j] == open_token:
                depth += 1
            elif self.tokens[j] == close_token:
                depth -= 1
            j += 1

        if depth != 0:
            raise Exception("Unterminated loop")
        return j

    def _execute_range(self, start, end):
        i = start
        pending_number = None

        while i < end:
            tok = self.tokens[i]

            if tok == TOKENS[12]:
                pending_number = None
                i += 1
                continue

            if isinstance(tok, dict) and TOKENS[-2] in tok:
                next_tok = self.tokens[i + 1] if i + 1 < end else None
                if next_tok in (TOKENS[0], TOKENS[2]):
                    pending_number = tok[TOKENS[-2]]
                else:
                    self.counter = tok[TOKENS[-2]]
                i += 1
                continue
            
            if pending_number is not None and tok not in (TOKENS[0], TOKENS[2]):
                raise Exception("Number must be followed by '{' or '['")
            
            if isinstance(tok, dict) and TOKENS[-1] in tok:
                var_name = tok[TOKENS[-1]]
                next_tok = self.tokens[i + 1] if i + 1 < end else None

                if next_tok == TOKENS[9]:
                    self.vars[var_name] = self.counter
                    i += 2
                    continue

                if next_tok in (TOKENS[0], TOKENS[2]):
                    pending_number = self.vars.get(var_name, 0)
                else:
                    self.counter = self.vars.get(var_name, 0)
                i += 1
                continue

            if tok == TOKENS[0]:
                if pending_number is None:
                    j = self._find_block_end(i, TOKENS[0], TOKENS[1])
                    while True:
                        broke = self._execute_range(i + 1, j - 1)
                        if broke:
                            break
                    i = j
                    continue
                target = pending_number
                pending_number = None
                j = self._find_block_end(i, TOKENS[0], TOKENS[1])
                while self.counter != target:
                    broke = self._execute_range(i + 1, j - 1)
                    if broke:
                        break
                i = j
                continue

            if tok == TOKENS[2]:
                if pending_number is None:
                    raise Exception("Missing number before '['")
                target = pending_number
                pending_number = None
                j = self._find_block_end(i, TOKENS[2], TOKENS[3])
                if self.counter == target:
                    broke = self._execute_range(i + 1, j - 1)
                    if broke:
                        return True
                i = j
                continue

            if tok == TOKENS[4]:
                self.counter += 1
            elif tok == TOKENS[5]:
                self.counter -= 1
            elif tok == TOKENS[6]:
                print(self.counter, end='')
            elif tok == TOKENS[7]:
                print(chr(self.counter), end='')
            elif tok == TOKENS[8]:
                self.counter = int(input())
            elif tok == TOKENS[10]:
                exit(0)
            elif tok == TOKENS[11]:
                return True
            elif tok in (TOKENS[1], TOKENS[3]):
                raise Exception(f"Unexpected closing token: {tok}")
            else:
                raise Exception(f"Unknown token: {tok}")
            i += 1
    
    def printAST(self):
        indent = ""
        i = 0
        l = len(self.tokens)
        while i < l:
            tok = self.tokens[i]
            next_tok = self.tokens[i+1] if i+1 < l else None
            print(indent+str(tok)) if tok != TOKENS[12] else None
            if next_tok in (TOKENS[1], TOKENS[3]):
                indent = indent[:-1]
            elif tok in (TOKENS[0], TOKENS[2]):
                indent += "\t"
            i += 1

    def parse(self):
        broke = self._execute_range(0, len(self.tokens))
        if broke:
            raise Exception("BREAK_LOOP used outside a loop")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nusage: python3 interpreter.py your_file [--ast: to print the ast]\n")
        exit(0)
    with open(sys.argv[1],"r") as code:
        tokens = []
        for line in code:
            lexer = Lexer(line)
            tokens += lexer.tokenize()
        parser = Parser(tokens)
        try:
            if sys.argv[2] == "--ast":
                parser.printAST()
        except:
            parser.parse()
