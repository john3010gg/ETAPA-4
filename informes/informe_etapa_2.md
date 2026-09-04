# Informe Técnico: Analizador Sintáctico para BOT (SintBot)
John Garrido 20-10293
Andres Ramirez 21-10520

Este informe detalla la formulación, diseño e implementación de la segunda etapa del proyecto de la asignatura **CI3725 - Traductores e Interpretadores**, que consiste en el desarrollo del analizador sintáctico y la construcción del Árbol Sintáctico Abstracto (AST) para el lenguaje de programación **BOT**.

---

## 1. Formulación del Analizador Léxico (`lexer.py`)

El analizador léxico está construido con la herramienta **PLY (Python Lex-Yacc)** y es responsable de clasificar el flujo de caracteres de entrada en tokens. 

### Características del Diseño Léxico:
- **Palabras Reservadas:** Se mapean de forma segura mediante un diccionario (`reserved`) para evitar la colisión de variables con nombres de palabras clave (ej., `create`, `execute`, `end`, `int`, `bool`, `bot`, `on`, `activation`, `default`, `store`, `activate`, `advance`, `decelerate`, `if`, `while`).
- **Comentarios:** El lenguaje define comentarios delimitados por `$-` y `-$`. Estos se reconocen con una regla de expresión regular multilínea y se descartan para que no afecten al parsing, incrementando el contador de líneas del lexer según corresponda.
- **Diferenciación de Números:** Los números de punto flotante (`FLOAT`) se diferencian de los enteros (`NUMBER`). Para evitar problemas de análisis en sentencias como `store 3.`, la regla léxica exige dígitos después del punto decimal para emparejar un `FLOAT` (ej., `3.5`). En consecuencia, la cadena `3.` se desglosa correctamente en un entero `3` y un token `DOT` (`.`).
- **Recopilación de Errores:** En lugar de abortar al encontrar el primer carácter ilegal, la función `t_error` registra el error en una lista global (`lexical_errors`) con su correspondiente línea y columna, permitiendo al lexer continuar la lectura para reportar todos los problemas léxicos presentes en el archivo.

---

## 2. Formulación y Diseño de la Gramática (`parser.py`)

La gramática libre de contexto (CFG) para BOT se ha diseñado con la especificación LALR(1) que implementa el generador sintáctico de PLY.

### Resolución de Conflictos y Precedencia:
Se utiliza una gramática ambigua y se resuelven los conflictos mediante reglas explícitas de precedencia y asociatividad, lo cual simplifica la estructura de la gramática. La precedencia está ordenada de menor a mayor prioridad:
1. Asociatividad izquierda para operadores lógicos binarios (`or`, `and`).
2. Asociatividad derecha para la negación lógica (`not`).
3. No asociatividad (`nonassoc`) para los operadores relacionales (`==`, `!=`, `<`, `>`, `<=`, `>=`), evitando construcciones ambiguas y sintácticamente inválidas como `a < b < c`.
4. Asociatividad izquierda para operaciones aritméticas de suma/resta (`+`, `-`) y de multiplicación/división (`*`, `/`).
5. Precedencia especial para el operador menos unario (`UMINUS`).

### Reglas de Producción:
- **Estructura del Programa:** Un programa BOT consta de un bloque de creación `create ...` seguido de un bloque de ejecución `execute ...` y finaliza con `end`.
- **Declaraciones:** Los robots se declaran especificando su tipo (`int` o `bool`), la palabra clave `bot`, el identificador del robot, una lista de bloques de eventos de control (`on activation:` u `on default:`) y finaliza con `end`.
- **Instrucciones:** Las acciones simples de robot (`activate`, `advance`, `decelerate`, `store`) finalizan obligatoriamente con un punto (`.`). Las estructuras de control (`if` y `while`) contienen una condición (guardia) seguida de dos puntos (`:`) y finalizan con la palabra clave `end`.

---

## 3. Construcción del Árbol Sintáctico Abstracto (`bot_ast.py`)

El AST está compuesto por clases bien definidas en [bot_ast.py].

### Representación y Visualización:
Para facilitar la verificación y el cumplimiento exacto del formato solicitado en el enunciado, los nodos se clasifican en:
- **Nodos Simples (In-line):** Representan identificadores y valores constantes (literales). Se imprimen directamente en la línea de la propiedad correspondiente (ej. `operador izquierdo: bar`).
- **Nodos Complejos (Jerárquicos):** Representan instrucciones, condiciones y bloques de secuencia. Estos se imprimen en líneas separadas utilizando un formato indentado secuencial sin anidamientos innecesarios, de manera que la jerarquía relacional se entienda a partir del nombre del tipo de nodo (ej., `guardia: BIN_RELACIONAL`).

*Nota:* Como se especifica en el enunciado, las variables y las instrucciones contenidas dentro de las acciones de los robots se analizan sintácticamente en busca de errores, pero no se representan en la salida del AST. La salida representa exclusivamente las sentencias del bloque `execute`.

---

## 4. Estructura y Punto de Entrada (`main.py`)

El flujo de ejecución coordinado en `main.py` garantiza la correcta separación y jerarquía de reporte de errores:
1. **Fase Léxica:** Se consume la totalidad de los tokens del archivo de entrada. Si se encuentran errores léxicos, se imprimen todos en pantalla y se termina la ejecución con código de salida `1`.
2. **Fase Sintáctica:** Si no hay errores léxicos, se reinicia el lexer y se ejecuta el parser. Al encontrarse un error sintáctico, la función `p_error` captura el token conflictivo, calcula su línea y columna en el archivo fuente, imprime el error correspondiente a la primera falla encontrada y finaliza la ejecución de inmediato.
3. **Fase de Salida:** Si el programa es completamente correcto, se recupera el bloque de instrucciones principales `execute` del AST y se genera la salida jerárquica esperada.

## 5. Instrucciones de Ejecución y Dependencias

Para facilitar la evaluación y garantizar la portabilidad del analizador, se ha incluido el código fuente de la librería **PLY (Python Lex-Yacc)** localmente dentro del directorio del proyecto. 

Para ejecutar el analizador sintáctico sobre un archivo de prueba, simplemente se debe utilizar el script provisto desde la terminal.

**En entornos Linux/WSL:**
./SintBot archivo_de_prueba.bot
**En entornos Windows:**

SintBot.bat archivo_de_prueba.bot