# SMC Agent — Smart Money Concept analysis with a local LLM

> *"知行合一 / 交易之道 — Biết người biết ta, Trăm trận trăm thắng."*

A pure-Python detection engine for the Smart Money Concept (SMC) trading
methodology + an LLM-orchestrated agent that runs entirely on your machine
through **Ollama**. Inspired by the *"Phân Tích SMC & Setup 1:3 RR"* infographic
(Trade Coin Underground), with the *"4 Luật Nổi Tiếng Nhất Thế Giới"*
(Murphy / Kidlin / Wilson / Gilbert) baked in as the agent's permanent
**bộ nhớ trade** (trade memory).

---

## Architecture

```
                   ┌────────────────────────────────────────────┐
                   │   smc_agent (LLM orchestrator)             │
                   │                                            │
   user query ───► │   system prompt (VI)                       │
                   │   ├─ smc_methodology.md  (5-step process)  │
                   │   ├─ trading_laws.md      (4 laws filter)  │
                   │   └─ system_vi.md         (output format)  │
                   │                                            │
                   │   chat loop ⇄ Ollama (qwen2.5:7b default)  │
                   │   tool calls ─┐                            │
                   └───────────────┼────────────────────────────┘
                                   ▼
                   ┌────────────────────────────────────────────┐
                   │   smc_core (pure-Python detection engine)  │
                   │                                            │
                   │   • find_swings              (fractal)     │
                   │   • find_structure_events    (BOS / CHoCH) │
                   │   • find_idm_sweeps          (liquidity)   │
                   │   • find_fvgs                (imbalance)   │
                   │   • find_order_blocks                      │
                   │   • build_setups   ← combines all 5 steps  │
                   └────────────────────────────────────────────┘
                                   ▲
                                   │
                   ┌────────────────────────────────────────────┐
                   │   apply_trading_laws (deterministic)        │
                   │   Murphy · Kidlin · Wilson · Gilbert        │
                   │   + 4 trader lessons checklist             │
                   └────────────────────────────────────────────┘
```

The LLM is **only the orchestrator**. All structural decisions are made by
deterministic pure-Python detectors — making the agent reproducible and
auditable.

## Khái niệm cốt lõi

| Khái niệm | Detector | Vai trò |
|-----------|----------|---------|
| **BOS** (Break of Structure) | `find_structure_events` | Xác nhận tiếp diễn xu hướng. |
| **CHoCH** (Change of Character) | `find_structure_events` | Tín hiệu khả năng đảo chiều. |
| **IDM** (Internal Liquidity) | `find_idm_sweeps` | Quét đỉnh/đáy nhỏ trước khi đi tiếp. |
| **FVG** (Fair Value Gap) | `find_fvgs` | Khoảng trống giá trị công bằng. |
| **Order Block** | `find_order_blocks` | Vùng dấu chân Smart Money. |
| **1:3 RR Setup** | `build_setups` | Lắp ráp toàn bộ thành kế hoạch giao dịch. |

## Quy trình 5 bước (theo infographic)

1. Xác định xu hướng chính (**BOS**).
2. Tìm **IDM** bị quét.
3. Xác định **Order Block + FVG**.
4. Chờ tín hiệu xác nhận (**Price Action**).
5. Vào lệnh với tỉ lệ **1:3 RR**.

## Bộ nhớ trade — 4 định luật

| # | Định luật | Vai trò trong agent |
|---|-----------|---------------------|
| 1 | **Murphy** — *"Càng sợ điều gì xảy ra, càng dễ xảy ra."* | SL kỷ luật bắt buộc, giả định kịch bản xấu nhất. |
| 2 | **Kidlin** — *"Viết rõ vấn đề = giải quyết một nửa."* | Mọi setup phải kèm `notes[]` đủ 5 bước. |
| 3 | **Wilson** — *"Ưu tiên kiến thức, tiền sẽ đến."* | Phải có reasoning giải thích cấu trúc. |
| 4 | **Gilbert** — *"Trách nhiệm tìm cách tốt nhất là của bạn."* | Không bịa setup khi dữ liệu không hợp lệ. |

Các định luật được lưu ở `src/smc_agent/knowledge/trading_laws.md` và:

- Được **inject vào system prompt** mỗi lần agent chạy.
- Được **kiểm tra deterministic** bởi `apply_trading_laws()` — trả về severity
  `ok` / `caution` / `reject` cho mỗi setup.

Sau bộ lọc 4 định luật, agent chạy **checklist 4 bài học cho trader**:

1. Hiểu rõ tâm lý — kiểm soát cảm xúc.
2. Ghi chép rõ ràng — kế hoạch + bài học.
3. Đầu tư kiến thức — kiến thức là tài sản không mất giá.
4. Chịu trách nhiệm — không đổ lỗi, luôn tìm phương án tối ưu.

## Cài đặt

```bash
git clone <this-repo>
cd smc-agent
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Cài Ollama (cho lớp LLM)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b      # default model
# hoặc llama3.1:8b, qwen2.5:14b, etc.
```

Ollama lắng nghe ở `http://localhost:11434/v1` (OpenAI-compatible). Agent sẽ
tự động kết nối — không cần API key.

## Sử dụng

### 1. CLI (deterministic, không cần LLM)

```bash
# Sinh dữ liệu mẫu
python examples/generate_sample_data.py

# Phân tích
smc-agent analyze \
    --csv examples/data/sample_nzdusd_2h.csv \
    --symbol NZDUSD --timeframe 2h --no-llm
```

Output: bảng setup với side / entry / SL / TP / RR / severity.

### 2. CLI + LLM (Ollama)

```bash
ollama serve  # nếu chưa chạy

smc-agent analyze \
    --csv examples/data/sample_nzdusd_2h.csv \
    --symbol NZDUSD --timeframe 2h --llm \
    --model qwen2.5:7b
```

Agent sẽ gọi 5–6 tool theo đúng quy trình và trả về báo cáo tiếng Việt theo
format trong `prompts/system_vi.md`.

### 3. Python API

```python
from smc_core import load_ohlcv, build_setups
from smc_agent.laws import apply_trading_laws

ohlcv = load_ohlcv("data/nzdusd_2h.csv", symbol="NZDUSD", timeframe="2h")
setups = build_setups(ohlcv, rr_ratio=3.0)
checks = apply_trading_laws(setups)

for s, c in zip(setups, checks, strict=True):
    print(s.side.value, s.entry, "→", s.take_profit, "·", c.severity)
```

### 4. LLM Agent từ Python

```python
from smc_agent import SMCAgent, AgentConfig

agent = SMCAgent(AgentConfig(model="qwen2.5:7b"))
run = agent.run(
    "Phân tích examples/data/sample_nzdusd_2h.csv (NZDUSD 2h) "
    "và đề xuất setup 1:3 RR theo đúng quy trình SMC."
)
print(run.final_message)
```

## Cấu hình

Tất cả qua biến môi trường (xem `smc_agent/config.py`):

| Biến | Mặc định | Vai trò |
|------|----------|---------|
| `SMC_AGENT_BASE_URL` | `http://localhost:11434/v1` | Endpoint OpenAI-compatible. |
| `SMC_AGENT_MODEL` | `qwen2.5:7b` | Model Ollama. |
| `SMC_AGENT_TEMPERATURE` | `0.2` | Sampling temperature. |
| `SMC_AGENT_MAX_TOOL_ITERATIONS` | `6` | Số vòng tool tối đa. |
| `SMC_AGENT_TIMEOUT` | `120` | Timeout HTTP (giây). |

## Tools agent có thể gọi

| Tool | Mô tả |
|------|-------|
| `load_ohlcv_csv` | Load OHLCV từ file CSV. |
| `detect_swings` | Phát hiện đỉnh/đáy fractal. |
| `detect_structure` | BOS / CHoCH. |
| `detect_idm_sweep` | Quét IDM. |
| `detect_fvg` | Fair Value Gap. |
| `detect_order_block` | Order Block. |
| `build_rr_setup` | End-to-end pipeline → list setup 1:3 RR. |
| `apply_trading_laws` | Lọc qua 4 định luật + 4 bài học. |

## Kiểm thử

```bash
ruff check src tests examples
ruff format --check src tests examples
pytest -ra
```

29 unit tests bao phủ swings, structure, FVG, order block, liquidity, setup,
laws, tools, và CLI smoke tests.

## Lưu ý quan trọng

- **Phương pháp này chỉ là công cụ phân tích — không phải tín hiệu giao dịch
  được đảm bảo.** Mọi setup đều cần xác nhận thêm bằng tin tức, khung thời
  gian khác, và phán đoán cá nhân.
- **Quản lý vốn nghiêm ngặt:** SL kỷ luật, không bao giờ "phá SL" (Luật Murphy).
- **Backtest trước khi live:** Code này giúp tự động hoá việc nhận diện cấu
  trúc — kết quả thực tế phụ thuộc vào dữ liệu, timeframe, và market regime.

## License

MIT
