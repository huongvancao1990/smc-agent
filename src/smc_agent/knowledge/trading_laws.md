# Bộ nhớ trade — 4 định luật nổi tiếng & 4 bài học cho trader

> Nguồn: infographic *"4 Luật Nổi Tiếng Nhất Thế Giới — Tư duy đúng - Kỷ luật đúng - Kết quả đúng"*
> (Trade Coin Underground)

Agent phải **đọc và áp dụng** các định luật này như bộ lọc cuối cùng trước khi
đề xuất bất kỳ setup Buy/Sell nào. Nếu một setup vi phạm bất kỳ định luật nào,
agent phải **từ chối** hoặc **gắn cờ rủi ro cao** trong báo cáo.

---

## 01 · Luật Murphy — *"Bạn càng sợ điều gì đó xảy ra, thì khả năng đó xảy ra càng cao."*

**Diễn giải cho trade:**
- Mọi setup phải **giả định kịch bản xấu nhất** (worst-case) sẽ xảy ra.
- **SL kỷ luật**, đặt sẵn ngay khi vào lệnh — không "hy vọng" giá quay đầu.
- Nếu cấu trúc đang yếu (BOS không đủ mạnh, IDM chưa quét, OB nằm xa), **giảm size** hoặc **bỏ qua**.

**Quy tắc cứng cho agent:**
- Không đề xuất setup nào không có SL rõ ràng.
- Nếu khoảng cách entry → SL quá nhỏ (< 0.05% giá) → cảnh báo "fakeout risk".
- Nếu reward không đạt tối thiểu 3R → reject.

---

## 02 · Luật Kidlin — *"Nếu bạn viết một vấn đề ra một cách rõ ràng và cụ thể, thì bạn đã giải quyết được một nửa rồi."*

**Diễn giải cho trade:**
- **Viết rõ kế hoạch** trước khi vào lệnh: BOS ở đâu? IDM mức nào? OB từ index nào? Tín hiệu price action gì?
- Mọi setup phải có **trade journal entry** với 6 ô: bias, BOS, IDM, OB/FVG, entry trigger, SL/TP.

**Quy tắc cứng cho agent:**
- Output bắt buộc phải bao gồm trường `notes[]` mô tả **từng bước** đã được thỏa mãn.
- Nếu thiếu bất kỳ bước nào trong quy trình 5 bước → **không** trả về setup, trả về `unconfirmed` kèm lý do.

---

## 03 · Luật Wilson — *"Nếu bạn ưu tiên kiến thức và trí tuệ, tiền bạc sẽ tiếp tục đến."*

**Diễn giải cho trade:**
- **Kiến thức > kết quả ngắn hạn.** Một lệnh thua đúng quy trình tốt hơn một lệnh thắng do may mắn.
- Trước khi đề xuất, agent phải **giải thích** vì sao cấu trúc hợp lệ — không chỉ in ra số.

**Quy tắc cứng cho agent:**
- Mỗi setup kèm phần **"reasoning"** (1-3 câu) lý giải bias.
- Khi thiếu dữ liệu (ví dụ < 50 nến), **từ chối** thay vì đoán.

---

## 04 · Luật Gilbert — *"Khi bạn đảm nhận một nhiệm vụ, việc tìm ra cách tốt nhất để đạt được kết quả mong muốn luôn là trách nhiệm của bạn."*

**Diễn giải cho trade:**
- **Trách nhiệm thuộc về trader.** Không đổ lỗi cho thị trường, broker, hay tin tức.
- Agent phải **chủ động** tìm setup chất lượng cao nhất trong dữ liệu được cấp, không "ép" tín hiệu.

**Quy tắc cứng cho agent:**
- Nếu dữ liệu không có setup hợp lệ, trả về danh sách rỗng + giải thích — **không bịa setup**.
- Khi tham số không hợp lý (ví dụ swing window quá nhỏ), agent phải gợi ý điều chỉnh thay vì im lặng tạo noise.

---

## Bài học rút ra cho trader (4 bài học)

Sau khi build setup, agent **phải** chạy checklist 4 bài học này trước khi báo cáo:

| # | Bài học | Câu hỏi kiểm tra |
|---|---------|------------------|
| 1 | **Hiểu rõ tâm lý** — Kiểm soát cảm xúc, không để nỗi sợ chi phối quyết định. | Setup này có FOMO không? Có "đu" theo nến lớn không? |
| 2 | **Ghi chép rõ ràng** — Viết kế hoạch, vấn đề, giải pháp, bài học. | `notes[]` đã đầy đủ 5 bước? Có trade journal entry? |
| 3 | **Đầu tư kiến thức** — Kiến thức là tài sản duy nhất không bao giờ mất giá. | Lý do entry có giải thích cấu trúc SMC rõ ràng? |
| 4 | **Chịu trách nhiệm** — Không đổ lỗi, luôn tìm cách tốt nhất để đạt kết quả. | Đã chọn setup chất lượng nhất, không ép tín hiệu? |

Nếu **bất kỳ câu hỏi nào** trả lời "không" → setup được gắn nhãn `caution` trong output.
