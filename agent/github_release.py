import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from agent.config import Config

class GitHubReleaseManager:
    TAG = "apks"

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
    def upload_apk(cls, apk_path: Path) -> Optional[str]:
        apk_path = Path(apk_path)
        if not apk_path.exists():
            return None

        cls.ensure_release()
        res = subprocess.run(
            ["gh", "release", "upload", cls.TAG, str(apk_path), "--clobber"],
            cwd=Config.BASE_DIR,
            capture_output=True,
            text=True
        )

        filename = apk_path.name
        return f"https://github.com/{Config.GITHUB_USER}/{Config.GITHUB_REPO}/releases/download/{cls.TAG}/{filename}"

    @classmethod
    def upload_batch(cls, apk_paths: List[Path]) -> Dict[str, str]:
        results = {}
        for p in apk_paths:
            url = cls.upload_apk(p)
            if url:
                results[p.name] = url
        return results
