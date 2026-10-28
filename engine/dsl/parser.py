"""安全因子公式 DSL（05 文件第 6 節）。**絕不使用 eval/exec**：用 ast.parse(mode="eval") 解析，
經白名單驗證後轉成對寬表（index=交易日、columns=股票）的運算閉包。

允許：Expression, BinOp(+ - * / **), UnaryOp(+ -), Compare(單一比較運算子), Call(白名單函式、位置參數),
      Name(白名單變數), Constant(數值)。
拒絕：屬性存取、下標、lambda、comprehension、關鍵字參數、任何含雙底線的名稱、字串/None 常數、
      BoolOp/IfExp 等其他節點。
上限：運算式長度 <= 500 字元、節點數 <= 200、巢狀深度 <= 10、時間視窗 <= 252、指數為 |常數| <= 10。

DSL 函式（仿 Alpha101 算子）：
  截面： rank(x)（百分位排名）、zscore(x)
  時序： delay(x,d) delta(x,d) ts_mean ts_std ts_sum ts_min ts_max ts_rank ts_corr(x,y,d) ts_cov(x,y,d)
  逐點： log abs sign sqrt where(cond,a,b) max2(a,b) min2(a,b)
所有時序算子只往過去看（d >= 1 的 shift / rolling），沒有負向位移。
"""
from __future__ import annotations

import ast
from typing import Callable

import numpy as np
import pandas as pd

MAX_LEN = 500
MAX_NODES = 200
MAX_DEPTH = 10
MAX_WINDOW = 252
MAX_EXP = 10

# DSL 變數 -> 資料欄位
PRICE_VARS = {"open": "open", "high": "high", "low": "low", "close": "close_adj", "volume": "volume",
              "vwap": "vwap", "mktcap": "market_cap"}
FIN_VARS = ["book_equity", "net_income", "operating_cash_flow", "total_assets", "revenue", "cogs",
            "gross_profit", "sga_expense", "interest_expense", "long_term_debt", "current_assets",
            "current_liabilities", "shares_outstanding", "turnover_value", "monthly_revenue"]
VARIABLES = set(PRICE_VARS) | {"returns"} | set(FIN_VARS)


class DSLError(ValueError):
    """公式不合法（語法、白名單、上限）。"""


# ---- 算子實作 ----
def _rank(x):
    return x.rank(axis=1, pct=True)


def _zscore(x):
    return x.sub(x.mean(axis=1), axis=0).div(x.std(axis=1, ddof=1).replace(0, np.nan), axis=0)


def _delay(x, d):
    return x.shift(int(d))


def _delta(x, d):
    return x - x.shift(int(d))


def _ts_mean(x, d):
    return x.rolling(int(d)).mean()


def _ts_std(x, d):
    return x.rolling(int(d)).std()


def _ts_sum(x, d):
    return x.rolling(int(d)).sum()


def _ts_min(x, d):
    return x.rolling(int(d)).min()


def _ts_max(x, d):
    return x.rolling(int(d)).max()


def _ts_rank(x, d):
    return x.rolling(int(d)).rank(pct=True)


def _ts_corr(x, y, d):
    return x.rolling(int(d)).corr(y).replace([np.inf, -np.inf], np.nan)


def _ts_cov(x, y, d):
    return x.rolling(int(d)).cov(y)


def _where(c, a, b):
    if isinstance(c, pd.DataFrame):
        a_ = a if isinstance(a, pd.DataFrame) else pd.DataFrame(a, index=c.index, columns=c.columns)
        b_ = b if isinstance(b, pd.DataFrame) else pd.DataFrame(b, index=c.index, columns=c.columns)
        return a_.where(c, b_)
    raise DSLError("where 的第一個參數必須是比較式（寬表）")


def _max2(a, b):
    return np.maximum(a, b)


def _min2(a, b):
    return np.minimum(a, b)


# name -> (callable, 參數型態)；'x' 為資料、'w' 為視窗常數
FUNCS: dict[str, tuple[Callable, str]] = {
    "rank": (_rank, "x"), "zscore": (_zscore, "x"),
    "delay": (_delay, "xw"), "delta": (_delta, "xw"),
    "ts_mean": (_ts_mean, "xw"), "ts_std": (_ts_std, "xw"), "ts_sum": (_ts_sum, "xw"),
    "ts_min": (_ts_min, "xw"), "ts_max": (_ts_max, "xw"), "ts_rank": (_ts_rank, "xw"),
    "ts_corr": (_ts_corr, "xxw"), "ts_cov": (_ts_cov, "xxw"),
    "log": (lambda x: np.log(x), "x"), "abs": (lambda x: np.abs(x), "x"),
    "sign": (lambda x: np.sign(x), "x"), "sqrt": (lambda x: np.sqrt(x), "x"),
    "where": (_where, "xxx"), "max2": (_max2, "xx"), "min2": (_min2, "xx"),
}


def _depth(node: ast.AST) -> int:
    kids = list(ast.iter_child_nodes(node))
    return 1 + (max(_depth(k) for k in kids) if kids else 0)


_ALLOWED_BIN = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b,
                ast.Div: lambda a, b: a / b, ast.Pow: lambda a, b: a ** b}
_ALLOWED_UN = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}
_ALLOWED_CMP = {ast.Gt: lambda a, b: a > b, ast.GtE: lambda a, b: a >= b, ast.Lt: lambda a, b: a < b,
                ast.LtE: lambda a, b: a <= b, ast.Eq: lambda a, b: a == b, ast.NotEq: lambda a, b: a != b}


class CompiledFormula:
    def __init__(self, expr: str, fn: Callable[[dict], object], variables: set[str]):
        self.expr = expr
        self._fn = fn
        self.variables = variables

    def evaluate(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """data: 欄位詞彙表寬表字典。回傳寬表；inf 轉 NaN。"""
        env = {}
        for v in self.variables:
            if v == "returns":
                env[v] = data["close_adj"].pct_change(fill_method=None)
            elif v in PRICE_VARS:
                env[v] = data[PRICE_VARS[v]]
            else:
                env[v] = data[v]
        out = self._fn(env)
        if not isinstance(out, pd.DataFrame):
            raise DSLError("公式結果必須是寬表（至少包含一個變數）")
        return out.replace([np.inf, -np.inf], np.nan)


def _build(node: ast.AST, variables: set[str]) -> Callable[[dict], object]:
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise DSLError("只允許數值常數")
        return lambda env, v=v: v
    if isinstance(node, ast.Name):
        if "__" in node.id:
            raise DSLError("名稱不可含雙底線")
        if node.id not in VARIABLES:
            raise DSLError(f"未知變數：{node.id}")
        variables.add(node.id)
        return lambda env, n=node.id: env[n]
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _ALLOWED_UN:
            raise DSLError("不允許的一元運算子")
        f, op = _build(node.operand, variables), _ALLOWED_UN[type(node.op)]
        return lambda env: op(f(env))
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _ALLOWED_BIN:
            raise DSLError("不允許的二元運算子")
        if isinstance(node.op, ast.Pow):
            r = node.right
            neg = isinstance(r, ast.UnaryOp) and isinstance(r.op, ast.USub) and isinstance(r.operand, ast.Constant)
            c = r.operand if neg else r
            if not (isinstance(c, ast.Constant) and isinstance(c.value, (int, float))
                    and not isinstance(c.value, bool) and abs(c.value) <= MAX_EXP):
                raise DSLError(f"指數必須是 |常數| <= {MAX_EXP}")
        l, r_, op = _build(node.left, variables), _build(node.right, variables), _ALLOWED_BIN[type(node.op)]
        return lambda env: op(l(env), r_(env))
    if isinstance(node, ast.Compare):
        if len(node.ops) != 1 or type(node.ops[0]) not in _ALLOWED_CMP:
            raise DSLError("只允許單一比較運算子")
        l, r_, op = _build(node.left, variables), _build(node.comparators[0], variables), _ALLOWED_CMP[type(node.ops[0])]
        return lambda env: op(l(env), r_(env))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise DSLError("只能呼叫白名單函式名稱")
        name = node.func.id
        if "__" in name or name not in FUNCS:
            raise DSLError(f"未知函式：{name}")
        if node.keywords:
            raise DSLError("不允許關鍵字參數")
        impl, sig = FUNCS[name]
        if len(node.args) != len(sig):
            raise DSLError(f"{name} 需要 {len(sig)} 個參數")
        parts = []
        for a, kind in zip(node.args, sig):
            if kind == "w":
                if not (isinstance(a, ast.Constant) and isinstance(a.value, int) and not isinstance(a.value, bool)):
                    raise DSLError(f"{name} 的視窗必須是整數常數")
                if not 1 <= a.value <= MAX_WINDOW:
                    raise DSLError(f"視窗必須在 1~{MAX_WINDOW}")
                parts.append(lambda env, v=a.value: v)
            else:
                parts.append(_build(a, variables))
        return lambda env: impl(*[p(env) for p in parts])
    raise DSLError(f"不允許的語法：{type(node).__name__}")


def compile_formula(expr: str) -> CompiledFormula:
    if not isinstance(expr, str) or not expr.strip():
        raise DSLError("公式為空")
    if len(expr) > MAX_LEN:
        raise DSLError(f"公式過長（> {MAX_LEN} 字元）")
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except (SyntaxError, RecursionError, MemoryError, ValueError) as e:
        raise DSLError(f"語法錯誤：{type(e).__name__}") from e
    n = sum(1 for _ in ast.walk(tree))
    if n > MAX_NODES:
        raise DSLError(f"節點數過多（{n} > {MAX_NODES}）")
    try:
        d = _depth(tree.body)
    except RecursionError as e:
        raise DSLError("巢狀過深") from e
    if d > MAX_DEPTH:
        raise DSLError(f"巢狀過深（{d} > {MAX_DEPTH}）")
    variables: set[str] = set()
    fn = _build(tree.body, variables)
    return CompiledFormula(expr, fn, variables)
