from decimal import Decimal

class CurrencyService:
    # Cotações fixas para BRL (mockadas)
    RATES = {
        "BRL": Decimal("1.0"),
        "USD": Decimal("5.20"),
        "EUR": Decimal("5.60"),
        "COP": Decimal("0.0013") # 1000 COP = 1.3 BRL
    }

    @classmethod
    def to_brl(cls, amount: Decimal, currency: str) -> Decimal:
        rate = cls.RATES.get(currency.upper(), Decimal("1.0"))
        return amount * rate

currency_service = CurrencyService()
