# Overcooked Layouts with N > 2 Players

This document catalogs all available Overcooked layouts supporting more than 2 players. There are **83 layouts** total across 3, 4, and 5-player configurations.

> **Legend**: `P` = Pot, `O` = Onion, `D` = Delivery, `S` = Serving, `T` = Tomato, `X` = Wall, `1-5` = Player spawn

---

## Layouts Currently Used by This Project

Defined in `scripts/utils/layout_config.py`:

### `complex_3_chefs_layouts` (teammates_len=2, num_players=3)

| Layout | Grid | Description |
|--------|------|-------------|
| `dec_3_chefs_storage_room` | 8×5 | Asymmetric room with players stacked on the left, single pot/onion/delivery. Tests how 3 agents divide simple tasks with limited resources. |
| `dec_3_chefs_secret_heaven` | 12×7 | Same large map as 2-chef version — resource-rich hidden room on left, players packed on right. Tests whether agents discover and exploit the secret room. |
| `dec_3_chefs_counter_circuit` | 7×5 | Loop track with central wall. Players split across top/bottom tracks. Tests circular coordination with a third agent. |

### `complex_5_chefs_layouts` (teammates_len=4, num_players=5)

| Layout | Grid | Description |
|--------|------|-------------|
| `dec_5_chefs_counter_circuit` | 11×5 | Extended loop with 4P, 3O, 2D, 2S. Even/odd players on top/bottom tracks. Tests large-team counter-passing in a circuit. |
| `dec_5_chefs_storage_room` | 12×5 | Symmetric map with central resource islands, players split left (1,2,3) and right (4,5). Tests team division in a mirrored layout. |
| `dec_5_chefs_secret_heaven` | 12×7 | Same grid as 2-chef version, 5 players squeezed into the right side. Tests congestion management in a resource-rich environment. |
| `selected_5_chefs_spacious_room_no_counter_space` | 10×6 | Wide open room, resources on all walls, no counter tiles for item passing. Forces direct hand-off coordination. |

---

## All Available N > 2 Layouts

### 3-Player Layouts (46 maps)

#### Category: Core Map Adaptations

Standard multi-chef versions of classic 2-player maps, redesigned with expanded grids and additional resources.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `3_chefs_asymmetric_advantages` | 9×6 | Redesigned with central wall, 3 serving points, player 3 at bottom. | Tests asymmetric resource access with 3 agents — each has different spatial advantages. |
| `3_chefs_coordination_ring` | 6×6 | Larger ring with internal walls, player 3 in lower-right corner. | Tests ring-based coordination where 3 agents must navigate shared narrow paths. |
| `3_chefs_counter_circuit` | 7×5 | Loop with central wall, 2P on top, resources on bottom. | Tests counter-passing in a circuit with an odd number of players splitting across lanes. |
| `3_chefs_cramped_room` | 5×5 | One row taller than 2-chef, extra pot and delivery. | Tests tight-space coordination with 3 agents — high collision potential. |
| `3_chefs_forced_coordination` | 7×5 | Wall separates onion side (left) from pot/delivery side (right). Player 3 gets own lane. | Forces cross-wall item passing; tests if a 3rd agent helps or hinders the bottleneck. |
| `3_chefs_secret_heaven` | 12×7 | Identical grid to 2-chef, player 3 added below player 2. | Tests whether adding a 3rd agent improves exploitation of the hidden resource room. |
| `3_chefs_storage_room` | 8×5 | Completely different design from 2-chef — small asymmetric room with players stacked vertically on left. | Tests simple task division with limited resources (1P, 1O, 1D, 1S). |

#### Category: Counter Circuit Variants

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `3_chefs_counter_circuit_standard` | 8×5 | Same grid as 2-chef `counter_circuit` but with player 3 placed on the delivery side. | Tests what happens when a 3rd player is added to the original 2-chef layout without redesigning it. |
| `3_chefs_counter_circuit_adv` | 7×5 | Players 1 & 2 start on the same (top) track, player 3 alone on the bottom. | Adversary-style: 2 players cooperate while 1 is isolated — tests robustness to unbalanced teams. |
| `3_chefs_long_counter_circuit` | 17×5 | Very wide (17 tiles!) loop. Much longer distances between resources. | Increases the cost of traveling around; motivates counter-passing instead of carrying items the long way. |

#### Category: Forced Coordination Variants

These all share the wall-divided design where onions are on one side and pots on the other. Pot placement is systematically varied.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `3_chefs_forced_coordination_3OP2S1D` | 7×5 | 3 onions, 3 pots (column), 2 servings, 1 delivery. Symmetric fill. | Maximum throughput variant — tests saturation when every row has resources. |
| `3_chefs_forced_coordination_three_pots` | 7×5 | 3 pots on the right side (high, mid, low positions). | Tests if 3 agents can each claim a pot or if they compete. |
| `3_chefs_forced_coordination_three_pots_plates_onions_12` | 7×5 | Similar to three_pots, different player spawn positions (1 and 2 swapped). | Tests how starting position affects role specialization with the same resources. |
| `3_chefs_forced_coordination_one_high_pot` | 7×5 | Single pot in top-right position only. | Resource scarcity — only 1 pot creates a severe bottleneck; tests queuing behavior. |
| `3_chefs_forced_coordination_one_med_pot` | 7×5 | Single pot in middle-right position. | Same scarcity, but pot is centrally accessible to all players. |
| `3_chefs_forced_coordination_one_low_pot` | 7×5 | Single pot in bottom-right position. | Same scarcity, but pot is far from onions — longer transport chain. |
| `3_chefs_forced_coordination_one_high_pot_one_low_pot` | 7×5 | Two pots: top and bottom of the right side. | Tests whether agents specialize on separate pots or compete for one. |
| `3_chefs_forced_coordination_one_med_pot_one_low_pot` | 7×5 | Two pots: middle and bottom. | Slightly different spatial arrangement for the same 2-pot question. |

#### Category: Kitchen Designs

Unique layouts not based on classic maps. Focus on different spatial arrangements.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `3_chefs_island_kitchen` | 7×6 | Central 2-pot "island" with players orbiting. Onions bottom, serving/delivery right. | Tests a kitchen-island work pattern — agents must share the central workspace. |
| `3_chefs_small_kitchen` | 9×5 | Rectangular room with resources spread to corners (P top-center, O bottom/right, D left, S right). | General-purpose 3-player kitchen; moderate distances and multiple viable strategies. |
| `3_chefs_small_kitchen_two_resources` | 9×5 | Like `small_kitchen` but with an extra delivery point. | More delivery options reduce the delivery bottleneck — tests if agents adapt. |
| `3_chefs_smaller_kitchen` | 7×5 | Compact version of `small_kitchen`. | Increased congestion at smaller scale — tests collision avoidance under pressure. |
| `3_chefs_clustered_kitchen` | 13×5 | Wide map with separate kitchen "clusters" connected by a corridor. Internal walls segment the space. | Tests spatial partitioning — do agents each claim a cluster or work together? |
| `3_chefs_4P_4O_4D_3S` | 10×5 | Resource-rich: 4 pots (top), 4 onions + 4 deliveries (bottom), 3 servings (right). | Abundance experiment — tests behavior when resources aren't the bottleneck; coordination is. |
| `3_chefs_long_onion` | 13×9 | Spiral maze. Onions at opposite corners, single pot in center. Long travel distances to onions. | Tests strategic planning: agents should stockpile onions via counters rather than making long trips. Easy to block each other. |
| `3_chefs_unequal_kitchens` | 13×7 | Three kitchens separated by walls — middle is best (more pots). All face a shared serving area at bottom. | Tests resource allocation: if all 3 agents crowd the middle kitchen, throughput drops. Optimal play requires splitting up. |

#### Category: Adversary Variants

Same grid as the `_adv` 2-chef version, but with a 3rd player. Designed for adversary training where one agent may sabotage.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `3_chefs_coordination_ring_adv` | 6×6 | Ring layout, player 3 added in lower-left with access to onion/delivery. | Adversary robustness testing with 3 agents in a tight ring. |
| `3_chefs_cramped_room_adv` | 6×4 | Extra pot added (3P total), player 3 starts next to onion. | Adversary testing in cramped quarters — easier to block and sabotage. |

#### Category: Decentralized (`dec_`)

Designed for decentralized control experiments. Minimal coordination required — tests independent decision-making.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `dec_3_chefs_counter_circuit` | 7×5 | Loop with central wall, balanced resource placement. | Decentralized variant — agents act more independently around the circuit. |
| `dec_3_chefs_cramped_room` | 5×4 | Nearly identical to 2-chef `cramped_room`, player 3 squeezed in top-left. Extra pot added as bottom. | Minimal adaptation for decentralized 3-agent experiments. |
| `dec_3_chefs_secret_heaven` | 12×7 | Same grid as 2-chef, 3rd player added. | Decentralized version — tests independent exploration of the secret room. |
| `dec_3_chefs_storage_room` | 8×5 | Small room, players stacked left, resources right. | Decentralized 3-agent storage room with limited resources. |

#### Category: Selected (`selected_`)

Systematically generated family of layouts. Each map type has a regular version (2 pots) and a `_one_pot` version (1 pot) to study resource scarcity.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `selected_3_chefs_coordination_ring` | 6×6 | Ring with 2P. Players 2,3 at bottom, player 1 at top. | Standardized 3-player ring for controlled experiments. |
| `selected_3_chefs_coordination_ring_one_pot` | 6×6 | Same ring, only 1P. | Tests how pot scarcity affects ring coordination. |
| `selected_3_chefs_counter_circuit` | 7×5 | Standard loop, 2P on top. | Baseline 3-player counter circuit. |
| `selected_3_chefs_counter_circuit_one_pot` | 7×5 | Same loop, 1P. | Pot scarcity in a circuit — agents must queue. |
| `selected_3_chefs_cramped_room` | 6×4 | Tight room with 2P, 2O. | Baseline cramped room for 3 agents. |
| `selected_3_chefs_cramped_room_one_pot` | 6×4 | Same room, 1P. | Bottleneck under scarcity. |
| `selected_3_chefs_double_counter_circuit` | 11×5 | Wide double-loop with 4P, 3O, 2D, 2S. | Longer circuit — tests whether 3 agents spread out or cluster. |
| `selected_3_chefs_double_counter_circuit_one_pot` | 11×5 | Double loop, only 1P. | Extreme scarcity in a large space — long travel to single pot. |
| `selected_3_chefs_secret_coordination_ring` | 12×6 | Large map with hidden resource room (6P) + coordination ring on right. | Tests secret resource discovery in a ring-connected layout. |
| `selected_3_chefs_secret_coordination_ring_one_pot` | 12×6 | Secret room stripped of resources, only 1P on right side. | Scarce version — secret room is useless; agents must share 1 pot. |
| `selected_3_chefs_spacious_room_few_resources` | 10×6 | Large open room with only 2P, 2O, 1D, 1S spread to edges. | Tests coordination in open space with scarce resources. |
| `selected_3_chefs_spacious_room_few_resources_one_pot` | 10×6 | Same room, 1P. | Further scarcity in open space. |
| `selected_3_chefs_spacious_room_no_counter_space` | 10×6 | Open room, resources on all walls. Counter tiles replaced — no counter passing possible. | Forces hand-to-hand style play; tests direct agent coordination without counter shortcuts. |
| `selected_3_chefs_spacious_room_no_counter_space_one_pot` | 10×6 | Same, 1P. | Scarcity + no counters = hardest coordination challenge. |
| `selected_3_chefs_storage_room` | 12×5 | Symmetric storage room, players split left/bottom and right side. 2P, 2O, 2D, 2S. | Baseline symmetric 3-agent storage room. |
| `selected_3_chefs_storage_room_one_pot` | 12×5 | Same, 1P (right pot removed). | Asymmetric scarcity in a symmetric map. |

#### Category: Other

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `n_players` | 8×5 | Standard `counter_circuit` grid but with 3 player spawns. | Generic multi-player test layout. |

---

### 4-Player Layouts (10 maps)

4-player layouts are relatively rare. They consist of one original design and one systematic (`selected_`) family.

#### Category: Original

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `4_chefs_asymmetric_advantages` | 9×9 | Large two-story design: top half mirrors the 2-chef version (players 1,2), bottom half adds a mirrored kitchen for players 3,4. Connected through a central delivery row. | Tests asymmetric advantages doubled — two teams of 2 effectively share a central delivery corridor. |
| `multiplayer_schelling` | 7×7 | Perfectly symmetric top/bottom map with pots + serving on both sides, onions on left/right. 4 players in each quadrant. | Game theory: named after Schelling's focal points. 4 agents must implicitly coordinate which side to use without communication. |

#### Category: Selected (`selected_`)

Systematically scaled versions of the `selected_3_chefs_` maps with an additional player. Same grid, one extra spawn.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `selected_4_chefs_coordination_ring` | 6×6 | Same ring as 3-chef, player 4 added top-left. | Tests ring congestion with 4 agents in a 6×6 space. |
| `selected_4_chefs_counter_circuit` | 7×5 | Same loop, player 4 added top track. | 4 agents in a small circuit — heavy traffic. |
| `selected_4_chefs_cramped_room` | 6×4 | Same cramped room, player 4 top-left. | Maximum density — 4 agents in 6×4 tiles. |
| `selected_4_chefs_double_counter_circuit` | 11×5 | Wide double-loop, 2 agents per track. | Balanced team split across a longer circuit. |
| `selected_4_chefs_secret_coordination_ring` | 12×6 | Secret room + ring with 4 players on the right. | Tests whether 4 agents can discover and utilize the hidden room. |
| `selected_4_chefs_spacious_room_few_resources` | 10×6 | Open room, player 4 bottom-left. | Scarcity + 4 agents in open space. |
| `selected_4_chefs_spacious_room_no_counter_space` | 10×6 | No counters, player 4 bottom-left. | 4 agents forced into direct coordination without counter passing. |
| `selected_4_chefs_storage_room` | 12×5 | Symmetric storage, players 1,3 left and 2,4 right. | Balanced 2+2 team split in symmetric environment. |

---

### 5-Player Layouts (27 maps)

#### Category: Core Map Adaptations

Expanded grids of classic maps, designed from scratch for 5-player coordination.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `5_chefs` | 7×6 | Compact custom layout: resources scattered, 3P, 2O, 3D, 3S. Irregular design. | General-purpose 5-agent test — no specific structural constraint. |
| `5_chefs_asymmetric_advantages` | 9×9 | Large two-story design, similar to 4-chef version but with 5 spawn points. | Tests asymmetric advantages at scale — spatial inequality among 5 agents. |
| `5_chefs_coordination_ring` | 7×6 | Rectangular with central wall column. Symmetric left/right halves, players distributed vertically. | Tests ring coordination completely redesigned for 5 agents. |
| `5_chefs_counter_circuit` | 11×5 | Extended wide loop: 4P top, 3O+2D bottom, 2S sides. Players alternate top/bottom tracks. | Tests large-team circuit coordination with abundant resources. |
| `5_chefs_cramped_room` | 7×5 | Wider cramped room: 2P, 4O, 2D, 3S. 5 agents packed tightly. | Maximum congestion — tests collision avoidance with 5 agents in a small space. |
| `5_chefs_forced_coordination` | 9×6 | Wall-divided: 4 onions (left), 3 pots (right). 2 serving points. | Extreme forced coordination — agents must pass items across the wall at scale. |
| `5_chefs_secret_heaven` | 12×7 | Identical grid to 2-chef version. 5 players squeezed into the right side. | Tests congestion and whether agents discover the secret room when severely crowded. |
| `5_chefs_storage_room` | 12×5 | Similar to 2-chef design but pots on sides. Players 1,2,3 left; 4,5 right. | Tests unbalanced team split (3 vs 2) in a symmetric storage environment. |

#### Category: Unique 5-Chef Designs

Maps that exist only in 5-player versions with novel spatial structures.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `5_chefs_central_chaos` | 11×9 | Delivery points in the center, all other resources on perimeter walls. Large open space. | Creates chaotic traffic as all 5 agents converge on the center. Tests emergent traffic patterns. |
| `5_chefs_maze_of_ambiguity` | 11×9 | Maze with internal pillars. Resources scattered everywhere: 6P, 4O, 2D, 4S. | Tons of choices with ambiguous optimal strategies. Tests decision-making when many options are available. |
| `5_chefs_ring_of_confusion` | 11×9 | Diamond-shaped internal obstacles. Resources on all 4 edges. | Confusing sight-lines and movement patterns. Tests navigation under spatial confusion. |
| `5_chefs_clustered_kitchen` | 25×5 | Very wide (25 tiles!). 5 separate kitchen clusters connected in a corridor. Each has own pot, onion, delivery, serving. | Tests whether agents each claim a cluster or share. Extremely long distances between ends. |
| `5_chefs_storage_room_lots_resources` | 12×5 | Abundant resources: 5O top, 2P sides, 4S+4D bottom. Wide open. | Abundance experiment at 5-player scale — coordination is the bottleneck, not resources. |

#### Category: Adversary Variants (`_adv`)

Designed for adversary/robustness training. Some agents may be adversarial.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `5_chefs_double_counter_circuit_adv` | 11×5 | Double loop. Player 5 placed on the top track near the wall gap — can block traffic. | Tests robustness when one of 5 agents may be adversarial in a circuit. |
| `5_chefs_secret_coordination_ring_adv` | 12×6 | Secret room + ring. Players spread across both areas, adversary can block the ring junction. | Tests adversary robustness in a complex multi-room layout. |
| `5_chefs_storage_room_adv` | 12×5 | Storage room with players 3,4 clustered in the center. | Adversary variant — central players can disrupt both sides. |

#### Category: Decentralized (`dec_`)

Used by this project in `complex_5_chefs_layouts`. Minimal coordination assumptions.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `dec_5_chefs_counter_circuit` | 11×5 | Wide loop, balanced resource placement. | Decentralized 5-agent circuit coordination. |
| `dec_5_chefs_secret_heaven` | 12×7 | Same 2-chef grid, 5 players on right side. | Decentralized secret room discovery with heavy crowding. |
| `dec_5_chefs_storage_room` | 12×5 | Symmetric storage with 3-2 player split. | Decentralized storage room at 5-player scale. |

#### Category: Selected (`selected_`)

Systematically generated. Same grids as 3/4-chef `selected_` variants but with 5 player spawns packed in.

| Layout | Grid | Description | Why It Exists |
|--------|------|-------------|---------------|
| `selected_5_chefs_coordination_ring` | 6×6 | Tiny ring with 5 players — extremely dense. | Maximum congestion in smallest possible ring. |
| `selected_5_chefs_counter_circuit` | 7×5 | Small loop, 5 players packed across 2 tracks (3 top, 2 bottom). | Stress tests circuit coordination at extreme density. |
| `selected_5_chefs_cramped_room` | 6×4 | 5 agents in 6×4 tiles. Barely any free space. | Tests the limits of cramped coordination. |
| `selected_5_chefs_double_counter_circuit` | 11×5 | Wider loop, player 5 on bottom track center. | More spread-out 5-agent circuit. |
| `selected_5_chefs_secret_coordination_ring` | 12×6 | Large secret room + ring, players 3,2 central with 4,5 bottom-right. | Tests secret room discovery at 5-player density. |
| `selected_5_chefs_spacious_room_few_resources` | 10×6 | Open room, players 4,5 on bottom. Scarce resources. | Tests 5-agent coordination with limited supplies in open space. |
| `selected_5_chefs_spacious_room_no_counter_space` | 10×6 | No counters, all resources on walls. Players 4,5 bottom. | 5 agents must coordinate without counter passing — hardest variant. |
| `selected_5_chefs_storage_room` | 12×5 | Symmetric storage, player 5 center-left. | Balanced 5-agent storage room. |

---

## Summary Statistics

| Player Count | Total Layouts | Used by Project | Unused |
|-------------|---------------|-----------------|--------|
| 3 players   | 46            | 3               | 43     |
| 4 players   | 10            | 0               | 10     |
| 5 players   | 27            | 4               | 23     |
| **Total**   | **83**        | **7**           | **76** |

## Layout Category Guide

| Prefix/Category | Meaning | Typical Use |
|----------------|---------|-------------|
| _(none)_ | Original designs, unique grid per player count | General training & research |
| `dec_` | Decentralized — minimal redesign from 2-chef | Decentralized control experiments |
| `selected_` | Systematically generated family, often with `_one_pot` variants | Controlled experiments varying pot count as independent variable |
| `_adv` | Adversary — player placement allows blocking/sabotage | Adversary robustness training |
| `_one_pot` | Single pot variant of a `selected_` layout | Resource scarcity studies |

## Design Patterns

| Pattern | Maps | Insight |
|---------|------|---------|
| **Same grid, more players** | `secret_heaven` family, `selected_` family | Tests crowding — same resources, more competition |
| **Redesigned grids** | `counter_circuit`, `coordination_ring`, `cramped_room` families | Tests how map structure should change with team size |
| **Pot count variation** | `selected_*_one_pot` variants, `forced_coordination_*` variants | Tests resource scarcity as an isolated variable |
| **Forced separation** | `forced_coordination` family, `schelling` | Tests cross-barrier coordination |
| **Hidden resources** | `secret_heaven`, `secret_coordination_ring` | Tests exploration and multi-room strategies |
| **Open space** | `spacious_room_*`, `large_room` | Tests coordination when movement isn't constrained |
| **Extreme congestion** | `selected_5_chefs_cramped_room`, `5_chefs_ring_of_confusion` | Tests collision avoidance at scale |
