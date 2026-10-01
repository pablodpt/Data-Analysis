"""Full, deterministic synthetic research fixture. Not actual market history."""
from pathlib import Path
import argparse
import json
import duckdb
import numpy as np
import pandas as pd
from demo import create


def create_full(root):
    path=create(root)  # refuses overwriting any existing database
    root=Path(root); rng=np.random.default_rng(104)
    dates=pd.bdate_range('2019-01-01','2026-09-30')
    symbols=[f'DEMO{i:02d}' for i in range(30)]
    sectors=['Technology','Health Care','Industrials']
    common=rng.normal(.00015,.007,len(dates))
    data=[]
    for i,symbol in enumerate(symbols):
        close=(40+i)*np.exp(np.cumsum(common+rng.normal(.0001,.009,len(dates))))
        data.extend((symbol,d,p,p,1000000) for d,p in zip(dates,close))
    prices=pd.DataFrame(data,columns=['symbol','date','close','adj_close','volume'])
    # Synthetic series explicitly interpreted as total-return for demonstration.
    tickers=pd.DataFrame([(s,f'Ficticia {s}',sectors[i%3],'USD') for i,s in enumerate(symbols)],columns=['symbol','company_name','sector','currency'])
    data=[]
    for day in pd.date_range('2020-01-01','2026-09-30',freq='MS'):
        for s in symbols:
            data.append((s,day,1e9,float(rng.uniform(8,35)),float(rng.uniform(1e7,8e7)),float(rng.uniform(.02,.2)),float(rng.uniform(.05,.3)),float(rng.uniform(-.1,.3)),float(rng.uniform(-.2,.4)),1e7,float(rng.uniform(.1,.8))))
    fundamentals=pd.DataFrame(data,columns=['symbol','snapshot_date','market_cap','pe_ratio','free_cashflow','roa','operating_margin','revenue_growth','earnings_growth','shares_outstanding','payout_ratio'])
    data=[]
    for day in pd.date_range('2020-02-01','2026-09-30',freq='MS'):
        for s in symbols:
            m,f,n=rng.normal(0,1,3)
            data.append((s,day,day+pd.Timedelta(hours=20),m,f,n,.5*m+.3*f+.2*n,'SINTETICO; sin alpha esperado'))
    signals=pd.DataFrame(data,columns=['symbol','as_of_date','computed_at','momentum_score','filings_score','news_score','composite_score','rationale'])
    data=[]
    for i,day in enumerate(pd.date_range('2021-01-01','2026-09-30',freq='5D')):
        s=symbols[i%len(symbols)]
        data.append((s,day,'Earnings results synthetic example','DEMO',float(rng.uniform(-1,1)),f'https://example.com/demo/{i}',day))
    news=pd.DataFrame(data,columns=['symbol','published_date','headline','source','sentiment_score','url','loaded_at'])
    data=[]
    for s in symbols:
        for year in range(2019,2026):
            revenue=1e8*1.08**(year-2019)
            values={'RevenueFromContractWithCustomerExcludingAssessedTax':revenue,'NetIncomeLoss':revenue*.15,
                    'OperatingIncomeLoss':revenue*.2,'NetCashProvidedByUsedInOperatingActivities':revenue*.18,
                    'PaymentsToAcquirePropertyPlantAndEquipment':revenue*.04,'EarningsPerShareDiluted':revenue*.15/1e7}
            for concept,value in values.items():
                filed=pd.Timestamp(year+1,2,15)
                data.append((s,'10-K',pd.Timestamp(year,1,1),pd.Timestamp(year,12,31),filed,filed,concept,value,'USD/shares' if concept.startswith('Earnings') else 'USD',f'{s}-{year}','https://example.com/filing'))
    filings=pd.DataFrame(data,columns=['symbol','form_type','period_start','period_end','filed_date','loaded_at','concept','value','unit','accession_number','source_url'])
    dividends=pd.DataFrame([(s,d,.1*1.05**(d.year-2019)) for s in symbols for d in pd.date_range('2019-03-15','2026-09-30',freq='3MS')],columns=['symbol','date','amount'])
    with duckdb.connect(str(root/'demo.duckdb')) as con:
        for name in ['prices','tickers','fundamentals','signals','news','filings','dividends']:
            con.register('data',locals()[name])
            con.execute(f'CREATE OR REPLACE TABLE {name} AS SELECT * FROM data')
            con.unregister('data')
    # Full research demo has no real portfolio: empty ledger intentionally avoids invented executions.
    (root/'ledger.csv').write_text('date,type,symbol,quantity,price,amount,fee,currency,note\n',encoding='utf-8')
    cfg=json.loads(path.read_text())
    cfg['research']={'adj_close_is_total_return':True,'dividends_split_adjusted':True,'max_fundamental_age_days':45,
        'min_sector_peers':5,'min_cross_section':20,'min_universe':20,'min_dollar_volume':1000000,
        'cost_bps':10,'portfolio_size':30,'max_weight':.15,'max_sector':.4,'pca_sessions':252,'pca_components':10}
    path.write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    return path

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='demo_full')
    args=parser.parse_args()
    print(create_full(args.output))
