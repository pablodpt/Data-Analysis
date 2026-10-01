"""One command: audit -> research -> portfolio monitor -> immutable run exports."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid
import duckdb
import pandas as pd
from core import config, analyze
from research import run_research
from report import export


def execute(cfg,as_of):
    cutoff=str(pd.Timestamp(as_of).date())
    run_id=pd.Timestamp.now(tz='UTC').strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]
    root=Path(cfg['report_dir'])/'runs'/run_id
    root.mkdir(parents=True,exist_ok=False)
    frames=run_research(cfg,cutoff)
    try:
        result=analyze(cfg,cutoff)
        monitoring={'stage':'10_dashboard','status':'COMPUTED','detail':'Cartera y monitor disponibles'}
    except Exception as exc:
        # Research is still useful without a ledger or with an unsupported portfolio.
        result={'stats':{},'frames':{},'metadata':{'as_of':cutoff,'configuration':cfg,'database':cfg['database']}}
        monitoring={'stage':'10_dashboard','status':'ERROR','detail':f'{type(exc).__name__}: {exc}'}
    frames['research_status']=pd.concat([frames['research_status'],pd.DataFrame([monitoring])],ignore_index=True)
    result['frames'].update(frames)
    code_hash=hashlib.sha256()
    for p in sorted(Path(__file__).parent.glob('*.py')):
        code_hash.update(p.name.encode()); code_hash.update(p.read_bytes())
    stat=Path(cfg['database']).stat()
    result['metadata'].update(run_id=run_id,version='2.0',code_sha256=code_hash.hexdigest(),
        generated_at_utc=pd.Timestamp.now(tz='UTC').isoformat(),
        source_file_size=stat.st_size,source_mtime_ns=stat.st_mtime_ns,
        source_note='Size/mtime are not a content hash. Archive a consistent immutable DuckDB copy for strict reproducibility.')
    report=export(result,root)
    # Separate output database: no source writes, one transaction, one database per run.
    output=root/'analytics.duckdb'
    with duckdb.connect(str(output)) as con:
        con.execute('BEGIN')
        for name,df in result['frames'].items():
            if len(df.columns)==0:
                continue
            con.register('frame',df)
            con.execute(f'CREATE TABLE "{name}" AS SELECT * FROM frame')
            con.unregister('frame')
        meta=pd.DataFrame([{'metadata_json':json.dumps(result['metadata'],ensure_ascii=False)}])
        con.register('meta',meta)
        con.execute('CREATE TABLE run_metadata AS SELECT * FROM meta')
        con.execute('COMMIT')
    manifest={'run_id':run_id,'as_of':cutoff,'database':cfg['database'],'report':str(report.resolve()),
              'analytics':str(output.resolve()),'created_at':result['metadata']['generated_at_utc']}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    # Atomic pointer only after all outputs complete. Concurrent runs never mix frames.
    pointer=Path(cfg['report_dir'])/f'.latest-{run_id}.tmp'
    pointer.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    pointer.replace(Path(cfg['report_dir'])/'latest.json')
    return result,manifest


def load_latest(cfg,as_of):
    pointer=Path(cfg['report_dir'])/'latest.json'
    if not pointer.exists():
        return None,{}
    manifest=json.loads(pointer.read_text(encoding='utf-8'))
    if manifest['as_of']!=str(pd.Timestamp(as_of).date()) or manifest['database']!=cfg['database']:
        return None,{}
    frames={}
    with duckdb.connect(manifest['analytics'],read_only=True) as con:
        for (name,) in con.execute('SHOW TABLES').fetchall():
            if name.startswith('research_'):
                frames[name]=con.execute(f'SELECT * FROM "{name}"').df()
    return manifest,frames


def main():
    parser=argparse.ArgumentParser(description='Pipeline de los 10 puntos; fuente DuckDB solo lectura')
    parser.add_argument('--config',default='config.json')
    parser.add_argument('--as-of',default=str(pd.Timestamp.today().date()))
    parser.add_argument('--strict',action='store_true',help='Salir con codigo 2 si una etapa queda bloqueada o falla')
    args=parser.parse_args()
    result,manifest=execute(config(args.config),args.as_of)
    status=result['frames']['research_status']
    print(status.to_string(index=False))
    print('\nInforme:',manifest['report'])
    print('Resultados DuckDB:',manifest['analytics'])
    if status.status.eq('ERROR').any() or (args.strict and status.status.isin(['BLOCKED','PARTIAL']).any()):
        return 2
    return 0

if __name__=='__main__':
    sys.exit(main())
