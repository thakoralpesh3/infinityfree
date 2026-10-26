import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from agent.config import Config

class DomainCatalog:
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or Config.DOMAINS_FILE
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save([])

    def _load(self) -> List[Dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, domains: List[Dict]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(domains, f, indent=2)

    def list_all(self) -> List[Dict]:
        return self._load()

    def get(self, domain_or_id: str) -> Optional[Dict]:
        for d in self._load():
            if d.get("domain") == domain_or_id or d.get("id") == domain_or_id:
                return d
        return None

    def add(self, domain_data: Dict) -> Dict:
        domains = self._load()
        domain_name = domain_data.get("domain", "").strip()
        if not domain_name:
            raise ValueError("Domain name cannot be empty")

        for d in domains:
            if d.get("domain") == domain_name:
                raise ValueError(f"Domain '{domain_name}' already exists in catalog")

        item = {
            "id": domain_data.get("id") or domain_name.replace(".", "-"),
            "domain": domain_name,
            "url": f"http://{domain_name}",
            "ssl_url": f"https://{domain_name}",
            "account_id": domain_data.get("account_id", "default"),
            "target_dir": domain_data.get("target_dir", "htdocs"),
            "status": domain_data.get("status", "configured"),
            "project": domain_data.get("project", "Web Application"),
            "github_repo": domain_data.get("github_repo", f"{Config.GITHUB_USER}/infinityfree"),
            "work_type": domain_data.get("work_type", "apk_distribution"),
            "description": domain_data.get("description", "Hosted application portal"),
            "hosted_apks": domain_data.get("hosted_apks", []),
            "last_synced": datetime.now().isoformat()
        }
        domains.append(item)
        self._save(domains)
        return item

    def update(self, domain_or_id: str, updates: Dict) -> Optional[Dict]:
        domains = self._load()
        target = None
        for i, d in enumerate(domains):
            if d.get("domain") == domain_or_id or d.get("id") == domain_or_id:
                domains[i].update(updates)
                domains[i]["last_synced"] = datetime.now().isoformat()
                target = domains[i]
                break
        if target:
            self._save(domains)
        return target

    def remove(self, domain_or_id: str) -> bool:
        domains = self._load()
        initial_len = len(domains)
        domains = [d for d in domains if d.get("domain") != domain_or_id and d.get("id") != domain_or_id]
        if len(domains) < initial_len:
            self._save(domains)
            return True
        return False

    def link_apk(self, domain_or_id: str, apk_info: Dict) -> bool:
        domain = self.get(domain_or_id)
        if not domain:
            return False
        
        apks = domain.get("hosted_apks", [])
        # Check if already present by filename
        filename = apk_info.get("filename")
        existing_idx = next((i for i, a in enumerate(apks) if a.get("filename") == filename), None)
        if existing_idx is not None:
            apks[existing_idx].update(apk_info)
        else:
            apks.append(apk_info)

        self.update(domain_or_id, {"hosted_apks": apks})
        return True
