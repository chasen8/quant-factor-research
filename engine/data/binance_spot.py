"""Binance 現貨日 K（data.binance.vision 月檔）：下載＋sha256 驗證＋載入（EXP-002 用）。

資料只放 C:\\trading-data\\quant-factors\\binance-spot\\（不進 OneDrive、不進 git）。
用法：python -m engine.data.binance_spot   （可續跑；已驗證的檔案跳過）
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
CDN = "https://data.binance.vision/"
PREFIX = "data/spot/monthly/klines/"
DATA_DIR = Path(r"C:\trading-data\quant-factors\binance-spot")
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
UA = {"User-Agent": "quant-factors-research/1.0"}
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "count", "taker_buy_base", "taker_buy_quote", "ignore"]


def _fetch(url: str, retries: int = 6, timeout: int = 60) -> bytes:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            if getattr(e, "code", None) == 404:
                raise
            time.sleep(min(30, 1.5 ** i))
    raise RuntimeError(f"下載失敗 {url}: {last}")


def _list(prefix: str, delimiter: str | None) -> tuple[list[str], list[str]]:
    """S3 listing，用 marker 分頁。回傳 (CommonPrefixes, Keys)。"""
    prefixes: list[str] = []
    keys: list[str] = []
    marker = ""
    while True:
        q = {"prefix": prefix, "marker": marker}
        if delimiter:
            q["delimiter"] = delimiter
        root = ET.fromstring(_fetch(S3 + "?" + urllib.parse.urlencode(q)))
        for e in root.findall("s:CommonPrefixes/s:Prefix", NS):
            prefixes.append(e.text)
        for e in root.findall("s:Contents/s:Key", NS):
            keys.append(e.text)
        trunc = (root.findtext("s:IsTruncated", namespaces=NS) or "").lower() == "true"
        if not trunc:
            break
        nm = root.findtext("s:NextMarker", namespaces=NS)
        marker = nm if nm else (keys[-1] if keys else prefixes[-1])
    return prefixes, keys


def list_usdt_symbols() -> list[str]:
    pref, _ = _list(PREFIX, "/")
    syms = [p[len(PREFIX):].strip("/") for p in pref]
    return sorted(s for s in syms if s.endswith("USDT"))


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _file_ok(zp: Path, cp: Path) -> bool:
    if not (zp.exists() and cp.exists()):
        return False
    want = cp.read_text(encoding="utf-8").split()[0].lower()
    return _sha256_bytes(zp.read_bytes()) == want


def _get_one(key: str, sym_dir: Path) -> str:
    """回傳 'skip' | 'ok' | 'bad'。驗證通過才寫入 zip 與 .CHECKSUM。"""
    name = key.rsplit("/", 1)[1]
    zp, cp = sym_dir / name, sym_dir / (name + ".CHECKSUM")
    if _file_ok(zp, cp):
        return "skip"
    for _ in range(3):
        cs = _fetch(CDN + urllib.parse.quote(key) + ".CHECKSUM").decode("utf-8")
        z = _fetch(CDN + urllib.parse.quote(key))
        if _sha256_bytes(z) == cs.split()[0].lower():
            zp.write_bytes(z)
            cp.write_text(cs, encoding="utf-8")
            return "ok"
    return "bad"


def _do_symbol(sym: str, data_dir: Path) -> dict:
    _, keys = _list(f"{PREFIX}{sym}/1d/", None)
    zips = [k for k in keys if k.endswith(".zip")]
    d = data_dir / sym
    d.mkdir(parents=True, exist_ok=True)
    cnt = {"skip": 0, "ok": 0, "bad": 0}
    bad = []
    for k in zips:
        r = _get_one(k, d)
        cnt[r] += 1
        if r == "bad":
            bad.append(k)
    return {"symbol": sym, "n": len(zips), **cnt, "bad_keys": bad}


def download(data_dir: Path = DATA_DIR, workers: int = 16, log_every: int = 25) -> dict:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    syms = list_usdt_symbols()
    print(f"USDT 交易對 {len(syms)} 個", flush=True)
    tot = {"symbols": len(syms), "files": 0, "ok": 0, "skip": 0, "bad": 0, "bad_keys": [], "failed_symbols": []}
    done = 0
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(_do_symbol, s, data_dir): s for s in syms}
        for f in as_completed(futs):
            s = futs[f]
            try:
                r = f.result()
            except Exception as e:  # noqa: BLE001
                tot["failed_symbols"].append(f"{s}: {e}")
                continue
            tot["files"] += r["n"]
            for k in ("ok", "skip", "bad"):
                tot[k] += r[k]
            tot["bad_keys"] += r["bad_keys"]
            done += 1
            if done % log_every == 0:
                print(f"{done}/{len(syms)} files={tot['files']} ok={tot['ok']} skip={tot['skip']} bad={tot['bad']}", flush=True)
    (data_dir / "download-summary.json").write_text(json.dumps(tot, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in tot.items() if k != "bad_keys"}, ensure_ascii=False), flush=True)
    return tot


# ------------------------------------------------------------------ 載入
def parse_open_time(ts: pd.Series) -> pd.Series:
    """依位數判斷：>=16 位（微秒，2025-01 起）或 13 位（毫秒）→ UTC 日期（normalize）。"""
    t = pd.to_numeric(ts, errors="coerce").astype("int64")
    ms = np.where(t >= 10**15, t // 1000, t)
    return pd.to_datetime(ms, unit="ms").normalize()


def read_zip(path: Path, info: dict | None = None) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        raw = z.read(z.namelist()[0]).decode("utf-8")
    first = raw.split("\n", 1)[0].split(",")[0].strip()
    skip = 0 if re.fullmatch(r"\d+", first) else 1        # 帶 header 列時略過
    if info is not None:
        info["header_files"] = info.get("header_files", 0) + skip
        info["micro_files"] = info.get("micro_files", 0) + (1 if skip == 0 and len(first) >= 16 else 0)
        info["milli_files"] = info.get("milli_files", 0) + (1 if skip == 0 and len(first) < 16 else 0)
    df = pd.read_csv(io.StringIO(raw), header=None, skiprows=skip, names=COLS, usecols=range(12))
    df = df.dropna(subset=["open_time"])
    out = pd.DataFrame({"date": parse_open_time(df["open_time"]), "close": df["close"].astype(float),
                        "quote_volume": df["quote_volume"].astype(float)})
    return out


def load_all(data_dir: Path = DATA_DIR, cache: bool = True) -> pd.DataFrame:
    """回傳長表 [symbol, date, close, quote_volume]，以 (symbol,date) 去重、排序。"""
    data_dir = Path(data_dir)
    cp = data_dir / "daily_all.parquet"
    if cache and cp.exists():
        return pd.read_parquet(cp)
    parts = []
    info: dict = {}
    for d in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        for z in sorted(d.glob("*.zip")):
            df = read_zip(z, info)
            df.insert(0, "symbol", d.name)
            parts.append(df)
    allf = pd.concat(parts, ignore_index=True)
    n0 = len(allf)
    allf = allf.drop_duplicates(["symbol", "date"], keep="first").sort_values(["symbol", "date"]).reset_index(drop=True)
    info["n_rows_raw"] = n0
    info["n_rows_dedup"] = len(allf)
    if cache:
        allf.to_parquet(cp)
        (data_dir / "load-stats.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    return allf


def dir_stats(data_dir: Path = DATA_DIR) -> dict:
    zs = [p for p in Path(data_dir).glob("*/*.zip")]
    return {"n_symbols": len({p.parent.name for p in zs}), "n_zip": len(zs),
            "total_mb": sum(p.stat().st_size for p in zs) / 1e6}


if __name__ == "__main__":
    r = download()
    sys.exit(1 if (r["bad"] or r["failed_symbols"]) else 0)
