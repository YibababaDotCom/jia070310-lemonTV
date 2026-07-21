import requests

M3U_URL = "https://raw.githubusercontent.com/jia070310/lemonTV/refs/heads/main/iptv-fe.m3u"
OUTPUT_FILE = "cctv5.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 频道映射关系：{ M3U中的频道识别特征: (输出的ID/名称, 显示标题) }
TARGET_CHANNELS = {
    "CCTV5+体育赛事": {
        "id": "CCTV5+",
        "title": "CCTV-5+ 体育赛事"
    },
    "CCTV5体育": {
        "id": "CCTV5",
        "title": "CCTV-5 体育"
    },
    "CCTV1综合": {
        "id": "CCTV1",
        "title": "CCTV-1综合"
    },
    "CCTV2财经": {
        "id": "CCTV2",
        "title": "CCTV-2财经"
    },
    "CCTV3综艺": {
        "id": "CCTV3",
        "title": "CCTV-3综艺"
    },
    "CCTV4中文国际": {
        "id": "CCTV4",
        "title": "CCTV-4中文国际"
    },
    "CCTV6电影": {
        "id": "CCTV6",
        "title": "CCTV-6电影"
    }
}

def extract_channel_urls(m3u_text):
    """提取各频道的原始 URL"""
    lines = m3u_text.splitlines()
    found_urls = {}

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            # 遍历我们关心的目标频道
            for target_name in TARGET_CHANNELS.keys():
                if target_name in found_urls:
                    continue  # 已找到的频道跳过
                
                # 准确检查 #EXTINF 行是否包含完整的频道名称
                if target_name in line:
                    # 往下寻找第一条非空的 URL 链接
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            found_urls[target_name] = next_line
                            break

    return found_urls

def resolve_real_url(initial_url):
    """跟进 302 重定向，获取最终真实 URL"""
    try:
        response = requests.head(initial_url, headers=headers, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"解析真实 URL 失败: {e}")
        return initial_url

def main():
    print("正在下载原始 M3U 文件...")
    resp = requests.get(M3U_URL, headers=headers, timeout=15)
    resp.raise_for_status()

    raw_urls = extract_channel_urls(resp.text)
    
    m3u_lines = ["#EXTM3U"]

    # 按照 TARGET_CHANNELS 的顺序处理
    for target_name, config in TARGET_CHANNELS.items():
        raw_url = raw_urls.get(target_name)
        if not raw_url:
            print(f"⚠️ 未找到频道: {target_name}")
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
        
    print(f"已成功写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
