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

DB_PATH = 'db_test.json'
class TestCachingDataSource:
    def test_read_write(self):
        # Remove the database file if it exists
        try:
            import os
            os.remove(DB_PATH)
        except FileNotFoundError:
            pass

        # Create the empty database which should have nothing in it
        cds = securities.CachingDataSource(DB_PATH, expiry_hours = 12)
        assert len(cds.db) is 0

        # Fetch data from a real security which will serve as the source of truth
        true_name = securities.YahooFinanceData.name(REAL_SECURITY)
        true_price = securities.YahooFinanceData.price(REAL_SECURITY)

        # The security shouldn't exist yet
        assert cds.get_symbol(REAL_SECURITY) is None

        # Let's compare name and price against truth
        assert cds.name(REAL_SECURITY) == true_name
        assert cds.price(REAL_SECURITY) == true_price

        # Clean up the db file
        del cds # delete the cds object so that tinydb releases the file handle
        os.remove(DB_PATH)

