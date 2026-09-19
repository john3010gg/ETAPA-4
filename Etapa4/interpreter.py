# interpreter.py
import sys
from bot_ast import (
    ProgramNode, RobotDeclNode, EventBlockNode,
    VarNode, LiteralNode, SeqNode, ActivateNode,
    AdvanceNode, DecelerateNode, DeactivateNode, StoreNode,
    IfNode, WhileNode, BinaryOpNode, UnaryOpNode,
    CollectNode, DropNode, MoveNode, ReadNode, SendNode, ASTNode
)

class Robot:
    def __init__(self, name, robot_type, behaviors=None):
        self.name = name
        self.type = robot_type  # 'int', 'bool', 'char'
        self.active = False
        self.has_value = False
        self.value = None
        self.pos = [0, 0]
        self.behaviors = behaviors if behaviors else []

    def __repr__(self):
        return f"<Robot {self.name} ({self.type}) active={self.active} val={self.value} pos={self.pos}>"

class Interpreter:
    def __init__(self):
        self.robots = {}
        self.matrix = {}  # (x, y) -> (value, type)
        self.local_scopes = []
        self.current_robot = None

    def runtime_error(self, message, lineno):
        print(f"Error en tiempo de ejecucion en la linea {lineno}: {message}")
        sys.exit(1)

    def push_scope(self):
        self.local_scopes.append({})

    def pop_scope(self):
        if self.local_scopes:
            self.local_scopes.pop()

    def set_local_var(self, name, value, var_type):
        if self.local_scopes:
            self.local_scopes[-1][name] = (value, var_type)

    def lookup_local_var(self, name):
        for scope in reversed(self.local_scopes):
            if name in scope:
                return scope[name]
        return None

    def interpret(self, ast_root):
        self.correr(ast_root)

    def correr(self, node):
        """Ejecuta árboles que representan instrucciones."""
        if node is None:
            return

        node_type = type(node).__name__

        if node_type == 'ProgramNode':
            self.correr_ProgramNode(node)
        elif node_type == 'SeqNode':
            self.correr_SeqNode(node)
        elif node_type == 'ActivateNode':
            self.correr_ActivateNode(node)
        elif node_type in ('DeactivateNode', 'DecelerateNode'):
            self.correr_DeactivateNode(node)
        elif node_type == 'AdvanceNode':
            self.correr_AdvanceNode(node)
        elif node_type == 'StoreNode':
            self.correr_StoreNode(node)
        elif node_type == 'CollectNode':
            self.correr_CollectNode(node)
        elif node_type == 'DropNode':
            self.correr_DropNode(node)
        elif node_type == 'MoveNode':
            self.correr_MoveNode(node)
        elif node_type == 'ReadNode':
            self.correr_ReadNode(node)
        elif node_type == 'SendNode':
            self.correr_SendNode(node)
        elif node_type == 'IfNode':
            self.correr_IfNode(node)
        elif node_type == 'WhileNode':
            self.correr_WhileNode(node)
        else:
            raise Exception(f"Instruccion desconocida para correr: {node_type}")

    def correr_ProgramNode(self, node):
        if node.declarations:
            for decl in node.declarations:
                names = getattr(decl, 'names', [decl.name])
                for name in names:
                    self.robots[name] = Robot(name, decl.robot_type, decl.event_blocks)

        if node.execute_block:
            self.correr(node.execute_block)

    def correr_SeqNode(self, node):
        for stmt in node.statements:
            self.correr(stmt)

    def correr_ActivateNode(self, node):
        vars_list = getattr(node, 'vars', [getattr(node, 'var', None)])
        for name in vars_list:
            if name not in self.robots:
                self.runtime_error(f"Robot '{name}' no ha sido declarado.", node.lineno)
            robot = self.robots[name]
            if robot.active:
                self.runtime_error(f"Activacion ilegal: El robot '{name}' ya se encuentra activo.", node.lineno)
            
            robot.active = True
            # Ejecutar comportamiento on activation si existe
            for b in robot.behaviors:
                if b.event_name == 'activation':
                    self.execute_behavior(robot, b)
                    break

    def correr_DeactivateNode(self, node):
        vars_list = getattr(node, 'vars', [getattr(node, 'var', None)])
        for name in vars_list:
            if name not in self.robots:
                self.runtime_error(f"Robot '{name}' no ha sido declarado.", node.lineno)
            robot = self.robots[name]
            if not robot.active:
                self.runtime_error(f"Desactivacion ilegal: El robot '{name}' ya se encuentra inactivo.", node.lineno)
            
            # Ejecutar comportamiento on deactivation si existe
            for b in robot.behaviors:
                if b.event_name == 'deactivation':
                    self.execute_behavior(robot, b)
                    break
            robot.active = False

    def correr_AdvanceNode(self, node):
        vars_list = getattr(node, 'vars', [getattr(node, 'var', None)])
        for name in vars_list:
            if name not in self.robots:
                self.runtime_error(f"Robot '{name}' no ha sido declarado.", node.lineno)
            robot = self.robots[name]
            if not robot.active:
                self.runtime_error(f"El robot '{name}' no esta activo para avanzar.", node.lineno)

            # Buscar comportamiento correspondiente
            chosen_behavior = None
            default_behavior = None

            for b in robot.behaviors:
                if b.event_name in ('activation', 'deactivation'):
                    continue
                elif b.event_name == 'default':
                    default_behavior = b
                else:
                    # Guardia booleana
                    cond_val, _ = self.evaluar(b.event_name, robot)
                    if cond_val is True:
                        chosen_behavior = b
                        break

            if chosen_behavior is None and default_behavior is not None:
                chosen_behavior = default_behavior

            if chosen_behavior is None:
                self.runtime_error(f"Comportamiento inexistente: Al avanzar el robot '{name}', ninguna de sus guardias se cumplio.", node.lineno)

            self.execute_behavior(robot, chosen_behavior)

    def execute_behavior(self, robot, behavior_node):
        prev_robot = self.current_robot
        self.current_robot = robot
        self.push_scope()
        try:
            if behavior_node.statements:
                for stmt in behavior_node.statements:
                    self.correr(stmt)
        finally:
            self.pop_scope()
            self.current_robot = prev_robot

    def correr_StoreNode(self, node):
        if self.current_robot is None:
            self.runtime_error("Instruccion 'store' fuera del comportamiento de un robot.", node.lineno)
        
        val, val_type = self.evaluar(node.expr, self.current_robot)
        expected_type = self.current_robot.type

        # Almacenamiento inadecuado: verificar tipo consistente
        if expected_type == 'int':
            if val_type not in ('int', 'float') or isinstance(val, bool):
                self.runtime_error(f"Almacenamiento inadecuado: Se esperaba 'int' pero se obtuvo '{val_type}'.", node.lineno)
            self.current_robot.value = int(val)
        elif expected_type == 'bool':
            if val_type != 'bool':
                self.runtime_error(f"Almacenamiento inadecuado: Se esperaba 'bool' pero se obtuvo '{val_type}'.", node.lineno)
            self.current_robot.value = bool(val)
        elif expected_type == 'char':
            if val_type != 'char':
                self.runtime_error(f"Almacenamiento inadecuado: Se esperaba 'char' pero se obtuvo '{val_type}'.", node.lineno)
            self.current_robot.value = str(val)

        self.current_robot.has_value = True

    def correr_CollectNode(self, node):
        if self.current_robot is None:
            self.runtime_error("Instruccion 'collect' fuera del comportamiento de un robot.", node.lineno)

        pos = (self.current_robot.pos[0], self.current_robot.pos[1])
        if pos not in self.matrix:
            self.runtime_error(f"Coleccion inadecuada: La celda {pos} de la matriz esta vacia.", node.lineno)

        cell_val, cell_type = self.matrix[pos]

        if node.target_var:
            self.set_local_var(node.target_var, cell_val, cell_type)
        else:
            expected_type = self.current_robot.type
            if expected_type == 'int' and cell_type in ('int', 'float') and not isinstance(cell_val, bool):
                self.current_robot.value = int(cell_val)
            elif expected_type == cell_type:
                self.current_robot.value = cell_val
            else:
                self.runtime_error(f"Coleccion inadecuada: El valor en la matriz ({cell_type}) es inconsistente con el tipo del robot '{self.current_robot.name}' ({expected_type}).", node.lineno)
            self.current_robot.has_value = True

    def correr_DropNode(self, node):
        if self.current_robot is None:
            self.runtime_error("Instruccion 'drop' fuera del comportamiento de un robot.", node.lineno)

        val, val_type = self.evaluar(node.expr, self.current_robot)
        expected_type = self.current_robot.type

        # Soltado inadecuado: verificar consistencia con el tipo del robot
        if expected_type == 'int' and (val_type not in ('int', 'float') or isinstance(val, bool)):
            self.runtime_error(f"Soltado inadecuado: El valor a soltar ({val_type}) es inconsistente con el robot ({expected_type}).", node.lineno)
        elif expected_type == 'bool' and val_type != 'bool':
            self.runtime_error(f"Soltado inadecuado: El valor a soltar ({val_type}) es inconsistente con el robot ({expected_type}).", node.lineno)
        elif expected_type == 'char' and val_type != 'char':
            self.runtime_error(f"Soltado inadecuado: El valor a soltar ({val_type}) es inconsistente con el robot ({expected_type}).", node.lineno)

        pos = (self.current_robot.pos[0], self.current_robot.pos[1])
        self.matrix[pos] = (val, val_type)

    def correr_MoveNode(self, node):
        if self.current_robot is None:
            self.runtime_error("Instruccion de movimiento fuera del comportamiento de un robot.", node.lineno)

        steps = 1
        if node.expr:
            val, val_type = self.evaluar(node.expr, self.current_robot)
            if val_type not in ('int', 'float') or isinstance(val, bool) or val < 0:
                self.runtime_error(f"Movimiento invalido: El desplazamiento debe ser entero no negativo (obtenido: {val}).", node.lineno)
            steps = int(val)

        d = node.direction
        if d == 'right':
            self.current_robot.pos[0] += steps
        elif d == 'left':
            self.current_robot.pos[0] -= steps
        elif d == 'up':
            self.current_robot.pos[1] += steps
        elif d == 'down':
            self.current_robot.pos[1] -= steps

    def correr_ReadNode(self, node):
        if self.current_robot is None:
            self.runtime_error("Instruccion 'read'/'receive' fuera del comportamiento de un robot.", node.lineno)

        try:
            line = sys.stdin.readline()
            if line == '':
                raw = ''
            else:
                raw = line.rstrip('\r\n')
        except Exception:
            raw = ''

        expected_type = self.current_robot.type

        # Lectura inadecuada: verificar si la entrada es inconsistente con el tipo
        # (Nótese: un dígito como '7' es válido como entero y como caracter)
        val = None
        val_type = None

        if expected_type == 'int':
            try:
                val = int(raw.strip())
                val_type = 'int'
            except ValueError:
                self.runtime_error(f"Lectura inadecuada: Se esperaba una entrada entera para el robot '{self.current_robot.name}', pero se recibio '{raw}'.", node.lineno)
        elif expected_type == 'bool':
            stripped = raw.strip().lower()
            if stripped == 'true':
                val = True
                val_type = 'bool'
            elif stripped == 'false':
                val = False
                val_type = 'bool'
            else:
                self.runtime_error(f"Lectura inadecuada: Se esperaba 'true' o 'false' para el robot '{self.current_robot.name}', pero se recibio '{raw}'.", node.lineno)
        elif expected_type == 'char':
            if len(raw) == 1:
                val = raw
                val_type = 'char'
            else:
                self.runtime_error(f"Lectura inadecuada: Se esperaba un solo caracter para el robot '{self.current_robot.name}', pero se recibio '{raw}'.", node.lineno)

        if node.target_var:
            self.set_local_var(node.target_var, val, val_type)
        else:
            self.current_robot.value = val
            self.current_robot.has_value = True

    def correr_SendNode(self, node):
        if self.current_robot is None:
            self.runtime_error("Instruccion 'send' fuera del comportamiento de un robot.", node.lineno)

        if not self.current_robot.has_value:
            self.runtime_error(f"Uso del robot '{self.current_robot.name}' sin valor asignado.", node.lineno)

        val = self.current_robot.value
        if isinstance(val, bool):
            sys.stdout.write("true" if val else "false")
        else:
            sys.stdout.write(str(val))
        sys.stdout.flush()

    def correr_IfNode(self, node):
        guardia_val, _ = self.evaluar(node.guardia, self.current_robot)
        if guardia_val is True:
            self.correr(node.exito)
        elif getattr(node, 'fracaso', None) is not None:
            self.correr(node.fracaso)

    def correr_WhileNode(self, node):
        while True:
            guardia_val, _ = self.evaluar(node.guardia, self.current_robot)
            if not guardia_val:
                break
            self.correr(node.cuerpo)

    def evaluar(self, node, robot_context=None):
        """Evalúa árboles que representan expresiones, retornando (valor, tipo)."""
        if node is None:
            return None, 'none'

        node_type = type(node).__name__

        if node_type == 'LiteralNode':
            if isinstance(node.value, bool):
                return node.value, 'bool'
            elif isinstance(node.value, int):
                return node.value, 'int'
            elif isinstance(node.value, float):
                return node.value, 'float'
            elif isinstance(node.value, str):
                return node.value, 'char'
            return node.value, 'unknown'

        elif node_type == 'VarNode':
            if node.name == 'me':
                if robot_context is None:
                    self.runtime_error("Uso de 'me' fuera de un comportamiento.", node.lineno)
                if not robot_context.has_value:
                    self.runtime_error(f"El robot '{robot_context.name}' no tiene valor asignado.", node.lineno)
                return robot_context.value, robot_context.type

            # Verificar variables locales de comportamientos
            local_res = self.lookup_local_var(node.name)
            if local_res is not None:
                return local_res

            # Verificar nombres de robots globales
            if node.name in self.robots:
                bot = self.robots[node.name]
                if not bot.has_value:
                    self.runtime_error(f"El robot '{bot.name}' no tiene valor asignado.", node.lineno)
                return bot.value, bot.type

            self.runtime_error(f"Variable '{node.name}' no declarada.", node.lineno)

        elif node_type == 'BinaryOpNode':
            left_val, left_type = self.evaluar(node.left, robot_context)
            right_val, right_type = self.evaluar(node.right, robot_context)

            op = node.op_val
            op_kind = node.op_type

            if op_kind == 'ARITMETICA':
                if op == '+':
                    res = left_val + right_val
                elif op == '-':
                    res = left_val - right_val
                elif op == '*':
                    res = left_val * right_val
                elif op == '/':
                    if right_val == 0:
                        self.runtime_error("Division por cero: Intento de division entre cero.", node.lineno)
                    if left_type == 'int' and right_type == 'int':
                        res = left_val // right_val
                    else:
                        res = left_val / right_val
                elif op == '%':
                    if right_val == 0:
                        self.runtime_error("Division por cero: Intento de modulo entre cero.", node.lineno)
                    res = left_val % right_val
                else:
                    raise Exception(f"Operador aritmetico no soportado: {op}")

                res_type = 'float' if isinstance(res, float) else 'int'
                return res, res_type

            elif op_kind == 'RELACIONAL':
                if op in ('==', '='):
                    return (left_val == right_val), 'bool'
                elif op in ('!=', '/='):
                    return (left_val != right_val), 'bool'
                elif op == '<':
                    return (left_val < right_val), 'bool'
                elif op == '<=':
                    return (left_val <= right_val), 'bool'
                elif op == '>':
                    return (left_val > right_val), 'bool'
                elif op == '>=':
                    return (left_val >= right_val), 'bool'

            elif op_kind == 'BOOLEANA':
                if op in ('and', '/\\'):
                    return bool(left_val and right_val), 'bool'
                elif op in ('or', '\\/'):
                    return bool(left_val or right_val), 'bool'

            raise Exception(f"Operacion binaria no soportada: {op}")

        elif node_type == 'UnaryOpNode':
            val, val_type = self.evaluar(node.expr, robot_context)
            if node.op_val in ('not', '~'):
                return not val, 'bool'
            elif node.op_val == '-':
                return -val, val_type
            raise Exception(f"Operacion unaria no soportada: {node.op_val}")

        raise Exception(f"Nodo de expresion no soportado: {node_type}")
