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

        # Si hubo errores lexicos no se continua con el analisis sintactico
        sys.exit(1)

    # Limpiar los errores para evitar duplicados
    lexical_errors.clear()
    ast_root = None

    try:
        # Si se encuentra error sintáctico, la función p_error imprimirá y abortará el script (sys.exit)
        lexer.lineno = 1
        ast_root = parser.parse(content, lexer=lexer)
    except SystemExit:
        sys.exit(1)
        
    # Análisis de Contexto
    if ast_root:
        from context_analyzer import ContextAnalyzer
        analyzer = ContextAnalyzer()
        context_errors = analyzer.analyze(ast_root)
        
        if context_errors:
            for err in context_errors:
                print(err)
            sys.exit(1)
            
        # Impresión del AST de ser correcto (sin errores lexicos, sintacticos ni de contexto)
        if ast_root.execute_block:
            # Imprimimos usando un nivel de indentación base de 0
            print(ast_root.execute_block.print_node(0))

if __name__ == "__main__":
    main()