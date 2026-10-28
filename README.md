# open-webui-pipeline-for-ragflow
一个好用又好看的大模型ui+rag在大模型问答类项目上简直太香了。open-webui+ragflow简直是绝配，既有ragflow的功能，又有open-webui漂亮强大的交互界面。使用open-webui中的pipeline技术在open-webui中调用ragflow实现基于知识库的智能对话简直太棒了！

:smile:很高兴这个小项目能真正帮助到有需要的人，也特别感谢🙏🙏🙏那些给我发红包:red_envelope:请我喝咖啡:coffee:的人！是你们让我有了意外之喜:smile::smile::smile:。

我这么说，并不是索要红包哦！您仍然可以放心的、毫无心理负担的无偿使用，这里我仅仅只是想感谢一下他们。

## 关于[open-webui](https://github.com/open-webui/open-webui)
open-webui是一个非常好的大模型聊天集成软件，他提供的[pipelines](https://github.com/open-webui/pipelines)的方式，极大便利了集成其它大模型工具API到它的对话中来。
## 关于[ragflow](https://github.com/infiniflow/ragflow)
ragflow是我在实际项目中使用过的比较好用的大模型知识库开源项目，它成功支撑了我所负责的项目，用户在实际使用中也给予了很好的评价。
## 关于本项目
由于AI编程能力突飞猛进，想来靠AI这个项目已经没有意义了，已经不准备维护了，但近来客户要升级，找来找去，还没有发现比这个更好的方式，所以还是继续维护起来吧。（写于2026年10月28日）

在我所负责的大模型项目中，ragflow很好地处理了基于知识库的问答，但不幸的是，ragflow并没有提供一个很好的对话交互界面，自带的界面仅仅是便于调试，完全无法让用户使用，因此需要将ragflow集成进入一个比较成熟的对话界面软件，经过多种软件对比，我选择了open-webui。因为open-webui提供了一种集成技术[pipelines](https://github.com/open-webui/pipelines)。因此我开发了可以把ragflow集成入open-webui的[pipelines](https://github.com/open-webui/pipelines)。因为觉得好用，也想分享给有需的人，完全免费的分享，没有任何版权协议限制，您可以随便使用。仅仅是希望您不吝赐星一枚^_^

## 两个版本的管道

| 文件 | 对应 Release | 适用 ragflow | 对接对象 | 状态 |
|---|---|---|---|---|
| **`ragflow_chat_pipeline.py`**（[1.0.x](../../releases)，推荐） | **1.0.x** | v1.0.0-rc2+（Go 版） | 聊天助手（Chat Assistant） | 当前维护 |
| `rag_flow_webapi_pipeline_cs.py`（[0.0.x](../../releases)） | 0.0.x | ≤ 0.21.x（Python 版） | Agent | 仅存档，ragflow v1.0 已移除对应 API |

## 1.0.x 使用方法（ragflow v1.0+，聊天助手）

> 适配版本组合：本管道（对应 Release **1.0.x**）实测通过于 **open-webui 0.12.4 + [pipelines](https://github.com/open-webui/pipelines) 官方 `main` 镜像（2025-08 版）+ ragflow v1.0.0-rc2（补丁镜像）**。0.0.x 版管道的适配版本见文末历史。

参照 [pipelines 官方使用指南](https://github.com/open-webui/pipelines#-getting-started)三步走：

1. **启动 pipelines 容器**：

   ```sh
   docker run -d -p 9099:9099 --add-host=host.docker.internal:host-gateway \
     -v pipelines:/app/pipelines --name pipelines --restart always \
     ghcr.io/open-webui/pipelines:main
   ```

   如需自定义访问密钥，加 `-e PIPELINES_API_KEY=<你的key>`。注意变量名必须**精确写成 `PIPELINES_API_KEY`（以 `_KEY` 结尾）**——如果多写一个字母 S 变成 `PIPELINES_API_KEYS`，服务不会报错但会**静默忽略**它，继续使用默认密钥 `0p3n-w3bu!`，导致你在 open-webui 里填自己的 key 时连不上。不设此变量时默认密钥就是 `0p3n-w3bu!`。

2. **在 open-webui 中连接**：**设置 → 连接 → OpenAI API** 添加连接，URL 填 `http://<pipelines主机>:9099`，密钥填上一步的 key（open-webui 若跑在 docker 里，主机用 `host.docker.internal`）。

3. **上传管道并配置参数**：进入 **管理员面板 → 设置 → Pipelines** 页签，上传本项目的 `ragflow_chat_pipeline.py`，上传后该管道会出现在列表中，在同一个页面点击它配置 Valves：

   | 参数 | 说明 |
   |---|---|
   | `API_KEY` | ragflow 的 API Key（界面右上角头像 → API 密钥生成） |
   | `API_BASE` | ragflow API 服务地址，如 `http://192.168.1.X:9380` |
   | `WEB_BASE` | ragflow **网页**地址（引用链接跳转用），如 `http://192.168.1.X:80` |
   | `CHAT_ID` | ragflow **聊天助手** ID（绑定了知识库的那个，不是 agent id） |
   | `TOP_K_REF` | 参考来源最多展示几个文档（默认 6） |

配置完成后即可在 open-webui 中选择该管道模型对话：流式回答、多轮上下文（直接透传 messages，无需会话管理）、**思考过程自动折叠**、答案末尾附**参考来源文档链接**（点击跳 ragflow 文档页）。

> [!NOTE]
> 若不走界面上传、而是直接把 `ragflow_chat_pipeline.py` 放进容器挂载目录 `/app/pipelines`，也能用；但该版本 pipelines **不会热重载磁盘文件**——此后每次直接修改该文件都要 `docker restart pipelines` 才生效（通过界面上传新版本则无此问题）。

**重要前置——使用修改过的 ragflow 镜像**：ragflow v1.0.0-rc2 的 OpenAI 兼容层会把模型思考混入正文，需要使用打过补丁的镜像，待上游官方修复后可回归官方镜像。

**直接拉取已打好补丁的镜像**（基于官方 `infiniflow/ragflow:v1.0.0-rc2` 构建）：

```sh
docker pull luyilong2026/ragflow:v1.0.0-rc2-fixes
```

然后把 ragflow 部署中 `docker/.env` 的 `RAGFLOW_IMAGE` 改为该镜像名即可，数据与官方镜像完全兼容。

## 与ragflow和open-webui的版本适配历史
- 2026年10月28日，1.0.0（ragflow_chat_pipeline.py）与open-webui 0.12.4和ragflow v1.0.0-rc2适配测试通过：改走聊天助手 OpenAI 兼容端点，支持流式/引用/思考折叠；ragflow 侧需本地补丁修复思考混入正文问题（见上）。
- 2025年10月30日，与open-webui 0.6.34和ragflow 0.21.1适配测试通过，已经处理了ragflow数据格式变化造成的问题。
- 2025年6月19日，与open-webui 0.6.15和ragflow 0.19.0适配测试通过。
- 2025年4月8日，与open-webui 0.5.20和ragflow 0.17.0适配测试通过。

## 联系我
如果有好的想法或发现了什么问题，请您一定要告诉我哦，扫码加我微信，如果看不见码，我的微信ID：qiuzhiyushi
<img src="./wechat.jpg" alt="我的微信：qiuzhiyushi" width="300">
