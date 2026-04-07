# Test Results

## Môi trường

- Đã cài: `langchain`, `langchain-openai`, `langgraph`, `python-dotenv`
- Đã kiểm tra cú pháp:
  - `python -m py_compile tools.py`
  - `python -m py_compile agent.py`
- Đã chạy agent thật với `OPENAI_API_KEY`

## Test 1 — Direct Answer

**User**

```text
Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.
```

**Console log**

```text
TravelBuddy đang suy nghĩ...
Trả lời trực tiếp

TravelBuddy: Xin chào! Rất vui được hỗ trợ bạn trong chuyến du lịch. Bạn có thể cho tôi biết thêm về sở thích của bạn không? Bạn muốn khám phá thành phố, biển, núi hay một địa điểm nào khác? Ngoài ra, bạn có ngân sách dự kiến cho chuyến đi này không?
```

**Kết quả**

- Đúng kỳ vọng: không gọi tool, hỏi thêm sở thích và ngân sách.

## Test 2 — Single Tool Call

**User**

```text
Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng
```

**Console log**

```text
TravelBuddy đang suy nghĩ...
Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
Trả lời trực tiếp

TravelBuddy: Dưới đây là danh sách chuyến bay từ Hà Nội đi Đà Nẵng:

1. **VietJet Air** | 08:30 - 09:50 | hạng phổ thông | 890.000đ
2. **Bamboo Airways** | 11:00 - 12:20 | hạng phổ thông | 1.200.000đ
3. **Vietnam Airlines** | 06:00 - 07:20 | hạng phổ thông | 1.450.000đ
4. **Vietnam Airlines** | 14:00 - 15:20 | hạng thương gia | 2.800.000đ

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho tôi biết nhé!
```

**Kết quả**

- Đúng kỳ vọng: gọi `search_flights` và trả về 4 chuyến bay.

## Test 3 — Multi-Step Tool Chaining

**User**

```text
Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!
```

**Console log**

```text
TravelBuddy đang suy nghĩ...
Gọi tool: search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
Gọi tool: search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 2500000})
Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': '1100000,2000000'})
Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': '1100000,2500000'})
Gọi tool: calculate_budget({'total_budget': 5000000, 'expenses': 'vé máy bay: 1100000,khách sạn: 2500000'})
Trả lời trực tiếp

TravelBuddy: Chuyến bay:
- VietJet Air | 16:00 - 18:15 | economy | 1.100.000đ

Khách sạn:
- Sol by Meliá | 4 sao | Bãi Trường | rating 4.2 | 1.500.000đ/đêm (2 đêm: 3.000.000đ)

Tổng chi phí ước tính:
- Vé máy bay: 1.100.000đ
- Khách sạn: 3.000.000đ
- Tổng chi: 4.100.000đ
- Ngân sách: 5.000.000đ
- Còn lại: 900.000đ

Gợi ý thêm:
- Bạn có thể sử dụng số tiền còn lại để chi tiêu cho ăn uống, tham quan hoặc mua sắm tại Phú Quốc. Nếu cần thêm thông tin về các hoạt động tại đây, hãy cho tôi biết nhé!
```

**Kết quả**

- Đạt yêu cầu chaining: gọi `search_flights` -> `search_hotels` -> `calculate_budget`.
- Agent có 2 lần gọi `calculate_budget` sai format trước khi gọi đúng, nhưng vẫn tự sửa và kết luận chính xác.

## Test 4 — Missing Info / Clarification

**User**

```text
Tôi muốn đặt khách sạn
```

**Console log**

```text
TravelBuddy đang suy nghĩ...
Trả lời trực tiếp

TravelBuddy: Bạn có thể cho tôi biết thành phố mà bạn muốn đặt khách sạn và ngân sách mỗi đêm của bạn là bao nhiêu không?
```

**Kết quả**

- Đúng guardrail: chưa gọi tool khi thiếu dữ kiện quan trọng.

## Test 5 — Guardrail / Refusal

**User**

```text
Giải giúp tôi bài tập lập trình Python về linked list
```

**Console log**

```text
TravelBuddy đang suy nghĩ...
Trả lời trực tiếp

TravelBuddy: Xin lỗi, nhưng tôi không thể giúp bạn với bài tập lập trình. Tuy nhiên, nếu bạn cần thông tin về du lịch, tôi rất sẵn lòng hỗ trợ! Bạn có kế hoạch đi đâu không?
```

**Kết quả**

- Đúng guardrail: từ chối yêu cầu ngoài phạm vi du lịch.

## Kiểm tra thêm cho tools

Đã kiểm tra local các tool trong [tools.py](c:\Users\dqmin\2A202600022-lap4\tools.py):

- `search_flights` trả đúng danh sách chuyến bay và format tiền.
- `search_hotels` lọc theo giá, sắp xếp theo rating giảm dần.
- `calculate_budget` tính đúng tổng chi, số dư và báo lỗi khi sai định dạng.
