import gradio as gr
import os
import time
import chat
import json
from image_generate import image_generate
from fetch import fetch
from search import search  # <--- 在这里添加这行代码

messages = []
current_file_text = None


def add_text(history, text):
    global messages

    text = text.strip()
    if not text:
        return history, gr.update(value="", interactive=True)

    # (处理 /image 的代码保持不变)
    if text.lower().startswith("/image "):
        # ... existing /image code ...
        return history, gr.update(value="", interactive=False)

    # (处理 /fetch 的代码保持不变)
    if text.lower().startswith("/fetch "):
        # ... existing /fetch code ...
        # 注意：这里的实现会丢失历史上下文。
        url = text[len("/fetch "):].strip()
        question = fetch(url)
        messages = [{"role": "user", "content": question}]
        history.append({"role": "user", "content": text})
        return history, gr.update(value="", interactive=False)

    # --- ▼▼▼ 在这里添加新的 /search 处理逻辑 ▼▼▼ ---
    if text.lower().startswith("/search "):
        query = text[len("/search "):].strip()
        print(f"[DEBUG] 触发网络搜索，查询: {query}")

        # 在历史记录中添加用户输入
        history.append({"role": "user", "content": text})

        # 调用 search 函数获取处理后的提问
        question = search(query)

        # 将 search 函数返回的 prompt 作为本次调用的唯一消息
        # 这与 /fetch 的无上下文模式保持一致
        messages = [{"role": "user", "content": question}]

        return history, gr.update(value="", interactive=False)
    # --- ▲▲▲ 新增代码结束 ▲▲▲ ---


    # (普通文本处理代码保持不变)
    user_entry = {"role": "user", "content": text}
    messages.append(user_entry)
    history.append(user_entry)

    return history, gr.update(value="", interactive=False)

def add_file(history, file):
    global messages
    filename = os.path.basename(file.name)
    _, ext = os.path.splitext(filename)
    ext = ext.lower() if ext else ""

    text_extensions = ['.txt', '.py', '.js', '.html', '.css', '.md', '.json']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    file_info = f"📁 Uploaded file: {filename} (Type: {ext[1:] if ext else 'unknown'})"
    content_to_append = file_info

    if ext in text_extensions:
        try:
            with open(file.name, 'r', encoding='utf-8') as f:
                file_content = f.read(2000)
            if file_content:
                content_to_append = f"{file_info}\n\nFile content preview:\n```\n{file_content}\n```"
        except Exception as e:
            content_to_append = f"{file_info}\n\nError reading file: {str(e)}"

    if ext in image_extensions:
        content_to_append = (file.name, f"Uploaded image: {filename}")

    history.append({"role": "user", "content": content_to_append})
    messages.append({
        "role": "user",
        "content": f"🖼️ Uploaded image: {filename}",
        "is_file": True,
        "file_path": file.name,
        "file_ext": ext
    })

    return history


def bot(history):
    global messages

    print("Current messages:")
    print(json.dumps(messages, indent=2, ensure_ascii=False))

    if not any(m["role"] == "user" for m in messages):
        welcome = {"role": "assistant", "content": "Hello, I'm your AI assistant. What can I do for you?"}
        messages.append(welcome)
        history.append(welcome)
        return history

    if messages[-1].get("is_file", False):
        response = "What do you want me to do with this file?"
        messages.append({"role": "assistant", "content": response})
        history.append({"role": "assistant", "content": response})
        return history

    full_response = ""
    history.append({"role": "assistant", "content": full_response})
    yield history

    try:
        response_stream = chat.chat(messages, timeout=120)
        for chunk in response_stream:
            full_response += chunk
            history[-1]["content"] = full_response
            yield history

    except Exception as e:
        full_response = f"Error: {str(e)}"
        history[-1]["content"] = full_response
        yield history

    messages.append({"role": "assistant", "content": full_response})
    print("Full response added to messages:", full_response[:50] + "..." if len(full_response) > 50 else full_response)


with gr.Blocks() as demo:
    # 获取头像路径
    current_dir = os.path.dirname(__file__)
    avatar_path = os.path.join(current_dir, "avatar.png")

    # 修复括号问题
    chatbot = gr.Chatbot(
        type="messages",
        elem_id="chatbot",
        avatar_images=(None, avatar_path)
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image, and the assistant would help you!",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    debug_output = gr.Textbox(label="Debug Output", visible=False)


    def clear_chat():
        global messages
        messages = []
        return []


    txt_msg = txt.submit(
        add_text, [chatbot, txt], [chatbot, txt], queue=False
    ).then(
        bot, chatbot, chatbot
    ).then(
        lambda: gr.update(interactive=True), None, [txt], queue=False
    )

    file_msg = btn.upload(
        add_file, [chatbot, btn], [chatbot], queue=False
    ).then(
        bot, chatbot, chatbot
    )

    clear_btn.click(clear_chat, None, chatbot, queue=False)

demo.queue()
demo.launch()