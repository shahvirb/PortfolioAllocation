import pytest
import securities
import os

REAL_SECURITY_SYMBOL = 'VTI'
DB_PATH = 'db_test.json'


class TestYahooFinanceData:
    def test_real_security_name(self):
        name = securities.YahooFinanceData.name(REAL_SECURITY_SYMBOL)
        assert name is not None
        assert len(name) > 1
        assert 'Vanguard' in name

    def test_real_security_price(self):
        price = securities.YahooFinanceData.price(REAL_SECURITY_SYMBOL)
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
        true_name = securities.YahooFinanceData.name(REAL_SECURITY_SYMBOL)
        true_price = securities.YahooFinanceData.price(REAL_SECURITY_SYMBOL)

        # The security shouldn't exist yet
        assert cds.get_symbol(REAL_SECURITY_SYMBOL) is None

        # Let's compare name and price against truth
        assert cds.name(REAL_SECURITY_SYMBOL) == true_name
        assert len(cds.db) is 1
        assert cds.get_symbol(REAL_SECURITY_SYMBOL) is not None
        assert cds.price(REAL_SECURITY_SYMBOL) == true_price

    def test_expired(self, cds):
        # Fetch the security price which shouldn't be blank. This creates a record in the database
        assert cds.name(REAL_SECURITY_SYMBOL) != ''
        created = cds.get_symbol(REAL_SECURITY_SYMBOL)['record_created']
        # Now let's create an expired timestamp and update the db entry to have this expired timestamp
        expired = created - (cds.expiry_hours + 1) * 3600
        import tinydb
        import tinydb.operations
        cds.db.update(tinydb.operations.set('record_created', expired), tinydb.Query().symbol == REAL_SECURITY_SYMBOL)
        # Also let's set the name to a bad value which we should never be able to read back
        bad_name = 'bad bad bad'
        cds.db.update(tinydb.operations.set('name', bad_name), tinydb.Query().symbol == REAL_SECURITY_SYMBOL)
        # Now doing get_symbol should return None because the record should be expired
        assert cds.get_symbol(REAL_SECURITY_SYMBOL) is None
        assert cds.name(REAL_SECURITY_SYMBOL) != bad_name
        assert len(cds.db) == 1