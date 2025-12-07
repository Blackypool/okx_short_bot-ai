#!/usr/bin/env python3.10
import sys, os, logging, time, json, pandas as pd, requests, numpy as np, functools
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict


sys.path.insert(0, os.path.dirname(__file__))
from config import *


for dir in ['logs', 'data/historical', 'reports/charts', 'reports/tex']:
    os.makedirs(dir, exist_ok=True)


load_dotenv()


logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO, 
                    format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler('logs/app.log'), logging.StreamHandler()])
logger = logging.getLogger('OKX_SHORT_BOT')


# ✅ ГЛОБАЛЬНЫЙ КЭШ 24H VOLUME (обновляем раз в 5 мин)
volume_cache = {}
cache_time = 0
CACHE_TTL = 300  # 5 минут


def get_all_tickers_once():
    """✅ ОДИН запрос на ВСЕ пары (экономим rate limit)"""
    global volume_cache, cache_time
    now = time.time()
    if now - cache_time < CACHE_TTL:
        return volume_cache
    
    try:
        url = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"
        data = requests.get(url, timeout=API_TIMEOUT).json()
        if data['code'] == '0':
            volume_cache = {}
            for t in data['data']:
                symbol = t['instId']
                vol = float(t.get('volCcy24h', 0))
                volume_cache[symbol] = vol
            
            cache_time = now
            logger.info(f'✅ Volume cache updated: {len(volume_cache)} pairs')
            return volume_cache
    except Exception as e:
        logger.error(f'Volume cache error: {e}')
    return volume_cache


def get_ticker_volume(symbol):
    """✅ 24H VOLUME ИЗ КЭША"""
    vols = get_all_tickers_once()
    return vols.get(symbol, 0.0)


def get_dynamic_symbols(min_vol=MIN_24H_VOL_USD):
    vols = get_all_tickers_once()
    symbols = [s for s in vols if vols[s] > min_vol and s.endswith('-USDT-SWAP') and 'BTC' not in s]
    logger.info(f'✅ {len(symbols[:MAX_SYMBOLS])} pairs (Vol>${min_vol/1e6:.0f}M)')
    return sorted(symbols, key=lambda x: vols[x], reverse=True)[:MAX_SYMBOLS]


class OKXShortBot:
    def __init__(self):
        all_symbols = get_dynamic_symbols()
        
        n = len(all_symbols)
        fvg_count = int(n * FVG_STRATEGY_PCT)
        trend_count = int(n * TREND_STRATEGY_PCT)
        combo_count = n - fvg_count - trend_count
        
        self.symbols_fvg = all_symbols[:fvg_count]
        self.symbols_trend = all_symbols[fvg_count:fvg_count+trend_count]
        self.symbols_combo = all_symbols[fvg_count+trend_count:]
        
        self.signals = []
        logger.info(f'🚀 v8.3 FIXED VOLUME: Corr<{MIN_CORR} | RR>{MIN_RR} | Vol>${MIN_24H_VOL_USD/1e6:.0f}M')
        logger.info(f'📊 Strategies: FVG({len(self.symbols_fvg)}) TREND({len(self.symbols_trend)}) COMBO({len(self.symbols_combo)})')


    def get_data(self, symbol):
        try:
            url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar={CANDLE_TIMEFRAME}&limit=300"
            data = requests.get(url, timeout=API_TIMEOUT).json()
            if data['code'] != '0': return None
            
            df = pd.DataFrame(data['data'], columns=['ts','o','h','l','c','vol','volCcy','volCcyQuote','confirm'])
            for col in ['o','h','l','c','vol']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df[['ts','o','h','l','c','vol']].dropna().sort_values('ts').reset_index(drop=True)
            return df if len(df) >= 50 else None
        except:
            return None


    def vol_24h_check(self, symbol):
        vol_24h = get_ticker_volume(symbol)
        is_active = vol_24h >= MIN_24H_VOL_USD
        return is_active, vol_24h


    def get_btc_data(self):
        try:
            url = f"https://www.okx.com/api/v5/market/candles?instId=BTC-USDT-SWAP&bar={CANDLE_TIMEFRAME}&limit=300"
            data = requests.get(url, timeout=API_TIMEOUT).json()
            if data['code'] != '0': return None
            df = pd.DataFrame(data['data'], columns=['ts','o','h','l','c','vol','volCcy','volCcyQuote','confirm'])
            for col in ['o','h','l','c']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df[['ts','o','h','l','c']].dropna().sort_values('ts').reset_index(drop=True)
        except:
            return None


    def fvg_count(self, df):
        fvgs = []
        for i in range(2, len(df)):
            if df['l'].iloc[i] > df['h'].iloc[i-2]:
                fvgs.append(i)
        return len([f for f in fvgs if f > len(df)-FVG_LOOKBACK_CANDLES])


    def trend_check(self, df):
        if len(df) < TREND_LOOKBACK_CANDLES: return False
        recent = df.tail(TREND_LOOKBACK_CANDLES)
        highs = recent['h'].values
        local_maxs = []
        for i in range(3, len(highs)-3):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1]:
                local_maxs.append((i, highs[i]))
        return len(local_maxs) >= 2 and local_maxs[-1][1] > local_maxs[-2][1]


    def corr_check(self, symbol, df):
        if 'BTC' in symbol: return 1.0
        btc = self.get_btc_data()
        if btc is None or len(df) < 50 or len(btc) < 50: return 0.5
        try:
            ret1 = df['c'].pct_change().dropna()
            ret2 = btc['c'].pct_change().dropna()
            min_len = min(len(ret1), len(ret2))
            if min_len < 20: return 0.5
            corr = abs(ret1.tail(min_len).corr(ret2.tail(min_len)))
            return corr if not pd.isna(corr) else 0.5
        except:
            return 0.5


    def manip_check(self, df):
        if len(df) < 50: return True
        recent = df.tail(min(288, len(df)))
        body = abs(recent['c'] - recent['o'])
        wick = (recent['h'] - np.maximum(recent['o'], recent['c'])) + (np.minimum(recent['o'], recent['c']) - recent['l'])
        ratio = wick / (body + 1e-10)
        return (ratio > MANIP_WICK_RATIO).sum() < MANIP_MAX_ANOMALIES


    def atr_pct(self, df):
        if len(df) < 14: return 0.0
        price = float(df['c'].iloc[-1])
        hl = df['h'] - df['l']
        hc = abs(df['h'] - df['c'].shift(1))
        lc = abs(df['l'] - df['c'].shift(1))
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        atr = tr.tail(14).mean()
        return float((atr / price) * 100) if price > 0 else 0.0


    def daily_range(self, df):
        if len(df) < 96: return None
        recent = df.tail(96)
        h = float(recent['h'].max())
        l = float(recent['l'].min())
        c = float(df['c'].iloc[-1])
        return {'range_pct': ((h-l)/c*100) if c > 0 else 0}


    def risk_calc(self, df):
        entry = float(df['c'].iloc[-1])
        atr = self.atr_pct(df)
        sl_pct = ATR_SL_MULT * atr
        tp_pct = ATR_TP_MULT * atr
        sl = entry + (entry * sl_pct / 100)
        tp = entry - (entry * tp_pct / 100)
        rr = tp_pct / sl_pct if sl_pct > 0 else 0.0
        return entry, sl, tp, float(rr), float(atr)


    def analyze(self, symbol, strategy):
        df = self.get_data(symbol)
        if df is None: return
        
        vol_24h_ok, vol_24h_usd = self.vol_24h_check(symbol)
        fvg = self.fvg_count(df)
        trend = self.trend_check(df)
        corr = self.corr_check(symbol, df)
        corr_ok = corr < MIN_CORR
        clean = self.manip_check(df)
        entry, sl, tp, rr, atr = self.risk_calc(df)
        daily = self.daily_range(df)
        
        if LOG_ALL_PAIRS or fvg >= 1 or vol_24h_ok:
            d_str = f"D:{daily['range_pct']:.1f}%" if daily else "D:N/A"
            vol_str = f"V24:${vol_24h_usd/1e6:.1f}M({vol_24h_ok})"
            logger.info(f'📊 {strategy} {symbol} | FVG:{fvg} | C:{corr:.2f}({corr_ok}) | T:{trend} | Cl:{clean} | {vol_str} | ATR:{atr:.2f}% | RR:{rr:.2f} | {d_str}')
        
        if strategy == 'FVG':
            if fvg >= MIN_FVG and corr_ok and vol_24h_ok and rr >= MIN_RR:
                logger.info(f'🔥 FVG-SIGNAL: {symbol} | V24:${vol_24h_usd/1e6:.1f}M')
                logger.info(f'   E:{entry:.6f} SL:{sl:.6f} TP:{tp:.6f} RR:{rr:.2f}')
                sig = {'ts': datetime.now().isoformat(), 'symbol': symbol, 'strategy': 'FVG', 'entry': entry, 'sl': sl, 'tp': tp, 'rr': rr, 'fvg': fvg, 'vol24h': vol_24h_usd}
                self.signals.append(sig)
                with open(f'logs/signals_{datetime.now().strftime("%Y%m%d")}.json', 'a') as f:
                    json.dump(sig, f)
                    f.write('\n')
        
        elif strategy == 'TREND':
            if trend and corr_ok and clean and vol_24h_ok and rr >= MIN_RR:
                logger.info(f'⬆️ TREND-SIGNAL: {symbol} | V24:${vol_24h_usd/1e6:.1f}M')
                logger.info(f'   E:{entry:.6f} SL:{sl:.6f} TP:{tp:.6f} RR:{rr:.2f}')
                sig = {'ts': datetime.now().isoformat(), 'symbol': symbol, 'strategy': 'TREND', 'entry': entry, 'sl': sl, 'tp': tp, 'rr': rr, 'vol24h': vol_24h_usd}
                self.signals.append(sig)
                with open(f'logs/signals_{datetime.now().strftime("%Y%m%d")}.json', 'a') as f:
                    json.dump(sig, f)
                    f.write('\n')
        
        elif strategy == 'COMBO':
            if fvg >= MIN_FVG and trend and corr_ok and clean and vol_24h_ok and rr >= MIN_RR:
                logger.info(f'🔥🔥🔥 COMBO-SIGNAL: {symbol} | V24:${vol_24h_usd/1e6:.1f}M')
                logger.info(f'   E:{entry:.6f} SL:{sl:.6f} TP:{tp:.6f} RR:{rr:.2f}')
                sig = {'ts': datetime.now().isoformat(), 'symbol': symbol, 'strategy': 'COMBO', 'entry': entry, 'sl': sl, 'tp': tp, 'rr': rr, 'fvg': fvg, 'vol24h': vol_24h_usd}
                self.signals.append(sig)
                with open(f'logs/signals_{datetime.now().strftime("%Y%m%d")}.json', 'a') as f:
                    json.dump(sig, f)
                    f.write('\n')

    def gen_report(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/tex/report_{timestamp}.tex"

        fvg_sigs = [s for s in self.signals if s['strategy'] == 'FVG']
        trend_sigs = [s for s in self.signals if s['strategy'] == 'TREND']
        combo_sigs = [s for s in self.signals if s['strategy'] == 'COMBO']

        tex = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{booktabs}
\title{OKX Short Bot Report - v8.3}
\date{""" + datetime.now().strftime('%Y-%m-%d %H:%M') + r"""}
\begin{document}
\maketitle

\section{Configuration}
Corr<""" + str(MIN_CORR) + r""" \quad RR>""" + str(MIN_RR) + r""" \quad Vol>$""" + str(int(MIN_24H_VOL_USD/1e6)) + r"""M \quad SL """ + str(ATR_SL_MULT) + r"""× \quad TP """ + str(ATR_TP_MULT) + r"""×

\section{Signals}
Total: """ + str(len(self.signals)) + r""" \quad FVG: """ + str(len(fvg_sigs)) + r""" \quad Trend: """ + str(len(trend_sigs)) + r""" \quad Combo: """ + str(len(combo_sigs)) + r"""

"""

        if fvg_sigs:
            tex += r"""\subsection{FVG Signals}
\begin{tabular}{lrrrr}
\toprule
Symbol & Entry & SL & TP & RR \\
\midrule
"""
            for s in fvg_sigs:
                tex += f"{s['symbol']} & {s['entry']:.6f} & {s['sl']:.6f} & {s['tp']:.6f} & {s['rr']:.2f} \\\\\n"
            tex += r"""\bottomrule
\end{tabular}

"""

        if trend_sigs:
            tex += r"""\subsection{Trend Signals}
\begin{tabular}{lrrrr}
\toprule
Symbol & Entry & SL & TP & RR \\
\midrule
"""
            for s in trend_sigs:
                tex += f"{s['symbol']} & {s['entry']:.6f} & {s['sl']:.6f} & {s['tp']:.6f} & {s['rr']:.2f} \\\\\n"
            tex += r"""\bottomrule
\end{tabular}

"""

        if combo_sigs:
            tex += r"""\subsection{Combo Signals}
\begin{tabular}{lrrrr}
\toprule
Symbol & Entry & SL & TP & RR \\
\midrule
"""
            for s in combo_sigs:
                tex += f"{s['symbol']} & {s['entry']:.6f} & {s['sl']:.6f} & {s['tp']:.6f} & {s['rr']:.2f} \\\\\n"
            tex += r"""\bottomrule
\end{tabular}

"""

        tex += r"\end{document}"

        with open(filename, "w") as f:
            f.write(tex)
        logger.info(f"📄 Report: {filename}")


    def run(self):
        while True:
            try:
                total = len(self.symbols_fvg) + len(self.symbols_trend) + len(self.symbols_combo)
                logger.info(f'🔍 SCAN {total} pairs | {time.strftime("%H:%M:%S")}')
                self.signals = []
                
                for sym in self.symbols_fvg:
                    self.analyze(sym, 'FVG')
                    time.sleep(SLEEP_BETWEEN_SYMBOLS)
                logger.info(f'  ✅ FVG: {len(self.symbols_fvg)}/{len(self.symbols_fvg)}')
                
                for sym in self.symbols_trend:
                    self.analyze(sym, 'TREND')
                    time.sleep(SLEEP_BETWEEN_SYMBOLS)
                logger.info(f'  ✅ TREND: {len(self.symbols_trend)}/{len(self.symbols_trend)}')
                
                for i, sym in enumerate(self.symbols_combo):
                    self.analyze(sym, 'COMBO')
                    time.sleep(SLEEP_BETWEEN_SYMBOLS)
                    if (i+1) % 30 == 0:
                        logger.info(f'  ✅ COMBO: {i+1}/{len(self.symbols_combo)}')
                
                logger.info(f'🎯 Signals: {len(self.signals)}')
                self.gen_report()
                
                if SINGLE_SCAN_MODE:
                    logger.info('✅ Single scan complete')
                    break
                
                logger.info(f'⏳ Next in {SCAN_INTERVAL_SEC}s')
                time.sleep(SCAN_INTERVAL_SEC)
            except KeyboardInterrupt:
                logger.info('👋 STOPPED')
                self.gen_report()
                break


def main():
    bot = OKXShortBot()
    bot.run()


if __name__ == '__main__':
    main()
