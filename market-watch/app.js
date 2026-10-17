const indices = [
  {name:'S&P 500',code:'SPX',value:5842.47,change:0.68,color:'#a8e66b',base:5750},
  {name:'NASDAQ',code:'IXIC',value:18421.36,change:1.24,color:'#9ddc6b',base:18140},
  {name:'DOW JONES',code:'DJI',value:42831.19,change:-0.18,color:'#ef8280',base:42908},
  {name:'RUSSELL 2000',code:'RUT',value:2214.82,change:0.42,color:'#a8e66b',base:2205}
];
const watchlist = [
  {symbol:'AAPL',name:'Apple Inc.',price:245.27,change:0.82,color:'#a6d4bc'},
  {symbol:'NVDA',name:'NVIDIA Corp.',price:142.88,change:2.34,color:'#a9dd79'},
  {symbol:'MSFT',name:'Microsoft',price:518.62,change:-0.24,color:'#8cb9e4'},
  {symbol:'TSLA',name:'Tesla, Inc.',price:441.70,change:1.76,color:'#e89085'},
  {symbol:'AMZN',name:'Amazon.com',price:221.39,change:-0.63,color:'#dabd7d'},
  {symbol:'GOOGL',name:'Alphabet Inc.',price:251.08,change:0.43,color:'#90b5de'},
  {symbol:'META',name:'Meta Platforms',price:742.15,change:1.08,color:'#85b8ec'},
  {symbol:'NFLX',name:'Netflix, Inc.',price:1198.46,change:-0.91,color:'#e58383'}
];
const snapshots = [
  {label:'CBOE Volatility Index',short:'VIX',value:'18.42',suffix:'pts',change:-3.16},
  {label:'US 10-Year Treasury',short:'US10Y',value:'4.12',suffix:'%',change:-0.48},
  {label:'US Dollar Index',short:'DXY',value:'99.18',suffix:'',change:0.21},
  {label:'Gold Futures',short:'GC',value:'4,386.20',suffix:'/oz',change:0.57}
];
let selectedIndex=0, selectedMover='gainers', selectedRange='1D';
const $=s=>document.querySelector(s);
const fmt=(n,d=2)=>n.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const signed=n=>`${n>=0?'+':''}${n.toFixed(2)}%`;
const classFor=n=>n>=0?'positive':'negative';

function makeSpark(seed, up=true, width=94, height=45){
  let vals=[],v=24;for(let i=0;i<28;i++){let t=(Math.sin((i+seed)*1.17)*.9+Math.cos((i+seed)*.43)*.55+(Math.sin(i*.18+seed)*.35));v+=t*(up?1:-1)*.68+(up?.15:-.08);vals.push(v)}
  const min=Math.min(...vals)-2,max=Math.max(...vals)+2;
  const pts=vals.map((n,i)=>`${(i/(vals.length-1))*width},${height-((n-min)/(max-min))*height}`).join(' ');
  return `<svg class="mini-chart" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="${up?'#a8e66b':'#ef8280'}" stroke-width="1.3" vector-effect="non-scaling-stroke"/></svg>`;
}
function renderIndices(){
  $('#indexGrid').innerHTML=indices.map((x,i)=>`<article class="index-card ${selectedIndex===i?'selected':''}" data-index="${i}" tabindex="0"><div class="index-top"><div><div class="index-title">${x.name}</div><div class="index-code">${x.code}</div></div></div><div class="index-bottom"><span class="index-value">${fmt(x.value)}</span><span class="index-change ${classFor(x.change)}">${signed(x.change)}</span></div>${makeSpark(i+3,x.change>=0)}</article>`).join('');
  document.querySelectorAll('.index-card').forEach(card=>{card.addEventListener('click',()=>selectIndex(+card.dataset.index));card.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectIndex(+card.dataset.index)}})});
}
function renderWatchlist(){
  $('#sideWatchlist').innerHTML=watchlist.map(s=>`<div class="watch-row" data-symbol="${s.symbol}" title="${s.name}"><span class="ticker-icon" style="color:${s.color}">${s.symbol.slice(0,1)}</span><span class="watch-meta"><b>${s.symbol}</b><small>${s.name}</small></span><span class="watch-change ${classFor(s.change)}">${signed(s.change)}</span></div>`).join('');
}
function chartPoints(seed,up,count=85){
  let out=[],v=.42+seed*.015;for(let i=0;i<count;i++){let t=i/(count-1);v+=((Math.sin(i*.63+seed)*.20)+(Math.cos(i*.19+seed*2)*.13)+(Math.sin(i*.08+seed)*.17))*(up?1:-1)+((up?.009:-.002));v=Math.max(.12,Math.min(.89,v));out.push(v)}return out;
}
function renderChart(){
  const idx=indices[selectedIndex], up=idx.change>=0;
  $('#chartName').textContent=idx.name==='DOW JONES'?'Dow Jones':idx.name==='NASDAQ'?'Nasdaq Composite':idx.name==='RUSSELL 2000'?'Russell 2000':idx.name;
  $('#chartSymbol').textContent=idx.code;$('#chartValue').textContent=fmt(idx.value);$('#chartChange').textContent=signed(idx.change);$('#chartChange').className=classFor(idx.change);
  $('#indexSelect').innerHTML=`${idx.name==='DOW JONES'?'Dow Jones':idx.name==='NASDAQ'?'Nasdaq':idx.name==='RUSSELL 2000'?'Russell 2000':'S&P 500'} <span>⌄</span>`;
  const points=chartPoints(selectedIndex+4,up,selectedRange==='1D'?85:selectedRange==='1W'?76:selectedRange==='1M'?74:selectedRange==='3M'?80:90);
  const coords=points.map((v,i)=>`${(i/(points.length-1))*800},${220-v*190}`);
  const stroke=up?'#a8e66b':'#ef8280';
  const fillPath=`M ${coords[0]} L ${coords.slice(1).join(' L ')} L 800,245 L 0,245 Z`;
  const linePath=`M ${coords.join(' L ')}`;
  $('#marketChart').innerHTML=`<defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="${stroke}" stop-opacity=".19"/><stop offset="100%" stop-color="${stroke}" stop-opacity="0"/></linearGradient></defs><path d="${fillPath}" fill="url(#area)"/><path d="${linePath}" fill="none" stroke="${stroke}" stroke-width="2" vector-effect="non-scaling-stroke"/><circle cx="800" cy="${220-points.at(-1)*190}" r="3.5" fill="${stroke}" stroke="#111516" stroke-width="2" vector-effect="non-scaling-stroke"/>`;
  const scales={'1D':['09:30','11:00','12:30','14:00','16:00'],'1W':['Mon','Tue','Wed','Thu','Fri'],'1M':['Sep 19','Sep 26','Oct 03','Oct 10','Oct 16'],'3M':['Jul 16','Aug 01','Aug 16','Sep 01','Oct 16'],'1Y':['Oct ’25','Jan ’26','Apr ’26','Jul ’26','Oct ’26'],'ALL':['2020','2022','2023','2025','2026']};
  $('.chart-xlabels').innerHTML=scales[selectedRange].map(x=>`<span>${x}</span>`).join('');
  const d=selectedRange==='1D'?['5,900','5,850','5,800','5,750']:selectedRange==='1W'?['5,900','5,800','5,700','5,600']:selectedRange==='1M'?['6,000','5,900','5,800','5,700']:selectedRange==='1Y'?['6,200','5,800','5,400','5,000']:['6,200','5,500','4,800','4,100'];
  $('.chart-ylabels').innerHTML=d.map(x=>`<span>${x}</span>`).join('');
  $('#chartTooltip').innerHTML=`<b>${fmt(idx.value)}</b><small>Oct 16, 2026 · 4:00 PM</small>`;
}
const gainers=[['NVDA','NVIDIA Corp.','$142.88',2.34],['TSLA','Tesla, Inc.','$441.70',1.76],['AVGO','Broadcom Inc.','$361.42',1.51],['AMD','Advanced Micro Devices','$176.23',1.28]];
const losers=[['NFLX','Netflix, Inc.','$1,198.46',-.91],['AMZN','Amazon.com','$221.39',-.63],['MSFT','Microsoft Corp.','$518.62',-.24],['KO','Coca-Cola Co.','$71.84',-.18]];
function renderMovers(){let data=selectedMover==='gainers'?gainers:losers;$('#moverList').innerHTML=data.map((x,i)=>`<div class="mover-row"><span class="mover-icon" style="background:${['#263329','#392724','#2d2a21','#252f36'][i]}">${x[0][0]}</span><span class="mover-info"><b>${x[0]}</b><small>${x[1]}</small></span><span class="mover-price"><span>${x[2]}</span><span class="${classFor(x[3])}">${signed(x[3])}</span></span></div>`).join('')}
function renderSnapshots(){$('#snapshotGrid').innerHTML=snapshots.map(x=>`<article class="snapshot-card"><div class="snapshot-label"><span>${x.label}</span><em>${x.short}</em></div><div class="snapshot-value">${x.value}<small>${x.suffix}</small><span class="snapshot-change ${classFor(x.change)}">${signed(x.change)}</span></div></article>`).join('')}
function selectIndex(i){selectedIndex=i;renderIndices();renderChart()}
function toast(message){const el=$('#toast');el.textContent=message;el.classList.add('show');clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.classList.remove('show'),2400)}
renderIndices();renderWatchlist();renderChart();renderMovers();renderSnapshots();
document.querySelectorAll('#rangeTabs button').forEach(b=>b.addEventListener('click',()=>{document.querySelector('#rangeTabs .selected').classList.remove('selected');b.classList.add('selected');selectedRange=b.dataset.range;renderChart()}));
document.querySelectorAll('.mover-tabs button').forEach(b=>b.addEventListener('click',()=>{document.querySelector('.mover-tabs .selected').classList.remove('selected');b.classList.add('selected');selectedMover=b.dataset.mover;renderMovers()}));
$('#indexSelect').addEventListener('click',()=>selectIndex((selectedIndex+1)%indices.length));
$('#allMarkets').addEventListener('click',()=>toast('You’re viewing the major market indices.'));
$('#viewWatchlist').addEventListener('click',()=>{document.querySelector('#watchlist')?.scrollIntoView({behavior:'smooth'});toast('Your watchlist is in the left sidebar.')});
$('#searchButton').addEventListener('click',()=>openDialog());
$('#openAdd').addEventListener('click',()=>openDialog());
$('#dismissNotice').addEventListener('click',()=>$('.sample-notice').remove());
function openDialog(){const d=$('#addDialog');d.showModal();$('#tickerInput').focus()}
const catalog={AAPL:['Apple Inc.','$245.27',.82],NVDA:['NVIDIA Corp.','$142.88',2.34],MSFT:['Microsoft Corp.','$518.62',-.24],TSLA:['Tesla, Inc.','$441.70',1.76],AMZN:['Amazon.com, Inc.','$221.39',-.63],GOOGL:['Alphabet Inc.','$251.08',.43],META:['Meta Platforms','$742.15',1.08],NFLX:['Netflix, Inc.','$1,198.46',-.91],AMD:['Advanced Micro Devices','$176.23',1.28],AVGO:['Broadcom Inc.','$361.42',1.51],KO:['Coca-Cola Co.','$71.84',-.18],JPM:['JPMorgan Chase','$302.11',.32],SPY:['SPDR S&P 500 ETF','$672.64',.68],QQQ:['Invesco QQQ Trust','$603.11',1.21]};
function showSuggestions(){let q=$('#tickerInput').value.trim().toUpperCase();let matches=Object.entries(catalog).filter(([sym,item])=>!q||sym.includes(q)||item[0].toUpperCase().includes(q)).slice(0,5);$('#suggestions').innerHTML=matches.map(([sym,item])=>`<button class="suggestion" data-symbol="${sym}"><b>${sym}</b><small>${item[0]}</small></button>`).join('');document.querySelectorAll('.suggestion').forEach(b=>b.addEventListener('click',()=>addSymbol(b.dataset.symbol)))}
$('#tickerInput').addEventListener('input',showSuggestions);$('#tickerInput').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();const first=$('.suggestion');if(first)addSymbol(first.dataset.symbol)}});$('#addTicker').addEventListener('click',()=>{let q=$('#tickerInput').value.trim().toUpperCase();let found=Object.keys(catalog).find(s=>s===q)||Object.keys(catalog).find(s=>catalog[s][0].toUpperCase().includes(q));if(found)addSymbol(found);else toast('Try a listed ticker such as NVDA or AAPL.')});
function addSymbol(symbol){if(watchlist.some(x=>x.symbol===symbol)){toast(`${symbol} is already on your watchlist.`);$('#addDialog').close();return}const x=catalog[symbol];watchlist.push({symbol,name:x[0],price:parseFloat(x[1].replace(/[$,]/g,'')),change:x[2],color:'#a8d891'});renderWatchlist();$('#addDialog').close();$('#tickerInput').value='';$('#suggestions').innerHTML='';toast(`${symbol} added to your watchlist.`)}
$('#addDialog').addEventListener('click',e=>{if(e.target===$('#addDialog'))$('#addDialog').close()});
