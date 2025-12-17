# Repository Guidelines

## Project Structure & Module Organization
- `温度模拟量/`: Temperature loop cell with OB1/OB100, `主流程控制.scl`, `辅助函数块.scl`, and IO docs (`IO映射表.md`, `流程图.md`, `PLC变量表.csv`).
- `钻孔/`: Drilling station; main logic in `最终版本.scl` plus backup variants, safety/state-machine notes in `CLAUDE.md`, IO map in `IO映射表.md`.
- `转盘伺服/`: Rotary-table sample with `转盘最终版.scl`, IO map, and `PLC变量表.xlsx`.
- Cross-unit reference: `1500 伺服设备映射表.md`. Future generator plan: `docs/plans/2025-11-27-scl-io-mapping-generator.md` (place new code under `scl_generator/` and `tests/` if implemented).

## Build, Test, and Development Flow
- No repo-level build; import `.scl` into TIA Portal (Program blocks → External source → From file), compile (F7), then download or simulate with PLCSIM.
- Keep `.scl` files UTF-8 with BOM. When IO changes, sync `PLC变量表.csv`/`.xlsx` and matching `IO映射表.md`.
- For temperature module, verify init order: 升降上升 → 载料伸出 → 升降下降, then 20 s heating wait; confirm IW64/QW80 scaling if TemperatureControl is used.
- For drilling, respect four-condition start interlock and limit protections overriding outputs (see `钻孔/CLAUDE.md`).

## Coding Style & Naming Conventions
- Language: SCL with 4-space indentation; prefer Chinese identifiers matching hardware labels.
- Prefixes: `c状态_*` for state constants, `t*` for IEC_TIMERs, `b*` flags, `X/Y轴*` for motion outputs. Place constants in `VAR CONSTANT`.
- 函数返回值直接赋给函数名本身，不要加引号（示例：`MyFC := TRUE;`）。
- State machines: single `CASE`; put resets and safety interlocks before normal sequence logic; limit changes to scoped states. Use `//` for concise, non-obvious notes.

## Testing Guidelines
- Use PLCSIM/TIA online monitoring; watch `状态`, `b停止锁定标志`, timer `.Q`, and safety interlocks. Re-run start-up after OB100/init edits.
- For sequence changes, record observed values or watch-table snippets next to the modified file.

## Commit & Pull Request Guidelines
- Commit subject: imperative and name the unit (e.g., `温度模拟量: adjust heating timer bounds`). Keep changes localized; avoid deleting backup `.scl` variants unless approved.
- In descriptions, note hardware/IO assumptions (byte/bit moves, timers) and simulation coverage; attach screenshots or watch-table excerpts when available.
- PRs should summarize scope, link issues/tasks, and call out IO map or documentation updates.

## Safety & Documentation Updates
- Default outputs to safe/off on reset; interlocks precede sequence logic. After changing OB100 or init steps, rerun the full start-up path.
- Update flow docs (`流程图.md`/`结构化流程.md`) when step order changes, and refresh IO maps after remapping.
