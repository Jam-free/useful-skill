#!/usr/bin/env python3
"""
真实的公告抓取脚本 - 从官方渠道获取准确信息
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re

# 官方网站列表
official_sources = [
    {
        "name": "深圳市住房和建设局",
        "url": "https://zjj.sz.gov.cn",
        "notice_page": "https://zjj.sz.gov.cn/xxgk/tzgg/index.shtml"
    },
    {
        "name": "福田区住建局",
        "url": "https://www.szft.gov.cn",
        "notice_page": "https://www.szft.gov.cn/bmxx/qjsj/tzgg/index.shtml"
    },
    {
        "name": "龙华区住建局",
        "url": "https://www.szlhq.gov.cn",
        "notice_page": "https://www.szlhq.gov.cn/lhq/zdfwgb/zfztgb/zxgg38/index.shtml"
    }
]

def fetch_page(url):
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取 {url} 失败: {e}")
        return None

def parse_housing_notices(html, source_name):
    """解析保障房公告"""
    notices = []
    soup = BeautifulSoup(html, 'html.parser')

    # 查找包含安居房、人才房、公租房等关键词的链接
    keywords = ['安居房', '人才房', '公租房', '保障房', '配售', '配租', '住房']

    # 尝试不同的链接选择器
    link_selectors = [
        'a[href*="/xxgk/tzgg/"]',
        'a[href*="content/post"]',
        '.notice-list a',
        '.article-list a',
        'ul li a'
    ]

    for selector in link_selectors:
        links = soup.select(selector)
        if links:
            break
    else:
        # 如果没有找到特定的列表，获取所有链接
        links = soup.find_all('a', href=True)

    for link in links:
        try:
            title = link.get_text(strip=True)
            href = link.get('href', '')

            # 过滤相关公告
            if any(keyword in title for keyword in keywords):
                # 构建完整URL
                if href.startswith('/'):
                    full_url = f"https://zjj.sz.gov.cn{href}"
                elif not href.startswith('http'):
                    full_url = f"https://zjj.sz.gov.cn/xxgk/tzgg/{href}"
                else:
                    full_url = href

                # 尝试提取日期
                date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', title)
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d')

                notices.append({
                    "title": title,
                    "url": full_url,
                    "date": date_str,
                    "source": source_name
                })
        except Exception as e:
            continue

    return notices

def get_recent_notices(days=30):
    """获取最近N天的公告"""
    print(f"\n正在搜索最近 {days} 天的保障房公告...\n")
    all_notices = []
    cutoff_date = datetime.now() - timedelta(days=days)

    for source in official_sources:
        print(f"搜索 {source['name']}...")

        # 获取公告列表页
        html = fetch_page(source['notice_page'])
        if html:
            notices = parse_housing_notices(html, source['name'])
            all_notices.extend(notices)
            print(f"  找到 {len(notices)} 条相关公告")

    # 按日期排序并过滤
    valid_notices = []
    for notice in all_notices:
        try:
            notice_date = datetime.strptime(notice['date'], '%Y-%m-%d')
            if notice_date >= cutoff_date:
                valid_notices.append(notice)
        except:
            # 如果日期解析失败，保留这条记录
            valid_notices.append(notice)

    valid_notices.sort(key=lambda x: x['date'], reverse=True)
    return valid_notices

def display_notices(notices, limit=10):
    """显示公告列表"""
    if not notices:
        print("\n未找到符合条件的公告")
        return

    print(f"\n找到 {len(notices)} 条公告（显示最近 {min(limit, len(notices))} 条）：\n")
    print("=" * 80)

    for i, notice in enumerate(notices[:limit], 1):
        print(f"\n{i}. {notice['title']}")
        print(f"   发布日期: {notice['date']}")
        print(f"   来源: {notice['source']}")
        print(f"   链接: {notice['url']}")

    print("\n" + "=" * 80)

def main():
    """主函数"""
    print("=" * 80)
    print("深圳市保障房公告查询系统")
    print("=" * 80)

    # 获取最近30天的公告
    notices = get_recent_notices(days=30)

    # 显示结果
    display_notices(notices, limit=15)

    print("\n💡 提示：")
    print("1. 以上信息来自官方网站，请以官方公告为准")
    print("2. 点击链接查看完整的申请条件和流程")
    print("3. 注意申请截止时间，及时提交材料")

if __name__ == "__main__":
    main()
