# Weboku Interface Contracts

This document defines the interfaces between Weboku components.

The purpose is to allow team members to implement their assigned modules independently while keeping the final integration consistent.

---

# 1. General Rules

The internal Sudoku board uses zero-based indexes:

- Ring: `0–8`
- Column: `0–8`
- Value: `1–9`

The CLI displays human-friendly values:

- Ring: `1–9`
- Column: `1–9`

The center of the physical Weboku board is not a playable cell.

There are exactly:

- 9 rings
- 9 columns/sectors
- 9 regions
- 81 playable cells

The Python game engine is the source of truth.

The CLI must not implement Sudoku rules.

The AI must not decide whether a move is valid.

---

# 2. Cell

File:

```text
weboku/cell.py
