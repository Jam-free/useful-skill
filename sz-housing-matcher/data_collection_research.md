# 深圳保障房数据收集方案调研报告

调研时间：2025-01-20
调研目的：为深圳保障房匹配工具寻找可靠的数据收集方案

---

## 一、官方数据源（推荐优先使用）

### 1. 深圳市政府数据开放平台 ⭐⭐⭐⭐⭐

**网址：** https://opendata.sz.gov.cn

**优势：**
- ✅ 官方权威数据
- ✅ 提供标准API接口
- ✅ 支持多种格式（JSON、XML、CSV等）
- ✅ 数据更新及时
- ✅ 免费调用

**相关数据集：**
- 安居型商品房轮候数据（ID: 29200_01903539）
- 安居型商品房轮候册认购计次数据（ID: 29200_01903495）
- 政府保障房-房屋合同信息（售房）

**使用方式：**
```python
import requests

# 示例：调用安居房轮候数据API
api_url = "https://opendata.sz.gov.cn/api/29200_01903539"
response = requests.get(api_url)
data = response.json()
```

**获取API Key：**
1. 访问 https://opendata.sz.gov.cn
2. 注册账号
3. 进入"数据接口"页面
4. 选择需要的API
5. 获取调用凭证

---

### 2. 深圳市住房和建设局官网 ⭐⭐⭐⭐⭐

**网址：**
- 主站：https://zjj.sz.gov.cn
- 住房保障服务：https://zjj.sz.gov.cn/ztfw/zfbz/
- 通知公告：https://zjj.sz.gov.cn/xxgk/tzgg/

**关键页面：**
- 房源计划：https://zjj.sz.gov.cn/ztfw/zfbz/fyjh/
- 分配信息：https://zjj.sz.gov.cn/ztfw/zfbz/fpxx/
- 分配结果：https://zjj.sz.gov.cn/ztfw/zfbz/fpjg/
- 安居房轮候信息公示：https://zjj.sz.gov.cn/ztfw/zfbz/grfw/ajfgs/

**优势：**
- ✅ 第一手官方信息
- ✅ 更新及时
- ✅ 信息完整

**挑战：**
- ⚠️ 网站可能有反爬虫机制
- ⚠️ 需要解析HTML

**解决方案：**
- 使用Selenium/Playwright模拟浏览器
- 设置合理的请求间隔（如每隔1-2小时）
- 添加User-Agent
- 考虑使用代理IP池

---

### 3. 深圳住建局微信公众号 ⭐⭐⭐⭐

**公众号名称：** 深圳市住房和建设局

**优势：**
- ✅ 官方渠道
- ✅ 推送及时
- ✅ 方便接收通知

**数据获取方案：**
- 方案A：使用第三方API服务（如新榜、清博大数据）
- 方案B：人工订阅+手动记录
- 方案C：使用自动化工具监控公众号文章（需注意合规性）

---

### 4. 各区住建局官网 ⭐⭐⭐⭐

**福田区：** https://www.szft.gov.cn/bmxx/qjsj/tzgg/
**龙华区：** https://www.szlhq.gov.cn/lhq/zdfwgb/zfztgb/zxgg38/
**光明区：** https://www.szgm.gov.cn/gmjsj/zcfg/
**南山区：** https://www.szns.gov.cn/nsqzjj/gkmlpt/

**优势：**
- ✅ 区域房源信息更详细
- ✅ 补充市级官网信息

---

## 二、第三方权威平台（辅助使用）

### 1. 深圳本地宝 ⭐⭐⭐

**网址：** https://sz.bendibao.com

**优势：**
- ✅ 整理及时
- ✅ 解读详细
- ✅ 有房源汇总文章

**示例文章：**
- "深圳14173套公租房、保租房、人才房、安居房正在申请"
- "2025深圳公共租赁住房配租最新消息"

**使用建议：**
- 作为参考和验证
- 不作为唯一数据源

---

## 三、技术方案对比

### 方案A：官方API（推荐）⭐⭐⭐⭐⭐

**技术栈：**
- Python requests
- 定时任务（cron或APScheduler）

**实现步骤：**
```python
import requests
from datetime import datetime

def fetch_housing_data():
    """从开放平台获取住房数据"""
    api_base = "https://opendata.sz.gov.cn/api"

    # 获取安居房轮候数据
    response = requests.get(f"{api_base}/29200_01903539")
    data = response.json()

    # 处理数据
    return process_data(data)

# 定时任务：每天凌晨2点执行
schedule.every().day.at("02:00").do(fetch_housing_data)
```

**优点：**
- 稳定可靠
- 无需维护爬虫
- 数据格式标准

**缺点：**
- API可能有调用频率限制
- 数据可能不是最新的（有延迟）

---

### 方案B：网页爬虫 ⭐⭐⭐⭐

**技术栈：**
- Playwright（推荐）或 Selenium
- BeautifulSoup4
- 代理IP池（可选）

**实现示例：**
```python
from playwright.sync_api import sync_playwright
import time

def scrape_zjj_notices():
    """爬取深圳住建局通知公告"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 访问通知公告页
        page.goto("https://zjj.sz.gov.cn/xxgk/tzgg/")
        time.sleep(2)  # 等待页面加载

        # 提取公告列表
        notices = page.query_selector_all(".notice-list a")

        for notice in notices:
            title = notice.inner_text()
            url = notice.get_attribute("href")

            # 过滤保障房相关公告
            if keyword in title:
                save_to_db(title, url)

        browser.close()
```

**优点：**
- 获取最新数据
- 信息全面

**缺点：**
- 需要维护（网站结构可能变化）
- 可能有反爬虫风险
- 请求频率受限

**改进措施：**
1. 使用浏览器指纹规避检测
2. 设置随机请求间隔（30-120分钟）
3. 使用代理IP池
4. 添加错误处理和重试机制
5. 记录爬取日志

---

### 方案C：网页监控工具 ⭐⭐⭐⭐

**推荐工具：**

#### 1. changedetection.io
- **GitHub：** https://github.com/dgtlmoon/changedetection.io
- **特点：**
  - 开源免费
  - 支持20k+ stars
  - 可Docker部署
  - 支持多种通知方式（邮件、Webhook、微信等）

**部署示例：**
```bash
# Docker部署
docker run -d \
  --name changedetection \
  -p 5000:5000 \
  -v changedetection-data:/datastore \
  dgtlmoon/changedetection.io
```

**配置监控：**
1. 访问 http://localhost:5000
2. 添加监控URL：https://zjj.sz.gov.cn/xxgk/tzgg/
3. 设置检查频率：每小时
4. 配置通知方式：Webhook

**集成到Python：**
```python
import requests

def check_changes():
    """检查changedetection的更新"""
    api_url = "http://localhost:5000/api/v1/watch"
    response = requests.get(api_url)
    updates = response.json()

    for update in updates:
        if update['has_changed']:
            process_new_notice(update['url'])
```

#### 2. WebMonitor
- **GitHub：** https://github.com/xxx/webmonitor
- **特点：**
  - Python编写
  - 支持Docker部署
  - 支持微信推送
  - 支持RSS监控

---

### 方案D：RSS订阅（如果可用）⭐⭐⭐

**检查RSS是否可用：**
```bash
curl -I https://zjj.sz.gov.cn/xxgk/tzgg/rss.xml
```

**如果网站不支持RSS，可以使用：**
- Feed43（将网页转换为RSS）
- RSSHub（开源RSS生成器）

---

## 四、推荐实施方案（混合方案）

### 架构设计：

```
┌─────────────────────────────────────────┐
│           数据收集层                      │
├─────────────────────────────────────────┤
│ 1. 深圳市政府数据开放平台API (主要数据源) │
│ 2. 网页监控工具 (changedetection.io)     │
│ 3. 各区住建局官网爬虫 (补充数据)         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│           数据处理层                      │
├─────────────────────────────────────────┤
│ - 数据清洗                               │
│ - 去重合并                               │
│ - 数据存储 (JSON/SQLite/MySQL)          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│           应用服务层                      │
├─────────────────────────────────────────┤
│ - 用户匹配算法                           │
│ - 交通分析 (高德API)                     │
│ - 结果展示                               │
└─────────────────────────────────────────┘
```

### 实施步骤：

#### 第一阶段（基础版 - 1-2天）
1. ✅ 使用changedetection.io监控官网
2. ✅ 实现基础爬虫获取公告列表
3. ✅ 手动验证数据准确性

#### 第二阶段（优化版 - 1周）
1. ⏳ 申请深圳市政府数据开放平台API
2. ⏳ 实现API数据获取
3. ⏳ 建立数据库存储历史数据
4. ⏳ 实现自动匹配算法

#### 第三阶段（完善版 - 持续迭代）
1. ⏳ 添加微信公众号监控
2. ⏳ 实现数据可视化
3. ⏳ 添加微信通知功能
4. ⏳ 优化匹配算法

---

## 五、技术选型建议

### 数据收集优先级：

1. **最高优先级：** changedetection.io 监控官网通知公告页
2. **次要优先级：** 深圳市政府数据开放平台API
3. **补充优先级：** 各区住建局官网爬虫
4. **辅助优先级：** 第三方平台（本地宝等）

### 技术栈推荐：

```python
# 核心依赖
requests>=2.31.0          # HTTP请求
beautifulsoup4>=4.12.0    # HTML解析
playwright>=1.40.0        # 浏览器自动化
apscheduler>=3.10.0       # 定时任务
sqlite3                   # 数据库（Python内置）
```

### 部署方式：

**开发环境：** 本地运行
**生产环境：**
- Docker容器化部署
- 定时任务：cron
- 日志记录：log文件
- 错误通知：邮件/微信

---

## 六、注意事项

### 法律合规：
✅ 遵守robots.txt
✅ 不爬取个人信息
✅ 请求频率合理（建议1-2小时间隔）
✅ 数据仅用于个人使用

### 技术注意：
⚠️ 网站结构可能变化，需要定期维护
⚠️ IP可能被封，需要代理池
⚠️ 数据准确性需要验证

### 数据验证：
✅ 定期人工检查数据准确性
✅ 对比多个数据源
✅ 保留数据源链接，方便用户核对

---

## 七、预算和时间评估

### 开发时间：
- 基础版：1-2天
- 完整版：1-2周
- 优化维护：持续进行

### 费用预算：
- 服务器（如需）：¥50-200/月
- 代理IP（可选）：¥100-500/月
- 域名（可选）：¥50-100/年
- **免费方案：** 本地运行 + 免费监控工具

---

## 八、下一步行动

### 立即可做：
1. ✅ 部署changedetection.io监控官网
2. ✅ 编写基础爬虫脚本
3. ✅ 验证数据准确性

### 本周完成：
1. ⏳ 申请开放平台API Key
2. ⏳ 建立数据库
3. ⏳ 实现完整的匹配流程

### 持续优化：
1. ⏳ 添加更多数据源
2. ⏳ 优化匹配算法
3. ⏳ 改进用户体验

---

## 九、参考资料

### 官方网站：
- [深圳市政府数据开放平台](https://opendata.sz.gov.cn)
- [深圳市住房和建设局](https://zjj.sz.gov.cn)
- [住房保障服务](https://zjj.sz.gov.cn/ztfw/zfbz/)

### 工具项目：
- [changedetection.io](https://github.com/dgtlmoon/changedetection.io)
- [深圳市政府数据开放平台API列表](https://opendata.sz.gov.cn/data/api/toApi)

### 文章参考：
- [20k Star网页监控神器推荐](https://cloud.tencent.com/developer/article/2479246)
- [WebMonitor Docker部署教程](https://zhuanlan.zhihu.com/p/1905008134990313279)

---

**报告生成时间：** 2025-01-20
**下次更新时间：** 根据实施情况调整
