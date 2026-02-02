#!/usr/bin/env python3
"""
测试高德地图 API 连接
"""

import sys
import os
import json
import requests

def test_amap_api(api_key: str):
    """测试高德地图 API 是否可用"""

    print("=== 高德地图 API 测试 ===\n")

    # 测试 1：地理编码
    print("测试 1：地理编码（地址 -> 坐标）")
    geocode_url = "https://restapi.amap.com/v3/geocode/geo"

    test_addresses = [
        "深圳市南山区科技园",
        "深圳北站",
        "深圳宝安国际机场"
    ]

    for address in test_addresses:
        try:
            response = requests.get(geocode_url, params={
                "key": api_key,
                "address": address
            })

            data = response.json()

            if data.get('status') == '1' and data.get('geocodes'):
                location = data['geocodes'][0]['location']
                print(f"  ✓ {address} -> {location}")
            else:
                print(f"  ✗ {address} -> 失败：{data.get('info', '未知错误')}")

        except Exception as e:
            print(f"  ✗ {address} -> 错误：{e}")

    # 测试 2：路径规划
    print("\n测试 2：路径规划（距离和时间）")

    origin = "113.946,22.539"  # 深圳科技园附近
    destination = "114.0325,22.6107"  # 深圳北站

    driving_url = "https://restapi.amap.com/v3/direction/driving"

    try:
        response = requests.get(driving_url, params={
            "key": api_key,
            "origin": origin,
            "destination": destination,
            "extensions": "base"
        })

        data = response.json()

        if data.get('status') == '1' and data.get('route'):
            route = data['route']['paths'][0]
            distance = int(route['distance']) / 1000  # 转换为公里
            duration = int(route['duration']) / 60  # 转换为分钟
            print(f"  ✓ 路径规划成功")
            print(f"    距离：{distance:.1f} 公里")
            print(f"    时间：{duration:.0f} 分钟")
        else:
            print(f"  ✗ 路径规划失败：{data.get('info', '未知错误')}")

    except Exception as e:
        print(f"  ✗ 路径规划错误：{e}")

    # 测试 3：周边搜索
    print("\n测试 3：周边搜索（查找附近地铁站）")

    around_url = "https://restapi.amap.com/v3/place/around"

    try:
        response = requests.get(around_url, params={
            "key": api_key,
            "location": "113.946,22.539",
            "keywords": "地铁站",
            "radius": "1000"
        })

        data = response.json()

        if data.get('status') == '1' and data.get('pois'):
            print(f"  ✓ 找到 {len(data['pois'])} 个地铁站")
            for poi in data['pois'][:3]:  # 只显示前 3 个
                print(f"    - {poi['name']} ({poi.get('address', 'N/A')})")
        else:
            print(f"  ✗ 周边搜索失败：{data.get('info', '未知错误')}")

    except Exception as e:
        print(f"  ✗ 周边搜索错误：{e}")

    print("\n=== 测试完成 ===")


def main():
    """主函数"""

    # 从配置文件读取 API Key
    config_file = os.path.expanduser("~/.sz-housing/config.json")

    if not os.path.exists(config_file):
        print("错误：配置文件不存在")
        print("请先运行：python sz_housing_matcher.py setup")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    api_key = config.get('api_keys', {}).get('amap')

    if not api_key or api_key == "YOUR_AMAP_API_KEY_HERE":
        print("错误：未配置高德地图 API Key")
        print("\n请按以下步骤获取 API Key：")
        print("1. 访问 https://lbs.amap.com/")
        print("2. 注册并创建应用")
        print("3. 获取 Web服务 API Key")
        print("4. 在配置文件中更新 API Key")
        print(f"\n配置文件位置：{config_file}")
        sys.exit(1)

    # 运行测试
    test_amap_api(api_key)


if __name__ == "__main__":
    main()
