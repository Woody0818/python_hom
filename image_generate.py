import requests
from typing import Optional


def image_generate(prompt: str, size: str = "256x256") -> Optional[str]:
    """
    调用 LocalAI 的 Stable Diffusion API 生成图片

    Args:
        prompt: 图片描述文本（英文效果更好，如 "A cute cat"）
        size: 图片尺寸（默认 "256x256"）

    Returns:
        图片URL（如 "http://localhost:8080/generated-images/xxx.png"）
        失败时返回 None
    """
    api_url = "http://localhost:8080/v1/images/generations"
    print(f"[DEBUG] 请求URL: {api_url}")  # 调试输出

    data = {
        "prompt": prompt,
        "size": "256x256",
        "model": "stablediffusion"
    }
    print(f"[DEBUG] 请求数据: {data}")  # 调试输出

    try:
        response = requests.post(api_url, json=data, timeout=600)
        print(f"[DEBUG] 响应状态: {response.status_code}")  # 调试输出
        print(f"[DEBUG] 响应内容: {response.text}")  # 调试输出

        response.raise_for_status()
        return response.json()["data"][0]["url"]
    except Exception as e:
        print(f"[ERROR] 完整错误: {str(e)}")
        return None


if __name__ == "__main__":
    # 测试代码
    test_url = image_generate("A cute baby sea otter")
    if test_url:
        print(f"图片生成成功！访问地址:\n{test_url}")
    else:
        print("生成失败，请检查：")
        print("1. LocalAI 服务是否运行（docker ps）")
        print("2. 模型是否加载（curl http://localhost:8080/models）")
