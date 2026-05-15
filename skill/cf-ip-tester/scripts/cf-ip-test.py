#!/usr/bin/env python3
"""CF IP Tester - 测试 Cloudflare IP 的延迟和下载速度"""

import concurrent.futures
import json
import random
import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class IPResult:
    ip: str
    latency_ms: Optional[float] = None
    download_speed_mb: Optional[float] = None
    score: float = 0

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

def main():
    print("正在获取 Cloudflare IP 段...")
    ips = []
    for cidr in CF_IP_RANGES:
        ips.extend(ip_from_cidr(cidr, count=20))

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

    print("\n" + "="*60)
    print("Top 20 最快 Cloudflare IP（按延迟排序）")
    print("="*60)
    print(f"{'IP':<20} {'延迟(ms)':<12}")
    print("-"*60)

    for r in top20:
        latency_str = f"{r.latency_ms:.1f}" if r.latency_ms else "N/A"
        speed_str = f"{r.download_speed_mb:.1f}" if r.download_speed_mb else "N/A"
        print(f"{r.ip:<20} {latency_str:<12}")

    # 保存结果
    output = {
        "update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tested": len(results),
        "top_20": [
            {"ip": r.ip, "latency_ms": round(r.latency_ms, 1) if r.latency_ms else None,
             "speed_mb": round(r.download_speed_mb, 1) if r.download_speed_mb else None}
            for r in top20
        ]
    }

    with open("cf-best-ips.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n结果已保存到 cf-best-ips.json")

if __name__ == "__main__":
    main()