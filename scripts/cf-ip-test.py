#!/usr/bin/env python3
"""CF IP Tester - 测试 Cloudflare IP 的延迟和下载速度"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import concurrent.futures
import json
import os
import random
import socket
import subprocess
import time
import urllib.request
import base64
from dataclasses import dataclass
from typing import Optional, Dict

# 尝试加载 dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 从环境变量或 .env 读取 GitHub 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "chanriver")
GITHUB_REPO = os.getenv("GITHUB_REPO", "claude-cfip")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

# 国家名称中英文对照
COUNTRY_NAME_CN = {
    "Canada": "加拿大",
    "United States": "美国",
    "United Kingdom": "英国",
    "Germany": "德国",
    "France": "法国",
    "Japan": "日本",
    "Singapore": "新加坡",
    "Hong Kong": "香港",
    "Taiwan": "台湾",
    "Australia": "澳大利亚",
    "Netherlands": "荷兰",
    "Sweden": "瑞典",
    "Switzerland": "瑞士",
    "Italy": "意大利",
    "Spain": "西班牙",
    "Poland": "波兰",
    "Brazil": "巴西",
    "India": "印度",
    "South Korea": "韩国",
    "Russia": "俄罗斯",
    "Hungary": "匈牙利",
    "Finland": "芬兰",
    "Norway": "挪威",
    "Denmark": "丹麦",
    "Austria": "奥地利",
    "Ireland": "爱尔兰",
    "Belgium": "比利时",
    "Czech Republic": "捷克",
    "Portugal": "葡萄牙",
    "Mexico": "墨西哥",
}


def disable_proxy():
    """关闭系统代理"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("[代理] 已关闭系统代理")
        return True
    except Exception as e:
        print(f"[代理] 关闭失败: {e}")
        return False


def enable_proxy(proxy_server=None):
    """开启系统代理"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                             0, winreg.KEY_SET_VALUE)
        if proxy_server:
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        else:
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("[代理] 已重新开启系统代理" if proxy_server else "[代理] 已重置代理")
        return True
    except Exception as e:
        print(f"[代理] 开启失败: {e}")
        return False


@dataclass
class GeoInfo:
    """IP地理位置信息"""
    country: str
    country_code: str
    region: str
    city: str

@dataclass
class IPResult:
    ip: str
    latency_ms: Optional[float] = None
    download_speed_mb: Optional[float] = None
    score: float = 0
    geo: Optional[GeoInfo] = None

# Cloudflare IP 段
CF_IP_RANGES = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22"
]

def ip_from_cidr(cidr: str, count: int = 5) -> list:
    """从CIDR段中随机选取IP"""
    import ipaddress
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = list(network.hosts())
    return [str(h) for h in random.sample(hosts, min(count, len(hosts)))]

def test_latency(ip: str, timeout: int = 3) -> Optional[float]:
    """测试IP延迟"""
    try:
        start = time.time()
        sock = socket.create_connection((ip, 443), timeout=timeout)
        sock.close()
        return (time.time() - start) * 1000
    except:
        return None

def test_download_speed(ip: str, timeout: int = 5) -> Optional[float]:
    """测试下载速度 MB/s"""
    try:
        # 使用 curl 测试，下载一个小文件测速
        result = subprocess.run([
            "curl", "-o", "/dev/null", "-s", "-w", "%{speed_download}",
            "--connect-timeout", str(timeout), "-L",
            f"https://{ip}/cdn-cgi/trace"
        ], capture_output=True, text=True, timeout=timeout + 2)

        if result.returncode == 0 and result.stdout.strip():
            speed = float(result.stdout.strip()) / (1024 * 1024)  # bytes to MB
            return speed
    except:
        pass
    return None

def test_ip(ip: str) -> IPResult:
    """测试单个IP的延迟和下载速度"""
    result = IPResult(ip=ip)

    # 测试延迟
    result.latency_ms = test_latency(ip)

    # 如果延迟测试成功，测试下载速度
    if result.latency_ms and result.latency_ms < 500:
        result.download_speed_mb = test_download_speed(ip)

    # 计算分数
    if result.latency_ms and result.download_speed_mb:
        result.score = result.download_speed_mb * 1000 / result.latency_ms

    return result


def country_to_flag(country_code: str) -> str:
    """将ISO 3166-1 alpha-2国家代码转换为国旗emoji"""
    if not country_code or len(country_code) != 2:
        return "🏳️"
    return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)


def fetch_geo_info(ips: list) -> Dict[str, Optional[GeoInfo]]:
    """批量查询IP地理位置信息（使用ip-api.com）"""
    geo_results = {}
    batch_size = 100

    for i in range(0, len(ips), batch_size):
        batch = ips[i:i+batch_size]
        payload = json.dumps([{"query": ip} for ip in batch]).encode('utf-8')

        try:
            req = urllib.request.Request(
                "http://ip-api.com/batch",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                results = json.loads(response.read().decode('utf-8'))
                for item in results:
                    if item.get("status") == "success":
                        geo_results[item["query"]] = GeoInfo(
                            country=item.get("country", ""),
                            country_code=item.get("countryCode", ""),
                            region=item.get("regionName", ""),
                            city=item.get("city", "")
                        )
                    else:
                        geo_results[item["query"]] = None
        except Exception:
            for ip in batch:
                if ip not in geo_results:
                    geo_results[ip] = None

        if i + batch_size < len(ips):
            time.sleep(1)

    return geo_results


def push_to_github():
    """推送到 GitHub"""
    import requests

    file_path = "cf-best-ips.json"
    if not os.path.exists(file_path):
        print(f"[GitHub] 文件不存在: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{file_path}"

    # 获取当前文件 SHA（如果存在）
    get_resp = requests.get(api_url, headers=headers)
    sha = None
    if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")
        print(f"[GitHub] 文件已存在, SHA: {sha}")
    elif get_resp.status_code == 404:
        print("[GitHub] 文件不存在，将创建新文件")
    else:
        print(f"[GitHub] 检查文件失败: {get_resp.status_code} {get_resp.text}")

    # 创建或更新文件
    data = {
        "message": f"Update CF best IPs - {json.loads(content)['update_time']}",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": GITHUB_BRANCH
    }
    if sha:
        data["sha"] = sha

    resp = requests.put(api_url, headers=headers, json=data)
    if resp.status_code in [200, 201]:
        print(f"[GitHub] ✓ 已推送至 https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{file_path}")
    else:
        print(f"[GitHub] ✗ 推送失败: {resp.status_code} {resp.text}")


def main():
    # 关闭系统代理（避免代理干扰测速）
    print("=" * 60)
    print("CF IP Tester - 开始测速")
    print("=" * 60)
    disable_proxy()

    print("正在获取 Cloudflare IP 段...")

    # 扩大IP数量，并优先采集亚太地区的IP
    target_count = 1500

    # 按地区优先级分配采样数量
    # Cloudflare在全球有节点，但亚太地区的IP段需要更多采样才能命中
    ip_sources = [
        # 亚太地区优先采样
        ("108.162.192.0/18", 200),  # 日本/韩国/台湾
        ("141.101.64.0/18", 200),   # 亚太
        ("172.64.0.0/13", 200),      # 全球，主要覆盖亚太
        ("162.158.0.0/15", 200),     # 全球
        ("104.16.0.0/13", 200),      # 全球
        ("104.24.0.0/14", 200),      # 全球
        # 其他地区
        ("173.245.48.0/20", 50),
        ("103.21.244.0/22", 50),
        ("103.22.200.0/22", 50),
        ("103.31.4.0/22", 50),
        ("198.41.128.0/17", 100),
        ("190.93.240.0/20", 50),   # 南美
        ("188.114.96.0/20", 50),   # 欧洲
        ("197.234.240.0/22", 30),
        ("131.0.72.0/22", 20),
    ]

    ips = []
    for cidr, count in ip_sources:
        try:
            ips.extend(ip_from_cidr(cidr, count))
        except:
            pass

    ips = ips[:target_count]
    print(f"共获取 {len(ips)} 个IP，开始测速...")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(test_ip, ip): ip for ip in ips}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if result.latency_ms:
                results.append(result)
                print(f"[{i+1}/{len(ips)}] {result.ip} - 延迟: {result.latency_ms:.1f}ms, 速度: {result.download_speed_mb:.1f}MB/s" if result.download_speed_mb else f"[{i+1}/{len(ips)}] {result.ip} - 延迟: {result.latency_ms:.1f}ms")

    # 排序并输出前20（按延迟排序，延迟越低越好）
    results.sort(key=lambda x: x.latency_ms if x.latency_ms else 999999)
    top20 = results[:20]

    # 查询IP地理位置 - 扩大搜索范围到前100名
    print("\n正在查询IP地理位置...")
    search_results = results[:100] if len(results) > 100 else results
    top_ips = [r.ip for r in search_results]
    geo_map = fetch_geo_info(top_ips)

    # 关联地理信息到结果
    for r in search_results:
        r.geo = geo_map.get(r.ip)

    success_count = sum(1 for g in geo_map.values() if g is not None)
    print(f"地理位置查询完成: {success_count}/{len(top_ips)} 成功")

    # 直接选择延迟最低的前10个IP（无论地区）
    search_results = results[:100] if len(results) > 100 else results

    # 关联地理信息到结果
    for r in search_results:
        r.geo = geo_map.get(r.ip)

    # 排序并选择延迟最低的10个
    search_results.sort(key=lambda x: x.latency_ms if x.latency_ms else 999999)
    selected = search_results[:10]

    # 统计结果中的国家分布
    country_stats = {}
    for r in selected:
        if r.geo:
            c = r.geo.country
            country_stats[c] = country_stats.get(c, 0) + 1
    print(f"结果国家分布: {country_stats}")

    print("\n" + "="*70)
    print("Top 10 最快 Cloudflare IP（含目标地区）")
    print("="*70)
    print(f"{'IP':<20} {'延迟(ms)':<12} {'国旗':<8} {'国家/城市'}")
    print("-"*70)

    for r in selected:
        latency_str = f"{r.latency_ms:.1f}" if r.latency_ms else "N/A"
        if r.geo:
            flag = country_to_flag(r.geo.country_code)
            country_cn = COUNTRY_NAME_CN.get(r.geo.country, r.geo.country)
            geo_str = f"{flag} {country_cn} {r.geo.city}"
        else:
            geo_str = "🌐 Unknown"
        print(f"{r.ip:<20} {latency_str:<12} {geo_str}")

    # 保存结果
    output = {
        "version": "1.1",
        "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tested": len(results),
        "top_10": [
            {
                "ip": r.ip,
                "latency_ms": round(r.latency_ms, 1) if r.latency_ms else None,
                "speed_mb": round(r.download_speed_mb, 1) if r.download_speed_mb else None,
                "geo": {
                    "country": r.geo.country if r.geo else None,
                    "country_code": r.geo.country_code if r.geo else None,
                    "region": r.geo.region if r.geo else None,
                    "city": r.geo.city if r.geo else None,
                } if r.geo else None
            }
            for r in selected
        ]
    }

    with open("cf-best-ips.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n结果已保存到 cf-best-ips.json")

    # 生成 txt 格式文件
    txt_file = "cf-best-ips.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        for r in selected:
            flag = country_to_flag(r.geo.country_code) if r.geo and r.geo.country_code else "🌐"
            country_name_en = r.geo.country if r.geo else "Unknown"
            country_name_cn = COUNTRY_NAME_CN.get(country_name_en, country_name_en)
            city_name = r.geo.city if r.geo else ""
            geo_text = f"{flag}{country_name_cn}" + (f"/{city_name}" if city_name else "")
            f.write(f"{r.ip}:443#{geo_text},{r.latency_ms:.1f}ms\n")
    print(f"结果已保存到 {txt_file}")

    # 恢复代理
    enable_proxy()

    # 推送到 GitHub（如果配置了 token）
    if GITHUB_TOKEN:
        push_to_github()
    else:
        print("\n[GitHub] 未配置 GITHUB_TOKEN，跳过推送")

if __name__ == "__main__":
    main()