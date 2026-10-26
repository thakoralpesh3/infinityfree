import sys
import argparse
import json
from pathlib import Path
from tabulate import tabulate
from agent.config import Config
from agent.catalog import DomainCatalog
from agent.apk_scanner import APKScanner
from agent.ftp_client import InfinityFreeFTP
from agent.portal_builder import PortalBuilder
from agent.health_checker import DomainHealthChecker
from agent.markdown_generator import MarkdownGenerator

def cmd_status(args):
    print("\n--- InfinityFree Manager Agent Status ---")
    summary = Config.get_summary()
    print(f"GitHub Repository: {summary['github_target']}")
    print(f"FTP Host:          {summary['ftp_host']}:{summary['ftp_port']}")
    print(f"FTP Configured:    {'✓ Yes' if summary['ftp_user_configured'] else '✗ No (Set IF_FTP_USER and IF_FTP_PASS in .env)'}")
    print(f"Web2APK Output:    {'✓ Found' if summary['web2apk_dir_exists'] else '✗ Missing'} ({Config.WEB2APK_OUTPUT_DIR})")
    print(f"APK TV Output:     {'✓ Found' if summary['apk_tv_dir_exists'] else '✗ Missing'} ({Config.APK_TV_OUTPUT_DIR})")
    
    catalog = DomainCatalog()
    domains = catalog.list_all()
    total_apks = sum(len(d.get("hosted_apks", [])) for d in domains)
    print(f"Active Domains:    {len(domains)}")
    print(f"Total Hosted APKs: {total_apks}\n")

def cmd_list_domains(args):
    catalog = DomainCatalog()
    domains = catalog.list_all()
    if not domains:
        print("No domains configured in catalog yet. Use 'add-domain' to register one.")
        return

    table_data = []
    for d in domains:
        apks_count = len(d.get("hosted_apks", []))
        table_data.append([
            d.get("domain"),
            d.get("status", "configured"),
            d.get("project", "General"),
            d.get("github_repo", ""),
            apks_count,
            d.get("target_dir", "htdocs")
        ])

    headers = ["Domain / Subdomain", "Status", "Project / Work", "GitHub Repo", "APKs", "FTP Target"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid") + "\n")

def cmd_add_domain(args):
    catalog = DomainCatalog()
    domain_data = {
        "domain": args.domain,
        "project": args.project or "Android Web Application",
        "github_repo": args.repo or f"{Config.GITHUB_USER}/infinityfree",
        "description": args.description or f"Official landing portal and APK distribution for {args.domain}",
        "target_dir": args.target_dir or "htdocs"
    }
    try:
        res = catalog.add(domain_data)
        print(f"✓ Domain '{res['domain']}' successfully added to catalog.")
        # Regenerate DOMAINS.md
        MarkdownGenerator.write_domains_md(catalog.list_all())
    except Exception as e:
        print(f"Error adding domain: {e}")

def cmd_remove_domain(args):
    catalog = DomainCatalog()
    if catalog.remove(args.domain):
        print(f"✓ Domain '{args.domain}' removed from catalog.")
        MarkdownGenerator.write_domains_md(catalog.list_all())
    else:
        print(f"Domain '{args.domain}' not found.")

def cmd_scan_apks(args):
    scanner = APKScanner()
    apks = scanner.scan_all_apks()
    print(f"\n--- Discovered {len(apks)} Local APK Builds ---")
    table_data = []
    for a in apks:
        table_data.append([
            a["app_name"],
            a["version"],
            a["device_target"],
            f"{a['size_kb']} KB",
            a["filename"]
        ])
    headers = ["App Name", "Version", "Target", "Size", "Filename"]
    print(tabulate(table_data, headers=headers, tablefmt="simple") + "\n")

    if args.link:
        # Match APKs to catalog domains based on keyword
        catalog = DomainCatalog()
        domains = catalog.list_all()
        linked_count = 0
        for apk in apks:
            app_lower = apk["app_name"].lower().replace(" ", "")
            for d in domains:
                d_lower = d["domain"].lower()
                proj_lower = d.get("project", "").lower().replace(" ", "")
                if app_lower in d_lower or app_lower in proj_lower:
                    catalog.link_apk(d["domain"], {
                        "filename": apk["filename"],
                        "app_name": apk["app_name"],
                        "version": apk["version"],
                        "device_target": apk["device_target"],
                        "size_kb": apk["size_kb"],
                        "download_path": f"apk/{apk['filename']}"
                    })
                    linked_count += 1
                    print(f"Linked '{apk['filename']}' to domain '{d['domain']}'")
        print(f"Finished auto-linking: {linked_count} association(s) updated.")
        MarkdownGenerator.write_domains_md(catalog.list_all())

def cmd_build_portal(args):
    catalog = DomainCatalog()
    domain_info = catalog.get(args.domain)
    if not domain_info:
        print(f"Domain '{args.domain}' not found in catalog.")
        return

    output_dir = Config.BASE_DIR / "staging" / args.domain
    index_file = PortalBuilder.generate_portal_files(domain_info, output_dir)
    print(f"✓ Portal generated at: {index_file}")

def cmd_health_check(args):
    catalog = DomainCatalog()
    domains = catalog.list_all()
    print(f"\nChecking live connectivity for {len(domains)} domain(s)...")
    results = DomainHealthChecker.check_all(domains)

    table_data = []
    health_map = {}
    for r in results:
        health_map[r["domain"]] = r
        table_data.append([
            r["domain"],
            "✓ Yes" if r["dns_resolved"] else "✗ No",
            r["http_status"],
            r["https_status"],
            f"{r['response_time_ms']} ms" if r['response_time_ms'] else "N/A",
            r["status_label"]
        ])
    headers = ["Domain", "DNS", "HTTP", "HTTPS", "Response Time", "Status"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid") + "\n")

    if args.sync:
        MarkdownGenerator.write_domains_md(domains, health_map)
        print("✓ Updated DOMAINS.md with live health check data.")

def cmd_sync_github(args):
    catalog = DomainCatalog()
    domains = catalog.list_all()
    out_file = MarkdownGenerator.write_domains_md(domains)
    print(f"✓ Generated and updated {out_file}")

def cmd_deploy(args):
    catalog = DomainCatalog()
    domain_info = catalog.get(args.domain)
    if not domain_info:
        print(f"Domain '{args.domain}' not found in catalog.")
        return

    ftp = InfinityFreeFTP()
    if not ftp.is_configured():
        print("FTP is not configured. Please set IF_FTP_USER and IF_FTP_PASS in .env")
        return

    print(f"Connecting to InfinityFree FTP ({ftp.host})...")
    ok, msg = ftp.test_connection()
    if not ok:
        print(f"FTP connection failed: {msg}")
        return
    print(f"✓ {msg}")

    target_htdocs = domain_info.get("target_dir", "htdocs")
    print(f"Setting up .htaccess in /{target_htdocs}...")
    ftp.setup_apk_htaccess(target_htdocs)

    print("Building responsive HTML portal...")
    staging_dir = Config.BASE_DIR / "staging" / args.domain
    index_html = PortalBuilder.generate_portal_files(domain_info, staging_dir)

    print(f"Uploading index.html to /{target_htdocs}/index.html...")
    ftp.upload_file(index_html, f"/{target_htdocs}/index.html")
    print("✓ Landing portal uploaded.")

    # Upload hosted APKs if requested
    if args.upload_apks:
        scanner = APKScanner()
        all_apks = {a["filename"]: a for a in scanner.scan_all_apks()}
        for apk in domain_info.get("hosted_apks", []):
            fn = apk.get("filename")
            if fn in all_apks:
                local_path = Path(all_apks[fn]["filepath"])
                remote_apk_path = f"/{target_htdocs}/apk/{fn}"
                print(f"Uploading APK {fn} ({all_apks[fn]['size_kb']} KB) -> {remote_apk_path}...")
                ftp.upload_file(local_path, remote_apk_path)
                print(f"✓ Uploaded {fn}")
            else:
                print(f"⚠️ Local APK file not found for {fn}, skipping binary upload.")

    print(f"\n🎉 Deployment complete! Visit: http://{args.domain}")

def main():
    parser = argparse.ArgumentParser(description="InfinityFree Account & Domain Manager Agent")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # status
    subparsers.add_parser("status", help="Show configuration & catalog status")

    # list-domains
    subparsers.add_parser("list-domains", help="List all registered domains and hosted APKs")

    # add-domain
    p_add = subparsers.add_parser("add-domain", help="Register a new domain/subdomain")
    p_add.add_argument("domain", help="Domain or subdomain name (e.g. app.epizy.com)")
    p_add.add_argument("--project", help="Project / application name")
    p_add.add_argument("--repo", help="Associated GitHub repo")
    p_add.add_argument("--description", help="Short description")
    p_add.add_argument("--target-dir", default="htdocs", help="InfinityFree htdocs target directory")

    # remove-domain
    p_rem = subparsers.add_parser("remove-domain", help="Remove a domain from catalog")
    p_rem.add_argument("domain", help="Domain name or ID")

    # scan-apks
    p_scan = subparsers.add_parser("scan-apks", help="Scan local directories for APK builds")
    p_scan.add_argument("--link", action="store_true", help="Auto-link found APKs to domains")

    # build-portal
    p_build = subparsers.add_parser("build-portal", help="Generate HTML portal locally")
    p_build.add_argument("domain", help="Domain to build portal for")

    # health-check
    p_health = subparsers.add_parser("health-check", help="Check DNS & HTTP status of domains")
    p_health.add_argument("--sync", action="store_true", help="Update DOMAINS.md with results")

    # sync-github
    subparsers.add_parser("sync-github", help="Generate DOMAINS.md for GitHub")

    # deploy
    p_dep = subparsers.add_parser("deploy", help="Deploy portal and APKs to InfinityFree via FTP")
    p_dep.add_argument("domain", help="Domain to deploy to")
    p_dep.add_argument("--upload-apks", action="store_true", help="Upload APK binary files to remote host")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "status": cmd_status,
        "list-domains": cmd_list_domains,
        "add-domain": cmd_add_domain,
        "remove-domain": cmd_remove_domain,
        "scan-apks": cmd_scan_apks,
        "build-portal": cmd_build_portal,
        "health-check": cmd_health_check,
        "sync-github": cmd_sync_github,
        "deploy": cmd_deploy
    }

    func = dispatch.get(args.command)
    if func:
        func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
