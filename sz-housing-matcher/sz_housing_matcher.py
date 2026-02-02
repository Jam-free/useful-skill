#!/usr/bin/env python3
"""
深圳市保障房政策追踪与匹配助手
自动搜索最新政策并按个人情况排序，包含交通便利性分析
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

class HousingMatcher:
    """保障房匹配器主类"""

    def __init__(self):
        self.home_dir = os.path.expanduser("~/.sz-housing")
        self.config_file = os.path.join(self.home_dir, "config.json")
        self.config_template = os.path.join(os.path.dirname(__file__), "config.template.json")
        self.urls_file = os.path.join(os.path.dirname(__file__), "urls.json")
        self.config = None
        self.urls = None

        # 确保配置目录存在
        os.makedirs(self.home_dir, exist_ok=True)

        # 加载配置和数据
        self._load_urls()
        self._load_config()

    def _load_urls(self):
        """加载网址列表"""
        try:
            with open(self.urls_file, 'r', encoding='utf-8') as f:
                self.urls = json.load(f)
        except FileNotFoundError:
            print(f"错误：找不到网址列表文件 {self.urls_file}")
            sys.exit(1)

    def _load_config(self):
        """加载用户配置"""
        if not os.path.exists(self.config_file):
            print("未找到配置文件，正在初始化...")
            self.setup_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败：{e}")
            sys.exit(1)

    def setup_config(self):
        """初始化用户配置"""
        print("\n=== 深圳市保障房匹配助手 - 首次配置 ===\n")

        config = {}
        with open(self.config_template, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 收集用户基本信息
        print("【基本信息】")
        config['user_profile']['basic_info']['hukou'] = input("户籍情况（深圳户籍/非深户）：")
        config['user_profile']['basic_info']['age'] = int(input("年龄："))
        config['user_profile']['basic_info']['social_insurance_years'] = int(input("社保缴纳年限（年）："))
        config['user_profile']['basic_info']['education'] = input("学历：")
        config['user_profile']['basic_info']['family_type'] = input("家庭结构（单身/已婚/已婚有子女等）：")
        config['user_profile']['basic_info']['phone'] = input("手机号：")

        # 收集资产信息
        print("\n【资产信息】")
        config['user_profile']['assets']['annual_income'] = float(input("家庭年收入（元）："))
        config['user_profile']['assets']['has_shenzhen_property'] = input("是否拥有深圳房产（y/n）：").lower() == 'y'
        config['user_profile']['assets']['has_car'] = input("是否拥有车辆（y/n）：").lower() == 'y'
        config['user_profile']['assets']['total_assets'] = float(input("家庭资产总额（元）："))

        # 收集偏好设置
        print("\n【偏好设置】")
        districts = input("期望区域（多个区域用逗号分隔，如：福田,南山,宝安）：")
        config['user_profile']['preferences']['preferred_districts'] = [d.strip() for d in districts.split(',')]

        housing_types = input("住房类型偏好（多个类型用逗号分隔，如：安居房,人才房）：")
        config['user_profile']['preferences']['housing_types'] = [t.strip() for t in housing_types.split(',')]

        config['user_profile']['preferences']['preferred_layout'] = input("户型偏好（如：两房一厅）：")

        budget = input("预算范围（如：200-400万，单位：万）：")
        if '-' in budget:
            min_b, max_b = budget.split('-')
            config['user_profile']['preferences']['budget_min'] = float(min_b) * 10000
            config['user_profile']['preferences']['budget_max'] = float(max_b.replace('万', '')) * 10000

        # 收集交通信息
        print("\n【交通信息】")
        config['user_profile']['transportation']['company_address'] = input("公司地址（或主要工作地点）：")
        config['user_profile']['transportation']['company_name'] = input("公司名称（可选）：")
        config['user_profile']['transportation']['commute_method'] = input("通勤方式（开车/地铁/公交）：")

        # 收集 API 密钥
        print("\n【API 配置】")
        print("高德地图 API Key 获取方法：")
        print("1. 访问 https://lbs.amap.com/")
        print("2. 注册并创建应用")
        print("3. 获取 Web服务 API Key\n")

        use_amap = input("是否现在配置高德地图 API？（y/n，跳过可稍后配置）：").lower() == 'y'
        if use_amap:
            config['api_keys']['amap'] = input("请输入高德地图 API Key：")

        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print("\n✅ 配置已保存！")
        self.config = config

    def search_policies(self) -> List[Dict]:
        """搜索最新的保障房政策"""
        print("\n正在搜索最新政策...")

        policies = []

        # 生成搜索关键词
        keywords = self._generate_keywords()

        # 搜索深圳市住建局
        print(f"搜索 {self.urls['shenzhen']['name']}...")
        policies.extend(self._search_shenzhen_gov(keywords))

        # 搜索各区住建局
        for district in self.urls['districts']:
            if district['name'] in self.config['user_profile']['preferences']['preferred_districts']:
                print(f"搜索 {district['name']}住建局...")
                policies.extend(self._search_district_gov(district, keywords))

        print(f"共找到 {len(policies)} 条相关政策")
        return policies

    def _generate_keywords(self) -> List[str]:
        """根据用户偏好生成搜索关键词"""
        keywords = []
        current_year = datetime.now().year

        for housing_type in self.config['user_profile']['preferences']['housing_types']:
            for district in self.config['user_profile']['preferences']['preferred_districts']:
                keywords.append(f"{housing_type} {district} {current_year}")
                keywords.append(f"{housing_type} {district} 申请")

        return keywords

    def _search_shenzhen_gov(self, keywords: List[str]) -> List[Dict]:
        """搜索深圳市住建局官网"""
        # 这里是示例实现，实际需要根据网站结构进行调整
        policies = []

        # TODO: 实现实际的网页抓取逻辑
        # 可以使用 requests + BeautifulSoup 或者 selenium

        # 示例数据
        sample_policy = {
            "title": "深圳市2025年安居房配售公告",
            "url": "http://zjj.sz.gov.cn/xxx/xxx",
            "publish_date": "2025-01-15",
            "district": "全市",
            "housing_type": "安居房",
            "project_name": "XX项目",
            "location": "南山区科技园",
            "total_units": 200,
            "layout": "两房一厅",
            "price": 28000,
            "application_start": "2025-01-15",
            "application_end": "2025-02-15",
            "requirements": {
                "hukou": "深圳户籍",
                "social_insurance": 5,
                "age_min": 18,
                "income_max": 400000
            }
        }
        policies.append(sample_policy)

        return policies

    def _search_district_gov(self, district: Dict, keywords: List[str]) -> List[Dict]:
        """搜索各区住建局官网"""
        policies = []

        # TODO: 实现实际的网页抓取逻辑

        return policies

    def geocode(self, address: str) -> Optional[str]:
        """地理编码：将地址转换为经纬度坐标"""
        amap_key = self.config['api_keys'].get('amap')
        if not amap_key or amap_key == "YOUR_AMAP_API_KEY_HERE":
            return None

        # 优化：对于已知地址使用预设坐标，避免地理编码错误
        known_locations = {
            "龙华区大浪街道": "114.0366,22.6546",
            "龙华大浪": "114.0366,22.6546",
        }

        for key, coord in known_locations.items():
            if key in address:
                return coord

        url = "https://restapi.amap.com/v3/geocode/geo"
        try:
            response = requests.get(url, params={
                "key": amap_key,
                "address": address
            }, timeout=10)
            data = response.json()
            if data['status'] == '1' and data['geocodes']:
                return data['geocodes'][0]['location']
        except Exception as e:
            pass
        return None

    def calculate_route(self, origin: str, destination: str) -> tuple:
        """路径规划：计算距离和时间"""
        amap_key = self.config['api_keys'].get('amap')
        if not amap_key or amap_key == "YOUR_AMAP_API_KEY_HERE":
            return None, None

        url = "https://restapi.amap.com/v3/direction/driving"
        try:
            response = requests.get(url, params={
                "key": amap_key,
                "origin": origin,
                "destination": destination,
                "extensions": "base"
            }, timeout=10)
            data = response.json()
            # 优化：修复数据类型问题，API返回的是字符串需要转换为float
            if data['status'] == '1' and data['route']['paths']:
                path = data['route']['paths'][0]
                distance = float(path['distance']) / 1000  # 转换为公里
                duration = float(path['duration']) / 60  # 转换为分钟
                return distance, duration
        except Exception as e:
            pass
        return None, None

    def get_commute_score(self, duration: float) -> tuple:
        """根据通勤时间给出评分"""
        if duration <= 20:
            return "优秀", "✓✓"
        elif duration <= 40:
            return "良好", "✓"
        elif duration <= 60:
            return "一般", "○"
        else:
            return "较远", "✗"

    def search_nearby(self, location: str, keywords: str = "地铁站", radius: int = 1000) -> List[Dict]:
        """搜索附近设施"""
        amap_key = self.config['api_keys'].get('amap')
        if not amap_key or amap_key == "YOUR_AMAP_API_KEY_HERE":
            return []

        url = "https://restapi.amap.com/v3/place/around"
        try:
            response = requests.get(url, params={
                "key": amap_key,
                "location": location,
                "keywords": keywords,
                "radius": radius
            }, timeout=10)
            data = response.json()
            if data['status'] == '1' and data['pois']:
                return data['pois'][:3]
        except Exception as e:
            pass
        return []

    def calculate_transport(self, origin: str, destination: str) -> Dict:
        """使用高德地图 API 计算距离和时间（兼容旧接口）"""
        origin_coord = self.geocode(origin)
        dest_coord = self.geocode(destination)

        if not origin_coord or not dest_coord:
            return {"error": "无法解析地址"}

        distance, duration = self.calculate_route(origin_coord, dest_coord)
        if distance and duration:
            return {
                "distance_km": round(distance, 1),
                "duration_min": round(duration),
                "origin_location": origin_coord,
                "dest_location": dest_coord
            }
        else:
            return {"error": "无法计算路线"}

    def match_policies(self, policies: List[Dict]) -> List[Dict]:
        """匹配用户条件并排序"""
        matched_policies = []

        for policy in policies:
            if self._check_requirements(policy):
                # 计算匹配分数
                score = self._calculate_score(policy)
                policy['match_score'] = score
                matched_policies.append(policy)

        # 按匹配分数排序
        matched_policies.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_policies

    def _check_requirements(self, policy: Dict) -> bool:
        """检查用户是否符合申请条件"""
        reqs = policy.get('requirements', {})
        user = self.config['user_profile']

        # 检查户籍
        if reqs.get('hukou'):
            if '深圳' in reqs['hukou'] and user['basic_info']['hukou'] != '深圳户籍':
                return False

        # 检查社保年限
        if reqs.get('social_insurance'):
            if user['basic_info']['social_insurance_years'] < reqs['social_insurance']:
                return False

        # 检查年龄
        if reqs.get('age_min'):
            if user['basic_info']['age'] < reqs['age_min']:
                return False

        # 检查收入
        if reqs.get('income_max'):
            if user['assets']['annual_income'] > reqs['income_max']:
                return False

        return True

    def _calculate_score(self, policy: Dict) -> float:
        """计算匹配分数"""
        score = 0.0
        user = self.config['user_profile']

        # 区域匹配（40分）
        if policy['district'] in user['preferences']['preferred_districts']:
            preferred_index = user['preferences']['preferred_districts'].index(policy['district'])
            score += 40 - preferred_index * 5

        # 通勤便利性（25分）
        if 'transport_info' in policy:
            commute_time = policy['transport_info'].get('to_company', {}).get('duration_min', 999)
            if commute_time <= 20:
                score += 25
            elif commute_time <= 40:
                score += 20
            elif commute_time <= 60:
                score += 15
            else:
                score += 10

        # 发布时间（20分）
        publish_date = datetime.strptime(policy['publish_date'], '%Y-%m-%d')
        days_ago = (datetime.now() - publish_date).days
        if days_ago <= 7:
            score += 20
        elif days_ago <= 30:
            score += 15
        elif days_ago <= 90:
            score += 10
        else:
            score += 5

        # 房源数量（15分）
        units = policy.get('total_units', 0)
        if units >= 500:
            score += 15
        elif units >= 200:
            score += 12
        elif units >= 100:
            score += 10
        else:
            score += 8

        return score

    def display_results(self, policies: List[Dict]):
        """展示匹配结果"""
        if not policies:
            print("\n未找到匹配的房源，请尝试放宽条件")
            return

        print(f"\n🏠 深圳市保障房匹配结果")
        print(f"搜索时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"找到 {len(policies)} 个匹配房源\n")

        medals = ['🥇', '🥈', '🥉']
        labels = ['[强烈推荐]', '[推荐]', '[备选]']

        for i, policy in enumerate(policies[:3]):
            medal = medals[i] if i < 3 else f"{i+1}."
            label = labels[i] if i < 3 else ''

            print(f"{medal} {label} {policy.get('project_name', policy['title'])}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # 基本信息
            print(f"\n📍 基本信息")
            print(f"- 位置：{policy.get('location', 'N/A')}")
            print(f"- 房源类型：{policy.get('housing_type', 'N/A')}")
            print(f"- 户型：{policy.get('layout', 'N/A')}")
            print(f"- 售价：{policy.get('price', 0):,.0f} 元/㎡")
            print(f"- 房源数量：{policy.get('total_units', 0)} 套")

            # 交通信息（如果有）
            if 'transport_info' in policy:
                print(f"\n🚗 交通便利性分析")

                # 到公司
                if 'to_company' in policy['transport_info']:
                    info = policy['transport_info']['to_company']
                    if 'error' not in info:
                        company_name = self.config['user_profile']['transportation']['company_name'] or '公司'
                        print(f"┌─────────────────────────────────────┐")
                        print(f"│  🏢 到{company_name}                  │")
                        print(f"│  • 距离：{info['distance_km']} 公里")
                        print(f"│  • 驾车：约 {info['duration_min']} 分钟")
                        print(f"│  • 评分：{self._get_commute_score(info['duration_min'])}")
                        print(f"└─────────────────────────────────────┘")

                # 到深圳北
                if 'to_shenzhen_north' in policy['transport_info']:
                    info = policy['transport_info']['to_shenzhen_north']
                    if 'error' not in info:
                        print(f"┌─────────────────────────────────────┐")
                        print(f"│  🚄 到深圳北站")
                        print(f"│  • 距离：{info['distance_km']} 公里")
                        print(f"│  • 驾车：约 {info['duration_min']} 分钟")
                        print(f"│  • 评分：{self._get_commute_score(info['duration_min'])}")
                        print(f"└─────────────────────────────────────┘")

                # 到宝安机场
                if 'to_baoan_airport' in policy['transport_info']:
                    info = policy['transport_info']['to_baoan_airport']
                    if 'error' not in info:
                        print(f"┌─────────────────────────────────────┐")
                        print(f"│  ✈️  到宝安机场")
                        print(f"│  • 距离：{info['distance_km']} 公里")
                        print(f"│  • 驾车：约 {info['duration_min']} 分钟")
                        print(f"│  • 评分：{self._get_commute_score(info['duration_min'])}")
                        print(f"└─────────────────────────────────────┘")

            # 申请信息
            print(f"\n⏰ 重要时间")
            print(f"- 申请时间：{policy.get('application_start', 'N/A')} 至 {policy.get('application_end', 'N/A')}")

            print(f"\n📊 匹配度评分：{policy['match_score']:.0f}/100")

            print(f"\n🔗 一键申请")
            print(f"[申请链接] {policy.get('url', 'N/A')}")

            print("\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # 显示常用网址
        self._display_useful_links()

    def _get_commute_score(self, duration_min: int) -> str:
        """根据通勤时间返回评分"""
        if duration_min <= 20:
            return "优秀 ✓✓"
        elif duration_min <= 40:
            return "良好 ✓"
        elif duration_min <= 60:
            return "一般"
        else:
            return "较远"

    def _display_useful_links(self):
        """显示常用网址"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📎 常用网址快捷入口")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for key, link in self.urls['useful_links'].items():
            print(f"🔗 {link['name']}：{link['url']}")

        print()

    def run(self):
        """运行主程序"""
        print("\n=== 深圳市保障房匹配助手 ===\n")

        # 搜索政策
        policies = self.search_policies()

        # 匹配用户条件
        matched = self.match_policies(policies)

        # 显示结果
        self.display_results(matched)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        matcher = HousingMatcher()

        if command == "setup":
            matcher.setup_config()
        elif command == "search":
            matcher.run()
        elif command == "config":
            print("配置功能开发中...")
        elif command == "history":
            print("历史记录功能开发中...")
        else:
            print(f"未知命令：{command}")
            print("可用命令：setup, search, config, history")
    else:
        print("深圳市保障房政策追踪与匹配助手")
        print("\n使用方法：")
        print("  python sz_housing_matcher.py setup  - 首次配置")
        print("  python sz_housing_matcher.py search - 搜索政策")
        print("  python sz_housing_matcher.py config - 修改配置")
        print("  python sz_housing_matcher.py history - 查看历史")


if __name__ == "__main__":
    main()
