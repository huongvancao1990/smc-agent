# Changelog

## 0.1.0 — initial release

- `smc_core`: pure-Python detection engine for SMC.
  - Swing high/low detection (`find_swings`).
  - Break of Structure / Change of Character (`find_structure_events`).
  - Internal Liquidity sweep (`find_idm_sweeps`).
  - Fair Value Gap (`find_fvgs`).
  - Order Block (`find_order_blocks`).
  - 1:3 RR setup builder (`build_setups`).
- `smc_agent`: LLM orchestrator.
  - Function-calling tool dispatcher (8 tools).
  - Ollama (OpenAI-compatible) client.
  - Vietnamese system prompt mirroring the SMC infographic methodology.
  - Trade memory: 4 famous laws (Murphy / Kidlin / Wilson / Gilbert) + 4 trader lessons.
  - Deterministic `apply_trading_laws` filter with severity levels.
- CLI: `smc-agent analyze --csv ... [--llm]`.
- Sample data generator and end-to-end demo.
- 29 unit tests covering all detectors and the tool dispatcher.
- GitHub Actions CI: ruff lint + format + pytest on Python 3.10 / 3.11 / 3.12.
