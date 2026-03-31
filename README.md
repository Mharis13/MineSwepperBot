# MineSwepperBot 🤖💣

Bot de Buscaminas escrito en Python puro. Este repositorio es una **base esqueleto**
para que lo implementes tú paso a paso. Cada archivo tiene comentarios `TODO` que
te guían exactamente qué hacer en cada función.

## Estructura del proyecto

```
MineSwepperBot/
├── minesweeper/
│   ├── __init__.py      # API pública (no necesitas tocarlo)
│   ├── game.py          # PASO 1 — Motor del juego
│   ├── solver.py        # PASO 2 — Solucionador con restricciones
│   ├── bot.py           # PASO 3 — Bot + estadísticas
│   └── display.py       # PASO 4 — Visualización en terminal
├── tests/
│   ├── test_game.py     # Tests del motor (con @skip hasta que implementes)
│   └── test_solver.py   # Tests del solucionador (con @skip hasta que implementes)
├── main.py              # CLI (ya está hecho, no lo toques hasta el final)
└── requirements.txt     # Solo pytest
```

---

## Plan paso a paso

### Paso 1 — Motor del juego (`minesweeper/game.py`)

El motor es la base de todo. Implementa los métodos en este orden:

| Sub-paso | Método | Qué hace |
|---|---|---|
| 1a | `neighbors(row, col)` | Devuelve los 8 vecinos válidos de una celda |
| 1b | `_place_mines(safe_row, safe_col)` | Coloca minas después del 1er click, zona 3×3 segura |
| 1c | `reveal(row, col)` | Revela una celda; gestiona el 1er click y estadísticas |
| 1d | `_reveal_cell(row, col)` | Reveal interno + flood-fill recursivo para celdas vacías |
| 1e | `flag(row, col)` | Alterna bandera en una celda oculta |
| 1f | `chord(row, col)` | Revela vecinos cuando el número está satisfecho por banderas |
| 1g | `_check_win()` | Detecta la victoria |
| — | `elapsed_time`, `remaining_mines`, `hidden_count` | Propiedades de consulta |

**Cómo probar:** descomenta los tests de `tests/test_game.py` según avances.

```bash
python -m pytest tests/test_game.py -v
```

---

### Paso 2 — Solucionador (`minesweeper/solver.py`)

Con el motor funcionando, implementa la inteligencia del bot:

| Sub-paso | Método | Qué hace |
|---|---|---|
| 2a | `_get_constraints()` | Extrae restricciones `{celdas} → K minas` de las celdas número |
| 2b | `_deduce()` (trivial) | Si K=0 → todas seguras; si K=\|celdas\| → todas minas |
| 2c | `_deduce()` (subconjunto) + `_subtract()` | Deriva nuevas restricciones por diferencia de conjuntos |
| 2d | `_best_guess()` | Estima probabilidades y elige la celda menos peligrosa |
| — | `next_move()` | Une los pasos anteriores y devuelve la jugada recomendada |

**Algoritmo de deducción (iteración hasta punto fijo):**
```
1. Para cada restricción C:
     - Si C.mines == 0          → todas C.cells son SEGURAS
     - Si C.mines == len(C.cells) → todas C.cells son MINAS
2. Para cada par (C1, C2):
     - Si C1.cells ⊆ C2.cells  → nueva restricción: C2-C1 con (K2-K1) minas
3. Repite hasta que no haya cambios
```

**Cómo probar:**
```bash
python -m pytest tests/test_solver.py -v
```

---

### Paso 3 — Bot y estadísticas (`minesweeper/bot.py`)

Une el motor y el solucionador en un bucle completo:

| Sub-paso | Qué implementar |
|---|---|
| 3a | `GameResult.efficiency` — fracción de reveals deterministas |
| 3b | `Statistics` — total, wins, win_rate, avg_time, best_time, summary() |
| 3c | `Bot.run_once()` — bucle solver → acción → juego hasta fin de partida |
| 3d | `Bot.run_batch(n)` — N partidas con progreso y estadísticas acumuladas |

---

### Paso 4 — Visualización (`minesweeper/display.py`) *(opcional)*

Implementa `render(game)` para ver el tablero en la terminal:

```
     0  1  2  3  4  5  6  7  8
    +--------------------------+
  0 | .  .  .  1  .  .  .  .  . |
  1 | .  1  1  2  .  .  .  .  . |
  ...
    +--------------------------+
  Status: ONGOING  |  Mines left:  10  |  Time: 5.2 ms
```

Leyenda: `.` oculta, `F` bandera, ` ` vacía, `1-8` número, `*` mina (al perder), `X` mina explotada.

---

### Paso 5 — Prueba el CLI

Cuando todos los pasos anteriores funcionen, prueba el CLI:

```bash
# Una partida Beginner con verbose
python main.py --difficulty beginner --verbose

# 100 partidas Intermediate con estadísticas
python main.py --difficulty intermediate --games 100

# Una partida con tablero visible (necesita el Paso 4)
python main.py --difficulty beginner --display

# Tablero personalizado con semilla fija
python main.py --custom 10 10 15 --games 50 --seed 42
```

---

## Cómo ejecutar los tests

```bash
# Instalar pytest (solo una vez)
pip install -r requirements.txt

# Ejecutar todos los tests (los marcados con @skip se omitirán)
python -m pytest tests/ -v

# Solo los tests que ya no están en skip
python -m pytest tests/ -v -k "not skip"
```

A medida que implementes cada función, **borra el `@pytest.mark.skip`** del test
correspondiente y comprueba que pasa.

---

## Consejos

- **Empieza siempre por el Paso 1**; el Solver no puede funcionar sin el motor.
- **Usa semillas aleatorias** (`random.seed(42)`) para reproducir errores.
- **El flood-fill** (Paso 1d) es recursivo; en tableros grandes puede provocar
  `RecursionError`. Si te pasa, usa una pila explícita (lista + while).
- **El solucionador** nunca debe marcar como mina una celda de la que no esté
  100 % seguro. El fallback probabilístico solo se usa cuando no hay jugada determinista.

