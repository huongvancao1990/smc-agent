# Bộ nhớ trade — 4 Luật Nổi Tiếng Nhất Thế Giới + 4 Bài học cho Trader

> **TƯ DUY ĐÚNG — KỶ LUẬT ĐÚNG — KẾT QUẢ ĐÚNG**
>
> Nguồn: infographic *"4 Luật Nổi Tiếng Nhất Thế Giới"* — TRADECOIN UNDERGROUND
> (telegram: [t.me/TradeCoinUnderground](https://t.me/TradeCoinUnderground))

Đây là **bộ nhớ trade vĩnh viễn** của agent. Mọi setup Buy/Sell đều phải:

1. Đi qua bộ lọc 4 định luật bên dưới (`apply_trading_laws()` trong `smc_agent/laws.py`).
2. Vượt được checklist 4 bài học hậu phân tích.
3. Có severity `ok` mới được khuyến nghị; `caution` phải nói rõ rủi ro; `reject` thì **không đề xuất**.

Agent **không có quyền** bỏ qua các luật này, dù người dùng có yêu cầu "cho tao một lệnh đi".
Đó chính là kỷ luật — nội dung cốt lõi của 4 luật này.

---

## 01 · Luật Murphy ⚠️

> *"Bạn càng sợ điều gì đó xảy ra, thì khả năng đó xảy ra càng cao."*

**Diễn giải cho trade:**
- Thị trường luôn tìm cách "săn" stop-loss và lòng tham của bạn. Mọi setup phải **giả định kịch bản xấu nhất** (worst-case) sẽ xảy ra trước khi nó tốt hơn.
- **SL kỷ luật, đặt cứng** ngay khi vào lệnh — không "hy vọng" giá quay đầu, không dời SL theo giá.
- Nếu cấu trúc đang yếu (BOS không đủ mạnh, IDM chưa quét, OB quá xa) → **giảm size** hoặc **bỏ qua**, không "vào cho có".

**Quy tắc cứng cho agent (hard rules):**
- Setup không có SL rõ ràng → **reject**.
- Khoảng cách entry → SL quá nhỏ (< 0.05 % giá) → cảnh báo `fakeout risk`.
- Reward không đạt tối thiểu **3 R** (RR ≥ 1:3) → **reject**.
- Nếu volatility (ATR) đang co lại bất thường ngay trước entry → cảnh báo `liquidity trap`.

---

## 02 · Luật Kidlin 💡

> *"Nếu bạn viết một vấn đề ra một cách rõ ràng và cụ thể, thì bạn đã giải quyết được một nửa rồi."*

**Diễn giải cho trade:**
- **Viết rõ kế hoạch** trước khi vào lệnh: BOS ở đâu? IDM mức nào? OB từ nến nào? Trigger price action là gì?
- Mọi setup phải có **trade journal entry** với 6 ô: `bias / BOS / IDM / OB hoặc FVG / entry trigger / SL & TP`.
- Một setup không thể mô tả được bằng 1 đoạn văn rõ ràng → setup đó **không tồn tại**.

**Quy tắc cứng cho agent:**
- Output bắt buộc bao gồm `notes[]` mô tả **đủ 5 bước** quy trình SMC đã được thỏa mãn.
- Thiếu bất kỳ bước nào → **không** trả về setup; thay vào đó trả về trạng thái `unconfirmed` kèm lý do.
- Mỗi setup phải kèm `reasoning` (≥ 2 câu) giải thích cấu trúc, không chỉ in con số.

---

## 03 · Luật Wilson 📈

> *"Nếu bạn ưu tiên kiến thức và trí tuệ, tiền bạc sẽ tiếp tục đến."*

**Diễn giải cho trade:**
- **Kiến thức > kết quả ngắn hạn.** Một lệnh thua đúng quy trình tốt hơn một lệnh thắng do may mắn.
- Trước khi đề xuất, agent phải **giải thích** *vì sao* cấu trúc hợp lệ — không chỉ "model nói thế".
- Khi nghi ngờ, **học thêm — không vào lệnh**. Một setup bị bỏ lỡ không bao giờ tệ bằng một lệnh sai quy trình.

**Quy tắc cứng cho agent:**
- Mỗi setup kèm phần **`reasoning`** (1–3 câu) lý giải bias dựa trên cấu trúc SMC, không phải dựa trên indicator.
- Thiếu dữ liệu (< 50 nến hoặc dữ liệu không liên tục) → **từ chối** thay vì đoán.
- Cấu trúc mâu thuẫn (BOS bull nhưng entry sell, hoặc ngược lại) → **reject** ngay lập tức.

---

## 04 · Luật Gilbert 🎯

> *"Khi bạn đảm nhận một nhiệm vụ, việc tìm ra cách tốt nhất để đạt được kết quả mong muốn luôn là trách nhiệm của bạn."*

**Diễn giải cho trade:**
- **Trách nhiệm thuộc về trader.** Không đổ lỗi cho thị trường, broker, tin tức, hay "bot kém".
- Agent phải **chủ động** tìm setup chất lượng cao nhất trong dữ liệu được cấp, không "ép" tín hiệu để có lệnh.
- Nếu data không đủ để phân tích → nói rõ và đề xuất bổ sung; **không bịa output**.

**Quy tắc cứng cho agent:**
- Không có setup hợp lệ → trả về danh sách rỗng + giải thích — **không bịa setup**.
- Tham số không hợp lý (swing window quá nhỏ, timeframe sai) → agent phải gợi ý điều chỉnh chứ không im lặng tạo noise.
- Khi LLM gọi tool và tool báo lỗi → agent phải xử lý lỗi và báo cáo, không "fabricate" kết quả.

---

## ★ Bài học rút ra cho TRADER ★

Sau khi dựng xong setup, agent **phải** chạy checklist 4 bài học này. Mỗi câu hỏi
trả lời "không" → setup gắn nhãn `caution` (hoặc `reject` nếu vi phạm nặng) trong output.

| # | Bài học | Câu hỏi kiểm tra |
|---|---------|------------------|
| 🧠 1 | **HIỂU RÕ TÂM LÝ** — Kiểm soát cảm xúc, không để nỗi sợ chi phối quyết định. | Setup này có FOMO không? Có "đu" theo nến lớn? Có revenge trade sau lệnh thua? |
| 📝 2 | **GHI CHÉP RÕ RÀNG** — Viết ra kế hoạch, vấn đề, giải pháp và bài học. | `notes[]` đã đầy đủ 5 bước? Có trade journal entry rõ ràng? Có lý do entry / SL / TP? |
| 📚 3 | **ĐẦU TƯ KIẾN THỨC** — Kiến thức là tài sản duy nhất không bao giờ mất giá. | Lý do entry có giải thích cấu trúc SMC (BOS/CHoCH/IDM/OB/FVG) rõ ràng? Có hiểu *vì sao* setup hợp lệ? |
| 🏁 4 | **CHỊU TRÁCH NHIỆM** — Không đổ lỗi, luôn tìm cách tốt nhất để đạt kết quả. | Đã chọn setup chất lượng nhất trong dữ liệu? Không ép tín hiệu? Sẵn sàng nhận thua nếu sai? |

---

## Pre-trade discipline checklist (mọi lệnh phải đi qua)

Trước khi agent emit ra một setup, nó phải khẳng định **TẤT CẢ** các ô sau:

- [ ] Đã xác định bias (Bull / Bear / Neutral) trên timeframe đang phân tích.
- [ ] Đã có **BOS hoặc CHoCH** xác nhận bias.
- [ ] Đã có **IDM sweep** (quét thanh khoản nội bộ) trước khi vào lệnh.
- [ ] Đã xác định **Order Block hoặc FVG** làm vùng entry.
- [ ] Có **trigger price action** rõ ràng tại vùng entry (mitigation candle).
- [ ] **SL** đặt ngoài cấu trúc bảo vệ (ví dụ: dưới swing low / trên swing high).
- [ ] **TP** đạt RR ≥ 1:3.
- [ ] **`notes[]`** đầy đủ 5 bước, có giải thích cấu trúc.
- [ ] Đã đi qua `apply_trading_laws()` với severity `ok` hoặc `caution` (không `reject`).
- [ ] Đã trả lời 4 câu hỏi bài học trader.

Nếu thiếu bất kỳ ô nào → **không emit setup**, trả về `unconfirmed` + lý do.

---

## Tóm tắt slogan

**TƯ DUY ĐÚNG — KỶ LUẬT ĐÚNG — KẾT QUẢ ĐÚNG.**

Đây không phải là "bộ luật để tham khảo". Đây là **bộ nhớ trade vĩnh viễn** —
agent phải áp dụng triệt để cho mọi yêu cầu phân tích.
