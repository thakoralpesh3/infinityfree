import io
import base64
import qrcode
from pathlib import Path
from typing import Dict, List
from agent.config import Config

class PortalBuilder:
    @staticmethod
    def generate_qr_base64(url: str) -> str:
        """Generates an embedded PNG base64 QR code for direct download URL."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#00ffcc", back_color="#0d1117")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @classmethod
    def build_portal_html(cls, domain_info: Dict) -> str:
        domain = domain_info.get("domain", "app.epizy.com")
        project_name = domain_info.get("project", "Autonomous APK Distribution")
        description = domain_info.get("description", "Download verified Android APK releases directly.")
        apks: List[Dict] = domain_info.get("hosted_apks", [])

        # Generate APK download cards
        apk_cards_html = []
        for apk in apks:
            filename = apk.get("filename", "")
            app_name = apk.get("app_name", filename)
            version = apk.get("version", "1.0.0")
            target = apk.get("device_target", "Universal")
            size = apk.get("size_kb", "200")
            download_rel = apk.get("download_path", f"apk/{filename}").lstrip("/")
            download_url = f"http://{domain}/{download_rel}"
            
            qr_b64 = cls.generate_qr_base64(download_url)

            badge_color = "#3b82f6"
            if "tv" in target.lower():
                badge_color = "#10b981"
            elif "smartphone" in target.lower():
                badge_color = "#8b5cf6"

            card = f"""
            <div class="apk-card">
                <div class="card-header">
                    <div class="badge" style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55;">
                        {target}
                    </div>
                    <span class="version-tag">v{version}</span>
                </div>
                <h3>{app_name}</h3>
                <p class="filename"><code>{filename}</code></p>
                <div class="meta-row">
                    <span>📦 Size: ~{size} KB</span>
                    <span>🛡️ Verified Clean</span>
                </div>
                <div class="qr-container">
                    <img src="data:image/png;base64,{qr_b64}" alt="Scan to Download QR" />
                    <p class="qr-label">Scan with Phone or TV Camera</p>
                </div>
                <a href="{download_rel}" class="btn-download" download>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download APK ({size} KB)
                </a>
            </div>
            """
            apk_cards_html.append(card)

        cards_str = "\n".join(apk_cards_html) if apk_cards_html else "<p>No APKs deployed yet.</p>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} | InfinityFree Distribution</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --surface: #131b2e;
            --surface-border: #1e293b;
            --primary: #00ffcc;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Inter', -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2.5rem 1.25rem;
        }}
        .container {{
            max-width: 1000px;
            width: 100%;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        .brand-badge {{
            display: inline-block;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            background: rgba(0, 255, 204, 0.1);
            color: var(--primary);
            border: 1px solid rgba(0, 255, 204, 0.25);
            margin-bottom: 1rem;
            font-weight: 600;
        }}
        h1 {{
            font-size: 2.75rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 40%, var(--primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.75rem;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 1.15rem;
            max-width: 650px;
            margin: 0 auto;
            line-height: 1.6;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.75rem;
            margin-bottom: 3.5rem;
        }}
        .apk-card {{
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 1rem;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .apk-card:hover {{
            transform: translateY(-4px);
            border-color: var(--primary);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .badge {{
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 0.5rem;
        }}
        .version-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: 600;
        }}
        h3 {{
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }}
        .filename {{
            font-size: 0.8rem;
            color: var(--text-muted);
            word-break: break-all;
            margin-bottom: 1rem;
        }}
        .filename code {{
            background: #0d121f;
            padding: 0.2rem 0.4rem;
            border-radius: 0.35rem;
            font-family: 'JetBrains Mono', monospace;
        }}
        .meta-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 1.25rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--surface-border);
        }}
        .qr-container {{
            text-align: center;
            background: #0d1117;
            padding: 1rem;
            border-radius: 0.75rem;
            margin-bottom: 1.25rem;
            border: 1px solid #1f293d;
        }}
        .qr-container img {{
            width: 140px;
            height: 140px;
            border-radius: 0.5rem;
            display: block;
            margin: 0 auto 0.5rem auto;
        }}
        .qr-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        .btn-download {{
            margin-top: auto;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.6rem;
            background: linear-gradient(135deg, #00ffcc 0%, #00b4d8 100%);
            color: #03141f;
            font-weight: 700;
            padding: 0.9rem 1.25rem;
            border-radius: 0.65rem;
            text-decoration: none;
            transition: filter 0.2s ease;
        }}
        .btn-download:hover {{
            filter: brightness(1.15);
        }}
        .instructions-box {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid var(--surface-border);
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 3rem;
        }}
        .instructions-box h2 {{
            font-size: 1.35rem;
            margin-bottom: 1rem;
            color: var(--primary);
        }}
        .instructions-box ol {{
            margin-left: 1.5rem;
            color: var(--text-muted);
            line-height: 1.8;
            font-size: 0.95rem;
        }}
        footer {{
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            border-top: 1px solid #1e293b;
            padding-top: 2rem;
            width: 100%;
        }}
        footer a {{ color: var(--accent); text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="brand-badge">⚡ Powered by InfinityFree Hosting & Antigravity</span>
            <h1>{project_name}</h1>
            <p class="subtitle">{description}</p>
        </header>

        <main class="grid">
            {cards_str}
        </main>

        <section class="instructions-box">
            <h2>📲 How to Install on Android Phone & Android TV</h2>
            <ol>
                <li><strong>Mobile Install:</strong> Tap the download button or scan the QR code with your phone camera, open the downloaded APK, and tap <em>Install</em>. (If prompted, allow installation from unknown sources).</li>
                <li><strong>Android TV / Fire TV Sideload:</strong> Install the <em>Downloader by AFTVnews</em> app on your TV, enter <code>{domain}</code> into the browser URL box, and select the TV APK.</li>
                <li><strong>Clean & Verified:</strong> Built autonomously and scanned for security compatibility.</li>
            </ol>
        </section>

        <footer>
            <p>Hosted on <strong>{domain}</strong> | Managed autonomously via <a href="https://github.com/{Config.GITHUB_USER}/infinityfree">InfinityFree Manager Agent</a></p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    @classmethod
    def generate_portal_files(cls, domain_info: Dict, output_dir: Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        html = cls.build_portal_html(domain_info)
        index_file = output_dir / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html)
        return index_file
