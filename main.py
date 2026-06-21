import sys
import os
from lexer import lexer, lexical_errors
from parser import parser

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <Archivo.bot>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: El archivo '{filepath}' no existe.")
        sys.exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)

    lexer.input(content)
    while True:
        tok = lexer.token()
        if not tok:
            break
            
    # Imprimir todos los errores léxicos encontrados
    hay_errores_lexicos = len(lexical_errors) > 0
    if hay_errores_lexicos:
        for err in lexical_errors:
            print(err)
            
    # Limpiar los errores para evitar duplicados 
    lexical_errors.clear()
    ast_root = None
    
    try:
       
        # Si se encuentra error sintáctico, la función p_error imprimirá y abortará el script (sys.exit)
        ast_root = parser.parse(content, lexer=lexer)
    except SystemExit:
        sys.exit(1)

    # El programa aborta sin imprimir el árbol.
    if hay_errores_lexicos:
        sys.exit(1)
        
    # Impresión del AST de ser correcto
    if ast_root and ast_root.execute_block:
        # Imprimimos usando un nivel de indentación base de 0
        print(ast_root.execute_block.print_node(0))

if __name__ == "__main__":
    main()