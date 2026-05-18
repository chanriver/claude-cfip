---
name: cf-ip-tester
description: |
  Cloudflare IP 测速工具 - 找出延迟最低、速度最快的 CF IP。

  当用户提到：cf IP 测速、cloudflare speed test、找最快 CF IP、CF 优选 IP、测试 CF 节点、
  想要获取优质的 Cloudflare CDN IP、需要 IP:端口 格式文件 时使用此 skill。

  功能：自动关闭系统代理 → 多线程测速 → 查询地理位置 → 输出 txt/json → 推送到 GitHub。
version: 1.3
---

# CF IP Tester

对 Cloudflare CDN IP 进行测速，找出延迟最低的 IP，支持自动推送到 GitHub。

## 何时使用

- 找最快的 Cloudflare IP
- 测试 CF 节点速度
- 获取优选 IP 列表
- cf IP 测速 / cloudflare speed test
- 需要 IP:端口 格式文件

## 测速流程

```
1. 读取 .env 配置（GitHub 信息）
2. 关闭系统代理（避免代理干扰）
3. 多线程并发测试延迟（TCP 连接 443 端口）
4. 查询 IP 地理位置（国家/城市/国旗）
5. 按延迟排序，输出 Top 10
6. 生成 txt 和 json 文件
7. 恢复系统代理
8. 自动推送到 GitHub（可选）
```

## 使用方法

### 1. 配置

创建 `scripts/.env` 文件：

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=your_username
GITHUB_REPO=your_repo
GITHUB_BRANCH=main
```

### 2. 运行

```bash
cd scripts
python cf-ip-test.py
```

### 3. 输出格式

```
108.162.193.244:443#🇨🇦加拿大/Toronto,62.7ms
162.159.38.253:443#🇭🇺匈牙利/Budapest,63.4ms
...
```

格式：`IP:端口#国家国旗/城市,延迟时间`

## GitHub Token 获取

1. 登录 GitHub → Settings → Developer settings
2. Personal access tokens → Generate new token
3. 勾选 `repo` 权限
4. 复制生成的 token

## 输出文件

### txt 格式 (cf-best-ips.txt)

```
162.159.38.34:443#🇭🇺匈牙利/Budapest,49.8ms
172.64.52.21:443#🇨🇦加拿大/Toronto,55.6ms
108.162.198.214:443#🇺🇸美国/Ashburn,63.7ms
...
```

### json 格式 (cf-best-ips.json)

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

## 技术实现

### 关键函数

1. **关闭代理**: 修改注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings`
2. **测试延迟**: Python socket TCP 连接，超时 3 秒
3. **并发测速**: `concurrent.futures.ThreadPoolExecutor`，默认 50 线程
4. **地理位置**: ip-api.com 批量查询（免费无 key）
5. **国旗转换**: ISO 3166-1 alpha-2 → emoji
6. **国家中文**: 中英文对照表（30+国家）
7. **GitHub 推送**: REST API `PUT /repos/{owner}/{repo}/contents/{path}`

### 依赖

- Python 3.x
- python-dotenv（从 .env 读取配置）
- requests（HTTP 请求）

## 目录结构

```
cf-ip-tester/
├── SKILL.md              # Skill 元数据
└── scripts/
    ├── cf-ip-test.py     # 主测速脚本
    ├── .env.example       # 配置模板（参考）
    ├── README.md          # 使用说明
    ├── cf-best-ips.txt     # 输出结果
    └── cf-best-ips.json    # 输出结果
```

## 移植到其他 Agent

1. 复制整个 `cf-ip-tester/` 目录到目标 Agent
2. 创建 `scripts/.env` 文件，填入 GitHub 配置
3. 可选：删除旧的 `cf-best-ips.txt` 和 `cf-best-ips.json`
4. 运行 `python cf-ip-test.py`

## 注意事项

1. `.env` 文件包含敏感信息，不要提交到公开仓库
2. 测速时会自动关闭/恢复系统代理
3. 国旗 emoji 需要 UTF-8 编码支持（脚本已处理）
4. 如果不需要 GitHub 推送，可以不创建 `.env` 文件
5. 测速结果受网络波动影响，建议每周更新一次