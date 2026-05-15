---
name: cf-ip-tester
description: |
  Cloudflare IP 测速工具 - 找出延迟最低、速度最快的 CF IP。

  当用户提到：cf IP 测速、cloudflare speed test、找最快 CF IP、CF 优选 IP、测试 CF 节点、
  想要获取优质的 Cloudflare CDN IP、需要 IP:端口 格式文件 时使用此 skill。

  功能：自动关闭系统代理 → 多线程测速 → 输出 txt/json → 可选推送到 GitHub。
version: 1.1
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
1. 关闭系统代理（避免代理干扰）
2. 从 Cloudflare 官方获取 IP 段
3. 每个 /24 段随机选取 IP
4. 多线程并发测试延迟（TCP 连接 443 端口）
5. 按延迟排序，输出 Top 20
6. 生成 txt 和 json 文件
7. 恢复系统代理
8. 可选：推送到 GitHub
```

## 使用方法

### 基本测速

```
测速 CF IP
```

### 配置 GitHub 推送

在调用 skill 时提供：
- `GITHUB_TOKEN`: Personal Access Token (ghp_xxx)
- `GITHUB_OWNER`: GitHub 用户名
- `GITHUB_REPO`: 仓库名
- `GITHUB_BRANCH`: 分支名（默认 main）

## 输出文件

### txt 格式 (cf-best-ips.txt)

```
162.159.46.22:443
173.245.59.12:443
162.159.19.122:443
...
```

### json 格式 (cf-best-ips.json)

```json
{
  "update_time": "2026-05-15 16:30:12",
  "total_tested": 74,
  "top_20": [
    {"ip": "162.159.46.22", "latency_ms": 66.0}
  ]
}
```

## 技术实现

### 关键函数

1. **关闭代理**: 修改注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings`
2. **获取 IP 段**: `curl -s https://www.cloudflare.com/ips-v4`
3. **测试延迟**: Python socket TCP 连接，超时 3 秒
4. **并发测速**: `concurrent.futures.ThreadPoolExecutor`，默认 50 线程
5. **GitHub 推送**: REST API `PUT /repos/{owner}/{repo}/contents/{path}`

### 依赖

- Python 3.x
- requests 库

## 注意事项

1. 测速时会自动关闭/恢复系统代理
2. 下载速度测试需要测速地址支持，当前仅测试延迟
3. 测速结果受网络波动影响，每次可能不同
4. 建议每周更新一次 IP 列表