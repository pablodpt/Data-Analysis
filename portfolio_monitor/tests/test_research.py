import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hashlib
import duckdb
import numpy as np
import pandas as pd
import pytest
from core import config
from demo_research import create_full
from pipeline import execute,load_latest
from research import (Unavailable, available, price_matrix, accounting, allocations,
                      backtests, performance, signal_validation, pca_risk, dividend_quality)


@pytest.fixture(scope='module')
def full(tmp_path_factory):
    root=tmp_path_factory.mktemp('research')
    cfg=config(create_full(root))
    before=hashlib.sha256(Path(cfg['database']).read_bytes()).hexdigest()
    result,manifest=execute(cfg,'2026-09-30')
    after=hashlib.sha256(Path(cfg['database']).read_bytes()).hexdigest()
    return cfg,result,manifest,before,after


def test_entire_pipeline_read_only_and_archived(full):
    cfg,result,manifest,before,after=full
    assert before==after
    statuses=result['frames']['research_status']
    assert len(statuses)==10
    assert statuses.status.str.startswith('COMPUTED').all(),statuses.to_dict('records')
    assert Path(manifest['report']).exists()
    assert Path(manifest['analytics']).exists()
    _,frames=load_latest(cfg,'2026-09-30')
    assert 'research_07_pca_explained' in frames
    assert load_latest(cfg,'2026-09-29')==(None,{})


def test_unconfirmed_prices_blocked():
    with pytest.raises(Unavailable,match='Confirmar'):
        price_matrix({}, {})


def test_public_and_system_availability():
    df=pd.DataFrame({'publication':pd.to_datetime(['2026-01-01']*2),'loaded':pd.to_datetime(['2026-01-02','2026-02-01'])})
    assert len(available(df,'2026-01-10','publication','loaded'))==1


def test_annual_durations_and_restated_concepts():
    rows=[]
    for year,concept,val in [(2023,'Revenues',100),(2024,'RevenueFromContractWithCustomerExcludingAssessedTax',120)]:
        rows.append(dict(symbol='A',concept=concept,value=val,unit='USD',period_start=pd.Timestamp(year,1,1),period_end=pd.Timestamp(year,12,31),filed_date=pd.Timestamp(year+1,2,1),loaded_at=pd.Timestamp(year+1,2,1),form_type='10-K',accession_number=str(year)))
    q=rows[-1].copy();q.update(form_type='10-Q',value=9999)
    out=accounting({'filings':pd.DataFrame(rows+[q])})
    assert len(out['annual_normalized'])==2
    assert out['annual_analysis'].iloc[-1].revenue_yoy==pytest.approx(.2)


def test_constrained_weights_and_failure():
    rng=np.random.default_rng(6)
    train=pd.DataFrame(rng.normal(.0003,.01,(200,9)),columns=list('ABCDEFGHI'))
    sectors=pd.Series(['S1']*3+['S2']*3+['S3']*3,index=train.columns)
    for w in allocations(train,sectors,{'max_weight':.2,'max_sector':.4}).values():
        assert w.sum()==pytest.approx(1,abs=1e-6)
        assert w.min()>=0 and w.max()<=.200001
        assert w.groupby(sectors).sum().max()<=.400001
    with pytest.raises(Unavailable):
        allocations(train,sectors,{'max_weight':.01})


def test_backtest_execution_costs_and_no_future_selection(full):
    cfg,result,*_=full
    f=result['frames']
    path=f['research_03_momentum_path']
    assert (path.entry>path.formation).all()
    assert (path.exit>path.entry).all()
    np.testing.assert_allclose(path.net_return,(1-.001*path.traded_fraction)*(1+path.gross_return)-1)
    # Last observed exit uses only the cutoff or earlier.
    assert path.exit.max()<=pd.Timestamp('2026-09-30')
    with duckdb.connect(cfg['database'],read_only=True) as con:
        tables={name:con.execute(f'SELECT * FROM {name}').df() for name in ['prices','tickers']}
    px=price_matrix(tables,{'adj_close_is_total_return':True})
    base=backtests(tables,px,cfg['research'])['weights']
    changed=px.copy(); changed.loc[changed.index>pd.Timestamp('2025-12-31'),'DEMO00']*=50
    changed_weights=backtests(tables,changed,cfg['research'])['weights']
    pd.testing.assert_frame_equal(base[base.formation<=pd.Timestamp('2025-12-31')].reset_index(drop=True),changed_weights[changed_weights.formation<=pd.Timestamp('2025-12-31')].reset_index(drop=True))


def test_missing_exit_invalidates_performance():
    frame=pd.DataFrame({'strategy':['A','A'],'net_return':[.1,np.nan],'traded_fraction':[1,.1]})
    summary=performance(frame)
    assert summary.iloc[0].status.startswith('BLOCKED')
    assert 'cagr' not in summary


def test_signal_computed_after_cutoff_not_scored():
    dates=pd.bdate_range('2020-01-01',periods=200)
    px=pd.DataFrame({f'A{i}':np.arange(200)+10+i for i in range(25)},index=dates)
    s=pd.DataFrame({'symbol':list(px),'as_of_date':pd.Timestamp('2020-01-01'),'computed_at':pd.Timestamp('2021-01-01'),'momentum_score':range(25)})
    with pytest.raises(Unavailable,match='maduras'):
        signal_validation({'signals':s},px,{'min_cross_section':20})


def test_pca_scaling_and_variance(full):
    _,result,*_=full
    f=result['frames']; load=f['research_07_pca_loadings'].set_index('symbol').to_numpy()
    np.testing.assert_allclose(load.T@load,np.eye(load.shape[1]),atol=1e-10)
    explained=f['research_07_pca_explained'].explained_variance_fraction
    assert 0<explained.sum()<=1+1e-12
    assert not f['research_07_pca_portfolio_exposures'].empty


def test_dividend_semantics_required():
    with pytest.raises(Unavailable,match='Confirmar'):
        dividend_quality({'dividends':pd.DataFrame([{'symbol':'A','date':'2026-01-01','amount':1}])},'2026-09-30',{})


def test_current_targets_timestamp(full):
    _,result,*_=full
    targets=result['frames']['research_06_portfolios_current_targets']
    assert targets.formation.max()==pd.Timestamp('2026-09-30')
    assert targets.groupby('strategy').weight.sum().between(.999999,1.000001).all()


def test_unconfirmed_pipeline_still_exports_partial_report(tmp_path):
    from demo import create
    cfg=config(create(tmp_path))
    result,manifest=execute(cfg,'2026-09-30')
    status=result['frames']['research_status'].set_index('stage')
    assert status.loc['03_momentum','status']=='BLOCKED'
    assert status.loc['10_dashboard','status']=='COMPUTED'
    assert Path(manifest['report']).exists()


def test_duplicate_prices_are_not_silently_deduplicated():
    p=pd.DataFrame({'symbol':['A','A'],'date':pd.to_datetime(['2026-01-01']*2),'adj_close':[10.,10.]})
    with pytest.raises(Unavailable,match='duplicadas'):
        price_matrix({'prices':p},{'adj_close_is_total_return':True})
