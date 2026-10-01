import os
import pandas as pd
import streamlit as st
from core import config, analyze
from report import DISCLAIMER, export
from pipeline import execute, load_latest

st.set_page_config(page_title='Monitor de cartera', page_icon='📊', layout='wide')
st.title('Monitor de cartera')
st.caption('Oportunidades · Riesgo · Cambios · Resultados')
path = st.sidebar.text_input('Configuracion JSON', os.environ.get('MONITOR_CONFIG', 'config.json'))
as_of = st.sidebar.date_input('Fecha de corte inclusive', pd.Timestamp.today().date())
st.sidebar.caption('Recarga al cambiar la fecha o pulsar Actualizar. No se escribe en la base.')
st.sidebar.button('Actualizar')
try:
    cfg = config(path)
    result = analyze(cfg, as_of)
except Exception as exc:
    st.error(f'No se puede construir el informe: {exc}')
    st.info('Consulte README.md. Para probar sin su base: python demo.py')
    try:
        cfg = config(path)
    except Exception:
        st.stop()
    result = {'stats': {}, 'frames': {'daily': pd.DataFrame()}, 'metadata': {'as_of': str(as_of)}}
st.warning(DISCLAIMER)
f = result['frames']; stats = result['stats']
if stats:
    cols = st.columns(4)
    for col, label, value in zip(cols, ['Patrimonio USD', 'P&L USD', 'Rentabilidad TWR', 'Caida maxima'],
                               [f"{stats['nav_usd']:,.2f}", f"{stats['pnl_usd']:,.2f}", f"{stats['twr']:.2%}", f"{stats['max_drawdown']:.2%}"]):
        col.metric(label, value)
else:
    st.info('Sin operaciones anteriores al corte: solo se muestra investigacion de mercado.')
tabs = st.tabs(['Oportunidades', 'Riesgo', 'Cambios', 'Resultados', 'Calidad y exportacion', 'Proceso completo 1–9'])

def show(name):
    st.subheader(name.replace('_', ' ').title())
    df = f.get(name, pd.DataFrame())
    if df.empty:
        st.caption('Sin datos disponibles para este corte.')
    else:
        st.dataframe(df, width="stretch")
        st.download_button('Descargar CSV', df.to_csv(index=False), f'{name}.csv', 'text/csv', key=name)

with tabs[0]:
    st.caption('Ranking del composite_score existente: no optimiza pesos ni demuestra capacidad predictiva. Cambios frente al snapshot disponible antes de la ventana de eventos.')
    show('opportunities'); show('fundamentals')
with tabs[1]:
    show('alerts'); show('positions'); show('sectors')
    if not f['daily'].empty:
        st.line_chart(f['daily'].set_index('date')[['drawdown']])
        st.write('Volatilidad anualizada (serie diaria natural, √365):', stats['volatility_calendar_annualized'])
with tabs[2]:
    st.caption('Eventos publicados en la ventana configurada. Dividendos/splits son informativos: no se contabilizan automaticamente.')
    for name in ['news', 'filings', 'fundamental_changes', 'dividends', 'possible_dividend_cuts', 'splits']:
        show(name)
with tabs[3]:
    if not f['daily'].empty:
        st.line_chart(f['daily'].set_index('date')[['nav']])
        st.line_chart(f['daily'].set_index('date')[['wealth']])
    st.caption('Atribucion aditiva en USD, incluye costes de ejecucion y dividendos registrados. No es atribucion porcentual Brinson.')
    for name in ['attribution_week', 'attribution_symbols', 'attribution_sectors', 'daily']:
        show(name)
with tabs[4]:
    show('freshness'); show('updates')
    st.json(result['metadata'])
    if st.button('Guardar informe HTML y todos los CSV'):
        st.success(str(export(result, cfg['report_dir'])))

with tabs[5]:
    st.subheader('Pipeline de investigacion: puntos 1–9')
    st.caption('Resultados exploratorios. No son ordenes ni promesas de rentabilidad. Universo actual: posible sesgo de supervivencia.')
    if st.button('Ejecutar auditoria y todos los analisis para este corte'):
        try:
            with st.spinner('Calculando etapas; puede tardar varios minutos con la base completa...'):
                _, generated = execute(cfg, as_of)
            st.success('Ejecucion archivada: ' + generated['run_id'])
        except Exception as exc:
            st.error(str(exc))
    manifest, research_frames = load_latest(cfg, as_of)
    if manifest:
        st.caption('Ejecucion guardada: ' + manifest['run_id'] + ' · Generada: ' + manifest['created_at'])
        st.info('Estos resultados son un archivo de esa ejecucion. Si ha cambiado la fuente o la configuracion, vuelve a ejecutar el pipeline.')
        st.dataframe(research_frames.get('research_status', pd.DataFrame()), width='stretch')
        st.write(research_frames.get('research_limitations', pd.DataFrame()))
        names = sorted(k for k in research_frames if k not in ['research_status', 'research_limitations'])
        selected = st.selectbox('Resultado analitico', names) if names else None
        if selected:
            data = research_frames[selected]
            st.dataframe(data, width='stretch')
            st.download_button('Descargar resultado', data.to_csv(index=False), selected+'.csv', 'text/csv')
            if selected.endswith('_path') and {'exit','strategy','net_return'}.issubset(data):
                pivot=data.pivot(index='exit', columns='strategy', values='net_return')
                # Do not bridge missing-return intervals in a displayed equity curve.
                gap_table = selected.removesuffix('_path') + '_backtest_gaps'
                if pivot.notna().all().all() and research_frames.get(gap_table, pd.DataFrame()).empty:
                    st.line_chart((1+pivot).cumprod())
                else:
                    st.warning('Curva omitida: hay periodos ausentes o precios no disponibles.')
        st.caption('Informe completo en: ' + manifest['report'])
    else:
        st.info('No existe una ejecucion archivada para esta base y fecha. Ejecuta el pipeline aqui o desde pipeline.py.')
