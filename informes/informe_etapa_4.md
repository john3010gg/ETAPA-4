# Informe Técnico: Intérprete y Verificaciones Dinámicas para BOT (Etapa IV)
**Autores:**
- John Garrido (20-10293)
- Andres Ramirez (21-10520)

**Asignatura:** CI3725 - Traductores e Interpretadores  
**Institución:** Universidad Simón Bolívar (USB)  
**Periodo:** Abril – Julio 2026  

---

## 1. Introducción y Objetivos

El presente informe documenta el diseño, la formulación y la implementación de la **cuarta y última etapa** del proyecto de la asignatura Traductores e Interpretadores. En esta etapa se desarrolló el **intérprete final** para el lenguaje de programación **BOT**, el cual recibe el Árbol Sintáctico Abstracto (AST) generado y validado en las etapas anteriores y procede a su ejecución sobre un entorno de simulación que modela el mundo bidimensional, el estado de los robots y las interacciones con la base humana.

Además de la ejecución de programas válidos, el intérprete incorpora la detección y el reporte estricto de **errores dinámicos** (fallas en tiempo de ejecución no detectables estáticamente), abortando inmediatamente la ejecución ante cualquiera de ellos conforme a lo estipulado en las especificaciones del proyecto.

---

## 2. Arquitectura del Intérprete (`interpreter.py`)

Siguiendo las directrices del enunciado, la ejecución del AST se estructura en torno a dos funciones y procedimientos principales:

1. **`correr(node)`:** Despacha y ejecuta los nodos que representan instrucciones y sentencias de control (`ProgramNode`, `SeqNode`, `ActivateNode`, `DeactivateNode`, `AdvanceNode`, `StoreNode`, `CollectNode`, `DropNode`, `MoveNode`, `ReadNode`, `SendNode`, `IfNode`, `WhileNode`).
2. **`evaluar(node, robot_context)`:** Evalúa recursivamente las expresiones presentes en el programa (`LiteralNode`, `VarNode`, `BinaryOpNode`, `UnaryOpNode`), retornando una tupla `(valor, tipo_dinamico)`.

### 2.1 Modelo de Estado del Entorno

El estado de cómputo del intérprete se compone de tres elementos centrales:

- **Robots (`Robot`):** Cada robot declarado en el bloque `create` se representa con una instancia que encapsula:
  - `name`: Nombre identificador del robot.
  - `type`: Tipo de datos estático y dinámico (`'int'`, `'bool'`, `'char'`).
  - `active`: Booleano que indica si el robot está activo o inactivo (inicialmente `False`).
  - `has_value`: Booleano que indica si el robot almacena algún valor (inicialmente `False`, pues los robots no tienen valor por defecto).
  - `value`: Valor actualmente almacenado.
  - `pos`: Coordenadas `[x, y]` en la superficie, inicializadas en `[0, 0]` (la base humana).
  - `behaviors`: Lista secuencial de bloques de eventos/comportamientos definidos para el robot.

- **Superficie / Matriz Bidimensional (`matrix`):** Representada como una tabla hash (diccionario Python) que mapea coordenadas `(x, y) -> (valor, tipo)`. Al ser una matriz infinita, las posiciones no visitadas están vacías por defecto, lo que garantiza acceso en tiempo $O(1)$ sin consumo innecesario de memoria.

- **Pila de Alcances Locales (`local_scopes`):** Gestiona las variables locales declaradas dentro de un comportamiento (por ejemplo, mediante cláusulas `collect as x` o `read as x`), aislando su visibilidad al tiempo de vida del comportamiento correspondiente.

---

## 3. Semántica de Instrucciones y Ciclo de Vida de los Robots

### 3.1 Activación (`activate`)
Al activarse una lista de robots (de izquierda a derecha):
- Se verifica que el robot no se encuentre ya activo (previniendo **Activación ilegal**).
- Se marca `robot.active = True`.
- Se busca y ejecuta el manejador `on activation:` del robot si fue definido.

### 3.2 Desactivación (`deactivate` / `decelerate`)
Al desactivarse una lista de robots:
- Se verifica que el robot esté activo (previniendo **Desactivación ilegal**).
- Se ejecuta el manejador `on deactivation:` del robot si fue definido.
- Se marca `robot.active = False`.

### 3.3 Avance (`advance`) y Selección de Comportamientos
Al ordenar el avance de un robot:
- Se verifica que el robot esté activo.
- Se evalúan en orden de declaración las guardias de sus comportamientos (excluyendo `activation` y `deactivation`).
- Si una guardia condicional evalúa a `True`, se selecciona dicho comportamiento y finaliza la búsqueda.
- Si ninguna guardia condicional se cumple, pero el robot cuenta con un bloque `on default:`, se selecciona este último.
- Si ninguna guardia se cumple y no existe bloque `default`, se reporta el error dinámico de **Comportamiento inexistente**.
- Se ejecuta el cuerpo de instrucciones del comportamiento seleccionado.

### 3.4 Manipulación de Memoria y Matriz
- **`store <expr>.`:** Evalúa `<expr>` y almacena el resultado en el robot (`me`). Valida que el tipo del valor resultante sea consistente con el tipo del robot (**Almacenamiento inadecuado**).
- **`collect [as <id>].`:** Obtiene el contenido de la celda `(x, y)` donde se ubica el robot. Falla si la celda está vacía o si su tipo no coincide con el del robot (**Colección inadecuada**). Si se especifica `as <id>`, el valor se enlaza a una variable local.
- **`drop <expr>.`:** Evalúa `<expr>` y lo deposita en la celda actual de la matriz. Falla si el tipo del valor no es consistente con el del robot que lo suelta (**Soltado inadecuado**).
- **`left`, `right`, `up`, `down [ <expr> ].`:** Modifica las coordenadas del robot en múltiplos de 1 metro. Falla si la expresión evalúa a un número negativo.

### 3.5 Entrada y Salida
- **`read` / `receive [as <id>].`:** Solicita una entrada por teclado (`stdin`). Verifica que el texto ingresado pueda convertirse estrictamente al tipo esperado por el robot solicitante (**Lectura inadecuada**).
- **`send.`:** Transmite el valor actual de `me` a la salida estándar (`stdout`), permitiendo encadenar caracteres y valores sin saltos de línea forzados (e.g. salida del programa "Hello BOT!" y sucesión de Fibonacci).

---

## 4. Verificación y Manejo de Errores Dinámicos

Todos los errores dinámicos son reportados con el formato estandarizado y uniforme, abortando inmediatamente la ejecución con código de salida `1` (`sys.exit(1)`):

`Error en tiempo de ejecucion en la linea <L>: <Mensaje de Error>`

A continuación se detallan las verificaciones implementadas:

| Error Dinámico | Condición de Detección | Comportamiento |
| :--- | :--- | :--- |
| **Activación ilegal** | Ejecutar `activate` sobre un robot que ya tiene `active == True`. | Aborta reportando intento de activar robot ya activo. |
| **Desactivación ilegal** | Ejecutar `deactivate` sobre un robot inactivo (`active == False`). | Aborta reportando intento de desactivar robot inactivo. |
| **Comportamiento inexistente** | Ejecutar `advance` sin que ninguna guardia condicional sea `True` y en ausencia de `default`. | Aborta reportando que ninguna guardia se cumplió. |
| **División por cero** | Operaciones de división entera (`/`) o módulo (`%`) con denominador igual a `0`. | Aborta reportando división o módulo por cero. |
| **Lectura inadecuada** | Entrada recibida por `read`/`receive` inconsistente con el tipo del robot (ej. texto alfanumérico para robot `int`). | Aborta reportando lectura incompatible con el tipo del robot. |
| **Colección inadecuada** | Ejecutar `collect` sobre una celda vacía de la matriz o cuyo tipo difiera del robot. | Aborta reportando celda vacía o inconsistencia de tipos. |
| **Almacenamiento inadecuado** | Ejecutar `store` con una expresión cuyo valor dinámico difiere del tipo del robot. | Aborta reportando almacenamiento de tipo inconsistente. |
| **Soltado inadecuado** | Ejecutar `drop` con un valor inconsistente con el robot que lo suelta. | Aborta reportando soltado de tipo incompatible. |
| **Variable no inicializada** | Uso de un robot o variable sin valor asignado en una expresión. | Aborta reportando variable no inicializada. |
| **Movimiento inválido** | Expresión de desplazamiento con magnitud negativa. | Aborta reportando desplazamiento inválido. |

---

## 5. Instrucciones de Ejecución y Compatibilidad con el LDC

Para asegurar total portabilidad y cumplimiento estricto con los requerimientos de entrega en el Laboratorio Docente de Computación (**LDC**):

- Se creó el script ejecutable `./bot` para entornos Unix/Linux:
  ```bash
  chmod +x bot
  ./bot programa.bot
  ```
- Se creó el script auxiliar `bot.bat` para entornos Windows:
  ```cmd
  bot.bat programa.bot
  ```
- Las dependencias externas se encuentran completamente auto-contenidas (el paquete `ply` está incrustado en el propio repositorio), requiriendo únicamente una instalación estándar de Python 3.
