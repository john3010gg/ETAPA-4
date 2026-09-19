# lexer.py
import ply.lex as lex

# Palabras reservadas del lenguaje BOT
reserved = {
    'create': 'CREATE',
    'execute': 'EXECUTE',
    'end': 'END',
    'int': 'INT',
    'bool': 'BOOL',
    'char': 'CHAR_TYPE',
    'bot': 'BOT',
    'on': 'ON',
    'activation': 'ACTIVATION',
    'deactivation': 'DEACTIVATION',
    'default': 'DEFAULT',
    'store': 'STORE',
    'activate': 'ACTIVATE',
    'advance': 'ADVANCE',
    'decelerate': 'DECELERATE',
    'deactivate': 'DEACTIVATE',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'true': 'TRUE',
    'false': 'FALSE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'me': 'ME',
    'read': 'READ',
    'receive': 'RECEIVE',
    'send': 'SEND',
    'collect': 'COLLECT',
    'as': 'AS',
    'drop': 'DROP',
    'left': 'LEFT',
    'right': 'RIGHT',
    'up': 'UP',
    'down': 'DOWN'
}

# Lista de tokens
tokens = [
    'ID',
    'FLOAT',
    'NUMBER',
    'CHAR_LITERAL',
    'COLON',
    'DOT',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',
    'EQ',
    'NEQ',
    'GTE',
    'LTE',
    'GT',
    'LT'
] + list(reserved.values())

# Símbolos lógicos alternativos y relacionales
def t_AND_SYM(t):
    r'/\\'
    t.type = 'AND'
    t.value = 'and'
    return t

def t_OR_SYM(t):
    r'\\/'
    t.type = 'OR'
    t.value = 'or'
    return t

def t_NOT_SYM(t):
    r'~'
    t.type = 'NOT'
    t.value = 'not'
    return t

def t_NEQ(t):
    r'!=|/='
    t.value = '!='
    return t

def t_EQ(t):
    r'==|='
    t.value = '=='
    return t

# Expresiones regulares para tokens simples
t_COLON = r':'
t_DOT = r'\.'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_GTE = r'>='
t_LTE = r'<='
t_GT = r'>'
t_LT = r'<'

# Ignorar espacios, tabulaciones y retornos de carro
t_ignore = ' \t\r'

# Comentarios de una línea $$ ...
def t_LINE_COMMENT(t):
    r'\$\$[^\n]*'
    pass

# Comentarios multilínea de tipo $- ... -$
def t_COMMENT(t):
    r'\$-[\s\S]*?-\$'
    # Contamos las líneas dentro del comentario
    t.lexer.lineno += t.value.count('\n')
    pass

# Literales de caracteres (ej. 'H', ' ', '\n', '\t', '\'')
def t_CHAR_LITERAL(t):
    r"'([^'\\]|\\.)'"
    raw = t.value[1:-1]
    if raw == r'\n':
        t.value = '\n'
    elif raw == r'\t':
        t.value = '\t'
    elif raw == r"\'":
        t.value = "'"
    elif raw == r'\\':
        t.value = '\\'
    else:
        t.value = raw
    return t

# Identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Si es palabra reservada, cambia el tipo
    # Para constantes booleanas, convertimos el valor a bool
    if t.type == 'TRUE':
        t.value = True
    elif t.type == 'FALSE':
        t.value = False
    return t

# Números reales (FLOAT) - Debe ir antes de NUMBER
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Números enteros (NUMBER)
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Seguimiento de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Lista para almacenar los errores léxicos encontrados
lexical_errors = []

# Función para calcular la columna de un token o posición
def find_column(input_data, token_lexpos):
    line_start = input_data.rfind('\n', 0, token_lexpos) + 1
    return (token_lexpos - line_start) + 1

# Manejo de errores léxicos
def t_error(t):
    col = find_column(t.lexer.lexdata, t.lexpos)
    error_msg = f"Error lexico en la linea {t.lineno}, columna {col}: caracter inesperado '{t.value[0]}'"
    lexical_errors.append(error_msg)
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

