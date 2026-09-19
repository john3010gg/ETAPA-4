from bot_symtable import SymbolTable
from bot_ast import (
    ProgramNode, RobotDeclNode, EventBlockNode,
    VarNode, LiteralNode, SeqNode, ActivateNode,
    AdvanceNode, DecelerateNode, DeactivateNode, StoreNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode,
    CollectNode, DropNode, MoveNode, ReadNode, SendNode, ASTNode
)

class ContextAnalyzer:
    def __init__(self):
        self.symtable = SymbolTable()
        self.errors = []
        
    def add_error(self, message):
        self.errors.append(message)

    def analyze(self, node):
        self.visit(node)
        return self.errors
        
    def visit(self, node):
        if node is None:
            return None
            
        method_name = f'visit_{type(node).__name__}'
        # Handle DeactivateNode as DecelerateNode if needed
        if not hasattr(self, method_name) and isinstance(node, DecelerateNode):
            method_name = 'visit_DecelerateNode'
            
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_ProgramNode(self, node):
        # Declaraciones de robots (en alcance global)
        if node.declarations:
            for decl in node.declarations:
                self.visit(decl)
                
        # Bloque de ejecución principal
        if node.execute_block:
            self.visit(node.execute_block)

    def visit_RobotDeclNode(self, node):
        # Declarar cada robot de la lista en el alcance actual
        names = getattr(node, 'names', [node.name])
        for name in names:
            if not self.symtable.define(name, node.robot_type):
                self.add_error(f"Error estatico en linea {node.lineno}: Redeclaracion de la variable '{name}'.")
            
        # Analizar bloques de eventos del robot
        if node.event_blocks:
            for event_block in node.event_blocks:
                # Cada evento define un nuevo comportamiento
                # Empujar un nuevo alcance
                self.symtable.push_scope()
                # Declarar 'me' implícitamente con el tipo del robot
                self.symtable.define('me', node.robot_type)
                
                self.visit(event_block)
                
                self.symtable.pop_scope()

    def visit_EventBlockNode(self, node):
        # Si la condición es un nodo de expresión (guardia booleana)
        if isinstance(node.event_name, ASTNode):
            cond_type = self.visit(node.event_name)
            if cond_type not in ('bool', 'error'):
                self.add_error(f"Error estatico en linea {node.lineno}: La condicion del comportamiento debe ser bool, pero se obtuvo '{cond_type}'.")
                
        if node.statements:
            for stmt in node.statements:
                self.visit(stmt)

    def visit_SeqNode(self, node):
        if node.statements:
            for stmt in node.statements:
                self.visit(stmt)

    def visit_ActivateNode(self, node):
        vars_list = getattr(node, 'vars', [getattr(node, 'var', None)])
        for v in vars_list:
            t = self.symtable.lookup(v)
            if t is None:
                self.add_error(f"Error estatico en linea {node.lineno}: Variable '{v}' no declarada.")

    def visit_AdvanceNode(self, node):
        vars_list = getattr(node, 'vars', [getattr(node, 'var', None)])
        for v in vars_list:
            t = self.symtable.lookup(v)
            if t is None:
                self.add_error(f"Error estatico en linea {node.lineno}: Variable '{v}' no declarada.")

    def visit_DecelerateNode(self, node):
        vars_list = getattr(node, 'vars', [getattr(node, 'var', None)])
        for v in vars_list:
            t = self.symtable.lookup(v)
            if t is None:
                self.add_error(f"Error estatico en linea {node.lineno}: Variable '{v}' no declarada.")

    def visit_DeactivateNode(self, node):
        self.visit_DecelerateNode(node)

    def visit_StoreNode(self, node):
        expr_type = self.visit(node.expr)
        
        # Verificar que estamos dentro de un comportamiento ('me' debe estar definido)
        me_type = self.symtable.lookup('me')
        if me_type is None:
            pass
        elif expr_type != 'error':
            if me_type == 'int' and expr_type not in ('int', 'float', 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Error de tipos, se esperaba '{me_type}' pero se obtuvo '{expr_type}'.")
            elif me_type == 'bool' and expr_type not in ('bool', 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Error de tipos, se esperaba '{me_type}' pero se obtuvo '{expr_type}'.")
            elif me_type == 'char' and expr_type not in ('char', 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Error de tipos, se esperaba '{me_type}' pero se obtuvo '{expr_type}'.")

    def visit_CollectNode(self, node):
        if node.target_var:
            if not self.symtable.define(node.target_var, 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Redeclaracion de la variable '{node.target_var}'.")

    def visit_DropNode(self, node):
        self.visit(node.expr)

    def visit_MoveNode(self, node):
        if node.expr:
            expr_type = self.visit(node.expr)
            if expr_type not in ('int', 'float', 'error'):
                self.add_error(f"Error estatico en linea {node.lineno}: La expresion de movimiento debe ser de tipo numerico, pero se obtuvo '{expr_type}'.")

    def visit_ReadNode(self, node):
        if node.target_var:
            if not self.symtable.define(node.target_var, 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Redeclaracion de la variable '{node.target_var}'.")

    def visit_SendNode(self, node):
        pass

    def visit_IfNode(self, node):
        guardia_type = self.visit(node.guardia)
        if guardia_type != 'error' and guardia_type != 'bool':
            self.add_error(f"Error estatico en linea {node.lineno}: La condicion del 'if' debe ser bool, pero se obtuvo '{guardia_type}'.")
            
        self.symtable.push_scope()
        self.visit(node.exito)
        self.symtable.pop_scope()

        if getattr(node, 'fracaso', None) is not None:
            self.symtable.push_scope()
            self.visit(node.fracaso)
            self.symtable.pop_scope()

    def visit_WhileNode(self, node):
        guardia_type = self.visit(node.guardia)
        if guardia_type != 'error' and guardia_type != 'bool':
            self.add_error(f"Error estatico en linea {node.lineno}: La condicion del 'while' debe ser bool, pero se obtuvo '{guardia_type}'.")
            
        self.symtable.push_scope()
        self.visit(node.cuerpo)
        self.symtable.pop_scope()

    def visit_VarNode(self, node):
        var_type = self.symtable.lookup(node.name)
        if var_type is None:
            if node.name == 'me':
                self.add_error(f"Error estatico en linea {node.lineno}: Utilizacion de la palabra reservada 'me' fuera de un comportamiento.")
            else:
                self.add_error(f"Error estatico en linea {node.lineno}: Utilizacion de variable '{node.name}' no declarada.")
            return 'error'
        return var_type

    def visit_LiteralNode(self, node):
        if isinstance(node.value, bool):
            return 'bool'
        elif isinstance(node.value, float):
            return 'float'
        elif isinstance(node.value, int):
            return 'int'
        elif isinstance(node.value, str):
            return 'char'
        return 'error'

    def visit_BinaryOpNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        if left_type == 'error' or right_type == 'error':
            return 'error'
            
        if node.op_type == 'ARITMETICA':
            # Permite int y float; si cualquiera es 'any' (ej. variable de collect), se acepta
            if left_type not in ('int', 'float', 'any') or right_type not in ('int', 'float', 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion aritmetica ({node.op_val}) requiere tipos numericos (int o float), pero se obtuvieron '{left_type}' y '{right_type}'.")
                return 'error'
            return 'float' if 'float' in (left_type, right_type) else 'int'
            
        elif node.op_type == 'RELACIONAL':
            if node.op_val in ('==', '!='):
                # Podemos comparar numéricos con numéricos, booleanos con booleanos y caracteres con caracteres
                if left_type == 'any' or right_type == 'any':
                    return 'bool'
                if (left_type in ('int', 'float') and right_type not in ('int', 'float')) or \
                   (left_type == 'bool' and right_type != 'bool') or \
                   (left_type == 'char' and right_type != 'char'):
                    self.add_error(f"Error estatico en linea {node.lineno}: Tipos incompatibles para operacion relacional ({node.op_val}): '{left_type}' y '{right_type}'.")
                    return 'error'
            else:
                # <, >, <=, >= requieren numericos o caracteres
                if left_type == 'any' or right_type == 'any':
                    return 'bool'
                if (left_type in ('int', 'float') and right_type not in ('int', 'float')) and not (left_type == 'char' and right_type == 'char'):
                    self.add_error(f"Error estatico en linea {node.lineno}: Operacion relacional ({node.op_val}) requiere tipos numericos, pero se obtuvieron '{left_type}' y '{right_type}'.")
                    return 'error'
            return 'bool'
            
        elif node.op_type == 'BOOLEANA':
            if (left_type != 'bool' and left_type != 'any') or (right_type != 'bool' and right_type != 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion logica ({node.op_val}) requiere booleanos, pero se obtuvieron '{left_type}' y '{right_type}'.")
                return 'error'
            return 'bool'

        return 'error'

    def visit_UnaryOpNode(self, node):
        expr_type = self.visit(node.expr)
        if expr_type == 'error':
            return 'error'
            
        if node.op_val == 'not':
            if expr_type not in ('bool', 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion 'not' requiere un booleano, pero se obtuvo '{expr_type}'.")
                return 'error'
            return 'bool'
        elif node.op_val == '-':
            if expr_type not in ('int', 'float', 'any'):
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion '-' (menos unario) requiere un tipo numerico, pero se obtuvo '{expr_type}'.")
                return 'error'
            return expr_type
            
        return 'error'

