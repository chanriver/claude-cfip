# CF IP Tester - Cloudflare IP 测速工具

[![版本](https://img.shields.io/badge/version-1.3-blue.svg)](https://github.com/chanriver/claude-cfip)
[![平台](https://img.shields.io/badge/platform-Windows-green.svg)](https://github.com/chanriver/claude-cfip)

**CF IP Tester** 是一款专业的 Cloudflare IP 测速工具，可以快速找出延迟最低、速度最快的 CF IP，并支持自动推送到 GitHub。

## 功能特性

- ✅ **自动代理管理** - 测速前关闭系统代理，测速后自动恢复
- ✅ **多线程测速** - 50 线程并发测试，1500+ IP 样本
- ✅ **地理位置查询** - ip-api.com 免费查询（无需 API Key）
- ✅ **国旗 emoji 显示** - 自动转换国家代码为国旗
- ✅ **国家名称中文** - 30+ 国家中英文对照
- ✅ **双格式输出** - txt（简洁）和 json（完整）
- ✅ **GitHub 推送** - 可选自动推送到仓库

## 快速开始

### 1. 克隆或下载

```bash
git clone https://github.com/chanriver/claude-cfip.git
cd cf-ip-tester
```

### 2. 配置 GitHub（可选）

复制配置模板并填写：

```bash
cd scripts
copy .env.example .env
# 编辑 .env，填入 GitHub Token
```

`.env` 文件内容：

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo
GITHUB_BRANCH=main
```

### 3. 运行测速

```bash
python cf-ip-test.py
```

### 4. 查看结果

```bash
# txt 格式
type cf-best-ips.txt

# json 格式
type cf-best-ips.json
```

## 输出示例

### 终端输出

```
======================================================================
Top 10 最快 Cloudflare IP（含目标地区）
======================================================================
IP                   延迟(ms)       国旗       国家/城市
----------------------------------------------------------------------
162.159.38.34        49.8         🇭🇺 匈牙利 Budapest
172.64.52.21         55.6         🇨🇦 加拿大 Toronto
108.162.198.214      63.7         🇺🇸 美国 Ashburn
...
```

### txt 格式文件

```
162.159.38.34:443#🇭🇺匈牙利/Budapest,49.8ms
172.64.52.21:443#🇨🇦加拿大/Toronto,55.6ms
108.162.198.214:443#🇺🇸美国/Ashburn,63.7ms
```

### json 格式文件

```json
{
  "version": "1.1",
  "update_time": "2026-05-18 12:00:00",
  "total_tested": 1500,
  "top_10": [
    {
      "ip": "162.159.38.34",
      "latency_ms": 49.8,
      "geo": {
        "country": "Hungary",
        "country_code": "HU",
        "region": "Budapest",
        "city": "Budapest"
      }
    }
  ]
}
```

## 文件说明

### 目录结构

```
cf-ip-tester/
├── SKILL.md              # Skill 元数据
├── README.md              # 本文件
├── .gitignore             # Git 忽略配置
└── scripts/
    ├── cf-ip-test.py      # 主测速脚本
    ├── .env.example        # 配置模板
    ├── .env                 # 实际配置（不上传）
    ├── README.md            # scripts 说明
    ├── push_skill_to_github.py  # 推送脚本
    ├── cf-best-ips.txt       # 输出结果
    └── cf-best-ips.json      # 输出结果
```

### GitHub Token 获取

1. 登录 GitHub
2. 进入 **Settings** → **Developer settings** → **Personal access tokens**
3. 点击 **Generate new token**
4. 勾选 `repo` 权限
5. 复制生成的 token

## 测速流程

```
1. [读取配置] 加载 .env 环境变量
2. [关闭代理] 修改注册表，关闭系统代理
3. [获取IP段] 从 Cloudflare IP 段随机采样
4. [并发测速] 50 线程同时测试延迟
5. [地理位置] 批量查询 IP 的国家/城市
6. [排序输出] 按延迟排序，输出 Top 10
7. [生成文件] 保存 txt 和 json 文件
8. [恢复代理] 还原系统代理设置
9. [推送GitHub] 自动推送到仓库（可选）
```

## 技术实现

| 模块 | 技术方案 |
|------|----------|
| 代理管理 | Windows 注册表 `HKCU\...\Internet Settings` |
| 延迟测试 | Python socket TCP 连接，3 秒超时 |
| 并发测速 | `concurrent.futures.ThreadPoolExecutor` |
| 地理查询 | ip-api.com 批量 API（100 IP/请求） |
| 国旗转换 | ISO 3166-1 alpha-2 → emoji 公式 |
| GitHub 推送 | REST API `PUT /repos/{owner}/{repo}/contents/{path}` |

## 移植到其他 Agent

### 步骤

1. **复制整个目录**到目标 Agent
2. **创建 `.env` 文件**，填入 GitHub 配置
3. **运行测速**：`python cf-ip-test.py`

### 环境变量优先级

```
环境变量 > .env 文件 > 代码默认值
```

### 无 GitHub 配置

如果不创建 `.env` 文件，脚本会：
- 使用默认的 `GITHUB_OWNER=chanriver`
- 使用默认的 `GITHUB_REPO=claude-cfip`
- 跳过 GitHub 推送步骤

## 支持的国家/地区

| 中文 | English | 国旗 |
|------|---------|------|
| 加拿大 | Canada | 🇨🇦 |
| 美国 | United States | 🇺🇸 |
| 英国 | United Kingdom | 🇬🇧 |
| 德国 | Germany | 🇩🇪 |
| 法国 | France | 🇫🇷 |
| 日本 | Japan | 🇯🇵 |
| 新加坡 | Singapore | 🇸🇬 |
| 香港 | Hong Kong | 🇭🇰 |
| 台湾 | Taiwan | 🇹🇼 |
| 澳大利亚 | Australia | 🇦🇺 |
| 匈牙利 | Hungary | 🇭🇺 |
| 波兰 | Poland | 🇵🇱 |
| 巴西 | Brazil | 🇧🇷 |
| 印度 | India | 🇮🇳 |
| 韩国 | South Korea | 🇰🇷 |
| 俄罗斯 | Russia | 🇷🇺 |
| 荷兰 | Netherlands | 🇳🇱 |
| 瑞典 | Sweden | 🇸🇪 |
| 瑞士 | Switzerland | 🇨🇭 |
| 意大利 | Italy | 🇮🇹 |
| 西班牙 | Spain | 🇪🇸 |
| ... | ... | ... |

## 常见问题

### Q: 测速结果全是加拿大/美国？

这是因为你所在网络的路由策略。Cloudflare 在全球有很多节点，从中国大陆访问时，某些节点延迟更低。这是正常现象。

### Q: 如何只测特定地区的 IP？

当前版本不支持按地区筛选。如有需要，请提交 Issue。

### Q: 可以不用 GitHub 吗？

可以。不创建 `.env` 文件或 `GITHUB_TOKEN` 留空即可。

### Q: 国旗显示乱码怎么办？

脚本已内置 UTF-8 输出处理，无需额外配置。

## 更新日志

### v1.3 (2026-05-18)
- 增加国家名称中文显示
- 优化输出格式
- 增加 `.env.example` 模板
- 增加 `.gitignore`

### v1.2 (2026-05-15)
- 增加地理位置查询和国旗显示
- 增加 GitHub 自动推送

### v1.1 (2026-05-14)
- 增加代理自动关闭/恢复

### v1.0 (2026-05-10)
- 初始版本

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- GitHub: [chanriver/claude-cfip](https://github.com/chanriver/claude-cfip)
- 问题反馈: [提交 Issue](https://github.com/chanriver/claude-cfip/issues)