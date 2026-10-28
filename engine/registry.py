"""因子註冊表：載入 factors/factors.yaml，並把每個因子的 `python` 字串編譯成 compute 函式。

安全說明：此處是整個 engine 唯一使用 exec() 的地方。被執行的是本 repo 內、受信任、
由專案自己撰寫並經 git 審閱的 factors.yaml 程式碼。**使用者輸入的公式絕不走這裡，
一律走 engine.dsl（ast 白名單解析器，不 eval/exec）。**
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
FACTORS_YAML = ROOT / "factors" / "factors.yaml"


def load_factor_defs(path: Path | str = FACTORS_YAML) -> list[dict]:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return doc["factors"]


def default_params(f: dict) -> dict[str, float]:
    """factors.yaml `params[].default`（皆為數值）。"""
    return {p["name"]: p["default"] for p in f.get("params", [])}


def compile_compute(f: dict) -> Callable[..., pd.DataFrame]:
    """編譯受信任的 factors.yaml 程式碼。僅限 repo 內因子定義使用。"""
    ns: dict = {}
    exec(compile(f["python"], f"<factor {f['id']}>", "exec"), ns)  # noqa: S102 trusted repo code only
    return ns["compute"]


class Registry:
    def __init__(self, path: Path | str = FACTORS_YAML):
        self.defs = load_factor_defs(path)
        self.by_id = {f["id"]: f for f in self.defs}
        self._compiled: dict[str, Callable] = {}

    def ids(self) -> list[str]:
        return [f["id"] for f in self.defs]

    def compute_fn(self, fid: str) -> Callable[..., pd.DataFrame]:
        if fid not in self._compiled:
            self._compiled[fid] = compile_compute(self.by_id[fid])
        return self._compiled[fid]

    def compute(self, fid: str, data: dict[str, pd.DataFrame], **params) -> pd.DataFrame:
        f = self.by_id[fid]
        sub = {k: data[k] for k in f["required_fields"]}
        return self.compute_fn(fid)(sub, **params)

    def available(self, fid: str, data: dict) -> bool:
        return all(k in data for k in self.by_id[fid]["required_fields"])
