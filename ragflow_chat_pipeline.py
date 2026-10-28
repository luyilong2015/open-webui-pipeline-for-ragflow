"""
title: RAGFlow Chat Assistant Pipeline
author: luyilong2015
date: 2026-10-28
version: 1.0.0
license: MIT
description: 在 Open WebUI（及任何 OpenAI 兼容客户端）中调用 RAGFlow v1.0 聊天助手，
             流式回答并把 RAGFlow 的分块引用转换为 Markdown 来源链接。
required_open_webui_version: 0.5.0
"""
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import requests
import json


class Pipeline:
    # Valves 在 Open WebUI / Pipelines 管理界面里配置
    class Valves(BaseModel):
        API_KEY: str = ""          # RAGFlow API Key（界面-头像-API密钥 生成）
        API_BASE: str = "http://192.168.1.133:9380"   # RAGFlow API 服务地址
        WEB_BASE: str = "http://192.168.1.133:10080"  # RAGFlow 网页地址（引用链接跳转用）
        CHAT_ID: str = ""          # RAGFlow 聊天助手 ID（绑定了知识库的那个）
        TOP_K_REF: int = 6         # 引用列表最多展示几个文档

    def __init__(self):
        self.valves = self.Valves()

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass

    def pipe(
        self, user_message: str, model_id: str,
        messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        v = self.valves
        if not v.API_KEY or not v.CHAT_ID:
            yield "配置不完整：请在 Valves 中填写 API_KEY 和 CHAT_ID。"
            return

        url = f"{v.API_BASE}/api/v1/openai/{v.CHAT_ID}/chat/completions"
        payload = {
            # v1.0 契约: model 传字面量 "model" = 使用助手自己配置的模型；
            # extra_body.reference = 流末 chunk 的 delta 里附带分块引用
            "model": "model",
            "messages": messages,
            "stream": True,
            "extra_body": {"reference": True},
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {v.API_KEY}",
        }
        try:
            resp = requests.post(url, headers=headers, json=payload,
                                 stream=True, timeout=(10, 600))
        except requests.RequestException as e:
            yield f"RAGFlow 连接失败: {e}"
            return
        if resp.status_code != 200:
            yield f"RAGFlow 请求失败 (HTTP {resp.status_code}): {resp.text[:300]}"
            return

        refs_markdown = ""
        in_think = False      # 已输出 <think> 开标记
        think_closed = False  # 已输出 </think> 闭标记
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                data_str = line.decode("utf-8")
                if data_str.startswith("data: "):
                    data_str = data_str[6:]
                elif data_str.startswith("data:"):
                    data_str = data_str[5:]
                if data_str.strip() in ("", "[DONE]"):
                    continue
                chunk = json.loads(data_str)
                delta = (chunk.get("choices") or [{}])[0].get("delta") or {}

                # RAGFlow 修复后思考走 delta.reasoning_content；
                # 包成 <think> 标记让 Open WebUI 渲染为可折叠思维区
                reasoning = delta.get("reasoning_content")
                if reasoning:
                    if not in_think:
                        yield "<think>"
                        in_think = True
                    yield reasoning

                content = delta.get("content")
                if content:
                    if in_think and not think_closed:
                        yield "</think>"
                        think_closed = True
                    yield content

                # 引用挂在最后一个 chunk 的 delta.reference；实测有两种形态:
                # {"chunks": [...]} 对象 或 直接就是 list
                reference = delta.get("reference")
                chunks = None
                if isinstance(reference, dict):
                    chunks = reference.get("chunks")
                elif isinstance(reference, list):
                    chunks = reference
                if chunks:
                    seen, lines = set(), []
                    for c in chunks[: v.TOP_K_REF * 3]:
                        if not isinstance(c, dict):
                            continue
                        doc_id = c.get("document_id") or ""
                        if not doc_id or doc_id in seen:
                            continue
                        seen.add(doc_id)
                        name = c.get("document_name") or doc_id
                        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
                        link = f"{v.WEB_BASE}/document/{doc_id}?ext={ext}"
                        lines.append(f"- [{name}]({link})")
                        if len(lines) >= v.TOP_K_REF:
                            break
                    if lines:
                        refs_markdown = "\n\n---\n**参考来源**\n" + "\n".join(lines)
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError, KeyError):
                # 解析异常绝不打断回答流——最多丢一段引用
                continue

        if refs_markdown:
            yield refs_markdown
