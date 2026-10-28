"""Blave CDN 台股日資料：下載＋sha256 驗證＋載入＋寬表（EXP-001 用）。

資料檔只放 C:\\trading-data\\quant-factors\\blave-cdn\\（不進 OneDrive、不進 git）。
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

CDN_BASE = "https://download.blave.org/data/twstock/daily/v1/"
DATA_DIR = Path(r"C:\trading-data\quant-factors\blave-cdn")
ATTRIBUTION = "資料來源：臺灣證券交易所、證券櫃檯買賣中心（政府資料開放授權 https://data.gov.tw/license；經 Blave CDN 整理）"
YEARS = list(range(2010, 2027))


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _get(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "quant-factors-research/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)


def download(data_dir: Path = DATA_DIR) -> dict:
    """下載 manifest 與所需檔案；已存在且雜湊正確就不重下。回傳 manifest。"""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    mpath = data_dir / "manifest.json"
    _get(CDN_BASE + "manifest.json", mpath)
    man = json.loads(mpath.read_text(encoding="utf-8"))
    names = [f"year/{y}.parquet" for y in YEARS] + ["recent.parquet", "events.parquet"]
    for n in names:
        want = man["files"][n]
        want = want["sha256"] if isinstance(want, dict) else want
        dest = data_dir / n.replace("/", "_")
        if dest.exists() and _sha256(dest) == want:
            continue
        _get(CDN_BASE + n, dest)
        got = _sha256(dest)
        if got != want:
            raise RuntimeError(f"sha256 不符：{n} 預期 {want} 實得 {got}")
    return man


def load_raw(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    """回傳 (daily 長表, events 長表)；daily 以 (stock_id, date) 去重（recent 與年檔重疊）。"""
    data_dir = Path(data_dir)
    parts = [pd.read_parquet(data_dir / f"year_{y}.parquet") for y in YEARS]
    parts.append(pd.read_parquet(data_dir / "recent.parquet"))
    d = pd.concat(parts, ignore_index=True)
    d["stock_id"] = d["stock_id"].astype(str)
    d["date"] = pd.to_datetime(d["date"])
    d = d.drop_duplicates(["stock_id", "date"], keep="first")
    ev = pd.read_parquet(data_dir / "events.parquet")
    ev["stock_id"] = ev["stock_id"].astype(str)
    ev["date"] = pd.to_datetime(ev["date"])
    return d, ev


def build_wide(daily: pd.DataFrame, events: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """寬表：close_raw、volume、amount、ret（含息日報酬）、market。

    ret 規則：
    - 當日無成交（volume<=0 或收盤缺）：NaN。
    - 有成交日：基準價 = 上一個有成交日收盤，但若在（上一有成交日, 今日] 區間內有事件，
      則改用該區間內「最早事件」的 ref_price 當基準（保守：中間事件不重複計；
      同日多事件亦取第一筆，依 events 列序）。
      即 ret = C_t / base - 1。一般日（無事件）就是 C_t / C_{t-1} - 1。
      事件日當天且前一日有成交時，base = ref_price，符合規格 C_t/ref_price - 1。
    """
    return _build_wide(daily, events)


def _build_wide(daily: pd.DataFrame, events: pd.DataFrame) -> dict[str, pd.DataFrame]:
    close = daily.pivot(index="date", columns="stock_id", values="close").sort_index()
    vol = daily.pivot(index="date", columns="stock_id", values="volume").reindex(close.index)
    amt = daily.pivot(index="date", columns="stock_id", values="amount").reindex(close.index)
    traded = (vol > 0) & close.notna() & (close > 0)
    close = close.where(traded)
    vol = vol.where(traded)
    amt = amt.where(traded)

    dates = close.index
    C = close.to_numpy(dtype=float)
    T, N = C.shape
    # 事件基準價矩陣：event_ref[t, j] = 當日該股事件 ref_price（同日多筆取第一筆）
    ref = np.full((T, N), np.nan)
    ev = events.dropna(subset=["ref_price"])
    ev = ev[ev["ref_price"] > 0].drop_duplicates(["date", "stock_id"], keep="first")
    ti = dates.get_indexer(ev["date"])
    cols = {s: i for i, s in enumerate(close.columns)}
    ci = ev["stock_id"].map(cols)
    ok = (ti >= 0) & ci.notna().to_numpy()
    ref[ti[ok], ci[ok].astype(int).to_numpy()] = ev["ref_price"].to_numpy()[ok]

    ret = np.full((T, N), np.nan)
    last_c = np.full(N, np.nan)     # 上一有成交日收盤
    pend_ref = np.full(N, np.nan)   # 自上一有成交日以來最早的事件 ref_price
    for t in range(T):
        r_t = ref[t]
        newev = ~np.isnan(r_t) & np.isnan(pend_ref)
        pend_ref[newev] = r_t[newev]
        c = C[t]
        tr = ~np.isnan(c)
        base = np.where(np.isnan(pend_ref), last_c, pend_ref)
        valid = tr & ~np.isnan(base)
        ret[t, valid] = c[valid] / base[valid] - 1.0
        last_c[tr] = c[tr]
        pend_ref[tr] = np.nan
    retdf = pd.DataFrame(ret, index=dates, columns=close.columns)
    mk = daily.drop_duplicates("stock_id", keep="last").set_index("stock_id")["market"]
    return {"close_raw": close, "volume": vol, "amount": amt, "ret": retdf,
            "market": mk.reindex(close.columns)}
