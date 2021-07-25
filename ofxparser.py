import ofxtools


def readfile(path):
    parser = ofxtools.Parser.OFXTree()
    parser.parse(path)
    return parser.convert()


def tickers_map(ofx):
    return {sec.secinfo.secid.uniqueid: sec.secinfo.ticker for sec in ofx.securities}


def account_positions(ofx, statement_idx):
    tickers = tickers_map(ofx)
    return [(tickers[pos.invpos.secid.uniqueid], pos.invpos.units) for pos in ofx.statements[statement_idx].positions]


class Statement:
    def __init__(self, ofx, account_id):
        # self.ofx = ofx
        self.tickers_map = tickers_map(ofx)
        self.statement = None
        for st in ofx.statements:
            if st.account.acctid == str(account_id):
                self.statement = st
        if self.statement is None:
            raise KeyError('account_id not found in statements')

    def positions(self):
        return {self.tickers_map[pos.invpos.secid.uniqueid]: float(pos.invpos.units) for pos in self.statement.positions}

    # def cash_balance(self):
    #     return self.statement.balances.availcash

if __name__ == "__main__":
    ofx = readfile('OfxDownload.qfx')
    print(account_positions(ofx, 0))
