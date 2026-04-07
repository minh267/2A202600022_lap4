from __future__ import annotations

from typing import Any

from langchain_core.tools import tool


FLIGHTS_DB: dict[tuple[str, str], list[dict[str, Any]]] = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB: dict[str, list[dict[str, Any]]] = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}


def format_currency(value: int) -> str:
    return f"{value:,}".replace(",", ".") + "đ"


def safe_int(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("Giá trị không hợp lệ.")
    if isinstance(value, int):
        return value
    return int(str(value).strip())


@tool
def search_flights(origin: str, destination: str) -> str:
    """Tìm kiếm chuyến bay giữa hai thành phố."""
    try:
        normalized_origin = origin.strip()
        normalized_destination = destination.strip()
        if not normalized_origin or not normalized_destination:
            return "Thiếu thông tin nơi đi hoặc nơi đến để tìm chuyến bay."

        route = (normalized_origin, normalized_destination)
        reverse_route = (normalized_destination, normalized_origin)
        flights = FLIGHTS_DB.get(route)
        used_reverse = False

        if flights is None:
            flights = FLIGHTS_DB.get(reverse_route)
            used_reverse = flights is not None

        if not flights:
            return f"Không tìm thấy chuyến bay từ {normalized_origin} đến {normalized_destination}."

        sorted_flights = sorted(flights, key=lambda item: item["price"])
        lines = [f"Danh sách chuyến bay từ {normalized_origin} đến {normalized_destination}:"]
        if used_reverse:
            lines.append("- Không có tuyến đúng chiều trong dữ liệu, đang tham chiếu chiều ngược để bạn cân nhắc.")

        for index, flight in enumerate(sorted_flights, start=1):
            lines.append(
                f"- {index}. {flight['airline']} | {flight['departure']} - {flight['arrival']} | "
                f"{flight['class']} | {format_currency(flight['price'])}"
            )
        return "\n".join(lines)
    except Exception as exc:
        return f"Lỗi khi tìm chuyến bay: {exc}"


@tool
def search_hotels(city: str, max_price_per_night: int = 99_999_999) -> str:
    """Tìm khách sạn theo thành phố và ngân sách mỗi đêm."""
    try:
        normalized_city = city.strip()
        max_price = safe_int(max_price_per_night)
        if not normalized_city:
            return "Thiếu tên thành phố để tìm khách sạn."
        if max_price < 0:
            return "Ngân sách khách sạn phải lớn hơn hoặc bằng 0."

        hotels = HOTELS_DB.get(normalized_city)
        if not hotels:
            return f"Không tìm thấy dữ liệu khách sạn tại {normalized_city}."

        filtered_hotels = [hotel for hotel in hotels if hotel["price_per_night"] <= max_price]
        filtered_hotels.sort(key=lambda item: (-item["rating"], item["price_per_night"]))

        if not filtered_hotels:
            return (
                f"Không tìm thấy khách sạn tại {normalized_city} với giá dưới "
                f"{format_currency(max_price)}/đêm. Hãy thử tăng ngân sách."
            )

        lines = [f"Khách sạn tại {normalized_city} với ngân sách tối đa {format_currency(max_price)}/đêm:"]
        for index, hotel in enumerate(filtered_hotels, start=1):
            lines.append(
                f"- {index}. {hotel['name']} | {hotel['stars']} sao | {hotel['area']} | "
                f"rating {hotel['rating']} | {format_currency(hotel['price_per_night'])}/đêm"
            )
        return "\n".join(lines)
    except Exception as exc:
        return f"Lỗi khi tìm khách sạn: {exc}"


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Tính toán ngân sách còn lại từ tổng ngân sách và chuỗi khoản chi."""
    try:
        budget = safe_int(total_budget)
        raw_expenses = expenses.strip()
        if budget < 0:
            return "Tổng ngân sách phải lớn hơn hoặc bằng 0."
        if not raw_expenses:
            return "Thiếu danh sách khoản chi. Hãy dùng định dạng tên_khoản:số_tiền."

        parsed_expenses: list[tuple[str, int]] = []
        for chunk in raw_expenses.split(","):
            item = chunk.strip()
            if not item:
                continue
            if ":" not in item:
                raise ValueError(f"Khoản chi '{item}' không đúng định dạng tên_khoản:số_tiền.")
            name, amount_text = item.split(":", 1)
            expense_name = name.strip()
            if not expense_name:
                raise ValueError("Tên khoản chi không được để trống.")
            amount = safe_int(amount_text)
            if amount < 0:
                raise ValueError(f"Khoản chi '{expense_name}' không được âm.")
            parsed_expenses.append((expense_name, amount))

        if not parsed_expenses:
            return "Không có khoản chi hợp lệ để tính ngân sách."

        total_expense = sum(amount for _, amount in parsed_expenses)
        remaining = budget - total_expense

        lines = ["Bảng chi phí:"]
        for expense_name, amount in parsed_expenses:
            display_name = expense_name.replace("_", " ").capitalize()
            lines.append(f"- {display_name}: {format_currency(amount)}")
        lines.append("---")
        lines.append(f"Tổng chi: {format_currency(total_expense)}")
        lines.append(f"Ngân sách: {format_currency(budget)}")
        if remaining >= 0:
            lines.append(f"Còn lại: {format_currency(remaining)}")
        else:
            lines.append(f"Còn lại: -{format_currency(abs(remaining))}")
            lines.append(f"Vượt ngân sách {format_currency(abs(remaining))}! Cần điều chỉnh.")
        return "\n".join(lines)
    except Exception as exc:
        return f"Lỗi tính ngân sách: {exc}"
