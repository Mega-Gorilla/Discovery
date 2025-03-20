from langflow_chat import Langflow,ChatUI
from typing import Dict
import json
import voyager.utils as U
from .env import VoyagerEnv

class Voyager_devbox:
    def __init__(
        self,
        mc_port: int = None,
        mc_host: str = "host.docker.internal",
        server_port: int = 3000,
        server_host: str = "http://127.0.0.1",
        env_wait_ticks: int = 1,
        env_request_timeout: int = 600,
        ckpt_dir: str = "ckpt",
        resume: bool = False,
    ):
        """
        Voyagerのメインクラス。
        :param mc_port: マインクラフトのゲーム内ポート
        :param mc_host: マインクラフトのホスト名またはIP
        :param server_port: mineflayerのポート
        :param server_host: mineflayerのホスト
        :param env_wait_ticks: 各ステップの最後に待機するtick数
        :param env_request_timeout: 各ステップの待機秒数
        :param resume: チェックポイントから再開するかどうか
        """
        # init env
        self.env = VoyagerEnv(
            mc_port=mc_port,
            mc_host=mc_host,
            server_host=server_host,
            server_port=server_port,
            request_timeout=env_request_timeout,
        )
        self.env_wait_ticks = env_wait_ticks
        self.recorder = U.EventRecorder(ckpt_dir=ckpt_dir, resume=resume)
        self.resume = resume
        self.last_events = None
        self.tweaks = {
            "ChatOutput-LfK1l": {},
            "MinecraftDataFormatter-IHaIU": {},
            "LanguageTranslator-mzNKF": {},
            "ChatInput-DOdcW": {},
            "ChatOutput-Q7MzC": {},
            "CombineText-rKwk7": {},
            "TextInput-2JuA8": {},
            "TextInput-nk9Nz": {},
            "CombineText-0U3rh": {},
            "LanguageTranslator-5O13U": {},
            "Prompt-OvwRT": {},
            "CustomComponent-dequj": {},
            "Prompt-rVdLu": {},
            "Prompt-sWCJ6": {},
            "TextInput-i6PXB": {},
            "CombineText-QYYKl": {},
            "LanguageTranslator-tMJHM": {},
            "ChatOutput-sWSbt": {},
            "Agent-NWZia": {},
            "Agent-w6dVn": {},
            "AstraDB-On90D": {},
            "Prompt-kr33k": {},
            "TextInput-N8Zye": {},
            "MergeDataComponent-LzQjK": {},
            "Directory-sY9z8": {},
            "ParseDataFrame-cE0qI": {},
            "AlterMetadata-oTNIq": {},
            "CustomComponent-nd9EO": {},
            "Agent-mwbxB": {},
            "TextInput-L0Cgw": {},
            "CombineText-fWCzB": {},
            "LanguageTranslator-VvUP9": {},
            "ChatOutput-yR3Yo": {},
            "CustomComponent-qSzkx": {},
            "CombineText-ovBJG": {}
        }
        self.langflow = Langflow()
        self.chat_ui = ChatUI(
            langflow_instance=self.langflow,
            port=7850,
            host="127.0.0.1",
            title="Langflow Chat UI",
            auto_open=True
        )
        # バックグラウンドでチャットUIを起動
        self.chat_ui.start_background()

    def learn(self):
        # mineflyer サーバーの初期化
        if self.resume:
            # 再開時はインベントリを維持
            self.env.reset(
                options={
                    "mode": "soft",  # ソフトリセット：インベントリや位置情報を保持
                    "wait_ticks": self.env_wait_ticks,  # 環境が安定するまで待機するティック数
                }
            )
        else:
            # インベントリをクリア
            self.env.reset(
                options={
                    "mode": "hard",  # ハードリセット：すべての状態を初期化
                    "wait_ticks": self.env_wait_ticks,  # 環境が安定するまで待機するティック数
                }
            )
            self.resume = True  # 次回からはresumeモードとして扱う
        self.last_events = self.env.step("")  # 空のコマンドを実行してサーバー環境の現在の状態を取得
        print(f"last_events:\n{self.last_events}")
        langflow_dict,_ = self.langflow.run_flow(
            message=self.last_events,
            endpoint="b9b5f30d-835a-49ca-b76b-6d3b068af83a",
            tweaks=self.tweaks
        )
        action_agent_code = langflow_dict["Action Code"] 
        skill_manager_code = langflow_dict["Skill Manager Code"]
        events = json.loads(self.env.step(action_agent_code,programs=skill_manager_code))
        print(f"events:\n{events}")
        nearbychests = events[-1][1]["nearbyChests"]
        print(f"nearbychests:\n{nearbychests}")
        