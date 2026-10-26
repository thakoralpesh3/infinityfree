import os
import ftplib
import ssl
from pathlib import Path
from typing import Tuple, List, Optional
from agent.config import Config

class InfinityFreeFTP:
    def __init__(self, host: str = None, user: str = None, password: str = None, port: int = 21):
        self.host = host or Config.FTP_HOST
        self.user = user or Config.FTP_USER
        self.password = password or Config.FTP_PASS
        self.port = port or Config.FTP_PORT

    def is_configured(self) -> bool:
        return bool(self.host and self.user and self.password)

    def _connect(self) -> ftplib.FTP:
        if not self.is_configured():
            raise ValueError(
                "InfinityFree FTP credentials are not configured. "
                "Please configure IF_FTP_USER and IF_FTP_PASS in your .env file."
            )

        try:
            # Try FTPS (TLS) first
            ftps = ftplib.FTP_TLS(timeout=30)
            ftps.connect(self.host, self.port)
            ftps.login(self.user, self.password)
            ftps.prot_p()  # Secure data connection
            return ftps
        except Exception:
            # Fallback to plain FTP
            ftp = ftplib.FTP(timeout=30)
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.password)
            return ftp

    def test_connection(self) -> Tuple[bool, str]:
        if not self.is_configured():
            return False, "FTP credentials missing (IF_FTP_USER / IF_FTP_PASS not set in .env)"
        try:
            ftp = self._connect()
            welcome = ftp.getwelcome()
            ftp.quit()
            return True, f"Successfully connected to {self.host} ({welcome.strip()})"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def list_dir(self, remote_dir: str = "/") -> List[str]:
        ftp = self._connect()
        try:
            ftp.cwd(remote_dir)
            files = ftp.nlst()
            return files
        finally:
            ftp.quit()

    def ensure_dir(self, remote_path: str) -> None:
        """Recursively ensures remote directories exist."""
        ftp = self._connect()
        try:
            parts = [p for p in remote_path.strip("/").split("/") if p]
            current = ""
            for part in parts:
                current += f"/{part}"
                try:
                    ftp.cwd(current)
                except ftplib.error_perm:
                    try:
                        ftp.mkd(current)
                        ftp.cwd(current)
                    except Exception as e:
                        pass
        finally:
            ftp.quit()

    def upload_file(self, local_path: Path, remote_dest_path: str) -> bool:
        """Uploads a local file to remote_dest_path (full remote path including filename)."""
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        parent_dir = str(Path(remote_dest_path).parent).replace("\\", "/")
        self.ensure_dir(parent_dir)

        ftp = self._connect()
        try:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_dest_path}", f, blocksize=65536)
            return True
        finally:
            ftp.quit()

    def setup_apk_htaccess(self, target_htdocs: str = "htdocs") -> bool:
        """Uploads or updates .htaccess in target htdocs to support APK downloads."""
        htaccess_content = (
            "# InfinityFree APK & Portal Configuration\n"
            "AddType application/vnd.android.package-archive .apk\n"
            "AddType application/octet-stream .ipa\n"
            "Options -Indexes\n"
            "<FilesMatch \"\\.(apk|ipa)$\">\n"
            "    Header set Content-Disposition \"attachment\"\n"
            "</FilesMatch>\n"
        )
        temp_file = Config.BASE_DIR / "staging" / ".htaccess"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(htaccess_content)

        remote_path = f"/{target_htdocs.strip('/')}/.htaccess"
        return self.upload_file(temp_file, remote_path)
