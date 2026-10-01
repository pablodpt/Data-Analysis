"""Create deterministic SYNTHETIC data; never open a user's database."""
from pathlib import Path
import json
import duckdb
import numpy as np
import pandas as pd


def create(root):
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    database = root / 'demo.duckdb'
    if database.exists():
        raise FileExistsError(f'{database} ya existe. No se sobrescribe.')
    rng = np.random.default_rng(42)
    days = pd.bdate_range('2025-09-01', '2026-09-30')
    rows = []
    for symbol, initial in [('AAA', 100), ('BBB', 60), ('CCC', 150)]:
        price = initial * np.exp(np.cumsum(rng.normal(.0003, .01, len(days))))
        rows.extend((symbol, d, p, p, 1000000) for d, p in zip(days, price))
    prices = pd.DataFrame(rows, columns=['symbol','date','close','adj_close','volume'])
    tickers = pd.DataFrame([('AAA','Empresa ficticia A','Technology','USD'),('BBB','Empresa ficticia B','Health Care','USD'),('CCC','Empresa ficticia C','Industrials','USD')], columns=['symbol','company_name','sector','currency'])
    signals = pd.DataFrame([(s,pd.Timestamp(d),v,f'Senal sintetica {s}',pd.Timestamp(d)+pd.Timedelta(hours=22)) for d in ['2026-09-18','2026-09-29'] for s,v in [('AAA',.8),('BBB',.5),('CCC',.2)]], columns=['symbol','as_of_date','composite_score','rationale','computed_at'])
    with duckdb.connect(str(database)) as con:
        for name in ['prices','tickers','signals']:
            con.execute(f'CREATE TABLE {name} AS SELECT * FROM {name}')
        con.execute("CREATE TABLE news(symbol VARCHAR,published_date TIMESTAMP,headline VARCHAR,source VARCHAR,sentiment_score DOUBLE,url VARCHAR,loaded_at TIMESTAMP)")
        con.execute("INSERT INTO news VALUES ('AAA','2026-09-29','Noticia ficticia de demostracion','DEMO',0.5,'https://example.com','2026-09-29')")
        con.execute("CREATE TABLE filings(symbol VARCHAR,form_type VARCHAR,filed_date DATE,period_end DATE,accession_number VARCHAR,source_url VARCHAR,loaded_at TIMESTAMP)")
        con.execute("CREATE TABLE dividends(symbol VARCHAR,date DATE,amount DOUBLE)")
        con.execute("CREATE TABLE splits(symbol VARCHAR,date DATE,ratio DOUBLE)")
        con.execute("CREATE TABLE fundamentals(symbol VARCHAR,snapshot_date DATE,market_cap DOUBLE,pe_ratio DOUBLE)")
        con.execute("INSERT INTO fundamentals VALUES ('AAA','2026-09-29',10000000,15)")
        con.execute("CREATE TABLE update_log(run_id INTEGER,started_at TIMESTAMP,finished_at TIMESTAMP,status VARCHAR,details VARCHAR)")
        con.execute("INSERT INTO update_log VALUES (1,'2026-09-30','2026-09-30','OK','DATOS SINTETICOS')")
    (root/'ledger.csv').write_text('date,type,symbol,quantity,price,amount,fee,currency,note\n2025-09-01,DEPOSIT,,0,0,100000,0,USD,DEMO\n2025-09-01,BUY,AAA,200,100,0,2,USD,DEMO\n2025-09-01,BUY,BBB,300,60,0,2,USD,DEMO\n2026-09-15,DIVIDEND,AAA,0,0,100,0,USD,DEMO\n', encoding='utf-8')
    (root/'config.json').write_text(json.dumps({'database':'demo.duckdb','ledger':'ledger.csv','report_dir':'reports','base_currency':'USD','event_days':7,'stale_days':7,'lookback_days':365,'max_position_weight':.15,'max_sector_weight':.35,'drawdown_warning':-.15}, indent=2), encoding='utf-8')
    return root/'config.json'

if __name__ == '__main__':
    print(create('demo_data'))
    print('python report.py --config demo_data/config.json --as-of 2026-09-30')
