# Informe Técnico: Analizador de Contexto para BOT (ContBot)
John Garrido 20-10293
Andres Ramirez 21-10520

Este informe detalla la formulación, diseño e implementación de la tercera etapa del proyecto, correspondiente al análisis de contexto (verificación de errores estáticos) sobre el Árbol Sintáctico Abstracto (AST) del lenguaje **BOT**, construido en la etapa anterior.

---

## 1. Tabla de Símbolos (`symtable.py`)

La tabla de símbolos se implementó como una pila de alcances (`scopes`), donde cada alcance es un diccionario Python (estructura de hash) que mapea `nombre_variable -> tipo`. Usar diccionarios garantiza inserción y búsqueda en tiempo promedio O(1), tal como recomienda el enunciado.

- **`push_scope()` / `pop_scope()`:** añaden y eliminan un nivel de alcance al entrar y salir de una estructura que introduce un nuevo ámbito.
- **`define(name, type)`:** declara una variable únicamente en el alcance **más interno** (el tope de la pila). Si el nombre ya existe en ese mismo alcance, retorna `False` (redeclaración); si el nombre existe en un alcance más externo, no hay conflicto y la declaración procede con normalidad.
- **`lookup(name)`:** recorre los alcances desde el más interno hacia el más externo (`reversed(self.scopes)`) y retorna el tipo del primer alcance donde se encuentre el nombre, o `None` si no aparece en ninguno.

### Alcances en BOT
En el lenguaje BOT los alcances se manejan así:
- Existe un alcance **global** donde se declaran los nombres de los robots (`create ... bot NOMBRE ...`).
- Cada bloque de evento (`on activation:`, `on default:`, etc.) de un robot abre su **propio alcance interno**, en el cual se declara implícitamente la palabra reservada `me` con el tipo del robot dueño del comportamiento.
- Las estructuras `if` y `while` también empujan un alcance propio para su cuerpo.

---

## 2. Analizador de Contexto (`context_analyzer.py`)

Se implementó con el **patrón Visitor**: un método `visit_<TipoDeNodo>` por cada clase de nodo del AST, despachado dinámicamente mediante `getattr` sobre `type(node).__name__`. Cada método retorna, cuando aplica, el **tipo estático** del subárbol visitado (`'int'`, `'float'`, `'bool'` o `'error'`), lo que permite que los nodos padres validen sus propias reglas de tipo sin recorrer el árbol de nuevo.

### 2.1 Errores estáticos verificados
Siguiendo el enunciado, se detectan y reportan **todos** los errores estáticos presentes (no se aborta en el primero):

1. **Variable no declarada:** al visitar un `VarNode`, o al usar un identificador en `activate`, `advance` o `decelerate`, se hace `lookup` en la tabla de símbolos; si no existe, se reporta el error.
2. **Redeclaración en el mismo alcance:** al declarar un robot (`visit_RobotDeclNode`) se usa `symtable.define`; si retorna `False`, se reporta la redeclaración.
3. **Uso de `me` fuera de un comportamiento:** como `me` solo se define al entrar a un bloque de evento, si `lookup('me')` falla y el nombre buscado es literalmente `'me'`, se emite un mensaje específico distinto al de "variable no declarada" genérica.
4. **Errores de tipo:** se valida que
   - las operaciones aritméticas (`+ - * /`) reciban operandos numéricos (`int`/`float`),
   - las operaciones relacionales de orden (`< > <= >=`) reciban numéricos, mientras que `==`/`!=` aceptan además comparar dos booleanos entre sí,
   - las operaciones lógicas (`and`, `or`, `not`) reciban booleanos,
   - el `store` sea compatible con el tipo del robot dueño del comportamiento (`me`): un robot `int` acepta expresiones `int` o `float`; un robot `bool` exige una expresión `bool`,
   - la guardia de `if`/`while` sea de tipo `bool`.


### 2.2 Detalle de implementación: tratamiento de literales `float`
El lexer (`lexer.py`) reconoce por separado los tokens `NUMBER` (enteros) y `FLOAT` (con parte decimal, `\d+\.\d+`), convirtiendo su valor de texto a `int` o `float` de Python respectivamente desde la propia regla léxica. Esta distinción se preserva en el AST: un `LiteralNode` guarda el valor ya tipado (`int` o `float` de Python), y `visit_LiteralNode` en el analizador de contexto usa `isinstance(node.value, float)` / `isinstance(node.value, int)` para derivar el tipo estático `'float'` o `'int'` del literal (verificando `bool` primero, ya que en Python `bool` es subclase de `int`).

Esto tiene una consecuencia directa sobre las reglas de tipo:
- En operaciones **aritméticas**, si cualquiera de los operandos es `float`, el resultado se tipa como `float`; solo si ambos son `int` el resultado es `int`. Así, `3 + 2` es `int`, pero `3 + 2.5` es `float`.
- En **comparaciones** (relacionales) y en el **store**, `int` y `float` se tratan como mutuamente compatibles (ambos son "numéricos"), ya que se evalúan sobre el mismo dominio numérico; por ejemplo, un robot `int bot` puede recibir `store 3.5.` sin error de tipo, y `bar > 2.5` es una comparación válida aunque `bar` sea `int` y `2.5` sea `float`.
- Un `float` nunca es compatible con `bool`, por lo que expresiones como `store true` en un robot numérico, o `3.5 and true`, siguen siendo detectadas como errores de tipo.

### 2.3 Alcance de la impresión del AST
Al igual que en la etapa anterior, si el programa no presenta errores léxicos, sintácticos ni de contexto, se imprime únicamente el AST del bloque `execute` (no las declaraciones de robots ni el contenido de sus comportamientos), respetando el formato de nodos simples (en línea) y nodos complejos (jerárquicos e indentados) definido en la etapa 2.

---

## 4. Pruebas realizadas

Se verificó el comportamiento con casos que cubren cada categoría de error, además de un programa válido:

- Archivo sin errores → imprime el AST del `execute`.
- Archivo con errores léxicos → se listan todos, sin arrastrar errores sintácticos.
- Archivo con error sintáctico → se imprime solo el primero.
- Archivo con múltiples errores de contexto simultáneos (redeclaración de robot, variable no declarada, error de tipo en `store`, error de tipo en operación aritmética) → se listan todos, en el orden en que aparecen al recorrer el AST.
- Uso de `me` fuera de un bloque de evento → mensaje específico de palabra reservada mal utilizada.
