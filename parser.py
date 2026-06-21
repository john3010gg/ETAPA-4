# parser.py
import ply.yacc as yacc
from lexer import tokens, find_column
from bot_ast import (
    VarNode, LiteralNode, SeqNode, ActivateNode, AdvanceNode,
    DecelerateNode, StoreNode, IfNode, WhileNode, BinaryOpNode,
    UnaryOpNode, ProgramNode, RobotDeclNode, EventBlockNode
)

# Definición de precedencia y asociatividad de operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
)

# Función auxiliar para construir bloques de instrucciones
def make_block(stmt_list, lineno):
    if len(stmt_list) == 1:
        return stmt_list[0]
    return SeqNode(stmt_list, lineno)

# Reglas gramaticales del lenguaje BOT

def p_program(p):
    'program : CREATE decl_list EXECUTE stmt_list END'
    p[0] = ProgramNode(p[2], SeqNode(p[4], p.lineno(3)), p.lineno(1))

# Lista de declaraciones de robots
def p_decl_list_multiple(p):
    'decl_list : decl_list decl'
    p[0] = p[1] + [p[2]]

def p_decl_list_single(p):
    'decl_list : decl'
    p[0] = [p[1]]

# Declaración de un robot
def p_decl(p):
    'decl : type BOT ID event_block_list END'
    p[0] = RobotDeclNode(p[1], p[3], p[4], p.lineno(2))

# Tipos válidos
def p_type(p):
    '''type : INT
            | BOOL'''
    p[0] = p[1]

# Lista de bloques de eventos de un robot
def p_event_block_list_multiple(p):
    'event_block_list : event_block_list event_block'
    p[0] = p[1] + [p[2]]

def p_event_block_list_single(p):
    'event_block_list : event_block'
    p[0] = [p[1]]

# Bloque de eventos
def p_event_block(p):
    'event_block : ON event_name COLON stmt_list END'
    p[0] = EventBlockNode(p[2], p[4], p.lineno(1))

# Nombres de eventos permitidos (incluyendo ID genérico para flexibilidad)
def p_event_name(p):
    '''event_name : ACTIVATION
                 | DEFAULT
                 | ID'''
    p[0] = p[1]

# Lista de instrucciones
def p_stmt_list_multiple(p):
    'stmt_list : stmt_list stmt'
    p[0] = p[1] + [p[2]]

def p_stmt_list_single(p):
    'stmt_list : stmt'
    p[0] = [p[1]]

# Instrucciones en BOT
def p_stmt_action(p):
    '''stmt : ACTIVATE ID DOT
            | ADVANCE ID DOT
            | DECELERATE ID DOT'''
    action = p[1]
    var_name = p[2]
    lineno = p.lineno(1)
    
    if action == 'activate':
        p[0] = ActivateNode(var_name, lineno)
    elif action == 'advance':
        p[0] = AdvanceNode(var_name, lineno)
    elif action == 'decelerate':
        p[0] = DecelerateNode(var_name, lineno)

def p_stmt_store(p):
    'stmt : STORE expr DOT'
    p[0] = StoreNode(p[2], p.lineno(1))

def p_stmt_if(p):
    'stmt : IF expr COLON stmt_list END'
    p[0] = IfNode(p[2], make_block(p[4], p.lineno(1)), p.lineno(1))

def p_stmt_while(p):
    'stmt : WHILE expr COLON stmt_list END'
    p[0] = WhileNode(p[2], make_block(p[4], p.lineno(1)), p.lineno(1))

# Reglas de expresiones
def p_expr_var(p):
    'expr : ID'
    p[0] = VarNode(p[1], p.lineno(1))

def p_expr_literal_number(p):
    '''expr : NUMBER
            | FLOAT'''
    p[0] = LiteralNode(p[1], p.lineno(1))

def p_expr_literal_bool(p):
    '''expr : TRUE
            | FALSE'''
    p[0] = LiteralNode(p[1], p.lineno(1))

# Expresiones binarias relacionales
def p_expr_binary_relational(p):
    '''expr : expr GT expr
            | expr LT expr
            | expr GTE expr
            | expr LTE expr
            | expr EQ expr
            | expr NEQ expr'''
    p[0] = BinaryOpNode('RELACIONAL', p[2], p[1], p[3], p.lineno(2))

# Expresiones binarias aritméticas
def p_expr_binary_arithmetic(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = BinaryOpNode('ARITMETICA', p[2], p[1], p[3], p.lineno(2))

# Expresiones binarias booleanas
def p_expr_binary_boolean(p):
    '''expr : expr AND expr
            | expr OR expr'''
    p[0] = BinaryOpNode('BOOLEANA', p[2], p[1], p[3], p.lineno(2))

# Expresiones unarias
def p_expr_unary_not(p):
    'expr : NOT expr'
    p[0] = UnaryOpNode('not', p[2], p.lineno(1))

def p_expr_unary_minus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = UnaryOpNode('-', p[2], p.lineno(1))

# Expresiones entre paréntesis
def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

# Manejo de errores sintácticos
def p_error(p):
    import sys
    if p:
        col = find_column(p.lexer.lexdata, p.lexpos)
        print(f"Error sintactico en la linea {p.lineno}, columna {col}: token inesperado '{p.value}'")
    else:
        print("Error sintactico: fin de archivo inesperado")
    sys.exit(1)

# Construir el parser
parser = yacc.yacc()
