import pytest
import securities

REAL_SECURITY = 'VTI'
class TestYahooFinanceData:
    def test_real_security_name(self):
        name = securities.YahooFinanceData.name(REAL_SECURITY)
        assert name is not None
        assert len(name) > 1
        assert 'Vanguard' in name

    def test_real_security_price(self):
        price = securities.YahooFinanceData.price(REAL_SECURITY)
        assert type(price) is float
        assert price > 0
