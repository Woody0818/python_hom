import gradio as gr
import os
import time
import chat

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.

messages = []
current_file_text = None

def add_text(history, text):
    """
    Adds user text to the conversation history and messages list
    """
    global messages
    history.append({"role": "user", "content": text})
    messages.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    """
    Adds uploaded file to the conversation history and messages list
    """
    global messages

    # 获取文件名和扩展名
    filename = os.path.basename(file.name)
    _, ext = os.path.splitext(filename)
    ext = ext.lower() if ext else ""

    # 文件类型分类
    text_extensions = ['.txt', '.py', '.js', '.html', '.css', '.md', '.json']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    # 初始化文件信息
    file_info = f"📁 Uploaded file: {filename} (Type: {ext[1:] if ext else 'unknown'})"
    content_to_append = file_info  # 默认使用文本信息

    # 读取文件内容（如果是文本文件）
    if ext in text_extensions:
        try:
            with open(file.name, 'r', encoding='utf-8') as f:
                file_content = f.read(2000)  # 只读取前2000字符
            if file_content:
                content_to_append = f"{file_info}\n\nFile content preview:\n```\n{file_content}\n```"
        except Exception as e:
            content_to_append = f"{file_info}\n\nError reading file: {str(e)}"

    # 处理图片文件
    if ext in image_extensions:
        # 使用 Gradio 支持的图片格式：(file_path, alt_text)
        content_to_append = (file.name, f"Uploaded image: {filename}")

    # 添加到历史记录和消息列表
    history.append({"role": "user", "content": content_to_append})
    messages.append({
        "role": "user",
        "content": f"🖼️ Uploaded image: {filename}",
        "is_file": True,  # 标记为文件上传
        "file_path": file.name,  # 保存文件路径供后续处理
        "file_ext": ext  # 保存文件扩展名
    })

    return history

def bot(history):
    """
    Gets bot response using the chat function and updates history
    """
    global messages

    if len(messages) <= 1:  # 只有系统提示没有用户消息
        response = "Hello,I'm your AI assistant.What can I do for you?"
        messages.append({"role": "assistant", "content": response})
        history.append({"role": "assistant", "content": response})
        return history

    start_time = time.time()
    last_message = messages[-1]

    start_time = time.time()
    last_message = messages[-1]

    # 检查是否是文件上传
    if last_message.get("is_file", False):
        response = "What do you want me to do with this file?"
        messages.append({"role": "assistant", "content": response})
        history.append({"role": "assistant", "content": response})
        return history

    try:
        # 调用聊天函数，设置120秒超时
        response = chat.chat(messages, timeout=120)
    except Exception as e:
        response = f"Error: {str(e)}"

        # 计算处理时间
    processing_time = time.time() - start_time

    # 添加处理时间到正常响应
    if response != "Time out!":
        response = f"{response}\n\n⏱️ Processing time: {processing_time:.2f}s"

    messages.append({"role": "assistant", "content": response})
    history.append({"role": "assistant", "content": response})
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        type="messages",
        elem_id="little!",
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image,and the assistant would help you!!",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot
    )
    txt_msg.then(lambda: gr.update(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear_btn.click(lambda: messages.clear(), None, chatbot, queue=False)

demo.queue()
demo.launch()

