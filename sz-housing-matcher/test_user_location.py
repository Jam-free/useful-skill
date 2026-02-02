#!/usr/bin/env python3
"""
测试用户公司地址到主要交通枢纽的距离和时间
"""

import requests
import json

def calculate_route(api_key, origin, destination, name):
    """计算两点间的距离和时间"""

    # 地理编码
    geocode_url = "https://restapi.amap.com/v3/geocode/geo"

    # 获取起点坐标
    origin_resp = requests.get(geocode_url, params={
        "key": api_key,
        "address": origin
    })
    origin_coord = json.loads(origin_resp.text)

    # 获取终点坐标
    dest_resp = requests.get(geocode_url, params={
        "key": api_key,
        "address": destination
    })
    dest_coord = json.loads(dest_resp.text)

    if not origin_coord.get('geocodes') or not dest_coord.get('geocodes'):
        print(f"  ✗ {name} - 无法解析地址")
        return

    origin_location = origin_coord['geocodes'][0]['location']
    dest_location = dest_coord['geocodes'][0]['location']

    # 路径规划
    driving_url = "https://restapi.amap.com/v3/direction/driving"
    route_resp = requests.get(driving_url, params={
        "key": api_key,
        "origin": origin_location,
        "destination": dest_location,
        "extensions": "base"
    })

    route_data = json.loads(route_resp.text)

    if route_data.get('status') == '1' and route_data.get('route'):
        route = route_data['route']['paths'][0]
        distance_km = round(int(route['distance']) / 1000, 1)
        duration_min = round(int(route['duration']) / 60)

        # 评分
        if duration_min <= 20:
            score = "优秀 ✓✓"
        elif duration_min <= 40:
            score = "良好 ✓"
        elif duration_min <= 60:
            score = "一般"
        else:
            score = "较远"

        print(f"\n┌─────────────────────────────────────┐")
        print(f"│  {name}")
        print(f"│  • 距离：{distance_km} 公里")
        print(f"│  • 驾车：约 {duration_min} 分钟")
        print(f"│  • 评分：{score}")
        print(f"└─────────────────────────────────────┘")
    else:
        print(f"  ✗ {name} - 无法计算路线")


def main():
    api_key = "a3cf5941231bd1bc0f214109db4f7dad"
    company = "深圳市龙岗区坂田街道天安云谷"

    print("=" * 50)
    print("从坂田天安云谷到主要交通枢纽的距离和时间")
    print("=" * 50)

    # 到深圳北站
    calculate_route(api_key, company, "深圳北站", "🚄 深圳北站")

    # 到宝安机场
    calculate_route(api_key, company, "深圳宝安国际机场", "✈️  宝安机场")

    # 到福田站
    calculate_route(api_key, company, "福田站", "🚄 福田站")

    # 到光明区（现在住的地方）
    calculate_route(api_key, company, "光明区政府", "🏠 光明区政府")

    # 到福田区
    calculate_route(api_key, company, "福田区政府", "🏢 福田区政府")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
