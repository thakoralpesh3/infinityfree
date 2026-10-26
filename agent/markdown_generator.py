from datetime import datetime
from typing import List, Dict
from pathlib import Path
from agent.config import Config

class MarkdownGenerator:
    @staticmethod
    def generate_domains_markdown(domains: List[Dict], health_data: Dict[str, Dict] = None) -> str:
        health_data = health_data or {}
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_domains = len(domains)
        total_apks = sum(len(d.get("hosted_apks", [])) for d in domains)

        md = [
            "# 🌐 InfinityFree Hosted Domains & APK Work Catalog",
            "",
            "> Real-time showcase of all InfinityFree domains and subdomains managed autonomously, mapping each domain to its live web application, download portal, and hosted Android/TV APK releases.",
            "",
            f"**Last Synchronized**: `{now_str}` | **Total Domains**: `{total_domains}` | **Total Hosted APKs**: `{total_apks}`",
            "",
            "---",
            "",
            "## 📊 Domain & APK Showcase Matrix",
            "",
            "| Domain / URL | Associated Work / Project | Target Architecture | Hosted APK(s) | Status |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        for d in domains:
            domain = d.get("domain", "")
            url = f"http://{domain}"
            project = d.get("project", "General Hosting")
            repo = d.get("github_repo", "")
            repo_link = f"[{project}](https://github.com/{repo})" if repo else project

            h = health_data.get(domain, {})
            status_label = h.get("status_label", d.get("status", "Active"))
            if "Online" in status_label:
                badge = f"🟢 `{status_label}`"
            elif "Resolving" in status_label:
                badge = f"🟡 `{status_label}`"
            else:
                badge = f"⚪ `{status_label}`"

            apks = d.get("hosted_apks", [])
            if apks:
                apk_entries = []
                targets = set()
                for a in apks:
                    fn = a.get("filename", "")
                    rel = a.get("download_path", f"apk/{fn}").lstrip("/")
                    size = a.get("size_kb", "")
                    size_str = f" ({size} KB)" if size else ""
                    dl_url = f"{url}/{rel}"
                    apk_entries.append(f"[`{fn}`]({dl_url}){size_str}")
                    targets.add(a.get("device_target", "Universal"))
                
                apks_col = "<br>".join(apk_entries)
                target_col = ", ".join(sorted(targets))
            else:
                apks_col = "*No APKs registered*"
                target_col = "Web / Static"

            md.append(f"| **[{domain}]({url})** | {repo_link} | {target_col} | {apks_col} | {badge} |")

        md.extend([
            "",
            "---",
            "",
            "## 📱 Deep Dive: Hosted Work & Download Portals",
            ""
        ])

        for d in domains:
            domain = d.get("domain", "")
            url = f"http://{domain}"
            project = d.get("project", "")
            desc = d.get("description", "")
            repo = d.get("github_repo", "")

            md.extend([
                f"### 🚀 [{domain}]({url}) - {project}",
                f"- **Live Portal URL**: [{url}]({url})",
                f"- **GitHub Repository**: [`{repo}`](https://github.com/{repo})" if repo else "",
                f"- **Description**: {desc}",
                f"- **Remote FTP Target**: `/{d.get('target_dir', 'htdocs')}`",
                "",
                "**Hosted APK Distribution:**",
                ""
            ])

            apks = d.get("hosted_apks", [])
            if apks:
                md.append("| APK File | App Name | Version | Target Device | Direct Download |")
                md.append("| :--- | :--- | :--- | :--- | :--- |")
                for a in apks:
                    fn = a.get("filename", "")
                    name = a.get("app_name", fn)
                    ver = a.get("version", "1.0.0")
                    dev = a.get("device_target", "Universal")
                    rel = a.get("download_path", f"apk/{fn}").lstrip("/")
                    dl_url = f"{url}/{rel}"
                    md.append(f"| `{fn}` | **{name}** | `v{ver}` | {dev} | [⬇️ Download APK]({dl_url}) |")
            else:
                md.append("*No APK releases deployed yet.*")

            md.append("")

        md.extend([
            "---",
            "",
            "## 🤖 How This Agent Works",
            "",
            "1. **Catalog Management**: Maintains `config/domains.json` mapping InfinityFree hosting to projects.",
            "2. **Automatic APK Discovery**: Scans local build folders (`Web2APK_Output` and `APK_TV_Converter_Output`) and matches packages.",
            "3. **Zero-Configuration Landing Pages**: Automatically generates HTML5 download portals with embedded QR codes and APK download links.",
            "4. **Continuous GitHub Sync**: Automatically pushes changes, transcripts, and status tables back to GitHub.",
            ""
        ])

        return "\n".join(md)

    @classmethod
    def write_domains_md(cls, domains: List[Dict], health_data: Dict[str, Dict] = None) -> Path:
        content = cls.generate_domains_markdown(domains, health_data)
        out_path = Config.DOMAINS_MD
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        return out_path
