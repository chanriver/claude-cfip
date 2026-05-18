# Cloudflare IP Tester

CF IP 测速工具 - 自动关闭代理、多线程测速、查询地理位置、输出 txt/json。

## 快速开始

### 1. 配置 GitHub（可选，用于自动推送）

创建 `scripts/.env` 文件：

```bash
# GitHub Configuration
GITHUB_TOKEN=your_token_here
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo
GITHUB_BRANCH=main
```

### 2. 运行测速

```bash
cd scripts
python cf-ip-test.py
```

### 3. 输出文件

- `cf-best-ips.txt` - IP:端口#国家/城市,延迟
- `cf-best-ips.json` - 完整数据（含地理信息）

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GITHUB_TOKEN` | (空) | GitHub Personal Access Token |
| `GITHUB_OWNER` | chanriver | GitHub 用户名 |
| `GITHUB_REPO` | claude-cfip | 仓库名 |
| `GITHUB_BRANCH` | main | 分支名 |

## GitHub Token 获取方法

1. 登录 GitHub → Settings → Developer settings
2. Personal access tokens → Generate new token
3. 勾选 `repo` 权限
4. 复制生成的 token

## 目录结构

```
cf-ip-tester/
├── SKILL.md              # Skill 元数据
└── scripts/
    ├── cf-ip-test.py     # 主测速脚本
    ├── .env.example       # 配置模板
    └── README.md          # 本文件
```

## 移植到其他 Agent

1. 复制整个 `cf-ip-tester/` 目录
2. 创建 `scripts/.env` 文件，填入 GitHub 配置
3. 运行 `python cf-ip-test.py`

## 功能特性

- ✅ 自动关闭/恢复系统代理
- ✅ 多线程并发测速（50线程）
- ✅ IP 地理位置查询（ip-api.com）
- ✅ 国旗 emoji 显示
- ✅ 国家名称中文显示
- ✅ txt/json 双格式输出
- ✅ 自动推送到 GitHub（可选）