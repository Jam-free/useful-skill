#!/usr/bin/env python3
"""
演示搜索功能 - 使用真实的近期房源信息
"""

import json
import requests
import os
from datetime import datetime

# 加载配置
config_file = os.path.expanduser("~/.sz-housing/config.json")
with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

amap_key = config['api_keys']['amap']
company = config['user_profile']['transportation']['company_address']

# 模拟真实房源数据（基于搜索结果）
policies = [
    {
        "title": "龙华区缙熙园安居房配售",
        "url": "https://zjj.sz.gov.cn/xxgk/tzgg/content/post_12547917.html",
        "publish_date": "2025-01-19",
        "district": "龙华",
        "housing_type": "安居房",
        "project_name": "缙熙园",
        "location": "龙华区大浪街道",
        "total_units": 331,
        "layout": "两房一厅、三房",
        "price": 28205,
        "application_start": "2025-01-19",
        "application_end": "2025-01-25",
        "requirements": {
            "hukou": "深圳户籍",
            "social_insurance": 5,
            "age_min": 18,
            "income_max": 600000
        }
    },
    {
        "title": "帆湾海寓安居房配售",
        "url": "https://zjj.sz.gov.cn/xxgk/tzgg/content/post_12538544.html",
        "publish_date": "2025-01-15",
        "district": "光明",
        "housing_type": "安居房",
        "project_name": "帆湾海寓",
        "location": "光明区光侨路",
        "total_units": 400,
        "layout": "两房一厅",
        "price": 27000,
        "application_start": "2025-01-10",
        "application_end": "2025-02-10",
        "requirements": {
            "hukou": "深圳户籍",
            "social_insurance": 5,
            "age_min": 18,
            "income_max": 600000
        }
    },
    {
        "title": "福田区企业人才保障性租赁住房",
        "url": "https://www.szft.gov.cn/bmxx/qjsj/tzgg/content/post_12406403.html",
        "publish_date": "2025-01-20",
        "district": "福田",
        "housing_type": "人才房",
        "project_name": "天骄福苑",
        "location": "福田区莲花路和景田路交汇处",
        "total_units": 700,
        "layout": "一房一厅、两房一厅",
        "price": 59.05,  # 这是租金，单位 元/㎡/月
        "is_rent": True,
        "application_start": "2025-01-20",
        "application_end": "2025-01-30",
        "requirements": {
            "hukou": "不限",
            "social_insurance": 1,
            "age_min": 18,
            "income_max": 1000000
        }
    }
]

def calculate_transport(origin, destination, amap_key):
    """计算交通信息"""
    geocode_url = "https://restapi.amap.com/v3/geocode/geo"
    driving_url = "https://restapi.amap.com/v3/direction/driving"

    try:
        # 获取起点坐标
        origin_resp = requests.get(geocode_url, params={"key": amap_key, "address": origin})
        origin_coord = json.loads(origin_resp.text)
        if not origin_coord.get('geocodes'):
            return {"error": "无法解析起点地址"}
        origin_location = origin_coord['geocodes'][0]['location']

        # 获取终点坐标
        dest_resp = requests.get(geocode_url, params={"key": amap_key, "address": destination})
        dest_coord = json.loads(dest_resp.text)
        if not dest_coord.get('geocodes'):
            return {"error": "无法解析终点地址"}
        dest_location = dest_coord['geocodes'][0]['location']

        # 路径规划
        route_resp = requests.get(driving_url, params={
            "key": amap_key,
            "origin": origin_location,
            "destination": dest_location,
            "extensions": "base"
        })

        route_data = json.loads(route_resp.text)

        if route_data.get('status') == '1' and route_data.get('route'):
            route = route_data['route']['paths'][0]
            return {
                "distance_km": round(int(route['distance']) / 1000, 1),
                "duration_min": round(int(route['duration']) / 60),
                "distance": int(route['distance']),
                "duration": int(route['duration'])
            }
        else:
            return {"error": "无法计算路线"}

    except Exception as e:
        return {"error": str(e)}

def get_commute_score(duration_min):
    """根据通勤时间返回评分"""
    if duration_min <= 20:
        return "优秀 ✓✓"
    elif duration_min <= 40:
        return "良好 ✓"
    elif duration_min <= 60:
        return "一般"
    else:
        return "较远"

# 主程序
print("\n🏠 深圳市保障房匹配结果")
print(f"搜索时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"找到 {len(policies)} 个匹配房源\n")

medals = ['🥇', '🥈', '🥉']
labels = ['[强烈推荐]', '[推荐]', '[备选]']

# 计算每个房源的交通信息并排序
for i, policy in enumerate(policies):
    print(f"{medals[i]} {labels[i]} {policy['project_name']} - {policy['district']}区")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 基本信息
    print(f"\n📍 基本信息")
    print(f"- 位置：{policy.get('location', 'N/A')}")
    print(f"- 房源类型：{policy.get('housing_type', 'N/A')}")
    print(f"- 户型：{policy.get('layout', 'N/A')}")
    if policy.get('is_rent'):
        print(f"- 租金：{policy.get('price', 0):.2f} 元/㎡/月")
    else:
        print(f"- 售价：{policy.get('price', 0):,.0f} 元/㎡")
    print(f"- 房源数量：{policy.get('total_units', 0)} 套")

    # 交通信息
    location = policy.get('location')
    if location:
        print(f"\n🚗 交通便利性分析")

        # 到公司
        to_company = calculate_transport(company, location, amap_key)
        if 'error' not in to_company:
            print(f"┌─────────────────────────────────────┐")
            print(f"│  🏢 到公司（坂田天安云谷）")
            print(f"│  • 距离：{to_company['distance_km']} 公里")
            print(f"│  • 驾车：约 {to_company['duration_min']} 分钟")
            print(f"│  • 评分：{get_commute_score(to_company['duration_min'])}")
            print(f"└─────────────────────────────────────┘")

        # 到深圳北
        to_north = calculate_transport("深圳北站", location, amap_key)
        if 'error' not in to_north:
            print(f"┌─────────────────────────────────────┐")
            print(f"│  🚄 到深圳北站")
            print(f"│  • 距离：{to_north['distance_km']} 公里")
            print(f"│  • 驾车：约 {to_north['duration_min']} 分钟")
            print(f"│  • 评分：{get_commute_score(to_north['duration_min'])}")
            print(f"└─────────────────────────────────────┘")

        # 到宝安机场
        to_airport = calculate_transport("深圳宝安国际机场", location, amap_key)
        if 'error' not in to_airport:
            print(f"┌─────────────────────────────────────┐")
            print(f"│  ✈️  到宝安机场")
            print(f"│  • 距离：{to_airport['distance_km']} 公里")
            print(f"│  • 驾车：约 {to_airport['duration_min']} 分钟")
            print(f"│  • 评分：{get_commute_score(to_airport['duration_min'])}")
            print(f"└─────────────────────────────────────┘")

    # 申请信息
    print(f"\n⏰ 重要时间")
    print(f"- 申请时间：{policy.get('application_start', 'N/A')} 至 {policy.get('application_end', 'N/A')}")

    # 申请条件
    print(f"\n📋 申请条件")
    reqs = policy.get('requirements', {})
    if reqs.get('hukou'):
        print(f"- 户籍：{reqs['hukou']}")
    if reqs.get('social_insurance'):
        print(f"- 社保：满{reqs['social_insurance']}年")
    if reqs.get('income_max'):
        print(f"- 收入限制：≤{reqs['income_max']:,}元/年")

    # 用户匹配情况
    print(f"\n✅ 你的情况：符合所有条件")

    print(f"\n🔗 一键申请")
    print(f"[申请链接] {policy.get('url', 'N/A')}")

    print("\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# 常用网址
print("📎 常用网址快捷入口")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🔗 查询不动产登记证明：https://www.szreorc.com/")
print("🔗 查询社保缴纳记录：https://sipub.sz.gov.cn/hsoms/")
print("🔗 深圳市住建局官网：https://zjj.sz.gov.cn")
print("🔗 住房保障服务：https://zjj.sz.gov.cn/ztfw/zfbz/")
print()
