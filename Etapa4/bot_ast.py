class ASTNode:
    def is_simple(self):
        return False
    
    def get_simple_value(self):
        raise NotImplementedError()
    
    def print_node(self, indent=0):
        raise NotImplementedError()

# Nodos simples
class VarNode(ASTNode):
    def __init__(self, name, lineno=0):
        self.name = name
        self.lineno = lineno
    def is_simple(self): return True
    def get_simple_value(self): return self.name

class LiteralNode(ASTNode):
    def __init__(self, value, lineno=0):
        self.value = value
        self.lineno = lineno
    def is_simple(self): return True
    def get_simple_value(self):
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        elif isinstance(self.value, str):
            return f"'{self.value}'"
        return str(self.value)

# Nodos complejos
class SeqNode(ASTNode):
    def __init__(self, statements, lineno=0):
        self.statements = statements
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        lines = [f"{prefix}SECUENCIACION"]
        for stmt in self.statements:
            lines.append(stmt.print_node(indent + 1))
        return "\n".join(lines)

class ActivateNode(ASTNode):
    def __init__(self, vars, lineno=0):
        self.vars = vars if isinstance(vars, list) else [vars]
        self.var = self.vars[0] if self.vars else None
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        if len(self.vars) == 1:
            return f"{prefix}ACTIVACION\n{prefix}  var: {self.var}"
        vars_str = ", ".join(self.vars)
        return f"{prefix}ACTIVACION\n{prefix}  vars: {vars_str}"

class AdvanceNode(ASTNode):
    def __init__(self, vars, lineno=0):
        self.vars = vars if isinstance(vars, list) else [vars]
        self.var = self.vars[0] if self.vars else None
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        if len(self.vars) == 1:
            return f"{prefix}AVANCE\n{prefix}  var: {self.var}"
        vars_str = ", ".join(self.vars)
        return f"{prefix}AVANCE\n{prefix}  vars: {vars_str}"

class DecelerateNode(ASTNode):
    def __init__(self, vars, lineno=0):
        self.vars = vars if isinstance(vars, list) else [vars]
        self.var = self.vars[0] if self.vars else None
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        if len(self.vars) == 1:
            return f"{prefix}DESACELERACION\n{prefix}  var: {self.var}"
        vars_str = ", ".join(self.vars)
        return f"{prefix}DESACELERACION\n{prefix}  vars: {vars_str}"

class DeactivateNode(DecelerateNode):
    def print_node(self, indent=0):
        prefix = "  " * indent
        if len(self.vars) == 1:
            return f"{prefix}DESACTIVACION\n{prefix}  var: {self.var}"
        vars_str = ", ".join(self.vars)
        return f"{prefix}DESACTIVACION\n{prefix}  vars: {vars_str}"

class StoreNode(ASTNode):
    def __init__(self, expr, lineno=0):
        self.expr = expr
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        lines = [f"{prefix}ALMACENAMIENTO"]
        if self.expr.is_simple():
            lines.append(f"{prefix}  expresion: {self.expr.get_simple_value()}")
        else:
            lines.append(f"{prefix}  expresion: {self.expr.get_node_type_name()}")
            lines.append(self.expr.print_fields(indent + 1))
        return "\n".join(lines)

class CollectNode(ASTNode):
    def __init__(self, target_var=None, lineno=0):
        self.target_var = target_var
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        if self.target_var:
            return f"{prefix}COLECCION\n{prefix}  as: {self.target_var}"
        return f"{prefix}COLECCION"

class DropNode(ASTNode):
    def __init__(self, expr, lineno=0):
        self.expr = expr
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        lines = [f"{prefix}SOLTADO"]
        if self.expr.is_simple():
            lines.append(f"{prefix}  expresion: {self.expr.get_simple_value()}")
        else:
            lines.append(f"{prefix}  expresion: {self.expr.get_node_type_name()}")
            lines.append(self.expr.print_fields(indent + 1))
        return "\n".join(lines)

class MoveNode(ASTNode):
    def __init__(self, direction, expr=None, lineno=0):
        self.direction = direction
        self.expr = expr
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        if self.expr:
            if self.expr.is_simple():
                return f"{prefix}MOVIMIENTO\n{prefix}  direccion: {self.direction}\n{prefix}  pasos: {self.expr.get_simple_value()}"
            return f"{prefix}MOVIMIENTO\n{prefix}  direccion: {self.direction}\n{prefix}  pasos: {self.expr.get_node_type_name()}"
        return f"{prefix}MOVIMIENTO\n{prefix}  direccion: {self.direction}"

class ReadNode(ASTNode):
    def __init__(self, target_var=None, lineno=0):
        self.target_var = target_var
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        if self.target_var:
            return f"{prefix}LECTURA\n{prefix}  as: {self.target_var}"
        return f"{prefix}LECTURA"

class SendNode(ASTNode):
    def __init__(self, lineno=0):
        self.lineno = lineno
    def print_node(self, indent=0):
        prefix = "  " * indent
        return f"{prefix}ENVIO"

class IfNode(ASTNode):
    def __init__(self, guardia, exito, fracaso=None, lineno=0):
        self.guardia = guardia
        self.exito = exito
        self.fracaso = fracaso
        self.lineno = lineno
        
    def print_node(self, indent=0):
        prefix = "  " * indent
        lines = [f"{prefix}CONDICIONAL"]
            
        # Guardia
        if self.guardia.is_simple():
            lines.append(f"{prefix}  guardia: {self.guardia.get_simple_value()}")
        else:
            lines.append(f"{prefix}  guardia: {self.guardia.get_node_type_name()}")
            lines.append(self.guardia.print_fields(indent + 1))
            
        # Exito
        if self.exito.is_simple():
            lines.append(f"{prefix}  exito: {self.exito.get_simple_value()}")
        else:
            exito_text = self.exito.print_node(indent + 1)
            first_line_prefix = "  " * (indent + 1)
            if exito_text.startswith(first_line_prefix):
                exito_text = f"{prefix}  exito: " + exito_text[len(first_line_prefix):]
            else:
                exito_text = f"{prefix}  exito: {exito_text}"
            lines.append(exito_text)
            
        # Fracaso (opcional)
        if self.fracaso is not None:
            if self.fracaso.is_simple():
                lines.append(f"{prefix}  fracaso: {self.fracaso.get_simple_value()}")
            else:
                fracaso_text = self.fracaso.print_node(indent + 1)
                first_line_prefix = "  " * (indent + 1)
                if fracaso_text.startswith(first_line_prefix):
                    fracaso_text = f"{prefix}  fracaso: " + fracaso_text[len(first_line_prefix):]
                else:
                    fracaso_text = f"{prefix}  fracaso: {fracaso_text}"
                lines.append(fracaso_text)
                
        return "\n".join(lines)

class WhileNode(ASTNode):
    def __init__(self, guardia, cuerpo, lineno=0):
        self.guardia = guardia
        self.cuerpo = cuerpo
        self.lineno = lineno
        
    def print_node(self, indent=0):
        prefix = "  " * indent
        lines = [f"{prefix}REPETICION_INDET"]
            
        # Guardia
        if self.guardia.is_simple():
            lines.append(f"{prefix}  guardia: {self.guardia.get_simple_value()}")
        else:
            lines.append(f"{prefix}  guardia: {self.guardia.get_node_type_name()}")
            lines.append(self.guardia.print_fields(indent + 1))
            
        # Cuerpo
        if self.cuerpo.is_simple():
            lines.append(f"{prefix}  cuerpo: {self.cuerpo.get_simple_value()}")
        else:
            cuerpo_text = self.cuerpo.print_node(indent + 1)
            first_line_prefix = "  " * (indent + 1)
            if cuerpo_text.startswith(first_line_prefix):
                cuerpo_text = f"{prefix}  cuerpo: " + cuerpo_text[len(first_line_prefix):]
            else:
                cuerpo_text = f"{prefix}  cuerpo: {cuerpo_text}"
            lines.append(cuerpo_text)
                
        return "\n".join(lines)

# Nodos de expresiones complejas
class BinaryOpNode(ASTNode):
    def __init__(self, op_type, op_val, left, right, lineno=0):
        self.op_type = op_type
        self.op_val = op_val
        self.left = left
        self.right = right
        self.lineno = lineno
        
    def get_node_type_name(self): return f"BIN_{self.op_type}"
        
    def print_fields(self, indent=0):
        prefix = "  " * indent
        op_translation = {
            '>': 'Mayor que', '<': 'Menor que', '>=': 'Mayor o igual que', '<=': 'Menor o igual que',
            '==': 'Igual que', '!=': 'Diferente que', '+': 'Suma', '-': 'Resta', '*': 'Multiplicacion',
            '/': 'Division', '%': 'Modulo', 'and': 'Y', 'or': 'O'
        }
        op_name = op_translation.get(self.op_val, self.op_val)
        lines = [f"{prefix}operacion: '{op_name}'"]
        
        if self.left.is_simple():
            lines.append(f"{prefix}operador izquierdo: {self.left.get_simple_value()}")
        else:
            lines.append(f"{prefix}operador izquierdo: {self.left.get_node_type_name()}")
            lines.append(self.left.print_fields(indent + 1))
            
        if self.right.is_simple():
            lines.append(f"{prefix}operador derecho: {self.right.get_simple_value()}")
        else:
            lines.append(f"{prefix}operador derecho: {self.right.get_node_type_name()}")
            lines.append(self.right.print_fields(indent + 1))
            
        return "\n".join(lines)

class UnaryOpNode(ASTNode):
    def __init__(self, op_val, expr, lineno=0):
        self.op_val = op_val
        self.expr = expr
        self.lineno = lineno
        
    def get_node_type_name(self): return "UNARIA"
        
    def print_fields(self, indent=0):
        prefix = "  " * indent
        op_translation = {'not': 'Negacion', '-': 'Menos unario'}
        op_name = op_translation.get(self.op_val, self.op_val)
        lines = [f"{prefix}operacion: '{op_name}'"]
        
        if self.expr.is_simple():
            lines.append(f"{prefix}operando: {self.expr.get_simple_value()}")
        else:
            lines.append(f"{prefix}operando: {self.expr.get_node_type_name()}")
            lines.append(self.expr.print_fields(indent + 1))
            
        return "\n".join(lines)

# Nodos de declaraciones 
class ProgramNode(ASTNode):
    def __init__(self, declarations, execute_block, lineno=0):
        self.declarations = declarations
        self.execute_block = execute_block
        self.lineno = lineno

class RobotDeclNode(ASTNode):
    def __init__(self, robot_type, names, event_blocks, lineno=0):
        self.robot_type = robot_type
        self.names = names if isinstance(names, list) else [names]
        self.name = self.names[0] if self.names else None
        self.event_blocks = event_blocks
        self.lineno = lineno

class EventBlockNode(ASTNode):
    def __init__(self, event_name, statements, lineno=0):
        # event_name puede ser una cadena ('activation', 'deactivation', 'default')
        # o un nodo de expresión (ASTNode) para una condición/guardia
        self.event_name = event_name
        self.statements = statements
        self.lineno = lineno