# -*- coding: utf-8 -*-
"""
分红数据预处理脚本
====================
读取 data/raw/dividend_raw.csv，完成清洗、类型转换与统计摘要生成，
输出清洗后数据 data/processed/dividend_clean.csv 和统计摘要
data/processed/dividend_summary.json。

清洗步骤：
  1. 去除空白字符和 HTML 残留
  2. 统一日期格式为 YYYY-MM-DD
  3. 数值字段类型转换（派息金额、送股比例等），处理 "--"、"不分配" 等非数值标记
  4. 缺失值处理（标记为 NaN 或合理默认值）
  5. 数据去重
"""

import os
import json
import re

import pandas as pd
import numpy as np

# ============================================================
# 路径配置（相对于项目根目录）
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "dividend_raw.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CLEAN_FILE = os.path.join(PROCESSED_DIR, "dividend_clean.csv")
SUMMARY_FILE = os.path.join(PROCESSED_DIR, "dividend_summary.json")


# ============================================================
# 清洗函数
# ============================================================

def clean_text(val) -> str:
    """去除空白字符和 HTML 残留，返回纯文本字符串"""
    if pd.isna(val):
        return ""
    s = str(val)
    # 去除 HTML 标签
    s = re.sub(r"<[^>]+>", "", s)
    # 去除首尾及中间多余空白
    s = s.strip()
    s = re.sub(r"\s+", "", s)
    return s


def parse_date(val) -> str:
    """
    将日期统一为 YYYY-MM-DD 格式
    无法解析或为 "--"、"不分配" 等无效标记时返回空字符串
    """
    s = clean_text(val)
    if s in ("", "--", "-", "不分配", "暂无"):
        return ""
    # 尝试解析常见日期格式
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return pd.to_datetime(s, format=fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    # 兜底：用 pandas 自动解析
    try:
        dt = pd.to_datetime(s, errors="coerce")
        if pd.notna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return ""


def parse_numeric(val) -> float:
    """
    将数值字段转换为 float
    遇到 "--"、"不分配"、空字符串等非数值标记时返回 NaN
    """
    s = clean_text(val)
    if s in ("", "--", "-", "不分配", "暂无", "nan", "None"):
        return np.nan
    # 去除可能的逗号、单位文字等
    s = s.replace(",", "").replace("元", "").replace("股", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("分红数据预处理")
    print("=" * 60)

    # 确保输出目录存在
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # ---- 1. 读取原始数据 ----
    print(f"\n[1/6] 读取原始数据: {RAW_FILE}")
    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig", dtype=str)
    print(f"  原始记录数: {len(df)}")
    print(f"  原始字段: {list(df.columns)}")

    # ---- 2. 文本清洗 ----
    print("\n[2/6] 清洗文本与去除空白...")
    text_cols = [
        "股票代码", "股票名称", "进度",
        "公告日期", "分红年度",
        "除权除息日", "股权登记日", "红股上市日",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # ---- 3. 日期格式统一 ----
    print("[3/6] 统一日期格式为 YYYY-MM-DD ...")
    date_cols = ["公告日期", "除权除息日", "股权登记日", "红股上市日"]
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_date)

    # ---- 4. 数值字段转换 ----
    print("[4/6] 数值字段类型转换 ...")
    numeric_cols = ["送股_每10股", "转增_每10股", "派息税前_每10股_元"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_numeric)
            # 派息金额为 NaN 时填 0（表示无现金分红），送股/转增同理
            df[col] = df[col].fillna(0)

    # 分红年度转为整数（若可解析）
    if "分红年度" in df.columns:
        df["分红年度"] = pd.to_numeric(df["分红年度"], errors="coerce").astype("Int64")

    # ---- 5. 数据去重 ----
    print("[5/6] 数据去重 ...")
    before = len(df)
    df = df.drop_duplicates(
        subset=["股票代码", "公告日期", "送股_每10股", "转增_每10股", "派息税前_每10股_元"],
        keep="first",
    ).reset_index(drop=True)
    after = len(df)
    print(f"  去重前 {before} 条 → 去重后 {after} 条（删除 {before - after} 条重复）")

    # ---- 6. 输出清洗后数据 ----
    print(f"[6/6] 保存清洗后数据: {CLEAN_FILE}")
    df.to_csv(CLEAN_FILE, index=False, encoding="utf-8-sig")

    # ============================================================
    # 生成统计摘要 JSON
    # ============================================================
    print("\n正在生成统计摘要 ...")
    summary = build_summary(df)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"统计摘要已保存至: {SUMMARY_FILE}")

    # ---- 打印预览 ----
    print_preview(df, summary)

    print("\n完成！")


def build_summary(df: pd.DataFrame) -> dict:
    """根据清洗后数据构建统计摘要"""
    summary = {}

    # 元信息
    valid_dates = df["公告日期"].dropna()
    valid_dates = valid_dates[valid_dates != ""]
    summary["元信息"] = {
        "总记录数": int(len(df)),
        "股票数量": int(df["股票代码"].nunique()),
        "股票列表": sorted(df["股票名称"].dropna().unique().tolist()),
        "数据时间范围": {
            "最早公告日期": str(valid_dates.min()) if len(valid_dates) > 0 else "",
            "最晚公告日期": str(valid_dates.max()) if len(valid_dates) > 0 else "",
        },
    }

    # 每只股票的分红总次数、累计派息金额
    stock_stats = []
    for (code, name), grp in df.groupby(["股票代码", "股票名称"]):
        total_dividend = float(grp["派息税前_每10股_元"].sum())
        stock_stats.append({
            "股票代码": str(code),
            "股票名称": str(name),
            "分红总次数": int(len(grp)),
            "累计派息税前_每10股_元": round(total_dividend, 4),
        })
    summary["每只股票统计"] = sorted(stock_stats, key=lambda x: x["股票代码"])

    # 按年份统计的分红总额（所有股票合计）
    # 使用分红年度字段
    yearly = {}
    for _, row in df.iterrows():
        yr = row["分红年度"]
        if pd.isna(yr):
            continue
        yr = int(yr)
        amt = float(row["派息税前_每10股_元"])
        yearly[yr] = yearly.get(yr, 0.0) + amt

    yearly_total = [
        {"年份": int(y), "分红总额_每10股_元": round(amount, 4)}
        for y, amount in sorted(yearly.items())
    ]
    summary["按年份分红总额_所有股票合计"] = yearly_total

    # 每只股票按年份的每股派息趋势
    # 派息字段为每10股税前金额，除以 10 得到每股
    per_stock_yearly = {}
    for (code, name), grp in df.groupby(["股票代码", "股票名称"]):
        yr_map = {}
        for _, row in grp.iterrows():
            yr = row["分红年度"]
            if pd.isna(yr):
                continue
            yr = int(yr)
            per_share = float(row["派息税前_每10股_元"]) / 10.0
            yr_map[yr] = yr_map.get(yr, 0.0) + per_share
        per_stock_yearly[f"{name}({code})"] = [
            {"年份": int(y), "每股派息_税前_元": round(amount, 4)}
            for y, amount in sorted(yr_map.items())
        ]
    summary["每只股票每股派息趋势"] = per_stock_yearly

    return summary


def print_preview(df: pd.DataFrame, summary: dict):
    """打印数据预览和基本统计信息"""
    print("\n" + "=" * 60)
    print("数据预览（前 5 行）")
    print("=" * 60)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.unicode.east_asian_width", True)
    print(df.head(5).to_string(index=False))

    print("\n" + "=" * 60)
    print("基本统计信息")
    print("=" * 60)
    print(f"总记录数: {summary['元信息']['总记录数']}")
    print(f"股票数量: {summary['元信息']['股票数量']}")
    print(f"股票列表: {summary['元信息']['股票列表']}")
    print(f"时间范围: {summary['元信息']['数据时间范围']['最早公告日期']} ~ "
          f"{summary['元信息']['数据时间范围']['最晚公告日期']}")

    print("\n每只股票分红统计:")
    for s in summary["每只股票统计"]:
        print(f"  {s['股票名称']}({s['股票代码']}): "
              f"{s['分红总次数']} 次, 累计派息 {s['累计派息税前_每10股_元']:.2f} 元/10股")

    print("\n按年份分红总额（最近 10 年）:")
    yearly = summary["按年份分红总额_所有股票合计"]
    for item in yearly[-10:]:
        print(f"  {item['年份']}: {item['分红总额_每10股_元']:.2f} 元/10股")


if __name__ == "__main__":
    main()
