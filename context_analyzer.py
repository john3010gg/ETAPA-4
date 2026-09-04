from bot_symtable import SymbolTable
from bot_ast import (
    ProgramNode, RobotDeclNode, EventBlockNode,
    VarNode, LiteralNode, SeqNode, ActivateNode,
    AdvanceNode, DecelerateNode, StoreNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode
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
        # Intentar declarar el robot en el alcance actual
        # node.robot_type es 'int' o 'bool'
        if not self.symtable.define(node.name, node.robot_type):
            self.add_error(f"Error estatico en linea {node.lineno}: Redeclaracion de la variable '{node.name}'.")
            
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
        if node.statements:
            for stmt in node.statements:
                self.visit(stmt)

    def visit_SeqNode(self, node):
        if node.statements:
            for stmt in node.statements:
                self.visit(stmt)

    def visit_ActivateNode(self, node):
        t = self.symtable.lookup(node.var)
        if t is None:
            self.add_error(f"Error estatico en linea {node.lineno}: Variable '{node.var}' no declarada.")

    def visit_AdvanceNode(self, node):
        t = self.symtable.lookup(node.var)
        if t is None:
            self.add_error(f"Error estatico en linea {node.lineno}: Variable '{node.var}' no declarada.")

    def visit_DecelerateNode(self, node):
        t = self.symtable.lookup(node.var)
        if t is None:
            self.add_error(f"Error estatico en linea {node.lineno}: Variable '{node.var}' no declarada.")

    def visit_StoreNode(self, node):
        expr_type = self.visit(node.expr)
        
        # Verificar que estamos dentro de un comportamiento ('me' debe estar definido)
        me_type = self.symtable.lookup('me')
        if me_type is None:
            # En la vida real, podría requerir un error extra "store fuera de comportamiento".
            # Pero asumiremos que nos centramos en validarlo según los requerimientos estrictos.
            pass
        elif expr_type != 'error':
            # BOT types: 'int', 'bool'.
            # Permitiremos asignar int y float indistintamente dado que se evalúan numéricamente
            if me_type == 'int' and expr_type not in ('int', 'float'):
                self.add_error(f"Error estatico en linea {node.lineno}: Error de tipos, se esperaba '{me_type}' pero se obtuvo '{expr_type}'.")
            elif me_type == 'bool' and expr_type != 'bool':
                self.add_error(f"Error estatico en linea {node.lineno}: Error de tipos, se esperaba '{me_type}' pero se obtuvo '{expr_type}'.")

    def visit_IfNode(self, node):
        guardia_type = self.visit(node.guardia)
        if guardia_type != 'error' and guardia_type != 'bool':
            self.add_error(f"Error estatico en linea {node.lineno}: La condicion del 'if' debe ser bool, pero se obtuvo '{guardia_type}'.")
            
        self.symtable.push_scope()
        self.visit(node.exito)
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
        return 'error'

    def visit_BinaryOpNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        
        if left_type == 'error' or right_type == 'error':
            return 'error'
            
        if node.op_type == 'ARITMETICA':
            if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion aritmetica ({node.op_val}) requiere tipos numericos (int o float), pero se obtuvieron '{left_type}' y '{right_type}'.")
                return 'error'
            return 'float' if 'float' in (left_type, right_type) else 'int'
            
        elif node.op_type == 'RELACIONAL':
            if node.op_val in ('==', '!='):
                # Podemos comparar numéricos con numéricos, y booleanos con booleanos.
                if (left_type in ('int', 'float') and right_type not in ('int', 'float')) or \
                   (left_type == 'bool' and right_type != 'bool'):
                    self.add_error(f"Error estatico en linea {node.lineno}: Tipos incompatibles para operacion relacional ({node.op_val}): '{left_type}' y '{right_type}'.")
                    return 'error'
            else:
                # <, >, <=, >= requieren numericos
                if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                    self.add_error(f"Error estatico en linea {node.lineno}: Operacion relacional ({node.op_val}) requiere tipos numericos, pero se obtuvieron '{left_type}' y '{right_type}'.")
                    return 'error'
            return 'bool'
            
        elif node.op_type == 'BOOLEANA':
            if left_type != 'bool' or right_type != 'bool':
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion logica ({node.op_val}) requiere booleanos, pero se obtuvieron '{left_type}' y '{right_type}'.")
                return 'error'
            return 'bool'

        return 'error'

    def visit_UnaryOpNode(self, node):
        expr_type = self.visit(node.expr)
        if expr_type == 'error':
            return 'error'
            
        if node.op_val == 'not':
            if expr_type != 'bool':
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion 'not' requiere un booleano, pero se obtuvo '{expr_type}'.")
                return 'error'
            return 'bool'
        elif node.op_val == '-':
            if expr_type not in ('int', 'float'):
                self.add_error(f"Error estatico en linea {node.lineno}: Operacion '-' (menos unario) requiere un tipo numerico, pero se obtuvo '{expr_type}'.")
                return 'error'
            return expr_type
            
        return 'error'
