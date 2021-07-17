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

if __name__ == "__main__":
    ofx = readfile('OfxDownload.qfx')
    print(account_positions(ofx, 0))
