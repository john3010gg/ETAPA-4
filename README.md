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
├── bot                             # Wrapper ejecutable para Linux/Unix
├── bot.bat                         # Wrapper ejecutable para Windows
├── README.md                       # Documentación principal
├── informes/                       # Informes técnicos de todas las etapas
│   ├── informe_etapa_2.md
│   ├── informe_etapa_3.md
│   └── informe_etapa_4.md          # Informe técnico detallado de la Etapa 4
└── Etapa4/                         # Implementación completa de la Etapa Final
    ├── bot                         # Script ejecutable en Linux/LDC
    ├── bot.bat                     # Script ejecutable en Windows
    ├── main.py                     # Punto de entrada del intérprete
    ├── interpreter.py              # Motor de ejecución y simulación dinámica
    ├── context_analyzer.py         # Analizador contextual
    ├── bot_symtable.py             # Tabla de símbolos
    ├── parser.py                   # Analizador sintáctico
    ├── bot_ast.py                  # Jerarquía del AST
    ├── lexer.py                    # Analizador léxico
    ├── ply/                        # Biblioteca PLY embebida
    └── tests/                      # Suite completa de pruebas de la Etapa 4
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
