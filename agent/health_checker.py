import socket
import requests
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DomainHealthChecker:
    @staticmethod
    def check_dns(domain: str) -> bool:
        try:
            socket.gethostbyname(domain)
            return True
        except (socket.gaierror, socket.herror):
            return False

    @classmethod
    def check_domain(cls, domain_info: Dict) -> Dict:
        domain = domain_info.get("domain", "")
        dns_ok = cls.check_dns(domain)
        
        http_status = None
        https_status = None
        response_time_ms = None
        apk_checks = []
        is_unassigned = False

        if dns_ok:
            # Check HTTP
            try:
                res = requests.get(f"http://{domain}", timeout=4, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                http_status = res.status_code
                response_time_ms = int(res.elapsed.total_seconds() * 1000)
                body_lower = res.text.lower()
                if "domain not found" in body_lower or "not added to hosting account" in body_lower or "dns resolution error" in body_lower:
                    is_unassigned = True
            except Exception:
                http_status = "Connection Error"

            # Check HTTPS
            try:
                res_ssl = requests.get(f"https://{domain}", timeout=4, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                https_status = res_ssl.status_code
            except Exception:
                https_status = "No SSL / Error"

            # Check hosted APK availability
            for apk in domain_info.get("hosted_apks", []):
                rel = apk.get("download_path", "").lstrip("/")
                if rel:
                    apk_url = f"http://{domain}/{rel}"
                    try:
                        head = requests.head(apk_url, timeout=3, allow_redirects=True)
                        apk_checks.append({
                            "filename": apk.get("filename"),
                            "status_code": head.status_code,
                            "accessible": head.status_code == 200 and not is_unassigned
                        })
                    except Exception:
                        apk_checks.append({
                            "filename": apk.get("filename"),
                            "status_code": "Unreachable",
                            "accessible": False
                        })

        if is_unassigned:
            status_label = "Domain Not In Account"
        elif http_status == 200 or (isinstance(http_status, int) and http_status < 400):
            status_label = "Online"
        elif dns_ok:
            status_label = "DNS Resolving"
        else:
            status_label = "Offline / Not Propagated"

        return {
            "domain": domain,
            "dns_resolved": dns_ok,
            "http_status": http_status,
            "https_status": https_status,
            "response_time_ms": response_time_ms,
            "status_label": status_label,
            "apk_checks": apk_checks
        }

    @classmethod
    def check_all(cls, domains: List[Dict]) -> List[Dict]:
        results = []
        with ThreadPoolExecutor(max_workers=min(len(domains), 8) or 1) as executor:
            future_to_domain = {executor.submit(cls.check_domain, d): d for d in domains}
            for future in as_completed(future_to_domain):
                try:
                    results.append(future.result())
                except Exception as e:
                    d = future_to_domain[future]
                    results.append({
                        "domain": d.get("domain", ""),
                        "dns_resolved": False,
                        "http_status": f"Error: {e}",
                        "https_status": "N/A",
                        "response_time_ms": None,
                        "status_label": "Check Failed",
                        "apk_checks": []
                    })
        return sorted(results, key=lambda x: x["domain"])

