"""python report.py --config config.json --as-of 2026-09-30"""
import argparse
import html
import json
from pathlib import Path
import pandas as pd
from core import config, analyze

DISCLAIMER = ('Cartera real solo si el libro de operaciones esta completo. USD, sin cortos ni margen. '
    'close debe ser precio historico no ajustado; dividendos netos y splits se registran manualmente. '
    'Aportaciones/retiros al inicio del dia. Sectores actuales, no historicos. '
    'No es una recomendacion de inversion. Consulte README para limites point-in-time.')


def export(result, root):
    folder = Path(root) / result['metadata']['as_of']
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'metadata.json').write_text(json.dumps(result['metadata'], indent=2, ensure_ascii=False), encoding='utf-8')
    (folder / 'metrics.json').write_text(json.dumps(result['stats'], indent=2, allow_nan=False), encoding='utf-8')
    body = ['<h1>Monitor de cartera</h1>', '<p>Corte: ' + html.escape(result['metadata']['as_of']) + '</p>',
            '<p>' + html.escape(DISCLAIMER) + '</p>', '<h2>Metricas</h2>',
            pd.DataFrame([result['stats']]).to_html(index=False, escape=True)]
    for name, df in result['frames'].items():
        df.to_csv(folder / f'{name}.csv', index=False)
        body += [f'<h2>{html.escape(name)}</h2>',
                 f'<p>{len(df)} filas. Vista limitada a 100; detalle completo en CSV.</p>',
                 df.head(100).to_html(index=False, escape=True)]
    content = '<!doctype html><html lang="es"><meta charset="utf-8"><title>Monitor de cartera</title><style>body{font:15px system-ui;margin:40px;color:#153047}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:8px;border:1px solid #ddd}h2{margin-top:40px}p{max-width:1000px}</style>' + ''.join(body) + '</html>'
    (folder / 'report.html').write_text(content, encoding='utf-8')
    return folder / 'report.html'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Informe de cartera, sin modificar DuckDB')
    parser.add_argument('--config', default='config.json')
    parser.add_argument('--as-of', default=str(pd.Timestamp.today().date()), help='Fecha inclusive YYYY-MM-DD')
    args = parser.parse_args()
    cfg = config(args.config)
    print(export(analyze(cfg, args.as_of), cfg['report_dir']))
