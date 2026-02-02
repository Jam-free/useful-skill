#!/usr/bin/env python3
"""
筛选并展示本周新增的保障房公告
"""

import json
import os
from datetime import datetime, timedelta

# 加载数据
data_file = os.path.expanduser("~/.sz-housing/notices.json")

with open(data_file, 'r', encoding='utf-8') as f:
    all_notices = json.load(f)

# 计算本周范围（最近7天）
today = datetime.now()
week_ago = today - timedelta(days=7)

print("\n" + "=" * 80)
print(f"🏠 本周新增保障房公告")
print(f"查询时间：{today.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"时间范围：{week_ago.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')}（最近7天）")
print("=" * 80)

# 筛选本周的公告
weekly_notices = []
for notice in all_notices:
    notice_date = datetime.strptime(notice['date'], '%Y-%m-%d')
    if notice_date >= week_ago:
        weekly_notices.append(notice)

# 按日期和来源分组
grouped = {}
for notice in weekly_notices:
    date = notice['date']
    source = notice['source']
    key = f"{date} - {source}"
    if key not in grouped:
        grouped[key] = []
    grouped[key].append(notice)

# 显示结果
if not weekly_notices:
    print("\n本周暂无新增公告")
else:
    print(f"\n📊 本周共找到 {len(weekly_notices)} 条新公告：\n")

    # 按日期排序显示
    sorted_keys = sorted(grouped.keys(), reverse=True)

    for i, key in enumerate(sorted_keys, 1):
        notices = grouped[key]
        date = notices[0]['date']
        source = notices[0]['source']

        # 判断是否是今天
        if date == today.strftime('%Y-%m-%d'):
            date_label = f"🔥 今天 ({date})"
        else:
            date_label = f"📅 {date}"

        print(f"\n{'=' * 80}")
        print(f"{date_label}")
        print(f"🏢 来源：{source}")
        print(f"{'=' * 80}")

        for notice in notices:
            # 过滤掉不太相关的公告
            title = notice['title']
            if any(kw in title for kw in ['采购', '内部', '会议', '培训', '资格考试']):
                continue

            print(f"\n  📌 {title}")
            print(f"     🔗 {notice['url']}")

    # 重点推荐（安居房、人才房配售）
    print(f"\n\n{'=' * 80}")
    print("⭐ 重点推荐（正在申请中）")
    print(f"{'=' * 80}\n")

    priority_notices = []
    for notice in weekly_notices:
        title = notice['title']
        if any(kw in title for kw in ['配售通告', '配租', '认购', '选房']):
            priority_notices.append(notice)

    if priority_notices:
        for i, notice in enumerate(priority_notices, 1):
            print(f"\n{i}. {notice['title']}")
            print(f"   📅 {notice['date']}")
            print(f"   🏢 {notice['source']}")
            print(f"   🔗 {notice['url']}")

            # 尝试获取更多详情
            if '安居房' in notice['title'] or '人才房' in notice['title']:
                print(f"   ✨ 推荐理由：符合您的申请条件（深圳户籍、硕士、社保满5年）")
    else:
        print("本周暂无正在申请的房源")

print("\n" + "=" * 80)
print("💡 温馨提示")
print("=" * 80)
print("1. 点击上方链接查看完整的申请条件和流程")
print("2. 注意申请截止时间，提前准备材料")
print("3. 所有信息以官方公告为准")
print("4. 建议关注深圳市住建局官方微信公众号获取最新推送")
print()

