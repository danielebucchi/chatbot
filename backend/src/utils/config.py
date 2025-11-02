import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.yaml")

with open(CONFIG_PATH, "r") as f:
    cfg = yaml.safe_load(f)

class Settings:
    def __init__(self):
        self.APP_TMP_DIR: str = cfg.get("app", {}).get("tmp_dir", "/tmp/datapizza")
        self.MAX_UPLOAD_SIZE_MB: int = cfg.get("app", {}).get("max_upload_size_mb", 50)
        os.makedirs(self.APP_TMP_DIR, exist_ok=True)

def get_settings() -> Settings:
    return Settings()
