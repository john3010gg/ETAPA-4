class SymbolTable:
    def __init__(self):
        # Pila de alcances (scopes). Cada alcance es un diccionario {nombre_variable: tipo}
        self.scopes = [{}]
        
    def push_scope(self):
        """Añade un nuevo nivel de alcance."""
        self.scopes.append({})
        
    def pop_scope(self):
        """Elimina el nivel de alcance actual."""
        if len(self.scopes) > 1:
            self.scopes.pop()
            
    def define(self, name, var_type):
        """
        Define una nueva variable en el alcance actual.
        Retorna False si ya existe en el MISMO alcance (redeclaración), True en caso contrario.
        """
        if name in self.scopes[-1]:
            return False
        self.scopes[-1][name] = var_type
        return True
        
    def lookup(self, name):
        """
        Busca una variable desde el alcance más interno hacia el más externo.
        Retorna su tipo si existe, de lo contrario None.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
