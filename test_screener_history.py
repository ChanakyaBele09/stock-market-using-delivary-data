import sqlite3
import time
from datetime import datetime

def get_screener_for_date(conn, date, min_deliv, min_to, spike_threshold, spike_min, max_fall):
    dates_30 = [r[0] for r in conn.execute(
        "SELECT DISTINCT date FROM daily_bhavcopy WHERE date <= ? ORDER BY date DESC LIMIT 30", (date,)
    ).fetchall()]
    if not dates_30: return []

    d_ph = ','.join('?' * len(dates_30))
    sql = f"""
        SELECT b.symbol, b.sector,
               COUNT(*) AS trading_days,
               ROUND(AVG(b.combined_deliv_per), 2) AS avg_deliv_30d,
               ROUND(SUM(b.total_volume * b.close) / 10000000.0 / COUNT(*), 2) AS avg_turnover_cr,
               ROUND(SUM(b.total_deliv_qty * b.close) / 10000000.0, 2) AS total_deliv_cr_30d,
               SUM(CASE WHEN b.combined_deliv_per > ? THEN 1 ELSE 0 END) AS spike_days,
               SUM(CASE WHEN b.combined_deliv_per >= ?
                        AND (b.total_volume * b.close / 10000000.0) >= ?
                   THEN 1 ELSE 0 END) AS repeat_days,
               ROUND(CAST(SUM(b.total_deliv_qty) AS REAL) / NULLIF(m.issued_size, 0) * 100, 4) AS deliv_mcap_pct,
               MAX(b.close) AS max_high_30d
        FROM daily_bhavcopy b
        LEFT JOIN stock_metadata m ON m.symbol = b.symbol
        WHERE b.date IN ({d_ph}) AND b.sector IS NOT NULL AND b.sector != '' AND b.sector != 'Unknown'
        GROUP BY b.symbol
        HAVING avg_deliv_30d >= ? AND avg_turnover_cr >= ? AND spike_days >= ?
        ORDER BY avg_deliv_30d DESC
    """
    params = [spike_threshold, min_deliv, min_to] + dates_30 + [min_deliv, min_to, spike_min]
    rows = conn.execute(sql, params).fetchall()
    data = [dict(r) for r in rows]

    dates_120 = [r[0] for r in conn.execute(
        "SELECT DISTINCT date FROM daily_bhavcopy WHERE date <= ? ORDER BY date DESC LIMIT 120", (date,)
    ).fetchall()]

    if dates_120 and data:
        d120_ph = ','.join('?' * len(dates_120))
        screener_symbols = [d['symbol'] for d in data]
        sym_ph = ','.join('?' * len(screener_symbols))

        price_sql = f"""
            SELECT symbol, date, close FROM daily_bhavcopy
            WHERE date IN ({d120_ph}) AND symbol IN ({sym_ph}, 'NIFTYBEES')
            ORDER BY date
        """
        price_rows = conn.execute(price_sql, dates_120 + screener_symbols).fetchall()

        prices = {}
        for pr in price_rows:
            prices.setdefault(pr['symbol'], {})[pr['date']] = pr['close']

        nifty_prices = prices.get('NIFTYBEES', {})
        sorted_dates = sorted(dates_120)

        def calc_return(sym_prices, n_days):
            if len(sorted_dates) < 2: return None
            latest_date = sorted_dates[-1]
            target_idx = max(0, len(sorted_dates) - n_days)
            old_date = sorted_dates[target_idx]
            p_new = sym_prices.get(latest_date)
            p_old = sym_prices.get(old_date)
            if p_new and p_old and p_old > 0:
                return (p_new - p_old) / p_old * 100
            return None

        nifty_ret_30 = calc_return(nifty_prices, 30)
        nifty_ret_90 = calc_return(nifty_prices, 90)
        nifty_ret_120 = calc_return(nifty_prices, 120)

        filtered_data = []
        for d in data:
            sym = d['symbol']
            sp = prices.get(sym, {})
            latest_price = sp.get(sorted_dates[-1])
            max_high_close = d.pop('max_high_30d', None)
            fall_30d = 0
            if latest_price and max_high_close and max_high_close > 0:
                fall_30d = round(((max_high_close - latest_price) / max_high_close) * 100, 2)
            d['fall_30d'] = fall_30d

            if fall_30d > max_fall: continue

            s30 = calc_return(sp, 30)
            s90 = calc_return(sp, 90)
            s120 = calc_return(sp, 120)

            rs_parts = []
            if s30 is not None and nifty_ret_30 is not None: rs_parts.append(0.25 * (s30 - nifty_ret_30))
            if s90 is not None and nifty_ret_90 is not None: rs_parts.append(0.25 * (s90 - nifty_ret_90))
            if s120 is not None and nifty_ret_120 is not None: rs_parts.append(0.50 * (s120 - nifty_ret_120))
            d['rs_score'] = round(sum(rs_parts), 2) if rs_parts else None
            filtered_data.append(d)
        data = filtered_data
    return data

conn = sqlite3.connect('data/stock_data.db')
conn.row_factory = sqlite3.Row
latest_date = conn.execute("SELECT MAX(date) FROM daily_bhavcopy").fetchone()[0]
all_dates = [r[0] for r in conn.execute("SELECT DISTINCT date FROM daily_bhavcopy WHERE date <= ? ORDER BY date DESC LIMIT 10", (latest_date,)).fetchall()]

t0 = time.time()
history = {}
for d in all_dates:
    history[d] = get_screener_for_date(conn, d, 40, 1, 50, 15, 100.0)
t1 = time.time()
print(f"Computed 10 days of screener data in {t1-t0:.2f} seconds.")
print(f"Stocks fetched on {latest_date}: {len(history[latest_date])}")
