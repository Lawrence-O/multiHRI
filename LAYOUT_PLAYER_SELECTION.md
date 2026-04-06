# Layout Player Selection: Which 2 Players to Keep

For each 3-chef and 5-chef layout, we show the grid, player spawn positions, and
recommend which 2 players to keep so that both sides of the map / all key areas
remain accessible.

Legend: `X`=wall, `O`=onion, `D`=dish, `P`=pot, `S`=serve, `1-5`=player spawns, ` `=floor

---

## 3-Chef Layouts

### 3_chefs_cramped_room (5×5)

```
XDPXX
X  2P
O1  D
X 3 X
XSOXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (1,2) | Left side, mid row |
| 2 | (3,1) | Right side, top row |
| 3 | (2,3) | Center, bottom row |

**Keep: 1, 2** — They are on opposite sides (left vs right). Player 3 is in the middle, redundant.

---

### 3_chefs_coordination_ring (6×6)

```
XXXPPX
X 1  P
X2XX X
D XX3X
O    X
XODXSX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,1) | Top-left area |
| 2 | (1,2) | Left side |
| 3 | (4,3) | Right side, behind wall |

**Keep: 1, 3** — Player 1 is top-left, player 3 is right side. Gives coverage of both halves. Player 2 is adjacent to player 1.

---

### 3_chefs_counter_circuit (7×5)

```
XXPXPXX
X  2  X
S XXX S
X 1 3 X
XXODOXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,3) | Bottom-left |
| 2 | (3,1) | Top-center |
| 3 | (4,3) | Bottom-right |

**Keep: 1, 2** — Player 1 bottom-left, player 2 top-center — covers both loops of the circuit. (Alternatively **1, 3** for bottom-left vs bottom-right.)

---

### 3_chefs_asymmetric_advantages (9×6)

```
XXXXXXXXX
S   P   S
X2  X  1X
XPDOXODPX
X   3   X
XXXXSXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (7,2) | Right kitchen |
| 2 | (1,2) | Left kitchen |
| 3 | (4,4) | Bottom center |

**3 ISOLATED ZONES** — center X (col 4) and counter row (XPDOXODPX) split the map into 3 independent kitchens. Each zone has O, P, D, S — fully self-sufficient, so agents work **independently** with no coordination.

**Keep: 1, 2** — Left kitchen vs right kitchen. Note: agents cannot interact at all (separate zones).

---

### 3_chefs_forced_coordination (7×5)

```
XXXXXXX
O X1P D
O2X P3D
X X X X
XXXXXSX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (3,1) | Center corridor (col 3) — pots on right wall, counter on left wall |
| 2 | (1,2) | Left corridor (col 1) — onion dispensers on left wall |
| 3 | (5,2) | Right corridor (col 5) — dish dispensers, serve tile, pot access |

Three **fully isolated** corridors separated by walls at col 2 and col 4. This is a 3-player relay pipeline: onions (left/P2) → counter → pot (center/P1) → plate+serve (right/P3). All three corridors are essential — no 2-player reduction preserves the full pipeline.

**Keep: 2, 3** — Left (onions) + right (dish/serve/pot). Skips center relay but keeps the two endpoints. Won't be optimal but avoids OOD.

---

### 3_chefs_secret_heaven (12×7)

```
XODSXXXXSDXX
X          X
S PP XX    X
D PP OX 1  X
O PP DX 2  X
X    SX 3  X
XSDOXXXXOPXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (8,3) | Right side, upper |
| 2 | (8,4) | Right side, middle |
| 3 | (8,5) | Right side, lower |

All 3 players are clustered on the right side! The left side (with pots, resources) is empty.

**Keep: 1, 3** — Maximises vertical spread on the right side (top vs bottom). But NOTE: all players start on the same side — no player starts near the left-side resources.

---

### 3_chefs_storage_room (8×5)

```
XXSXXXXX
X1   XXX
X2    OX
X3   XXX
XXPXDXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (1,1) | Left column, top |
| 2 | (1,2) | Left column, mid |
| 3 | (1,3) | Left column, bottom |

All 3 players in a column on the left.

**Keep: 1, 3** — Top vs bottom gives max vertical spread. All share the same open area so position doesn't matter much.

---

### 3_chefs_island_kitchen (7×6)

```
XXXSSXX
X    1X
X2 P  D
X  P  D
O    3X
XOXXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (5,1) | Top-right |
| 2 | (1,2) | Left side |
| 3 | (5,4) | Bottom-right |

**Keep: 2, 3** — Player 2 left side, player 3 bottom-right — good diagonal coverage. (Or **1, 2** for top-right vs left.)

---

### 3_chefs_long_onion (13×9)

```
XOXXXXDXXXXXX
X XX        X
X XX      X X
X XX X X XX X
X XD3 P 2DX X
X XX X X XX X
X X   1  XX X
X        XX X
XXXXXXSXXXXOX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (6,6) | Bottom-center |
| 2 | (8,4) | Center-right |
| 3 | (4,4) | Center-left |

**Keep: 2, 3** — Left vs right of the central corridor. Player 1 is below them. (Or **1, 3** for bottom vs center-left.)

---

### 3_chefs_unequal_kitchens (13×8)

```
XXXXXDXDXXXXX
X   P   P   X
X DXP   PXD X
X   O   O   X
XX XXX XXX XX
X           X
X 1   2   3 X
XXXXXXSXXXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,6) | Bottom-left |
| 2 | (6,6) | Bottom-center |
| 3 | (10,6) | Bottom-right |

All 3 on the bottom row, evenly spaced — accessing 3 separate kitchen areas above them.

**Keep: 1, 3** — Left vs right, maximises horizontal spread across different kitchens.

---

### 3_chefs_clustered_kitchen (13×5)

```
XXXXPXXXOXXXX
S  1 XXX    D
D     2   3 S
X    XXX    X
XOXXXXXXPXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (3,1) | Left side, top row |
| 2 | (6,2) | Center |
| 3 | (10,2) | Right side |

**Keep: 1, 3** — Left vs right, separated by the central wall.

---

## 5-Chef Layouts

### 5_chefs_counter_circuit (11×5)

```
XXPXPXPXPXX
X  2   4  X
S XXXXXXX S
X 1  3  5 X
XXODOXODOXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,3) | Bottom-left |
| 2 | (3,1) | Top-left |
| 3 | (5,3) | Bottom-center |
| 4 | (7,1) | Top-right |
| 5 | (8,3) | Bottom-right |

**Keep: 1, 4** — Bottom-left vs top-right, diagonal coverage of both corridors. (Or **2, 5** for top-left vs bottom-right.)

---

### 5_chefs_asymmetric_advantages (11×7)

```
XXXXXXXXXXX
S  4 O 5  S
D    P    D
P2   X  1 P
XXOPDXDPOXX
X   3     X
XXXXXSXXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (8,3) | Right kitchen |
| 2 | (1,3) | Left kitchen |
| 3 | (4,5) | Bottom-left |
| 4 | (3,1) | Top-left |
| 5 | (7,1) | Top-right |

**3 ISOLATED ZONES** — center X (col 5) and counter row split the map. Zone left: players 2,4 (O,P,D,S). Zone right: players 1,5 (O,P,D,S). Zone bottom: player 3 (O,P,D,S). Each zone fully self-sufficient — agents work **independently**.

**Keep: 1, 2** — Right kitchen vs left kitchen. Note: agents cannot interact at all (separate zones).

---

### 5_chefs_cramped_room (7×5)

```
XDPXOSX
X  2  P
O1  4 D
X 3  5O
XSOXOSX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (1,2) | Left side |
| 2 | (3,1) | Top-center |
| 3 | (2,3) | Bottom-left |
| 4 | (4,2) | Center-right |
| 5 | (5,3) | Bottom-right |

**Keep: 1, 5** — Left vs far-right, diagonal coverage. (Or **1, 4** for left vs center-right.)

---

### 5_chefs_coordination_ring (7×6)

```
XDDXXXX
P 1   S
X 2X4 X
X 3X5 X
P     S
XOOXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,1) | Left side, top |
| 2 | (2,2) | Left side, mid |
| 3 | (2,3) | Left side, bottom |
| 4 | (4,2) | Right side, top |
| 5 | (4,3) | Right side, bottom |

Two groups separated by central wall: left (1,2,3) and right (4,5).

**Keep: 1, 4** — One from each side (left-top vs right-top). (Or **3, 4** for left-bottom vs right-top.)

---

### 5_chefs_forced_coordination (9×6)

```
XXXXXXXSX
O  X  P X
O2 X1 P3D
O  X  P X
O4 X5 P X
XXXXXXXSX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (4,2) | Middle corridor (col 4-5) — pot access |
| 2 | (1,2) | Left corridor (col 1-2) — onion dispensers |
| 3 | (7,2) | Right corridor (col 7) — dish, serve, pot access |
| 4 | (1,4) | Left corridor (col 1-2) — same as P2 |
| 5 | (4,4) | Middle corridor (col 4-5) — same as P1 |

**3 ISOLATED ZONES** — walls at col 3 (X) and col 6 (P) create a 3-corridor relay pipeline:
- Left (col 1-2): players 2,4 — only onions (O). Missing D, P, S.
- Middle (col 4-5): players 1,5 — only pots (P). Missing D, O, S.
- Right (col 7): player 3 — dish (D), serve (S), pot (P). Missing O.

Pipeline: onion (left) → counter → cook (middle) → plate/serve (right). No 2-player pair preserves the full pipeline.

**Keep: 2, 1** — Left (onion) + middle (pots). Won't be optimal (no plate/serve access) but avoids OOD.

---

### 5_chefs_secret_heaven (12×7)

```
XODSXXXXSDXX
X          X
S PP XX    X
D PP OX 1  X
O PP DX 23 X
X    SX 45 X
XSDOXXXXOPXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (8,3) | Right side, row 3 |
| 2 | (8,4) | Right side, row 4 |
| 3 | (9,4) | Right side, row 4 (offset) |
| 4 | (8,5) | Right side, row 5 |
| 5 | (9,5) | Right side, row 5 (offset) |

All players clustered on the right side — no player on the left (resource side).

**Keep: 1, 4** — Max vertical spread within the right cluster (row 3 vs row 5).

---

### 5_chefs_storage_room (12×5)

```
XXXXXXXXXXXX
S 1 XODX 4 S
P 2        P
X 3 XDOX 5 X
XXXXXXXXXXXX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,1) | Left side, top |
| 2 | (2,2) | Left side, mid |
| 3 | (2,3) | Left side, bottom |
| 4 | (9,1) | Right side, top |
| 5 | (9,3) | Right side, bottom |

Symmetrical: left group (1,2,3) and right group (4,5).

**Keep: 1, 5** — Left-top vs right-bottom, diagonal max spread. (Or **1, 4** for left-top vs right-top.)


---

### 5_chefs_central_chaos (11×9)

```
XOXPXSXPXOX
X    1    X
P 2     3 P
X   XDX   X
S X  4  X S
X   XDX   X
P 5       P
X         X
XOXPXSXPXOX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (5,1) | Top-center |
| 2 | (2,2) | Left side |
| 3 | (8,2) | Right side |
| 4 | (5,4) | Center |
| 5 | (2,6) | Bottom-left |

**Keep: 3, 5** — Right-upper vs bottom-left, good diagonal spread. (Or **2, 3** for left vs right.)

---

### 5_chefs_maze_of_ambiguity (11×9)

```
XPXSXPXSXPX
X 1   2   X
XOX X X XOX
X    3    X
XDXXXXXXDXX
X    4    X
XOX X X XOX
X 5       S
XPXSXPXSXPX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,1) | **TOP half**, left |
| 2 | (6,1) | **TOP half**, right |
| 3 | (5,3) | **TOP half**, center |
| 4 | (5,5) | **BOTTOM half**, center |
| 5 | (2,7) | **BOTTOM half**, left |

**2 ISOLATED ZONES** — the central wall `XDXXXXXXDXX` (row 4) completely splits the map:
- Top half (rows 0-3): players 1, 2, 3 — has O, P, D, S (self-sufficient)
- Bottom half (rows 5-8): players 4, 5 — has O, P, D, S (self-sufficient)

Each half can independently cook and serve. Agents in different halves **cannot interact**.

**Keep: 1, 4** — One from each half (top-left vs bottom-center). Ensures both halves of the maze are covered. (Or **2, 5** for top-right vs bottom-left.)

---

### 5_chefs_ring_of_confusion (11×9)

```
XPXOXDXOXPX
X 1  S  2 X
X    X    X
O  X 3 X  O
S X  4  X S
O  X 5 X  O
X    X    X
X    S    X
XPXOXDXOXPX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (2,1) | Top-left outer ring |
| 2 | (8,1) | Top-right outer ring |
| 3 | (5,3) | Center-upper inner ring |
| 4 | (5,4) | Center inner ring |
| 5 | (5,5) | Center-lower inner ring |

Outer ring: players 1, 2 (left/right). Inner ring: players 3, 4, 5.

**Keep: 1, 2** — Left vs right in the outer ring, symmetric coverage. Access to both sides' resources. (Or **1, 4** for outer-left vs inner-center.)

---

### 5_chefs_storage_room_lots_resources (12×5)

```
XXOOOPOOOOXX
XD        DX
D  12345   D
P          P
XPSSSDDSSPPX
```

| Player | Position | Location notes |
|--------|----------|----------------|
| 1 | (3,2) | Center-left |
| 2 | (4,2) | Center |
| 3 | (5,2) | Center |
| 4 | (6,2) | Center |
| 5 | (7,2) | Center-right |

All 5 in a line in the center row. Symmetric open room.

**Keep: 1, 5** — Max horizontal spread (leftmost vs rightmost of the line).

---

## Summary Table

| Layout | Keep | Rationale |
|--------|------|-----------|
| **3-chef** | | |
| 3_chefs_cramped_room | **1, 2** | Left vs right |
| 3_chefs_coordination_ring | **1, 3** | Top-left vs right side |
| 3_chefs_counter_circuit | **1, 2** | Bottom-left vs top-center |
| 3_chefs_asymmetric_advantages | **1, 2** | Left kitchen vs right kitchen (isolated zones) |
| 3_chefs_forced_coordination | **2, 3** | Left corridor + right corridor (isolated relay) |
| 3_chefs_secret_heaven | **1, 3** | Right-top vs right-bottom (all right side) |
| 3_chefs_storage_room | **1, 3** | Top vs bottom (all left column) |
| 3_chefs_island_kitchen | **2, 3** | Left side vs bottom-right |
| 3_chefs_long_onion | **2, 3** | Center-right vs center-left |
| 3_chefs_unequal_kitchens | **1, 3** | Bottom-left vs bottom-right |
| 3_chefs_clustered_kitchen | **1, 3** | Left vs right |
| **5-chef** | | |
| 5_chefs_counter_circuit | **1, 4** | Bottom-left vs top-right diagonal |
| 5_chefs_asymmetric_advantages | **1, 2** | Left kitchen vs right kitchen (isolated zones) |
| 5_chefs_cramped_room | **1, 5** | Left vs far-right |
| 5_chefs_coordination_ring | **1, 4** | Left side vs right side |
| 5_chefs_forced_coordination | **2, 1** | Left corridor + middle corridor (isolated relay) |
| 5_chefs_secret_heaven | **1, 4** | Right-row3 vs right-row5 (all right) |
| 5_chefs_storage_room | **1, 5** | Left-top vs right-bottom |
| 5_chefs_central_chaos | **3, 5** | Right-upper vs bottom-left diagonal |
| 5_chefs_maze_of_ambiguity | **1, 4** | Top half vs bottom half (isolated zones) |
| 5_chefs_ring_of_confusion | **1, 2** | Outer ring left vs outer ring right |
| 5_chefs_storage_room_lots_resources | **1, 5** | Leftmost vs rightmost in row |

> **Note**: The "keep" column lists which original player numbers to retain.
> The dropped players' grid digits will be replaced with spaces.
> The kept players will be renumbered to **1** and **2** (in the order listed).

---

## TODO

- [ ] **Forced coordination layouts** (`2_on_3chefs_forced_coordination`, `2_on_5chefs_forced_coordination`): Skipped from SP training because isolated corridors have incomplete resource sets (no 2-player pair can complete a dish). Generate demonstration data for these layouts using a **motion planner** instead.
