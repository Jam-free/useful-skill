#!/usr/bin/env python3
"""
本周重点房源详情报告
"""

import json
import os
from datetime import datetime

# 项目详情
key_projects = [
    {
        "name": "缙熙园安居房",
        "batch": "住保售〔2026〕005号",
        "location": "龙华区大浪街道",
        "url": "https://zjj.sz.gov.cn/xxgk/tzgg/content/post_12606797.html",
        "total_units": 331,
        "layouts": [
            {"type": "两房", "area": "68㎡", "count": 267},
            {"type": "三房", "area": "89㎡", "count": 64}
        ],
        "application_period": "2026-01-19 18:00 至 2026-01-25 18:00",
        "application_status": "正在申请中",
        "price": "待定（安居房通常为市场价的60-70%）",
        "queues": {
            "第一队列": "安居房在册轮候家庭或领军人才",
            "第二队列": "非在册轮候申请家庭（新增开放！）"
        },
        "requirements": {
            "户籍": "深圳户籍",
            "社保": "本科及以上学历3年，其他5年",
            "年龄": "单身需年满35周岁",
            "房产": "无房且5年内未转让过住房",
            "政策性住房": "未购买过"
        }
    },
    {
        "name": "市级安居房配售",
        "batch": "住保售〔2026〕004号",
        "url": "https://zjj.sz.gov.cn/xxgk/tzgg/content/post_12606771.html",
        "note": "具体房源信息待官方公布",
        "application_status": "正在申请中"
    },
    {
        "name": "市级人才房配售",
        "batch": "住保售〔2026〕003号",
        "url": "https://zjj.sz.gov.cn/xxgk/tzgg/content/post_12604280.html",
        "note": "面向人才配售，具体房源信息待官方公布",
        "application_status": "正在申请中"
    }
]

# 用户条件
user_conditions = {
    "户籍": "深圳户籍",
    "年龄": "31岁",
    "学历": "硕士",
    "社保": "5年（2019年8月至今）",
    "家庭": "已婚无子女",
    "资产": "年收入60万，有车，无房"
}

def check_eligibility(project, user):
    """检查用户是否符合条件"""
    requirements = project.get("requirements", {})

    # 检查户籍
    if requirements.get("户籍") == "深圳户籍":
        if user["户籍"] != "深圳户籍":
            return False, "户籍不符合"

    # 检查社保
    社保要求 = requirements.get("社保", "")
    if "本科" in 社保要求:
        if user["学历"] in ["本科", "硕士", "博士"] and "5年" in user["社保"]:
            pass  # 符合
        elif user["学历"] in ["本科", "硕士", "博士"] and int(user["社保"].split("年")[0]) >= 3:
            pass  # 符合
        else:
            return False, "社保年限不符合"

    # 检查年龄
    if requirements.get("age"):
        age_min = int(requirements["age"].replace("单身需年满", "").replace("周岁", ""))
        if user["家庭"] == "单身" and user["年龄"] < age_min:
            return False, "年龄不符合（单身需35岁以上）"

    # 检查房产
    if requirements.get("房产") == "无房且5年内未转让过住房":
        if "无房" not in user["资产"]:
            return False, "已有住房"

    return True, "符合条件"

def generate_report():
    """生成详细报告"""

    print("\n" + "=" * 100)
    print("🏠 深圳保障房本周新增房源 - 详细报告")
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    print("\n📋 你的个人条件：")
    print("-" * 100)
    for key, value in user_conditions.items():
        print(f"  • {key}：{value}")

    print("\n\n" + "=" * 100)
    print("⭐ 重点推荐房源详情")
    print("=" * 100)

    for i, project in enumerate(key_projects, 1):
        print(f"\n\n{'🔥' if project['application_status'] == '正在申请中' else '📌'} 推荐 {i}: {project['name']}")
        print("=" * 100)

        # 基本信息
        print(f"\n📍 基本信息")
        print(f"  项目名称：{project['name']}")
        print(f"  批次编号：{project['batch']}")
        if 'location' in project:
            print(f"  项目位置：{project['location']}")
        print(f"  申请状态：{project['application_status']}")

        # 房源信息
        if 'layouts' in project:
            print(f"\n🏠 房源信息")
            print(f"  房源总数：{project['total_units']} 套")
            for layout in project['layouts']:
                print(f"  • {layout['type']}：{layout['area']}，{layout['count']} 套")
            print(f"  参考价格：{project['price']}")

        # 申请时间
        if 'application_period' in project:
            print(f"\n⏰ 申请时间")
            print(f"  申请时间：{project['application_period']}")
            print(f"  ⚠️  注意：截止时间为 {project['application_period'].split(' 至 ')[1]}")

        # 申请队列
        if 'queues' in project:
            print(f"\n👥 申请队列")
            for queue, desc in project['queues'].items():
                print(f"  {queue}：{desc}")

        # 申请条件
        if 'requirements' in project:
            print(f"\n📋 申请条件")
            for req, desc in project['requirements'].items():
                print(f"  • {req}：{desc}")

        # 用户匹配情况
        if 'requirements' in project:
            eligible, reason = check_eligibility(project, user_conditions)
            print(f"\n✅ 你的匹配情况：{reason}")

            if eligible:
                print(f"  💡 建议：{project['name']} 完全符合你的条件，建议立即申请！")
                if '本科' in project['requirements']['社保']:
                    print(f"  🎓 优势：你的硕士学历让社保要求从5年降低到3年")
                if '已婚' in user_conditions['家庭']:
                    print(f"  👨‍👩‍👧 家庭：已婚无子女可以申请两房户型")
            else:
                print(f"  ⚠️  注意：{reason}")

        # 官方链接
        print(f"\n🔗 官方链接")
        print(f"  详细公告：{project['url']}")
        print(f"  申请入口：https://zjj.sz.gov.cn -> 政务服务 -> 住房保障服务 -> 安居型商品房认购申请")

        if 'note' in project:
            print(f"\n📝 备注：{project['note']}")

    print("\n\n" + "=" * 100)
    print("💡 重要提醒")
    print("=" * 100)
    print("""
1. **申请截止时间紧迫**
   - 缙熙园项目：2026年1月25日18:00截止
   - 距离截止仅剩 3 天，请立即准备材料

2. **申请所需材料**
   - 身份证、户口簿
   - 结婚证（已婚）
   - 学历学位证书（硕士）
   - 社保证明
   - 无房证明

3. **申请流程**
   步骤1：登录深圳市住建局官网
   步骤2：进入"住房保障服务"页面
   步骤3：选择"安居型商品房认购申请"
   步骤4：填写信息并上传材料
   步骤5：提交申请并等待审核

4. **注意事项**
   - 所有信息必须真实准确
   - 材料截止前可以修改
   - 审核结果会公示5个工作日
   - 第二队列需要公证摇号确定选房顺序

5. **其他房源**
   - 住保售〔2026〕004号：待官方公布详情
   - 住保售〔2026〕003号（人才房）：待官方公布详情
   - 建议同时关注深圳住建局官网和官方微信公众号

    """)

    print("=" * 100)
    print("📞 咨询方式")
    print("=" * 100)
    print("""
  • 深圳市住房保障署
    地址：福田区红荔西路莲花大厦东面一楼
    电话：0755-88631666
    时间：工作日 9:00-12:00, 14:00-18:00

  • 举报投诉电话：0755-23913749
    """)

    print("\n🎯 立即行动建议")
    print("=" * 100)
    print("""
1. ✅ 今天内：准备所有申请材料
2. ✅ 明天前：登录官网熟悉申请流程
3. ✅ 本周五（1月25日）18:00前：完成网上认购申请

祝你好运！🍀
    """)

if __name__ == "__main__":
    generate_report()
