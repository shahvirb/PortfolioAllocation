import pytest
import securities
import os

REAL_SECURITY = 'VTI'
DB_PATH = 'db_test.json'


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


@pytest.fixture
def cds(request):
    def safe_delete():
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    # Let's just assume the environment might be dirty so remove the db file
    safe_delete()

    with securities.CachingDataSource(DB_PATH, expiry_hours=12) as db:
        yield db
    safe_delete()


class TestCachingDataSource:
    def test_read_write(self, cds):
        # empty database should have nothing in it
        assert len(cds.db) is 0

        # Fetch data from a real security which will serve as the source of truth
        true_name = securities.YahooFinanceData.name(REAL_SECURITY)
        true_price = securities.YahooFinanceData.price(REAL_SECURITY)

        # The security shouldn't exist yet
        assert cds.get_symbol(REAL_SECURITY) is None

        # Let's compare name and price against truth
        assert cds.name(REAL_SECURITY) == true_name
        assert cds.price(REAL_SECURITY) == true_price

        # Now the database should only have one symbol
        assert len(cds.db) is 1
