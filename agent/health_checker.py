import socket
import requests
from typing import Dict, List
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

        if dns_ok:
            # Check HTTP
            try:
                res = requests.get(f"http://{domain}", timeout=5, headers={"User-Agent": "Mozilla/5.0 InfinityFreeAgent"})
                http_status = res.status_code
                response_time_ms = int(res.elapsed.total_seconds() * 1000)
            except Exception:
                http_status = "Connection Error"

            # Check HTTPS
            try:
                res_ssl = requests.get(f"https://{domain}", timeout=5, verify=False, headers={"User-Agent": "Mozilla/5.0 InfinityFreeAgent"})
                https_status = res_ssl.status_code
            except Exception:
                https_status = "No SSL / Error"

            # Check hosted APK availability
            for apk in domain_info.get("hosted_apks", []):
                rel = apk.get("download_path", "").lstrip("/")
                if rel:
                    apk_url = f"http://{domain}/{rel}"
                    try:
                        head = requests.head(apk_url, timeout=4, allow_redirects=True)
                        apk_checks.append({
                            "filename": apk.get("filename"),
                            "status_code": head.status_code,
                            "accessible": head.status_code == 200
                        })
                    except Exception:
                        apk_checks.append({
                            "filename": apk.get("filename"),
                            "status_code": "Unreachable",
                            "accessible": False
                        })

        status_label = "Online" if (http_status == 200 or (isinstance(http_status, int) and http_status < 400)) else ("DNS Resolving" if dns_ok else "Offline / Not Propagated")

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
        for d in domains:
            results.append(cls.check_domain(d))
        return results
