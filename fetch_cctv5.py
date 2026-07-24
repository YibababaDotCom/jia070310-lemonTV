import requests

M3U_URL = "https://raw.githubusercontent.com/jia070310/lemonTV/refs/heads/main/iptv-fe.m3u"
OUTPUT_FILE = "cctv5.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

# 频道映射关系：支持多个可能的匹配关键字（列表形式），提高命中率
TARGET_CHANNELS = {
    "CCTV5+": {
        "id": "CCTV5+",
        "title": "CCTV-5+ 体育赛事",
        "keywords": ["CCTV5+体育赛事", "CCTV5+", "CCTV-5+"]
    },
    "CCTV5": {
        "id": "CCTV5",
        "title": "CCTV-5 体育",
        "keywords": ["CCTV5体育", "CCTV5", "CCTV-5"]
    },
    "CCTV1": {
        "id": "CCTV1",
        "title": "CCTV-1综合",
        "keywords": ["CCTV1综合", "CCTV1", "CCTV-1"]
    },
    "CCTV2": {
        "id": "CCTV2",
        "title": "CCTV-2财经",
        "keywords": ["CCTV2财经", "CCTV2", "CCTV-2"]
    },
    "CCTV3": {
        "id": "CCTV3",
        "title": "CCTV-3综艺",
        "keywords": ["CCTV3综艺", "CCTV3", "CCTV-3"]
    },
    "CCTV4": {
        "id": "CCTV4",
        "title": "CCTV-4中文国际",
        "keywords": ["CCTV4中文国际", "CCTV4", "CCTV-4"]
    },
    "CCTV6": {
        "id": "CCTV6",
        "title": "CCTV-6电影",
        "keywords": ["CCTV6电影", "CCTV6", "CCTV-6"]
    }
}

def extract_channel_urls(m3u_text):
    """优化后的提取逻辑，支持多关键字模糊匹配"""
    lines = m3u_text.splitlines()
    found_urls = {}

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            # 检查当前行是否命中了任何配置的关键字
            for config_key, config_data in TARGET_CHANNELS.items():
                if config_key in found_urls:
                    continue
                
                # 只要满足 keywords 列表中的任意一个词即视为匹配
                if any(kw in line for kw in config_data["keywords"]):
                    # 向下寻找第一个非注释的 URL 链接
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            found_urls[config_key] = next_line
                            break

    return found_urls

def resolve_real_url(initial_url):
    """增强版重定向解析：优先 HEAD，失败或受阻则降级为带有 stream 截断的 GET"""
    try:
        # 第一次尝试：使用 HEAD 请求
        response = requests.head(initial_url, headers=headers, allow_redirects=True, timeout=8)
        if response.status_code < 400:
            return response.url
    except Exception:
        pass

    try:
        # 第二次尝试：降级为 GET 请求（只读取头部流，避免下载完整视频）
        response = requests.get(initial_url, headers=headers, allow_redirects=True, stream=True, timeout=8)
        final_url = response.url
        response.close()
        return final_url
    except Exception as e:
        print(f"⚠️ 解析真实 URL 失败 ({initial_url}): {e}")
        return initial_url

def main():
    print("正在下载原始 M3U 文件...")
    try:
        resp = requests.get(M3U_URL, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ 下载 M3U 文件失败: {e}")
        return

    raw_urls = extract_channel_urls(resp.text)
    m3u_lines = ["#EXTM3U"]

    # 按照 TARGET_CHANNELS 的顺序处理
    for config_key, config in TARGET_CHANNELS.items():
        raw_url = raw_urls.get(config_key)
        if not raw_url:
            print(f"⚠️ 未找到频道: {config['title']}")
            continue

        print(f"[{config['id']}] 找到原始链接: {raw_url}")
        real_url = resolve_real_url(raw_url)
        print(f"[{config['id']}] 转换真实链接: {real_url}\n")

        # 写入 M3U 格式
        m3u_lines.append(f'#EXTINF:-1 tvg-id="{config["id"]}" tvg-name="{config["id"]}",{config["title"]}')
        m3u_lines.append(real_url)

    # 保存最终文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")
        
    print(f"✅ 已成功写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
