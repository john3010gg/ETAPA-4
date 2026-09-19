# parser.py
import ply.yacc as yacc
from lexer import tokens, find_column
from bot_ast import (
    VarNode, LiteralNode, SeqNode, ActivateNode, AdvanceNode,
    DecelerateNode, DeactivateNode, StoreNode, IfNode, WhileNode,
    BinaryOpNode, UnaryOpNode, ProgramNode, RobotDeclNode, EventBlockNode,
    CollectNode, DropNode, MoveNode, ReadNode, SendNode
)

# Definición de precedencia y asociatividad de operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'UMINUS'),
)

# Función auxiliar para construir bloques de instrucciones
def make_block(stmt_list, lineno):
    if len(stmt_list) == 0:
        return SeqNode([], lineno)
    if len(stmt_list) == 1:
        return stmt_list[0]
    return SeqNode(stmt_list, lineno)

# Reglas gramaticales del lenguaje BOT

def p_program(p):
    '''program : CREATE decl_list EXECUTE stmt_list END
               | EXECUTE stmt_list END'''
    if len(p) == 6:
        p[0] = ProgramNode(p[2], SeqNode(p[4], p.lineno(3)), p.lineno(1))
    else:
        p[0] = ProgramNode([], SeqNode(p[2], p.lineno(1)), p.lineno(1))

# Lista de declaraciones de robots
def p_decl_list_multiple(p):
    'decl_list : decl_list decl'
    p[0] = p[1] + [p[2]]

def p_decl_list_single(p):
    'decl_list : decl'
    p[0] = [p[1]]

# Declaración de robots (con o sin lista de comportamientos)
def p_decl_with_events(p):
    'decl : type BOT id_list event_block_list END'
    p[0] = RobotDeclNode(p[1], p[3], p[4], p.lineno(2))

def p_decl_no_events(p):
    'decl : type BOT id_list END'
    p[0] = RobotDeclNode(p[1], p[3], [], p.lineno(2))

# Lista de identificadores separados por comas
def p_id_list_multiple(p):
    'id_list : id_list COMMA ID'
    p[0] = p[1] + [p[3]]

def p_id_list_single(p):
    'id_list : ID'
    p[0] = [p[1]]

# Tipos válidos
def p_type(p):
    '''type : INT
            | BOOL
            | CHAR_TYPE'''
    if p[1] == 'char':
        p[0] = 'char'
    else:
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
    'event_block : ON event_cond COLON opt_stmt_list END'
    p[0] = EventBlockNode(p[2], p[4], p.lineno(1))

# Condiciones de eventos
def p_event_cond_named(p):
    '''event_cond : ACTIVATION
                  | DEACTIVATION
                  | DEFAULT'''
    p[0] = p[1]

def p_event_cond_expr(p):
    'event_cond : expr'
    p[0] = p[1]

# Lista de instrucciones
def p_stmt_list_multiple(p):
    'stmt_list : stmt_list stmt'
    p[0] = p[1] + [p[2]]

def p_stmt_list_single(p):
    'stmt_list : stmt'
    p[0] = [p[1]]

def p_opt_stmt_list_multiple(p):
    'opt_stmt_list : opt_stmt_list stmt'
    p[0] = p[1] + [p[2]]

def p_opt_stmt_list_empty(p):
    'opt_stmt_list :'
    p[0] = []

# Instrucciones en BOT
def p_stmt_action(p):
    '''stmt : ACTIVATE id_list DOT
            | ADVANCE id_list DOT
            | DECELERATE id_list DOT
            | DEACTIVATE id_list DOT'''
    action = p[1]
    id_list = p[2]
    lineno = p.lineno(1)
    
    if action == 'activate':
        p[0] = ActivateNode(id_list, lineno)
    elif action == 'advance':
        p[0] = AdvanceNode(id_list, lineno)
    elif action in ('decelerate', 'deactivate'):
        p[0] = DeactivateNode(id_list, lineno)

def p_stmt_store(p):
    'stmt : STORE expr DOT'
    p[0] = StoreNode(p[2], p.lineno(1))

def p_stmt_collect_as(p):
    'stmt : COLLECT AS ID DOT'
    p[0] = CollectNode(p[3], p.lineno(1))

def p_stmt_collect(p):
    'stmt : COLLECT DOT'
    p[0] = CollectNode(None, p.lineno(1))

def p_stmt_drop(p):
    'stmt : DROP expr DOT'
    p[0] = DropNode(p[2], p.lineno(1))

def p_stmt_move_expr(p):
    '''stmt : LEFT expr DOT
            | RIGHT expr DOT
            | UP expr DOT
            | DOWN expr DOT'''
    p[0] = MoveNode(p[1], p[2], p.lineno(1))

def p_stmt_move_simple(p):
    '''stmt : LEFT DOT
            | RIGHT DOT
            | UP DOT
            | DOWN DOT'''
    p[0] = MoveNode(p[1], None, p.lineno(1))

def p_stmt_read_as(p):
    '''stmt : READ AS ID DOT
            | RECEIVE AS ID DOT'''
    p[0] = ReadNode(p[3], p.lineno(1))

def p_stmt_read(p):
    '''stmt : READ DOT
            | RECEIVE DOT'''
    p[0] = ReadNode(None, p.lineno(1))

def p_stmt_send(p):
    'stmt : SEND DOT'
    p[0] = SendNode(p.lineno(1))

def p_stmt_if(p):
    'stmt : IF expr COLON opt_stmt_list END'
    p[0] = IfNode(p[2], make_block(p[4], p.lineno(1)), None, p.lineno(1))

def p_stmt_if_else(p):
    'stmt : IF expr COLON opt_stmt_list ELSE COLON opt_stmt_list END'
    p[0] = IfNode(p[2], make_block(p[4], p.lineno(1)), make_block(p[7], p.lineno(5)), p.lineno(1))

def p_stmt_while(p):
    'stmt : WHILE expr COLON opt_stmt_list END'
    p[0] = WhileNode(p[2], make_block(p[4], p.lineno(1)), p.lineno(1))

def p_stmt_scope_block(p):
    '''stmt : CREATE decl_list EXECUTE stmt_list END
            | EXECUTE stmt_list END'''
    if len(p) == 6:
        p[0] = ProgramNode(p[2], SeqNode(p[4], p.lineno(3)), p.lineno(1))
    else:
        p[0] = ProgramNode([], SeqNode(p[2], p.lineno(1)), p.lineno(1))

# Reglas de expresiones
def p_expr_var(p):
    'expr : ID'
    p[0] = VarNode(p[1], p.lineno(1))

def p_expr_me(p):
    'expr : ME'
    p[0] = VarNode('me', p.lineno(1))

def p_expr_literal_number(p):
    '''expr : NUMBER
            | FLOAT'''
    p[0] = LiteralNode(p[1], p.lineno(1))

def p_expr_literal_bool(p):
    '''expr : TRUE
            | FALSE'''
    p[0] = LiteralNode(p[1], p.lineno(1))

def p_expr_literal_char(p):
    'expr : CHAR_LITERAL'
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
            | expr DIVIDE expr
            | expr MOD expr'''
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

