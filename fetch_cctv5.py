import re
import requests

M3U_URL = "https://raw.githubusercontent.com/jia070310/lemonTV/refs/heads/main/iptv-fe.m3u"
OUTPUT_FILE = "cctv5.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_cctv5_url(m3u_text):
    """从 M3U 内容中找到 CCTV5 对应的播放链接"""
    lines = m3u_text.splitlines()
    for i, line in enumerate(lines):
        # 匹配频道名包含 CCTV5 或 CCTV-5 的 EXTINF 行
        if line.startswith("#EXTINF") and ("CCTV5" in line.upper() or "CCTV-5" in line.upper()):
            # 找到下一行非空且不以 # 开头的 URL
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith("#"):
                    return next_line
    return None

def resolve_real_url(initial_url):
    """跟进 HTTP 重定向，获取最终的真实 URL"""
    try:
        # allow_redirects=True 会自动跟随 301/302 重定向并返回最终响应
        response = requests.head(initial_url, headers=headers, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"解析真实 URL 失败: {e}")
        return initial_url

def main():
    print("正在下载原始 M3U 文件...")
    resp = requests.get(M3U_URL, headers=headers, timeout=15)
    resp.raise_for_status()

    raw_url = extract_cctv5_url(resp.text)
    if not raw_url:
        print("未在 M3U 文件中找到 CCTV5 频道！")
        return

    print(f"提取到原始 URL: {raw_url}")
    real_url = resolve_real_url(raw_url)
    print(f"解析后真实 URL: {real_url}")

    # 生成简化版 M3U 文件保存
    m3u_content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"CCTV5\" tvg-name=\"CCTV5\",CCTV-5 体育\n{real_url}\n"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"已更新保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
