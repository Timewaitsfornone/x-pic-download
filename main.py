import re
import requests
import os
import random
import string
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# 读取文件中的 curl 命令
with open("C:/Users/95779/Documents/downloadpic/surl.txt", "r", encoding="utf-8") as file:
    curl_commands = file.readlines()

# 用来保存提取的修改后URL
modified_urls = []

# 提取每一行中的 URL
for curl_command in curl_commands:
    if not curl_command.strip():
        continue
    
    url_match = re.search(r'https?://pbs.twimg.com/media/[^\s"]+', curl_command.strip())
    if not url_match:
        continue

    original_url = url_match.group(0)
    # 如果已经是最高分辨率，跳过
    if "&format=jpg&name=4096x4096" in original_url:
        # 初始化修改后的 URL
        modified_urls.append(original_url)
        continue
    # 处理不同的 URL 格式
    if "format=jpg" in original_url:
        modified_url = original_url.replace("format=jpg", "format=jpg&name=4096x4096")
    elif ".jpg" in original_url:
        # 如果是 .jpg 结尾，直接添加参数
        modified_url = original_url.replace(".jpg", "?format=jpg&name=4096x4096")
    elif ".png" in original_url:
        continue  # 跳过 PNG 文件（如果不需要处理 PNG）
    
    modified_urls.append(modified_url)

# 去重
modified_urls = list(set(modified_urls))

# 生成4个随机字母
def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

random_dir=generate_random_string()
# 确保保存图片的文件夹存在
download_folder = f"C:/Users/95779/Documents/downloadpic/picdown{random_dir}"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 将修改后的 URL 写入文件
with open("C:/Users/95779/Documents/downloadpic/url.txt", "w", encoding="utf-8") as output_file:
    for url in modified_urls:
        output_file.write(url + "\n")

print(f"已成功提取{len(modified_urls)}张图片，并保存修改后的 URL. 开始下载图片.")
starttime=time.time()
def download_image(image_url, save_path, progress_bar):
    try:
        # 设置超时时间为10秒，避免无限等待
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Image downloaded successfully: {save_path}")
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 无论成功或失败，更新进度条
        progress_bar.update(1)

# 下载图片并实时更新进度
def download_images():
    total_images = len(modified_urls)
    with tqdm(total=total_images, desc="Downloading Images", mininterval=0.1) as progress_bar:
        with ThreadPoolExecutor(max_workers=100) as executor:
            # 提交所有下载任务
            futures = []
            for index, image_url in enumerate(modified_urls):
                random_str = generate_random_string()
                save_path = os.path.join(download_folder, f"image_{random_str}_{index + 1}.jpg")
                futures.append(executor.submit(download_image, image_url, save_path, progress_bar))
            
            # 等待所有任务完成，最长等待60秒
            for future in futures:
                try:
                    future.result(timeout=30)
                except Exception as e:
                    print(f"Task failed with error: {e}")
    
    print(f"所有图片下载完成.总用时{(time.time()-starttime):.2f} S")

if __name__ == "__main__":
    download_images()