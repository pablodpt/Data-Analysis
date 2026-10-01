"""Research stages 1-9. Never writes to the market database or places orders."""
import re
import numpy as np
import pandas as pd
import duckdb
from scipy.optimize import minimize


class Unavailable(ValueError):
    """Insufficient or unconfirmed data; not an invented result."""


def require(frame, columns, name):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise Unavailable(f'{name}: faltan columnas {sorted(missing)}')
    if frame.empty:
        raise Unavailable(f'{name}: sin filas elegibles')


def available(df, cutoff, public, loaded=None):
    """End-of-day system availability, not reconstructed market availability."""
    if df.empty:
        return df.copy()
    require(df, [public] + ([loaded] if loaded else []), public)
    mask = pd.to_datetime(df[public], errors='coerce') < pd.Timestamp(cutoff) + pd.Timedelta(days=1)
    if loaded:
        mask &= pd.to_datetime(df[loaded], errors='coerce') < pd.Timestamp(cutoff) + pd.Timedelta(days=1)
    return df.loc[mask].copy()


def audit(tables, cutoff):
    rows = []
    keys = {'prices':['symbol','date'], 'tickers':['symbol'],
            'fundamentals':['symbol','snapshot_date'], 'signals':['symbol','as_of_date','computed_at'],
            'dividends':['symbol','date','amount'], 'splits':['symbol','date','ratio']}
    for name, df in tables.items():
        rows.append((name, 'rows', len(df), 'INFO'))
        if name in keys and set(keys[name]).issubset(df):
            count = int(df.duplicated(keys[name]).sum())
            rows.append((name, 'duplicate_keys', count, 'ERROR' if count else 'OK'))
        for col in df.columns:
            n = int(df[col].isna().sum())
            if n:
                rows.append((name, f'null:{col}', n, 'WARN'))
    prices = tables.get('prices', pd.DataFrame())
    if not prices.empty:
        for col in ['close','adj_close']:
            if col in prices:
                bad = (~np.isfinite(prices[col]) | (prices[col] <= 0)).sum()
                rows.append(('prices', f'invalid:{col}', int(bad), 'ERROR' if bad else 'OK'))
        if {'high','low','open','close'}.issubset(prices):
            bad = ((prices.high < prices[['low','open','close']].max(axis=1)) |
                   (prices.low > prices[['high','open','close']].min(axis=1))).sum()
            rows.append(('prices','ohlc_inconsistent',int(bad),'WARN' if bad else 'OK'))
    return pd.DataFrame(rows, columns=['table','check','count','severity'])


def price_matrix(tables, options):
    if not options.get('adj_close_is_total_return', False):
        raise Unavailable('Confirmar research.adj_close_is_total_return tras verificar el proveedor')
    p = tables['prices']
    require(p, ['date','symbol','adj_close'], 'prices')
    if p.duplicated(['symbol','date']).any():
        raise Unavailable('prices tiene claves duplicadas')
    if (~np.isfinite(p.adj_close) | (p.adj_close <= 0)).any():
        raise Unavailable('adj_close contiene precios nulos, no positivos o no finitos')
    return p.pivot(index='date', columns='symbol', values='adj_close').sort_index()


def latest(df, date):
    require(df, ['symbol',date], 'snapshot')
    if df.duplicated(['symbol', date]).any():
        raise Unavailable(f'snapshot ambiguo por symbol/{date}')
    return df.sort_values(date).groupby('symbol', as_index=False).tail(1).set_index('symbol')


def rank_factors(tables, px, cutoff, options):
    f = latest(tables['fundamentals'], 'snapshot_date').copy()
    t = tables['tickers']
    require(t, ['symbol','sector'], 'tickers')
    f = f.join(t.set_index('symbol')[['sector']], how='left')
    f['snapshot_age_days'] = (pd.Timestamp(cutoff) - pd.to_datetime(f.snapshot_date)).dt.days
    f = f[f.snapshot_age_days <= options.get('max_fundamental_age_days', 45)]
    features = {}
    def add(name, source, sign=1, positive=False):
        if source in f:
            x = pd.to_numeric(f[source], errors='coerce')
            if positive:
                x = x.where(x > 0)
            features[name] = sign*x
    add('earnings_yield','pe_ratio',positive=True)
    if 'earnings_yield' in features:
        features['earnings_yield'] = 1/features['earnings_yield']
    if {'free_cashflow','market_cap'}.issubset(f):
        features['fcf_yield'] = f.free_cashflow/f.market_cap.where(f.market_cap > 0)
    for name in ['roa','operating_margin','revenue_growth','earnings_growth']:
        add(name, name)
    if len(px) >= 253:
        features['momentum_12_1'] = (px.iloc[-22]/px.iloc[-253]-1).reindex(f.index)
    if len(px) >= 64:
        features['low_vol'] = -px.pct_change(fill_method=None).iloc[-63:].std().reindex(f.index)*np.sqrt(252)
    if not features:
        raise Unavailable('No hay factores calculables')
    raw = pd.DataFrame(features, index=f.index).replace([np.inf,-np.inf],np.nan)
    # Generic accounting metrics are not comparable for these business models.
    excluded = f.sector.eq('Financials') | f.sector.eq('Real Estate') | f.sector.isna()
    raw.loc[excluded, :] = np.nan
    scores = raw.groupby(f.sector).rank(pct=True)
    counts = raw.groupby(f.sector).transform('count')
    scores = scores.where(counts >= options.get('min_sector_peers', 5))
    groups = {'value':['earnings_yield','fcf_yield'], 'quality':['roa','operating_margin'],
              'growth':['revenue_growth','earnings_growth'], 'momentum':['momentum_12_1'], 'risk':['low_vol']}
    dimensions = pd.DataFrame(index=f.index)
    for name, cols in groups.items():
        cols = [c for c in cols if c in scores]
        dimensions[name] = scores[cols].mean(axis=1) if cols else np.nan
    dimensions['coverage'] = dimensions.notna().sum(axis=1)/5
    dimensions['score'] = dimensions[list(groups)].mean(axis=1).where(dimensions.coverage >= .8)
    result = f[['sector','snapshot_date','snapshot_age_days']].join(raw.add_prefix('raw_')).join(dimensions)
    result['note'] = np.where(excluded, 'Excluido: requiere modelo sectorial o sector conocido', 'Percentiles sectoriales; pesos iguales entre dimensiones disponibles')
    return result.sort_values('score', ascending=False, na_position='last').reset_index()


CONCEPTS = {
    'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet','SalesRevenueGoodsNet'],
    'net_income':['NetIncomeLoss','ProfitLoss'],
    'operating_income':['OperatingIncomeLoss'],
    'cfo':['NetCashProvidedByUsedInOperatingActivities'],
    'capex':['PaymentsToAcquirePropertyPlantAndEquipment'],
    'eps':['EarningsPerShareDiluted'],
}


def accounting(tables):
    f = tables['filings'].copy()
    require(f, ['symbol','concept','value','unit','period_start','period_end','filed_date','loaded_at','form_type','accession_number'], 'filings')
    f['duration'] = (pd.to_datetime(f.period_end)-pd.to_datetime(f.period_start)).dt.days
    f = f[f.form_type.isin(['10-K','10-K/A']) & f.duration.between(300,400)].copy()
    # Only comparable annual durations; never treat YTD cash flow as a quarter.
    mapped = {c:k for k,cs in CONCEPTS.items() for c in cs}
    priority = {c:i for cs in CONCEPTS.values() for i,c in enumerate(cs)}
    f['metric'] = f.concept.map(mapped)
    f['priority'] = f.concept.map(priority)
    f = f[f.metric.notna() & (((f.metric != 'eps') & f.unit.eq('USD')) | ((f.metric == 'eps') & f.unit.eq('USD/shares')))]
    if f.empty:
        raise Unavailable('Sin conceptos anuales comparables; revisar diccionario y unidades')
    f = f.sort_values(['filed_date','loaded_at','accession_number'], ascending=False).drop_duplicates(['symbol','period_end','metric','concept'])
    f = f.sort_values(['symbol','period_end','metric','priority']).drop_duplicates(['symbol','period_end','metric'])
    normalized = f[['symbol','period_start','period_end','metric','value','unit','filed_date','loaded_at','concept','accession_number']].copy()
    wide = f.pivot(index=['symbol','period_end'], columns='metric',values='value').sort_index().reset_index()
    wide.columns.name = None
    wide['period_end'] = pd.to_datetime(wide.period_end)
    gaps = wide.groupby('symbol').period_end.diff().dt.days
    for metric in CONCEPTS:
        if metric in wide:
            prev = wide.groupby('symbol')[metric].shift()
            # Negative / zero bases are not ordinary growth rates.
            wide[metric+'_yoy'] = (wide[metric]/prev-1).where((prev>0)&gaps.between(300,430))
    if {'revenue','operating_income'}.issubset(wide):
        wide['operating_margin'] = wide.operating_income/wide.revenue.where(wide.revenue>0)
    if {'cfo','net_income'}.issubset(wide):
        wide['cash_conversion'] = wide.cfo/wide.net_income.where(wide.net_income>0)
    if {'cfo','capex'}.issubset(wide):
        wide['fcf'] = wide.cfo-wide.capex
    wide['warning_profit_without_cash'] = False
    if {'net_income_yoy','cfo_yoy'}.issubset(wide):
        wide['warning_profit_without_cash'] = (wide.net_income_yoy>0)&(wide.cfo_yoy<0)
    if 'revenue_yoy' in wide:
        wide['revenue_growth_acceleration'] = wide.groupby('symbol').revenue_yoy.diff()
    return {'annual_normalized':normalized, 'annual_analysis':wide}


def performance(path):
    rows = []
    for name, g in path.groupby('strategy'):
        valid = g['net_return'].notna().all()
        if not valid:
            rows.append({'strategy':name,'status':'BLOCKED: falta precio de ejecucion/salida; no se eliminan perdidas desconocidas'})
            continue
        r = g.net_return
        wealth = (1+r).cumprod()
        drawdown = wealth/wealth.cummax().clip(lower=1)-1
        vol = r.std(ddof=1)*np.sqrt(12)
        rows.append({'strategy':name,'status':'EXPLORATORY', 'months':len(g),
            'total_return':wealth.iloc[-1]-1,'cagr':wealth.iloc[-1]**(12/len(g))-1,
            'volatility':vol, 'return_vol_ratio_rf0':r.mean()*12/vol if vol>0 else np.nan,
            'max_drawdown':drawdown.min(), 'mean_traded_fraction':g.traded_fraction.mean(),
            'positive_month_fraction':(r>0).mean()})
    return pd.DataFrame(rows)


def allocations(train, sectors, options):
    """Constrained portfolios; optimization failure is explicit, never equal-weight fallback."""
    n = train.shape[1]
    cap = options.get('max_weight', .15)
    sector_cap = options.get('max_sector', .4)
    if n < 2 or cap*n < 1-1e-9:
        raise Unavailable(f'Universo {n} incompatible con max_weight={cap}')
    cov = train.cov().to_numpy()*252
    cov = .8*cov + .2*np.diag(np.diag(cov)) + np.eye(n)*1e-8
    # Conservative shrinkage of highly noisy sample mean.
    mu = train.mean().to_numpy()*252
    mu = .25*mu + .75*mu.mean()
    sectors = sectors.reindex(train.columns).fillna('Unknown')
    constraints = [{'type':'eq','fun':lambda w: w.sum()-1}]
    for s in sectors.unique():
        mask = sectors.eq(s).to_numpy()
        constraints.append({'type':'ineq','fun':lambda w, m=mask: sector_cap-w[m].sum()})
    bounds = [(0,cap)]*n
    equal = np.ones(n)/n
    inv = 1/np.diag(cov); inv /= inv.sum()
    objectives = {
        'equal_capped':lambda w: np.sum((w-equal)**2),
        'inverse_variance_capped':lambda w: np.sum((w-inv)**2),
        'minimum_variance':lambda w: w@cov@w,
        'maximum_sharpe_rf0':lambda w: -(w@mu)/np.sqrt(w@cov@w),
    }
    out = {}
    for name, objective in objectives.items():
        res = minimize(objective, equal, method='SLSQP', bounds=bounds, constraints=constraints,
                       options={'maxiter':200,'ftol':1e-9})
        feasible = abs(res.x.sum()-1)<1e-6 and max(res.x)<=cap+1e-6 and min(res.x)>=-1e-6
        feasible &= all(res.x[sectors.eq(s)].sum() <= sector_cap+1e-6 for s in sectors.unique())
        if not res.success or not feasible:
            raise Unavailable(f'{name}: optimizacion no factible/convergente: {res.message}')
        out[name] = pd.Series(np.maximum(res.x,0), index=train.columns)
    return out


def backtests(tables, px, options, optimize=False):
    t = tables['tickers'].set_index('symbol')
    require(t.reset_index(), ['symbol','sector'], 'tickers')
    sectors = t.sector
    # Endpoints use actual last common session, never a future last price or forward fill.
    dates = px.groupby(px.index.to_period('M')).apply(lambda g:g.index[-1])
    # Require a next session for execution and at least 12 completed formation months.
    dates = [d for d in dates if px.index.get_loc(d)+1 < len(px)]
    if len(dates) < 14:
        raise Unavailable('Se requieren al menos 14 meses completos mas sesion de ejecucion')
    price_rows = tables['prices']
    require(price_rows, ['volume','close'], 'prices/liquidez')
    dv = None
    if {'volume','close'}.issubset(price_rows):
        dv = price_rows.assign(dollar_volume=price_rows.close*price_rows.volume).pivot(index='date',columns='symbol',values='dollar_volume').sort_index()
    cost = options.get('cost_bps', 10)/10000
    if not 0 <= cost < .01:
        raise ValueError('cost_bps debe estar entre 0 y 100 (excluido)')
    min_names = options.get('min_universe',20)
    prior, rows, weights_rows, failures = {}, [], [], []
    last_weights = {}
    for i in range(12,len(dates)-1):
        formed, next_formed = dates[i], dates[i+1]
        entry = px.index[px.index.get_loc(formed)+1]
        exit_date = px.index[px.index.get_loc(next_formed)+1]
        mom = px.loc[dates[i-1]]/px.loc[dates[i-12]]-1
        mom = mom.replace([np.inf,-np.inf],np.nan).dropna()
        mom = mom[px.loc[formed].reindex(mom.index).notna()]
        mom = mom[sectors.reindex(mom.index).notna()]
        if dv is not None:
            liquidity = dv.loc[:formed].tail(63).mean()
            mom = mom[liquidity.reindex(mom.index) >= options.get('min_dollar_volume', 1_000_000)]
        if len(mom) < min_names:
            failures.append({'date':formed,'reason':f'universo insuficiente: {len(mom)}'})
            continue
        if optimize:
            names = mom.nlargest(options.get('portfolio_size',30)).index
            train = px.loc[:formed,names].tail(253).pct_change(fill_method=None).iloc[1:]
            # Missing training prices cause exclusion based solely on past data.
            train = train.dropna(axis=1)
            if len(train) < options.get('min_training_sessions',126):
                failures.append({'date':formed,'reason':'historia de entrenamiento insuficiente'})
                continue
            try:
                targets = allocations(train,sectors,options)
            except Unavailable as exc:
                failures.append({'date':formed,'reason':str(exc)})
                continue
        else:
            top = mom.nlargest(max(1,int(np.ceil(len(mom)*.2)))).index
            neutral_parts = []
            for sector, g in mom.groupby(sectors.reindex(mom.index)):
                winners = g.nlargest(max(1,int(np.ceil(len(g)*.2)))).index
                neutral_parts.append(pd.Series(1/len(winners),index=winners))
            neutral = pd.concat(neutral_parts)/len(neutral_parts)
            # Matching sector-equal baseline distinguishes stock selection from sector tilts.
            sector_base = pd.concat([pd.Series(1/len(g),index=g.index) for _,g in mom.groupby(sectors.reindex(mom.index))])/len(neutral_parts)
            targets = {'momentum_top20':pd.Series(1/len(top),index=top), 'momentum_sector_equal':neutral,
                       'universe_equal':pd.Series(1/len(mom),index=mom.index), 'universe_sector_equal':sector_base}
        returns = px.loc[exit_date]/px.loc[entry]-1
        for name,w in targets.items():
            w = w[w>1e-8]; w = w/w.sum()
            r = returns.reindex(w.index)
            if not np.isfinite(r).all():
                gross = net = traded = np.nan
                status = 'MISSING_HELD_PRICE'
                prior.pop(name,None)
            else:
                old = prior.get(name,pd.Series(dtype=float))
                names = old.index.union(w.index)
                traded = (w.reindex(names,fill_value=0)-old.reindex(names,fill_value=0)).abs().sum()
                gross = float(w@r)
                net = (1-cost*traded)*(1+gross)-1
                prior[name] = w*(1+r)/(1+gross)
                status = 'OK'
            rows.append({'strategy':name,'formation':formed,'entry':entry,'exit':exit_date,
                         'gross_return':gross,'net_return':net,'traded_fraction':traded,'status':status})
            weights_rows.extend({'strategy':name,'formation':formed,'symbol':s,'weight':float(v)} for s,v in w.items())
            last_weights[name] = w
    if not rows:
        raise Unavailable('Ningun rebalanceo factible: '+str(failures[:3]))
    path = pd.DataFrame(rows)
    summary = performance(path)
    # Never advertise a continuous track record with silently omitted formation months.
    if failures:
        summary['status'] = 'INCOMPLETE: faltan rebalanceos; revisar backtest_gaps'
        for col in summary.columns.difference(['strategy','status','months']):
            summary[col] = np.nan
    result = {'path':path,'metrics':summary,'weights':pd.DataFrame(weights_rows),
              'backtest_gaps':pd.DataFrame(failures,columns=['date','reason'])}
    yearly = path.copy(); yearly['year'] = pd.to_datetime(yearly.exit).dt.year
    result['yearly'] = yearly.groupby(['strategy','year']).net_return.agg(lambda r: (1+r).prod()-1 if r.notna().all() else np.nan).reset_index()
    if failures:
        result['yearly']['net_return'] = np.nan
    return result


def current_portfolios(tables, px, options, ranking=None):
    if len(px) < 253:
        raise Unavailable('253 sesiones requeridas para cartera objetivo actual')
    sectors = tables['tickers'].set_index('symbol').sector
    mom = (px.iloc[-22]/px.iloc[-253]-1).replace([np.inf,-np.inf],np.nan).dropna()
    mom = mom[px.iloc[-1].reindex(mom.index).notna() & sectors.reindex(mom.index).notna()]
    source = tables['prices']
    require(source, ['volume','close'], 'prices/liquidez')
    dv = source.assign(dollar_volume=source.close*source.volume).pivot(index='date',columns='symbol',values='dollar_volume').sort_index().tail(63).mean()
    mom = mom[dv.reindex(mom.index)>=options.get('min_dollar_volume',1000000)]
    selection = mom
    method = 'momentum_12_1_252_sessions'
    if ranking is not None and not ranking.empty:
        selection = ranking.set_index('symbol').score.reindex(mom.index).dropna()
        method = 'current_sector_multifactor'
    names = selection.nlargest(options.get('portfolio_size',30)).index
    train = px[names].tail(253).pct_change(fill_method=None).iloc[1:].dropna(axis=1)
    targets = allocations(train,sectors,options)
    return pd.DataFrame([{'strategy':strategy,'formation':px.index[-1],'symbol':symbol,'weight':float(weight),'sector':sectors.get(symbol),'selection_method':method} for strategy,w in targets.items() for symbol,weight in w.items()])


def portfolio_research(tables, px, options, ranking=None):
    # Current targets and backtests have independent availability requirements.
    out = {}; errors = []
    try:
        out.update(backtests(tables,px,options,True))
    except Unavailable as exc:
        errors.append({'component':'walk_forward','status':'BLOCKED','reason':str(exc)})
    try:
        out['current_targets'] = current_portfolios(tables,px,options,ranking)
    except Unavailable as exc:
        errors.append({'component':'current_targets','status':'BLOCKED','reason':str(exc)})
    if not out:
        raise Unavailable(str(errors))
    out['component_status'] = pd.DataFrame(errors,columns=['component','status','reason'])
    return out


def signal_validation(tables, px, options):
    s = tables['signals'].copy()
    require(s,['symbol','as_of_date','computed_at'],'signals')
    cols = [c for c in ['momentum_score','filings_score','news_score','composite_score'] if c in s]
    if not cols:
        raise Unavailable('Sin columnas de scores')
    s['available_date'] = pd.concat([pd.to_datetime(s.as_of_date),pd.to_datetime(s.computed_at).dt.normalize()],axis=1).max(axis=1)
    s = s.sort_values('computed_at').drop_duplicates(['symbol','available_date'],keep='last')
    obs = []
    minimum = options.get('min_cross_section',20)
    for day,g in s.groupby('available_date'):
        idx = px.index.searchsorted(day,side='right') # next session close; conservative
        if idx >= len(px):
            continue
        for horizon in [21,63,126]:
            if idx+horizon >= len(px):
                continue
            future = px.iloc[idx+horizon]/px.iloc[idx]-1
            for col in cols:
                x = g.set_index('symbol')[col].rename('score').to_frame().join(future.rename('future_return')).replace([np.inf,-np.inf],np.nan).dropna()
                if len(x)<minimum or x.score.nunique()<2:
                    continue
                x['quintile'] = pd.qcut(x.score.rank(method='first'),5,labels=False)+1
                ic = x.score.rank().corr(x.future_return.rank())
                row = {'date':day,'entry':px.index[idx],'horizon_sessions':horizon,'signal':col,'n':len(x),'rank_ic':ic,
                       'top_minus_bottom':x.loc[x.quintile==5,'future_return'].mean()-x.loc[x.quintile==1,'future_return'].mean()}
                for q in range(1,6):
                    row[f'q{q}_return'] = x.loc[x.quintile==q,'future_return'].mean()
                if col != 'momentum_score' and 'momentum_score' in g:
                    z = x.join(g.set_index('symbol').momentum_score).dropna()
                    if len(z)>=minimum and z.momentum_score.nunique()>1:
                        control = np.column_stack([np.ones(len(z)),z.momentum_score.rank()])
                        xr=z.score.rank().to_numpy(); yr=z.future_return.rank().to_numpy()
                        xr-=control@np.linalg.lstsq(control,xr,rcond=None)[0]
                        yr-=control@np.linalg.lstsq(control,yr,rcond=None)[0]
                        row['partial_rank_ic_vs_momentum'] = np.corrcoef(xr,yr)[0,1] if np.std(xr)>1e-9 and np.std(yr)>1e-9 else np.nan
                obs.append(row)
    if not obs:
        raise Unavailable('Sin suficientes fechas maduras y empresas para validar scores; archivar hacia adelante')
    detail = pd.DataFrame(obs)
    summary = detail.groupby(['signal','horizon_sessions']).agg(dates=('date','nunique'),mean_rank_ic=('rank_ic','mean'),positive_ic_fraction=('rank_ic',lambda x:(x>0).mean()),mean_spread=('top_minus_bottom','mean')).reset_index()
    summary['evidence'] = np.where(summary.dates>=24,'Exploratoria: horizontes solapados, sin test independiente','INSUFICIENTE: menos de 24 fechas')
    return {'observations':detail,'summary':summary}


def pca_risk(px, weights, options):
    train = px.tail(options.get('pca_sessions',252)+1).pct_change(fill_method=None).iloc[1:].dropna(axis=1)
    train = train.loc[:,train.std()>1e-10]
    if len(train)<60 or train.shape[1]<3:
        raise Unavailable('PCA requiere 60 sesiones completas y 3 activos no constantes')
    mean, scale = train.mean(), train.std(ddof=1)
    z = (train-mean)/scale
    u,s,vt = np.linalg.svd(z.to_numpy(),full_matrices=False)
    k=min(options.get('pca_components',10),len(s))
    pcs=[f'PC{i+1}' for i in range(k)]
    load = pd.DataFrame(vt[:k].T,index=train.columns,columns=pcs)
    # Stable sign convention for reproducible interpretation.
    for i,c in enumerate(pcs):
        sign=1 if load.loc[load[c].abs().idxmax(),c]>=0 else -1
        load[c]*=sign; u[:,i]*=sign
    explained=pd.DataFrame({'component':pcs,'explained_variance_fraction':s[:k]**2/(s**2).sum()})
    residual=z.to_numpy()-(u[:,:k]*s[:k])@load.to_numpy().T
    diagnostics=pd.DataFrame({'symbol':train.columns,'residual_vol_annualized':residual.std(axis=0,ddof=1)*scale.to_numpy()*np.sqrt(252),'return_mean':mean,'return_scale':scale}).reset_index(drop=True)
    result={'loadings':load.rename_axis('symbol').reset_index(),'explained':explained,
            'scores':pd.DataFrame(u[:,:k]*s[:k],index=train.index,columns=pcs).rename_axis('date').reset_index(),
            'scaling':diagnostics,'fit_metadata':pd.DataFrame([{'start':train.index.min(),'end':train.index.max(),'sessions':len(train),'assets':len(train.columns),'input':'standardized daily adjusted returns'}])}
    if weights is not None and not weights.empty:
        exposures=[]
        for strategy,g in weights.groupby('strategy'):
            g=g[g.formation==g.formation.max()].set_index('symbol').weight
            missing=g.index.difference(load.index)
            if len(missing):
                exposures.append({'strategy':strategy,'component':'UNAVAILABLE','exposure':np.nan,'note':f'Sin PCA: {list(missing)}'})
                continue
            exposure=load.mul(scale,axis=0).T@g.reindex(load.index,fill_value=0)
            exposures.extend({'strategy':strategy,'component':c,'exposure':v,'note':'Sensibilidad diaria por unidad del score PC; no beta de mercado'} for c,v in exposure.items())
        result['portfolio_exposures']=pd.DataFrame(exposures)
    return result


EVENT_PATTERNS = [('earnings',r'earnings|results|guidance|profit|revenue'),('merger',r'merger|acquisition|acquire|takeover'),
                  ('legal',r'lawsuit|litigation|regulat|court|antitrust'),('product',r'launch|product|approval|patent'),
                  ('analyst',r'upgrade|downgrade|price target|rating')]


def news_events(tables,px,cutoff,options):
    n=tables['news'].copy()
    require(n,['symbol','published_date','loaded_at','headline','url','sentiment_score'],'news')
    n=n.sort_values('loaded_at').drop_duplicates(['symbol','url'])
    n['headline_key']=n.headline.fillna('').str.lower().str.replace(r'\W+',' ',regex=True).str.strip()
    n['day']=pd.to_datetime(n.published_date).dt.normalize()
    n=n.drop_duplicates(['symbol','day','headline_key'])
    n['event_type']=n.headline.fillna('').map(lambda text:next((name for name,pat in EVENT_PATTERNS if re.search(pat,text,re.I)),'other'))
    n['available_date']=pd.concat([pd.to_datetime(n.published_date),pd.to_datetime(n.loaded_at)],axis=1).max(axis=1).dt.normalize()
    rows=[]
    for r in n.itertuples():
        if r.symbol not in px:
            continue
        idx=px.index.searchsorted(r.available_date,side='right')
        for h in [1,5,20]:
            if idx+h>=len(px):
                continue
            ret=px.iloc[idx+h]/px.iloc[idx]-1
            other=ret.drop(index=r.symbol).dropna()
            if pd.isna(ret[r.symbol]) or len(other)<options.get('min_cross_section',20):
                continue
            rows.append({'symbol':r.symbol,'published_date':r.published_date,'entry':px.index[idx], 'event_type':r.event_type,'horizon_sessions':h,'return':ret[r.symbol],
                         'universe_return':other.mean(),'excess_return':ret[r.symbol]-other.mean(),'sentiment':r.sentiment_score,'url':r.url})
    detail=pd.DataFrame(rows)
    result={'classified_news':n.drop(columns='headline_key')}
    if not detail.empty:
        result['event_observations']=detail
        result['event_summary']=detail.groupby(['event_type','horizon_sessions']).agg(events=('symbol','size'),companies=('symbol','nunique'),mean_excess_return=('excess_return','mean'),median_excess_return=('excess_return','median')).reset_index()
    else:
        result['event_summary']=pd.DataFrame([{'status':'Sin eventos maduros suficientes; no implica ausencia de efecto'}])
    since=pd.Timestamp(cutoff)-pd.Timedelta(days=6)
    recent=n[n.day>=since].groupby('symbol').agg(articles_7d=('headline','size'),sentiment_7d=('sentiment_score','mean'))
    prior=n[(n.day<since)&(n.day>=since-pd.Timedelta(days=28))].groupby('symbol').size()/4
    recent['baseline_weekly_articles']=prior
    recent['volume_ratio']=recent.articles_7d/recent.baseline_weekly_articles.where(recent.baseline_weekly_articles>0)
    result['news_attention']=recent.reset_index()
    return result


def dividend_quality(tables,cutoff,options):
    d=tables['dividends'].copy()
    require(d,['symbol','date','amount'],'dividends')
    if not options.get('dividends_split_adjusted',False):
        raise Unavailable('Confirmar research.dividends_split_adjusted: pagos por accion comparables al corte')
    if d.duplicated(['symbol','date','amount']).any() or (d.amount<0).any() or not np.isfinite(d.amount).all():
        raise Unavailable('Dividendos duplicados o invalidos')
    f=latest(tables['fundamentals'],'snapshot_date')
    d['date']=pd.to_datetime(d.date)
    rows=[]
    for symbol,g in d.groupby('symbol'):
        g=g.sort_values('date'); cutoff=pd.Timestamp(cutoff)
        ttm=g.loc[g.date>cutoff-pd.Timedelta(days=365),'amount'].sum()
        old=g.loc[(g.date>cutoff-pd.Timedelta(days=730))&(g.date<=cutoff-pd.Timedelta(days=365)),'amount'].sum()
        row={'symbol':symbol,'dividend_ttm_per_share':ttm,'previous_ttm_per_share':old,
             'ttm_growth':ttm/old-1 if old>0 else np.nan,'last_dividend_date':g.date.max(),
             'lower_than_previous_payment':bool(len(g)>1 and g.amount.iloc[-1]<g.amount.iloc[-2])}
        for years in [3,5]:
            old_end=cutoff-pd.Timedelta(days=365*years)
            base=g.loc[(g.date>old_end-pd.Timedelta(days=365))&(g.date<=old_end),'amount'].sum()
            covered=g.date.min()<=old_end-pd.Timedelta(days=365)
            row[f'cagr_{years}y']=(ttm/base)**(1/years)-1 if covered and base>0 else np.nan
        row['payments_ttm']=int((g.date>cutoff-pd.Timedelta(days=365)).sum())
        intervals=g.date.diff().dt.days.dropna().tail(8)
        cadence=intervals.median() if len(intervals)>=3 else np.nan
        row['possible_interruption']=bool(pd.notna(cadence) and (cutoff-g.date.max()).days>1.5*cadence)
        if symbol in f.index:
            snap=f.loc[symbol]; row['snapshot_date']=snap.snapshot_date
            fresh=(cutoff-pd.Timestamp(snap.snapshot_date)).days<=options.get('max_fundamental_age_days',45)
            row['fresh_fundamentals']=fresh
            shares=snap.get('shares_outstanding',np.nan); fcf=snap.get('free_cashflow',np.nan)
            needed=ttm*shares
            row['estimated_fcf_coverage']=fcf/needed if fresh and needed>0 else np.nan
            row['payout_ratio_reported']=snap.get('payout_ratio',np.nan) if fresh else np.nan
            cap=snap.get('market_cap',np.nan)
            row['estimated_yield']=needed/cap if fresh and cap>0 else np.nan
        rows.append(row)
    out=pd.DataFrame(rows)
    out['note']='Cobertura aproximada: acciones actuales x dividendo TTM; no pagos totales reales. Reduccion no confirmada.'
    return out.sort_values('ttm_growth',ascending=False)


def run_research(cfg,as_of):
    cutoff=pd.Timestamp(as_of).normalize()
    options=cfg.get('research',{})
    tables={}; frames={}; statuses=[]
    # One connection for all reads. No SQL interpolation from user paths or table names.
    names=['prices','tickers','fundamentals','filings','news','signals','dividends','splits']
    filters={'prices':('date',None),'fundamentals':('snapshot_date',None),'filings':('filed_date','loaded_at'),
             'news':('published_date','loaded_at'),'signals':('as_of_date',None),'dividends':('date',None),'splits':('date',None)}
    with duckdb.connect(cfg['database'],read_only=True) as con:
        present={r[0] for r in con.execute('SHOW TABLES').fetchall()}
        for name in names:
            if name not in present:
                tables[name]=pd.DataFrame(); continue
            # Load then filter to audit columns and tolerate optional tables with partial schema.
            df=con.execute(f'SELECT * FROM "{name}"').df()
            if name in filters and filters[name][0] in df:
                public,loaded=filters[name]
                df=available(df,cutoff,public,loaded if loaded in df else None)
            if name=='prices' and 'date' in df:
                df['date']=pd.to_datetime(df.date)
            tables[name]=df
    def stage(number,fn):
        try:
            data=fn()
            if isinstance(data,pd.DataFrame): data={'result':data}
            for name,df in data.items():
                frames[f'research_{number}_{name}']=df
            status = 'COMPUTED_EXPLORATORY'
            detail = 'Consultar cobertura, supuestos y limitaciones'
            if number == '01_audit' and data['result'].severity.eq('ERROR').any():
                status, detail = 'BLOCKED', 'Auditoria detecta errores: revisar research_01_audit_result'
            if number == '02_ranking' and data['result'].score.notna().sum() == 0:
                status, detail = 'BLOCKED', 'Ninguna empresa cumple cobertura y comparabilidad sectorial'
            gaps = data.get('backtest_gaps', pd.DataFrame())
            component_status = data.get('component_status', pd.DataFrame())
            metrics = data.get('metrics', pd.DataFrame())
            if not gaps.empty or not component_status.empty or ('status' in metrics and metrics.status.str.startswith('BLOCKED').any()):
                status, detail = 'PARTIAL', 'Hay componentes bloqueados o periodos no evaluables; revisar tablas de estado'
            statuses.append({'stage':number,'status':status,'detail':detail})
            return data
        except Unavailable as exc:
            statuses.append({'stage':number,'status':'BLOCKED','detail':str(exc)})
        except Exception as exc:
            statuses.append({'stage':number,'status':'ERROR','detail':f'{type(exc).__name__}: {exc}'})
        return None
    stage('01_audit',lambda:audit(tables,cutoff))
    # Global schema ambiguity invalidates every join to sectors; keep audit visible.
    t=tables['tickers']
    if not t.empty and 'symbol' in t and t.symbol.duplicated().any():
        price_error='tickers contiene simbolos duplicados'
        px=None
    else:
        try: px=price_matrix(tables,options); price_error=''
        except (Unavailable,KeyError) as exc: px=None; price_error=str(exc)
    def needs_prices(fn):
        if px is None: raise Unavailable(price_error)
        return fn()
    ranking=stage('02_ranking',lambda:needs_prices(lambda:rank_factors(tables,px,cutoff,options)))
    stage('03_momentum',lambda:needs_prices(lambda:backtests(tables,px,options)))
    stage('04_filings',lambda:accounting(tables))
    stage('05_signals',lambda:needs_prices(lambda:signal_validation(tables,px,options)))
    portfolios=stage('06_portfolios',lambda:needs_prices(lambda:portfolio_research(tables,px,options,ranking['result'] if ranking else None)))
    stage('07_pca',lambda:needs_prices(lambda:pca_risk(px,portfolios.get('current_targets') if portfolios else None,options)))
    stage('08_news',lambda:needs_prices(lambda:news_events(tables,px,cutoff,options)))
    stage('09_dividends',lambda:dividend_quality(tables,cutoff,options))
    frames['research_status']=pd.DataFrame(statuses)
    frames['research_limitations']=pd.DataFrame({'limitation':[
        'Universo y sectores actuales: sesgo de supervivencia; no apto para afirmar alpha o resultados invertibles.',
        'Precios ajustados y snapshots sin versiones: reproducibilidad point-in-time incompleta. Conservar copia de la fuente.',
        'Ejecucion al cierre siguiente a disponibilidad; costes proporcionales configurables, sin modelo de impacto ni fiscalidad.',
        'No se imputa retorno cero a posiciones con precio de salida ausente: invalida la metrica de la estrategia.',
        'IC, estudios de eventos y medias son exploratorios: horizontes solapados, multiples pruebas y noticias correlacionadas.',
        'PCA ajustado hasta el corte describe riesgo actual; no se reutiliza retrospectivamente en backtests.',
        'No hay garantia de beneficios, no se conecta a broker ni envia ordenes.'
    ]})
    return frames
