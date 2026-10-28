"""偏誤檢查清單（04 文件 4.6），每次評估自動產生。"""
from __future__ import annotations

import numpy as np


def bias_checks(ctx, summary: dict, n_trials: int, n_periods: int, n_params: int) -> list[dict]:
    md = ctx.md
    out = []

    def add(key, status, msg):
        out.append({"key": key, "status": status, "message": msg})

    if ctx.n_delisted > 0:
        add("survivorship", "pass", f"股票池含 {ctx.n_delisted} 檔下市股，下市前（含下市損失）報酬計入。")
    else:
        add("survivorship", "warn", "股票池不含下市股，可能有存活者偏誤。")
    base = "訊號只用 t 日收盤前資料、t+1 收盤成交、前瞻報酬從 t+1 起算；"
    if md.pit_estimated:
        add("lookahead", "warn", base + "財報無逐筆公告日，套用法定截止日/保守落後估計 PIT（PIT 為估計）。")
    else:
        add("lookahead", "pass", base + "財報以公告日生效。")
    dsr = summary.get("dsr")
    st = "pass" if (dsr is not None and dsr >= 0.95 and n_trials >= 1) else "warn"
    add("data_snooping", st,
        f"試驗次數 N={n_trials}（僅預設參數）；DSR={'n/a' if dsr is None else format(dsr, '.3f')}"
        f"{'' if st == 'pass' else '，低於 0.95 不得升級到 L3'}。")
    is_m, oos_m = summary.get("is_rank_ic_mean"), summary.get("oos_rank_ic_mean")
    if is_m is None or oos_m is None or is_m <= 0:
        add("overfitting", "warn", f"樣本內 Rank IC 非正或缺漏；參數數量 {n_params}。")
    else:
        ratio = oos_m / is_m
        add("overfitting", "pass" if ratio >= 0.5 else "warn",
            f"樣本外/樣本內 Rank IC 比 = {ratio:.2f}（< 0.5 警示）；參數數量 {n_params}。")
    small = n_periods < 36 or ctx.avg_n_stocks < 100
    add("small_sample", "warn" if small else "pass",
        f"有效期數 {n_periods}、平均截面股票數 {ctx.avg_n_stocks:.0f}（期數 < 36 或股票數 < 100 警示）。")
    if md.is_demo:
        add("demo_data", "warn", "合成示範資料，結果只為展示介面，不是研究結論；驗證等級維持 L0。")
    return out
