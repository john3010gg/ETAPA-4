# BOT - Intérprete y Verificaciones Dinámicas (Etapa IV)

**Asignatura:** CI3725 - Traductores e Interpretadores  
**Institución:** Universidad Simón Bolívar (USB)  
**Periodo:** Abril – Julio 2026  

### Autores
- **John Garrido** (20-10293)
- **Andres Ramirez** (21-10520)

---

## 📌 Descripción del Proyecto

Este repositorio contiene la implementación completa y final del lenguaje de programación **BOT**, desarrollado en Python 3 para la asignatura CI3725 (Traductores e Interpretadores) de la Universidad Simón Bolívar.

El sistema comprende las cuatro etapas del proceso de traducción e interpretación:
1. **Análisis Léxico (`lexer.py`):** Tokenizador implementado con PLY (Python Lex-Yacc), reconociendo palabras clave, operadores, literales tipados y directivas de depuración.
2. **Análisis Sintáctico y Construcción del AST (`parser.py`, `bot_ast.py`):** Gramática libre de contexto LALR con resolución de precedencia de operadores, soporte para anidamiento y generación del Árbol Sintáctico Abstracto.
3. **Análisis de Contexto y Verificaciones Estáticas (`context_analyzer.py`, `bot_symtable.py`):** Comprobación de tipos, control de alcances de variables locales/globales y detección de errores estáticos.
4. **Intérprete y Verificaciones Dinámicas (`interpreter.py`, `main.py`):** Entorno de simulación de robots en una matriz infinita, despacho de comportamientos (`advance`, `activation`, `deactivation`), manipulación de memoria (`store`, `collect`, `drop`, desplazamientos) y detección estricta de errores en tiempo de ejecución.

---

## 📁 Estructura del Repositorio

```text
Traductores-Final/
├── bot                             # Script ejecutable para Linux/Unix
├── bot.bat                         # Script ejecutable para Windows
├── main.py                         # Punto de entrada principal
├── interpreter.py                  # Motor del intérprete y verificaciones dinámicas
├── context_analyzer.py             # Analizador contextual / chequeador de tipos
├── bot_symtable.py                 # Tabla de símbolos y manejo de alcances
├── parser.py                       # Analizador sintáctico (PLY yacc)
├── bot_ast.py                      # Clases y jerarquía de nodos del AST
├── lexer.py                        # Analizador léxico (PLY lex)
├── ply/                            # Biblioteca PLY embebida (sin dependencias externas)
├── informes/                       # Informes técnicos de las entregas
│   ├── informe_etapa_2.md
│   ├── informe_etapa_3.md
│   └── informe_etapa_4.md          # Informe técnico detallado de la Etapa 4
└── tests/                          # Batería de pruebas automatizadas
    ├── test_hello_bot.bot          # Prueba completa (imprime "Hello BOT!")
    ├── test_fibonacci.bot          # Prueba completa (sucesión de Fibonacci)
    ├── test_dinamico_01_*.bot      # Activación ilegal
    ├── test_dinamico_02_*.bot      # Desactivación ilegal
    ├── test_dinamico_03_*.bot      # Comportamiento inexistente
    ├── test_dinamico_04_*.bot      # División por cero
    ├── test_dinamico_05_*.bot      # Lectura inadecuada
    ├── test_dinamico_06_*.bot      # Colección inadecuada
    ├── test_dinamico_07_*.bot      # Almacenamiento inadecuado
    ├── test_dinamico_08_*.bot      # Soltado inadecuado
    └── test00_*.bot ... test10_*.bot # Pruebas estáticas y sintácticas
```

---

## 🚀 Instrucciones de Uso

El proyecto es completamente autocontenido y solo requiere una instalación estándar de **Python 3**.

### En Linux / macOS / LDC:
```bash
chmod +x bot
./bot tests/test_hello_bot.bot
```

### En Windows:
```cmd
bot.bat tests\test_hello_bot.bot
```

O directamente mediante Python:
```bash
python main.py tests/test_hello_bot.bot
```

---

## 🧪 Ejecución de Pruebas

Para ejecutar el programa de bienvenida:
```bash
./bot tests/test_hello_bot.bot
# Salida: Hello BOT!
```

Para ejecutar el cálculo de la serie de Fibonacci:
```bash
./bot tests/test_fibonacci.bot
# Salida: 011235
```

---

## ⚠️ Manejo de Errores Dinámicos

Todos los errores dinámicos son capturados durante la simulación y reportados en el formato exigido:

```text
Error en tiempo de ejecucion en la linea <L>: <Mensaje de Error>
```

El proceso finaliza inmediatamente con código de salida `1` (`sys.exit(1)`).
