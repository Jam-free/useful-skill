#!/usr/bin/env python3
"""
深圳保障房数据收集器 - 混合方案实现
结合多种数据源，确保数据准确可靠
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
import os
from urllib.parse import urljoin

class HousingDataFetcher:
    """保障房数据收集器"""

    def __init__(self):
        self.config_dir = os.path.expanduser("~/.sz-housing")
        self.data_file = os.path.join(self.config_dir, "notices.json")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # 官方数据源配置
        self.sources = {
            "sz_zjj": {
                "name": "深圳市住房和建设局",
                "base_url": "https://zjj.sz.gov.cn",
                "notice_url": "https://zjj.sz.gov.cn/xxgk/tzgg/",
                "housing_url": "https://zjj.sz.gov.cn/ztfw/zfbz/"
            },
            "futian": {
                "name": "福田区住建局",
                "base_url": "https://www.szft.gov.cn",
                "notice_url": "https://www.szft.gov.cn/bmxx/qjsj/tzgg/"
            },
            "longhua": {
                "name": "龙华区住建局",
                "base_url": "https://www.szlhq.gov.cn",
                "notice_url": "https://www.szlhq.gov.cn/lhq/zdfwgb/zfztgb/zxgg38/"
            },
            "guangming": {
                "name": "光明区住建局",
                "base_url": "https://www.szgm.gov.cn",
                "notice_url": "https://www.szgm.gov.cn/gmjsj/zcfg/"
            }
        }

    def fetch_page(self, url, max_retries=3):
        """获取网页内容（带重试）"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text
            except Exception as e:
                print(f"  获取 {url} 失败（尝试 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return None

    def parse_notice_list(self, html, base_url):
        """解析公告列表页"""
        notices = []
        soup = BeautifulSoup(html, 'html.parser')

        # 多种选择器模式（适应不同网站结构）
        selectors = [
            'ul li a[href*="content/post"]',  # 深圳市政府通用模式
            'a[href*="/tzgg/content/"]',      # 通知公告链接
            '.notice-list a',                  # 通知列表类
            '.article-list a',                 # 文章列表类
            'ul.list-txt li a',                # 文本列表
            '.txt-list li a'                   # 另一种文本列表
        ]

        for selector in selectors:
            links = soup.select(selector)
            if links:
                print(f"  使用选择器: {selector}, 找到 {len(links)} 个链接")
                break
        else:
            # 如果都没找到，尝试获取所有包含"配售"、"配租"的链接
            print("  使用关键词搜索...")
            all_links = soup.find_all('a', href=True)
            links = [a for a in all_links if any(kw in a.get_text() for kw in ['配售', '配租', '安居房', '人才房', '公租房', '保障房'])]

        # 提取信息
        for link in links[:20]:  # 限制最多获取20条
            try:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤相关公告
                keywords = ['安居房', '人才房', '公租房', '保障房', '配售', '配租', '住房']
                if not any(kw in title for kw in keywords):
                    continue

                # 构建完整URL
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif not href.startswith('http'):
                    full_url = urljoin(base_url, '/' + href)
                else:
                    full_url = href

                # 尝试从标题或周围元素提取日期
                date = self.extract_date(link, title)

                notices.append({
                    "title": title,
                    "url": full_url,
                    "date": date,
                    "source": self.get_source_name(base_url),
                    "fetched_at": datetime.now().isoformat()
                })
            except Exception as e:
                continue

        return notices

    def extract_date(self, link_element, title):
        """提取日期"""
        import re

        # 尝试从标题中提取日期
        date_match = re.search(r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})', title)
        if date_match:
            return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

        # 尝试从周围的span、time等元素获取
        parent = link_element.parent
        if parent:
            date_element = parent.find(['span', 'time', 'div'], class_=re.compile(r'date|time'))
            if date_element:
                date_text = date_element.get_text(strip=True)
                date_match = re.search(r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})', date_text)
                if date_match:
                    return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

        # 默认返回今天
        return datetime.now().strftime('%Y-%m-%d')

    def get_source_name(self, url):
        """根据URL获取来源名称"""
        for key, source in self.sources.items():
            if source['base_url'] in url:
                return source['name']
        return "未知来源"

    def fetch_all_sources(self):
        """从所有数据源获取公告"""
        all_notices = []
        cutoff_date = datetime.now() - timedelta(days=90)  # 最近90天

        print("\n" + "=" * 80)
        print("开始收集保障房公告信息...")
        print("=" * 80)

        for source_key, source_info in self.sources.items():
            print(f"\n【{source_info['name']}】")
            print(f"URL: {source_info['notice_url']}")

            html = self.fetch_page(source_info['notice_url'])
            if html:
                notices = self.parse_notice_list(html, source_info['base_url'])
                print(f"找到 {len(notices)} 条相关公告")
                all_notices.extend(notices)

                # 礼貌性延迟
                time.sleep(2)
            else:
                print(f"获取失败")

        # 去重和过滤
        unique_notices = self.deduplicate_notices(all_notices)
        recent_notices = [n for n in unique_notices
                         if datetime.strptime(n['date'], '%Y-%m-%d') >= cutoff_date]

        print("\n" + "=" * 80)
        print(f"总计找到 {len(unique_notices)} 条唯一公告（最近90天: {len(recent_notices)} 条）")
        print("=" * 80)

        return recent_notices

    def deduplicate_notices(self, notices):
        """去重（基于URL）"""
        seen_urls = set()
        unique = []

        for notice in notices:
            if notice['url'] not in seen_urls:
                seen_urls.add(notice['url'])
                unique.append(notice)

        return unique

    def save_notices(self, notices):
        """保存公告到文件"""
        os.makedirs(self.config_dir, exist_ok=True)

        # 读取已有数据
        existing = []
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)

        # 合并新数据（基于URL去重）
        existing_urls = {n['url'] for n in existing}
        new_count = 0

        for notice in notices:
            if notice['url'] not in existing_urls:
                existing.insert(0, notice)  # 新数据放在前面
                existing_urls.add(notice['url'])
                new_count += 1

        # 保存
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        print(f"\n💾 数据已保存到: {self.data_file}")
        print(f"   新增 {new_count} 条公告，总计 {len(existing)} 条")

    def display_notices(self, notices, limit=15):
        """显示公告列表"""
        if not notices:
            print("\n未找到符合条件的公告")
            return

        print(f"\n📋 最新保障房公告（显示最近 {min(limit, len(notices))} 条）：")
        print("=" * 80)

        for i, notice in enumerate(notices[:limit], 1):
            print(f"\n{i}. {notice['title'][:80]}...")
            print(f"   📅 发布日期: {notice['date']}")
            print(f"   🏢 来源: {notice['source']}")
            print(f"   🔗 链接: {notice['url']}")

        print("\n" + "=" * 80)

    def run(self):
        """运行主程序"""
        print("\n" + "🏠" * 40)
        print("\n深圳市保障房数据收集器")
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 获取数据
        notices = self.fetch_all_sources()

        # 显示结果
        self.display_notices(notices)

        # 保存数据
        self.save_notices(notices)

        print("\n✅ 数据收集完成！")
        print("\n💡 提示：")
        print("1. 以上信息来自官方网站，请以官方公告为准")
        print("2. 点击链接查看完整的申请条件和流程")
        print("3. 注意申请截止时间，及时提交材料")
        print("4. 数据已保存，可随时查看历史记录")

def main():
    """主函数"""
    fetcher = HousingDataFetcher()
    fetcher.run()

if __name__ == "__main__":
    main()
