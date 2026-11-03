import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict
from agent.config import Config

class APKScanner:
    def __init__(self, dirs: List[Path] = None):
        self.dirs = dirs or [Config.WEB2APK_OUTPUT_DIR, Config.APK_TV_OUTPUT_DIR]

    @staticmethod
    def _parse_apk_filename(filename: str) -> Dict[str, str]:
        """Parses app name, version, and target device from common naming conventions."""
        base = filename[:-4] if filename.endswith(".apk") else filename

        # Target detection
        target = "Universal"
        if "android-tv" in base.lower() or "converted-tv" in base.lower():
            target = "Android TV"
        elif "smartphone" in base.lower() or "mobile" in base.lower():
            target = "Smartphone"
        elif "universal" in base.lower():
            target = "Universal"

        # Version regex e.g. -v1.0.0 or _7.0.9
        version_match = re.search(r"[-_]v?(\d+\.\d+(\.\d+)?)", base)
        version = version_match.group(1) if version_match else "1.0.0"

        # Extract app name by removing target and version tags
        cleaned = re.sub(r"[-_]v?\d+\.\d+(\.\d+)?.*", "", base)
        cleaned = re.sub(r"[-_](universal|android-tv|smartphone|converted-tv|converted-mobile)", "", cleaned, flags=re.I)
        app_name = cleaned.replace("_", " ").replace("-", " ").strip()
        if not app_name:
            app_name = base

        return {
            "app_name": app_name.title(),
            "version": version,
            "device_target": target
        }

    def scan_all_apks(self) -> List[Dict]:
        results = []
        for d in self.dirs:
            if not d.exists() or not d.is_dir():
                continue

            for file_path in d.glob("*.apk"):
                size_bytes = file_path.stat().st_size
                if size_bytes == 0:
                    continue  # Ignore empty files

                size_kb = round(size_bytes / 1024, 1)
                size_mb = round(size_bytes / (1024 * 1024), 2)
                parsed = self._parse_apk_filename(file_path.name)

                # Compute quick sha256
                hasher = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        hasher.update(chunk)
                checksum = hasher.hexdigest()

                # Check for companion metadata files
                base_stem = file_path.stem
                listing_md = file_path.parent / f"{base_stem}-AI-Store-Listing.md"
                audit_json = file_path.parent / f"{base_stem}-AI-TV-Audit.json"

                results.append({
                    "filename": file_path.name,
                    "filepath": str(file_path),
                    "directory": str(d),
                    "size_bytes": size_bytes,
                    "size_kb": size_kb,
                    "size_mb": size_mb,
                    "sha256": checksum,
                    "app_name": parsed["app_name"],
                    "version": parsed["version"],
                    "device_target": parsed["device_target"],
                    "has_store_listing": listing_md.exists(),
                    "has_audit": audit_json.exists()
                })

        return sorted(results, key=lambda x: x["app_name"])

    def find_metadata_for_app(self, keyword: str) -> Dict[str, str]:
        """Extracts purpose, tagline, highlights and package from companion store listings."""
        clean_kw = keyword.lower().replace(".", "").replace("-", "").replace("_", "")
        for d in self.dirs:
            if not d.exists():
                continue
            for md_file in d.glob("*Store-Listing*.md"):
                file_stem = md_file.stem.lower().replace(".", "").replace("-", "").replace("_", "")
                if clean_kw in file_stem or any(clean_kw in part for part in file_stem.split()):
                    try:
                        content = md_file.read_text(encoding="utf-8")
                        pkg_match = re.search(r"Package[:\*`\s]+([a-zA-Z0-9_\.]+)", content)
                        tagline_match = re.search(r"##\s*Short Tagline\s*>\s*(.+)", content)
                        highlights_match = re.findall(r"^-\s+(.+)$", content, re.MULTILINE)
                        
                        pkg = pkg_match.group(1).strip("`* ") if pkg_match else ""
                        tagline = tagline_match.group(1).strip() if tagline_match else ""
                        highlights = highlights_match[:4] if highlights_match else []

                        return {
                            "package": pkg,
                            "tagline": tagline,
                            "highlights": highlights,
                            "source_file": md_file.name
                        }
                    except Exception:
                        pass
        return {}
