# -*- coding: utf-8 -*-
"""
新浪财经 A 股历史分红数据获取脚本
=====================================
数据源：新浪财经个股分红配股页面
URL 格式：https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{股票代码}.phtml

说明：
- 新浪财经分红配股页面编码为 gb2312，需指定编码解析
- 页面表格结构：第 0 行为标题"分红"，第 1 行为主表头，第 2 行为分红方案子表头，第 3 行起为数据
- 由于页面无显式"分红年度"字段，本脚本根据公告日期推导：
  1-6 月公告通常对应上一年度年报分红 → 分红年度 = 公告年份 - 1
  7-12 月公告通常对应当年中期/特别分红 → 分红年度 = 公告年份
"""

import time
import random
import csv
import os
import sys

import requests
from bs4 import BeautifulSoup

# ============================================================
# 配置
# ============================================================

# 目标股票列表（代码 -> 名称），选取代表性 A 股
STOCK_LIST = {
    "600519": "贵州茅台",
    "601398": "工商银行",
    "601318": "中国平安",
    "600036": "招商银行",
    "000858": "五粮液",
}

# 输出路径（相对于项目根目录）
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dividend_raw.csv")

# 请求配置
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.sina.com.cn/",
}
REQUEST_TIMEOUT = 20          # 秒
RETRY_TIMES = 3               # 重试次数
RETRY_DELAY = 5               # 重试间隔（秒）
SLEEP_MIN = 1.0               # 每只股票最小间隔
SLEEP_MAX = 2.0               # 每只股票最大间隔

# CSV 字段名
FIELDNAMES = [
    "股票代码",
    "股票名称",
    "公告日期",
    "分红年度",
    "送股_每10股",
    "转增_每10股",
    "派息税前_每10股_元",
    "进度",
    "除权除息日",
    "股权登记日",
    "红股上市日",
]


# ============================================================
# 工具函数
# ============================================================

def build_url(stock_code: str) -> str:
    """根据股票代码构造新浪财经分红配股页面 URL"""
    return (
        "https://vip.stock.finance.sina.com.cn/corp/go.php/"
        f"vISSUE_ShareBonus/stockid/{stock_code}.phtml"
    )


def fetch_page(url: str) -> str:
    """
    带重试机制的 HTTP 页面抓取
    返回 HTML 文本（已按 gb2312 解码）
    """
    last_err = None
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            # 新浪财经该页面使用 gb2312 编码
            resp.encoding = "gb2312"
            return resp.text
        except requests.RequestException as e:
            last_err = e
            print(f"  [第 {attempt}/{RETRY_TIMES} 次请求失败] {e}")
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_DELAY)
    raise ConnectionError(f"页面抓取失败，已重试 {RETRY_TIMES} 次: {last_err}")


def derive_dividend_year(announce_date: str) -> str:
    """
    根据公告日期推导分红年度
    规则：
      - 公告月份在 1-6 月：通常为上一年度年报分红 → 分红年度 = 公告年份 - 1
      - 公告月份在 7-12 月：通常为当年中期/特别分红 → 分红年度 = 公告年份
    若日期无法解析，返回空字符串。
    """
    try:
        parts = announce_date.strip().split("-")
        year = int(parts[0])
        month = int(parts[1])
        if month <= 6:
            return str(year - 1)
        else:
            return str(year)
    except (ValueError, IndexError):
        return ""


def parse_dividend_table(html: str, stock_code: str, stock_name: str) -> list:
    """
    解析分红配股页面 HTML，提取分红数据行
    返回字典列表，每个字典对应一条分红记录
    """
    soup = BeautifulSoup(html, "lxml")
    records = []

    # 通过表头内容定位分红表格（而非依赖固定表索引）
    tables = soup.find_all("table")
    dividend_table = None
    for t in tables:
        rows = t.find_all("tr")
        if len(rows) >= 4:
            row_text = rows[1].get_text() if len(rows) > 1 else ""
            if "公告日期" in row_text and "分红方案" in row_text:
                dividend_table = t
                break

    if dividend_table is None:
        print(f"  [警告] 未找到分红数据表格")
        return records

    rows = dividend_table.find_all("tr")
    # 数据行从第 4 行开始（索引 3），跳过标题行和两行表头
    for row in rows[3:]:
        cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        # 正常数据行应有 9 列（含"查看"列）
        if len(cells) < 8:
            continue
        # 跳过空行或"暂时没有数据"等提示行
        if not cells[0] or cells[0] == "暂时没有数据！":
            continue

        announce_date = cells[0].strip()
        record = {
            "股票代码": stock_code,
            "股票名称": stock_name,
            "公告日期": announce_date,
            "分红年度": derive_dividend_year(announce_date),
            "送股_每10股": cells[1].strip(),
            "转增_每10股": cells[2].strip(),
            "派息税前_每10股_元": cells[3].strip(),
            "进度": cells[4].strip(),
            "除权除息日": cells[5].strip(),
            "股权登记日": cells[6].strip(),
            "红股上市日": cells[7].strip(),
        }
        records.append(record)

    return records


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("新浪财经 A 股历史分红数据获取")
    print("=" * 60)

    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_records = []
    total = len(STOCK_LIST)

    for idx, (code, name) in enumerate(STOCK_LIST.items(), 1):
        print(f"\n[{idx}/{total}] 正在获取 {name}({code}) 分红数据 ...")
        url = build_url(code)

        try:
            html = fetch_page(url)
            records = parse_dividend_table(html, code, name)
            print(f"  成功获取 {len(records)} 条分红记录")
            all_records.extend(records)
        except Exception as e:
            print(f"  [错误] 获取 {name}({code}) 失败: {e}")
            continue

        # 随机间隔，避免请求过快被反爬
        if idx < total:
            sleep_sec = random.uniform(SLEEP_MIN, SLEEP_MAX)
            print(f"  等待 {sleep_sec:.1f} 秒 ...")
            time.sleep(sleep_sec)

    # 写入 CSV
    print(f"\n共获取 {len(all_records)} 条记录，正在写入 {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"原始数据已保存至: {OUTPUT_FILE}")
    print("完成！")


if __name__ == "__main__":
    main()
