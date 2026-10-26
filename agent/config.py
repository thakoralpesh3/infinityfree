import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from project root
load_dotenv(BASE_DIR / ".env")

class Config:
    # InfinityFree FTP settings
    FTP_HOST = os.getenv("IF_FTP_HOST", "ftpupload.net")
    FTP_PORT = int(os.getenv("IF_FTP_PORT", 21))
    FTP_USER = os.getenv("IF_FTP_USER", "")
    FTP_PASS = os.getenv("IF_FTP_PASS", "")

    # InfinityFree Client Area
    CLIENT_EMAIL = os.getenv("IF_CLIENT_AREA_EMAIL", "")
    CLIENT_PASSWORD = os.getenv("IF_CLIENT_AREA_PASSWORD", "")

    # GitHub repository settings
    GITHUB_USER = os.getenv("GITHUB_USER", "thakoralpesh3")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "infinityfree")

    # Local paths
    BASE_DIR = BASE_DIR
    CONFIG_DIR = BASE_DIR / "config"
    DOMAINS_FILE = CONFIG_DIR / "domains.json"
    DOMAINS_MD = BASE_DIR / "DOMAINS.md"
    README_MD = BASE_DIR / "README.md"
    CONVERSATION_DIR = BASE_DIR / "conversation"
    ARTIFACTS_DIR = BASE_DIR / "artifacts"
    
    # APK storage directories
    WEB2APK_OUTPUT_DIR = Path(os.getenv("WEB2APK_OUTPUT_DIR", "/home/alpesh/Web2APK_Output"))
    APK_TV_OUTPUT_DIR = Path(os.getenv("APK_TV_OUTPUT_DIR", "/home/alpesh/APK_TV_Converter_Output"))

    @classmethod
    def is_ftp_configured(cls) -> bool:
        return bool(cls.FTP_USER and cls.FTP_PASS and cls.FTP_HOST)

    @classmethod
    def get_summary(cls) -> dict:
        return {
            "ftp_host": cls.FTP_HOST,
            "ftp_port": cls.FTP_PORT,
            "ftp_user_configured": bool(cls.FTP_USER),
            "github_target": f"{cls.GITHUB_USER}/{cls.GITHUB_REPO}",
            "web2apk_dir_exists": cls.WEB2APK_OUTPUT_DIR.exists(),
            "apk_tv_dir_exists": cls.APK_TV_OUTPUT_DIR.exists(),
        }
