import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import pytest
from core import portfolio, config, analyze, read_ledger
from demo import create
from report import export


def fixtures():
    prices = pd.DataFrame([('A','2026-01-01',100),('A','2026-01-02',110),('A','2026-01-03',55)], columns=['symbol','date','close'])
    ledger = pd.DataFrame([
        ('2026-01-01','DEPOSIT','',0,0,1000,0),
        ('2026-01-01','BUY','A',5,100,0,1),
        ('2026-01-02','DIVIDEND','A',0,0,10,0),
        ('2026-01-03','SPLIT','A',2,0,0,0),
        ('2026-01-03','SELL','A',2,55,0,1)], columns=['date','type','symbol','quantity','price','amount','fee'])
    ledger.date = pd.to_datetime(ledger.date)
    tickers = pd.DataFrame([('A','Tech')],columns=['symbol','sector'])
    return prices, ledger, tickers


def test_accounting_and_split():
    p,l,t = fixtures()
    s,pos,d,a = portfolio(p,l,t,'2026-01-03')
    assert s['nav_usd'] == pytest.approx(1058)
    assert s['pnl_usd'] == pytest.approx(58)
    assert pos.iloc[0].quantity == 8
    assert a.pnl_usd.sum() == pytest.approx(d.pnl_usd.sum())
    assert s['twr'] == pytest.approx(.058)


def test_future_excluded():
    p,l,t = fixtures()
    s,*_ = portfolio(p,l,t,'2026-01-01')
    assert s['nav_usd'] == 999


def test_missing_price():
    p,l,t = fixtures()
    with pytest.raises(ValueError, match='precio'):
        portfolio(p.iloc[1:],l,t,'2026-01-03')


def test_duplicate_price():
    p,l,t = fixtures()
    with pytest.raises(ValueError, match='duplicados'):
        portfolio(pd.concat([p,p]),l,t,'2026-01-03')


def test_short_rejected():
    p,l,t = fixtures(); l.loc[4,'quantity']=100
    with pytest.raises(ValueError, match='negativo'):
        portfolio(p,l,t,'2026-01-03')


def test_demo_report_and_signal_availability(tmp_path):
    path = create(tmp_path)
    cfg = config(path)
    r = analyze(cfg,'2026-09-30')
    assert r['stats']['nav_usd'] > 0
    assert len(r['frames']['opportunities']) == 3
    assert export(r,cfg['report_dir']).exists()
    old = analyze(cfg,'2026-09-17')
    assert old['frames']['opportunities'].empty


def test_external_deposit_not_profit():
    p,l,t = fixtures()
    l = l.iloc[:2].copy()
    extra = l.iloc[[0]].copy(); extra['date'] = pd.Timestamp('2026-01-02'); extra['amount']=100
    s,_,d,a = portfolio(p,pd.concat([l,extra]),t,'2026-01-02')
    assert s['pnl_usd'] == 49
    assert a.pnl_usd.sum() == 49
    assert d.iloc[-1]['return'] == pytest.approx(50/1099)


def test_ledger_validation(tmp_path):
    f=tmp_path/'ledger.csv'
    f.write_text('date,type,symbol,quantity,price,amount,fee,currency,note\n2026-01-01,DEPOSIT,,0,0,100,3,USD,error\n')
    with pytest.raises(ValueError, match='fee'):
        read_ledger(f)
