# open-webui-pipeline-for-ragflow
一个好用又好看的大模型ui+rag在大模型问答类项目上简直太香了。open-webui+ragflow简直是绝配，既有ragflow的功能，又有open-webui漂亮强大的交互界面。使用open-webui中的pipeline技术在open-webui中调用ragflow的agent实现基于知识库的智能对话简直太棒了！
## 关于[open-webui](https://github.com/open-webui/open-webui)
open-webui是一个非常好的大模型聊天集成软件，他提供的[pipelines](https://github.com/open-webui/pipelines)的方式，极大便利了集成其它大模型工具API到它的对话中来。
## 关于[ragflow](https://github.com/infiniflow/ragflow)
ragflow是我在实际项目中使用过的比较好用的大模型知识库开源项目，它成功支撑了我所负责的项目，用户在实际使用中也给予了很好的评价。
## 关于本项目
在我所负责的大模型项目中，ragflow的agent很好的处理了基于知识库的问答，但不幸的是，ragflow并没有提供一个很好的对话交互界面，自带的界面仅仅是便于调试，完全无法让用户使用，因此需要将ragflow的agent集成进入一个比较成熟的对话界面软件，经过多种软件对比，我选择了open-webui。因为open-webui提供了一种集成技术[pipelines](https://github.com/open-webui/pipelines)。因此我开发了可以把在ragflow中所开发的agent集成入open-webui的[pipelines](https://github.com/open-webui/pipelines)。因为觉得好用，也想分享给有需的人，完全免费的分享，没有任何版权协议限制，您可以随便使用。仅仅是希望您不吝赐星一枚^_^
## 联系我
如果有好的想法或发现了什么问题，请您一定要告诉我哦，扫码加我微信，如果看不见码，我的微信ID：qiuzhiyushi
<img src="./wechat.jpg" alt="我的微信：qiuzhiyushi" width="300">

## 使用方法
- 首先下载open-webui的[pipelines](https://github.com/open-webui/pipelines)项目
- 启动这个项目后，参考[pipelines](https://github.com/open-webui/pipelines)的README，在open-webui中的配置好pipelines的链接
- 配置好链接后，将本项目的open-webui-pipeline-for-ragflow.py在open-webui中上传后，配置以下四个参数：
  - API_KEY: ragflow的apikey
  - AGENT_ID: ragflow的agentid
  - HOST: ragflow的host（要以http://或https://开头）
  - PORT: ragflow的port
然后你就可以实现在open-webui中调用ragflow中的agent，并且拥有美观的交互界面了。
## 与ragflow和open-webui的版本适配历史
- 2025年6月19日，与open-webui 0.6.15和ragflow 0.19.0适配测试通过。
- 2025年4月8日，与open-webui 0.5.20和ragflow 0.17.0适配测试通过。
