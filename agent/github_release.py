import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Set
from agent.config import Config

class GitHubReleaseManager:
    TAG = "apks"
    _existing_assets: Optional[Set[str]] = None

    @classmethod
    def ensure_release(cls) -> bool:
        check = subprocess.run(
            ["gh", "release", "view", cls.TAG],
            cwd=Config.BASE_DIR,
            capture_output=True,
            text=True
        )
        if check.returncode != 0:
            res = subprocess.run(
                [
                    "gh", "release", "create", cls.TAG,
                    "--title", "Hosted APK Binaries",
                    "--notes", "Autonomous APK releases for InfinityFree hosted domains"
                ],
                cwd=Config.BASE_DIR,
                capture_output=True,
                text=True
            )
            return res.returncode == 0
        return True

    @classmethod
    def get_existing_assets(cls, force_refresh: bool = False) -> Set[str]:
        if cls._existing_assets is not None and not force_refresh:
            return cls._existing_assets
        cls.ensure_release()
        res = subprocess.run(
            ["gh", "release", "view", cls.TAG, "--json", "assets"],
            cwd=Config.BASE_DIR,
            capture_output=True,
            text=True
        )
        cls._existing_assets = set()
        if res.returncode == 0:
            try:
                data = json.loads(res.stdout)
                cls._existing_assets = {a.get("name") for a in data.get("assets", []) if a.get("name")}
            except Exception:
                pass
        return cls._existing_assets

    @classmethod
    def get_download_url(cls, filename: str) -> str:
        return f"https://github.com/{Config.GITHUB_USER}/{Config.GITHUB_REPO}/releases/download/{cls.TAG}/{filename}"

    @classmethod
    def upload_apk(cls, apk_path: Path, force: bool = False) -> Optional[str]:
        apk_path = Path(apk_path)
        if not apk_path.exists():
            return None

        filename = apk_path.name
        existing = cls.get_existing_assets()

        if filename in existing and not force:
            return cls.get_download_url(filename)

        cls.ensure_release()
        res = subprocess.run(
            ["gh", "release", "upload", cls.TAG, str(apk_path), "--clobber"],
            cwd=Config.BASE_DIR,
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            if cls._existing_assets is not None:
                cls._existing_assets.add(filename)
            return cls.get_download_url(filename)
        return None

    @classmethod
    def upload_batch(cls, apk_paths: List[Path], force: bool = False) -> Dict[str, str]:
        results = {}
        for p in apk_paths:
            url = cls.upload_apk(p, force=force)
            if url:
                results[p.name] = url
        return results
