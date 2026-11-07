import os
import sys
import subprocess
from pathlib import Path
from tabulate import tabulate
from agent.config import Config
from agent.catalog import DomainCatalog
from agent.apk_scanner import APKScanner
from agent.ftp_client import InfinityFreeFTP
from agent.portal_builder import PortalBuilder
from agent.health_checker import DomainHealthChecker
from agent.markdown_generator import MarkdownGenerator
from agent.github_release import GitHubReleaseManager

class InteractiveUI:
    C_RESET = "\033[0m"
    C_BOLD = "\033[1m"
    C_CYAN = "\033[36m"
    C_GREEN = "\033[32m"
    C_YELLOW = "\033[33m"
    C_RED = "\033[31m"
    C_BLUE = "\033[34m"
    C_DIM = "\033[2m"

    @classmethod
    def show_header(cls):
        catalog = DomainCatalog()
        domains = catalog.list_all()
        scanner = APKScanner()
        apks = scanner.scan_all_apks()
        gh_assets = GitHubReleaseManager.get_existing_assets()
        ftp = InfinityFreeFTP()

        ftp_status = f"{cls.C_GREEN}✓ Configured{cls.C_RESET}" if ftp.is_configured() else f"{cls.C_YELLOW}⚠ Missing .env{cls.C_RESET}"
        
        try:
            svc_res = subprocess.run(["systemctl", "--user", "is-active", "infinityfree-sync.service"], capture_output=True, text=True)
            svc_active = svc_res.stdout.strip() == "active"
            sync_badge = f"{cls.C_GREEN}✓ Active (Daemon Running){cls.C_RESET}" if svc_active else f"{cls.C_DIM}Inactive{cls.C_RESET}"
        except Exception:
            sync_badge = "N/A"

        print(f"\n{cls.C_BOLD}{cls.C_CYAN}════════════════════════════════════════════════════════════════════{cls.C_RESET}")
        print(f"{cls.C_BOLD}  🚀 INFINITYFREE ACCOUNT & DOMAIN MANAGER (INTERACTIVE DASHBOARD)  {cls.C_RESET}")
        print(f"{cls.C_CYAN}════════════════════════════════════════════════════════════════════{cls.C_RESET}")
        print(f"  {cls.C_BOLD}GitHub Target:{cls.C_RESET}     {Config.GITHUB_USER}/{Config.GITHUB_REPO}")
        print(f"  {cls.C_BOLD}Active Domains:{cls.C_RESET}    {len(domains)} domain(s)")
        print(f"  {cls.C_BOLD}Local APKs:{cls.C_RESET}        {len(apks)} builds (Cached)")
        print(f"  {cls.C_BOLD}GitHub CDN Assets:{cls.C_RESET} {len(gh_assets)} releases (tag: {GitHubReleaseManager.TAG})")
        print(f"  {cls.C_BOLD}FTP Connection:{cls.C_RESET}    {Config.FTP_HOST}:{Config.FTP_PORT} [{ftp_status}]")
        print(f"  {cls.C_BOLD}Auto-Sync Service:{cls.C_RESET} {sync_badge}")
        print(f"{cls.C_CYAN}────────────────────────────────────────────────────────────────────{cls.C_RESET}\n")

    @classmethod
    def print_menu(cls):
        print(f"{cls.C_BOLD}Select an action:{cls.C_RESET}")
        print(f"  {cls.C_CYAN}[1]{cls.C_RESET} 🌐 List & Inspect Registered Domains")
        print(f"  {cls.C_CYAN}[2]{cls.C_RESET} ⚡ Quick-Sync Domain (Introspect metadata, upload APKs to GitHub CDN, build portal)")
        print(f"  {cls.C_CYAN}[3]{cls.C_RESET} 📦 Scan & Upload APKs to GitHub Releases")
        print(f"  {cls.C_CYAN}[4]{cls.C_RESET} 🩺 Run Live Health Check (DNS, HTTP & Latency)")
        print(f"  {cls.C_CYAN}[5]{cls.C_RESET} 🎨 Preview & Build HTML Download Portal")
        print(f"  {cls.C_CYAN}[6]{cls.C_RESET} ➕ Register New Domain / Subdomain")
        print(f"  {cls.C_CYAN}[7]{cls.C_RESET} 🔌 Test InfinityFree FTP Connection")
        print(f"  {cls.C_CYAN}[8]{cls.C_RESET} 🚀 Deploy Portal to InfinityFree Host")
        print(f"  {cls.C_CYAN}[9]{cls.C_RESET} 🔄 Trigger GitHub Sync & DOMAINS.md Update")
        print(f"  {cls.C_RED}[0]{cls.C_RESET} 🚪 Exit\n")

    @classmethod
    def action_list_domains(cls):
        catalog = DomainCatalog()
        domains = catalog.list_all()
        if not domains:
            print(f"{cls.C_YELLOW}No domains registered yet.{cls.C_RESET}")
            return
        table_data = []
        for d in domains:
            table_data.append([
                d.get("domain"),
                d.get("status", "active"),
                d.get("project", "N/A"),
                len(d.get("hosted_apks", [])),
                d.get("target_dir", "htdocs")
            ])
        print("\n" + tabulate(table_data, headers=["Domain", "Status", "Project", "Hosted APKs", "FTP Target"], tablefmt="fancy_grid") + "\n")

    @classmethod
    def action_sync_domain(cls):
        catalog = DomainCatalog()
        domains = catalog.list_all()
        default_dom = domains[0]["domain"] if domains else "openworld4all.gt.tc"
        user_in = input(f"Enter domain to sync [{default_dom}]: ").strip()
        domain = user_in if user_in else default_dom

        from agent.cli import cmd_sync_domain
        import argparse
        args = argparse.Namespace(domain=domain, project=None, description=None)
        cmd_sync_domain(args)

    @classmethod
    def action_scan_upload_apks(cls):
        from agent.cli import cmd_upload_github_apks
        import argparse
        args = argparse.Namespace(domain=None)
        cmd_upload_github_apks(args)

    @classmethod
    def action_health_check(cls):
        from agent.cli import cmd_health_check
        import argparse
        sync = input("Sync health results to DOMAINS.md? (Y/n): ").strip().lower() != "n"
        args = argparse.Namespace(sync=sync)
        cmd_health_check(args)

    @classmethod
    def action_build_portal(cls):
        catalog = DomainCatalog()
        domains = catalog.list_all()
        default_dom = domains[0]["domain"] if domains else "openworld4all.gt.tc"
        user_in = input(f"Domain to build portal for [{default_dom}]: ").strip()
        domain = user_in if user_in else default_dom
        from agent.cli import cmd_build_portal
        import argparse
        cmd_build_portal(argparse.Namespace(domain=domain))

    @classmethod
    def action_add_domain(cls):
        domain = input("Enter new domain / subdomain (e.g. app.epizy.com): ").strip()
        if not domain:
            print(f"{cls.C_RED}Domain name cannot be empty.{cls.C_RESET}")
            return
        project = input(f"Project name [Web Application]: ").strip() or "Web Application"
        desc = input(f"Description: ").strip() or f"Landing portal and APK distribution for {domain}"
        from agent.cli import cmd_add_domain
        import argparse
        cmd_add_domain(argparse.Namespace(domain=domain, project=project, repo=None, description=desc, target_dir="htdocs"))

    @classmethod
    def action_test_ftp(cls):
        ftp = InfinityFreeFTP()
        print(f"\nTesting FTP connection to {ftp.host}:{ftp.port}...")
        ok, msg = ftp.test_connection()
        if ok:
            print(f"{cls.C_GREEN}✓ {msg}{cls.C_RESET}\n")
        else:
            print(f"{cls.C_RED}✗ {msg}{cls.C_RESET}\n")

    @classmethod
    def action_deploy(cls):
        catalog = DomainCatalog()
        domains = catalog.list_all()
        default_dom = domains[0]["domain"] if domains else "openworld4all.gt.tc"
        user_in = input(f"Domain to deploy [{default_dom}]: ").strip()
        domain = user_in if user_in else default_dom
        up_apks = input("Upload local APKs directly to FTP? (Not recommended if files >10MB) (y/N): ").strip().lower() == "y"
        from agent.cli import cmd_deploy
        import argparse
        cmd_deploy(argparse.Namespace(domain=domain, upload_apks=up_apks))

    @classmethod
    def action_sync_github(cls):
        from agent.cli import cmd_sync_github
        import argparse
        cmd_sync_github(argparse.Namespace())

        try:
            from sync.sync_daemon import sync_cycle
            pushed = sync_cycle()
            if pushed:
                print(f"{cls.C_GREEN}✓ Git commit and push completed successfully!{cls.C_RESET}")
            else:
                print(f"{cls.C_DIM}Everything already up to date on GitHub.{cls.C_RESET}")
        except Exception as e:
            print(f"{cls.C_YELLOW}Sync cycle note: {e}{cls.C_RESET}")

def run_interactive_menu():
    while True:
        try:
            InteractiveUI.show_header()
            InteractiveUI.print_menu()
            choice = input("Enter option (0-9): ").strip()
            
            if choice == "0":
                print("\nGoodbye! 👋\n")
                break
            elif choice == "1":
                InteractiveUI.action_list_domains()
            elif choice == "2":
                InteractiveUI.action_sync_domain()
            elif choice == "3":
                InteractiveUI.action_scan_upload_apks()
            elif choice == "4":
                InteractiveUI.action_health_check()
            elif choice == "5":
                InteractiveUI.action_build_portal()
            elif choice == "6":
                InteractiveUI.action_add_domain()
            elif choice == "7":
                InteractiveUI.action_test_ftp()
            elif choice == "8":
                InteractiveUI.action_deploy()
            elif choice == "9":
                InteractiveUI.action_sync_github()
            else:
                print(f"\033[31mInvalid option '{choice}'. Please select 0 to 9.\033[0m")
            
            input("\nPress Enter to return to menu...")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting interactive mode. Goodbye! 👋\n")
            break
