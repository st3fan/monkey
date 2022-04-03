from monkey.token import Token, TokenType, lookup_ident


class Lexer:
    def __init__(self, input):
        self.input = input
        self.position = 0
        self.read_position = 0
        self.ch = None # TODO Does Python not have a single character type?
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = None
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        if self.read_position < len(self.input):
            return self.input[self.read_position]

    def read_identifier(self) -> str:
        position = self.position
        while self.ch is not None and self.ch.isalpha():
            self.read_char()
        return self.input[position:self.position]

    def read_number(self) -> str:
        position = self.position
        while self.ch is not None and self.ch.isdigit():
            self.read_char()
        return self.input[position:self.position]

    def skip_whitespace(self):
        while self.ch is not None and self.ch.isspace():
            self.read_char()

    def next_token(self) -> Token:
        if self.ch is not None and self.ch.isspace():
            self.skip_whitespace()

        if self.ch is not None and self.ch.isalpha():
            ident = self.read_identifier()
            return Token(lookup_ident(ident), ident)

        if self.ch is not None and self.ch.isdigit():
            return Token(TokenType.INT, self.read_number())
        
        match self.ch:
            case "=":
                if self.peek_char() == "=":
                    self.read_char()
                    tok = Token(TokenType.EQ, "==")
                else:
                    tok = Token(TokenType.ASSIGN, self.ch)
            case TokenType.SEMICOLON.value:
                tok = Token(TokenType.SEMICOLON, self.ch)
            case TokenType.LPAREN.value:
                tok = Token(TokenType.LPAREN, self.ch)
            case TokenType.RPAREN.value:
                tok = Token(TokenType.RPAREN, self.ch)
            case TokenType.LBRACE.value:
                tok = Token(TokenType.LBRACE, self.ch)
            case TokenType.RBRACE.value:
                tok = Token(TokenType.RBRACE, self.ch)
            case TokenType.COMMA.value:
                tok = Token(TokenType.COMMA, self.ch)
            case TokenType.PLUS.value:
                tok = Token(TokenType.PLUS, self.ch)
            case "!":
                if self.peek_char() == "=":
                    self.read_char()
                    tok = Token(TokenType.NOT_EQ, "!=")
                else: 
                    tok = Token(TokenType.BANG, self.ch)
            case TokenType.SLASH.value:
                tok = Token(TokenType.SLASH, self.ch)
            case TokenType.ASTERISK.value:
                tok = Token(TokenType.ASTERISK, self.ch)
            case TokenType.LT.value:
                tok = Token(TokenType.LT, self.ch)
            case TokenType.GT.value:
                tok = Token(TokenType.GT, self.ch)
            case TokenType.PLUS.value:
                tok = Token(TokenType.PLUS, self.ch)
            case TokenType.MINUS.value:
                tok = Token(TokenType.MINUS, self.ch)
            case None:
                tok = Token(TokenType.EOF, "")
            case _:
                tok = Token(TokenType.ILLEGAL, self.ch)
        self.read_char()
        return tok
