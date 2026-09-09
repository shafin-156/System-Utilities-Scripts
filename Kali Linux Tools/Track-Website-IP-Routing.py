#!/usr/bin/env python3
"""
Kali Linux traceroute + IP info script (no diagnostic timezone prints)

Filename format:
  hostName_DD-MM-YYYY_HH-MM-SS_tzname_offset.txt

Notes:
- Attempts to detect the OS timezone using timedatectl, /etc/timezone, /etc/localtime, TZ env, or astimezone.
- If a zone name is found, it sets TZ and calls time.tzset() so Python uses the same timezone as the OS.
- Each hop printed and saved as: IP (01) : x.x.x.x
- Requires: traceroute, requests (pip install requests). colorama optional (pip install colorama).
"""
from __future__ import annotations
import subprocess
import socket
import requests
import re
import os
import time
import filecmp
from datetime import datetime
from typing import Optional, Tuple

# Optional colorama
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except Exception:
    class _F:
        RED = ""
        GREEN = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
        YELLOW = ""
        BLUE = ""
    class _S:
        RESET_ALL = ""
        DIM = ""
    Fore = _F()
    Style = _S()

# Truecolor for IP label and pink for API label
GREEN_HEX = "\033[38;2;0;255;0m"
PINK_HEX = "\033[38;2;255;105;180m"
RESET = Style.RESET_ALL

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
FILENAME_SAFE_RE = re.compile(r'[<>:"/\\|?*\s]+')


def sanitize_hostname(name: str) -> str:
    name = name.replace("http://", "").replace("https://", "").split("/")[0]
    return FILENAME_SAFE_RE.sub('_', name)


def tz_from_timedatectl() -> Optional[str]:
    try:
        proc = subprocess.run(["timedatectl", "show", "-p", "Timezone", "--value"],
                              capture_output=True, text=True, timeout=2)
        tz = proc.stdout.strip()
        if tz:
            return tz
    except Exception:
        pass
    return None


def tz_from_etc_timezone() -> Optional[str]:
    try:
        path = "/etc/timezone"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                tz = fh.read().strip()
                if tz:
                    return tz
    except Exception:
        pass
    return None


def tz_from_localtime_symlink() -> Optional[str]:
    try:
        path = "/etc/localtime"
        if os.path.islink(path):
            target = os.readlink(path)
            if "zoneinfo" in target:
                tz = target.split("zoneinfo")[-1].lstrip("/\\")
                return tz
    except Exception:
        pass
    return None


def tz_from_localtime_filecmp() -> Optional[str]:
    try:
        local = "/etc/localtime"
        zoneinfo_dir = "/usr/share/zoneinfo"
        if os.path.exists(local) and os.path.isdir(zoneinfo_dir):
            for root, _, files in os.walk(zoneinfo_dir):
                for fn in files:
                    candidate = os.path.join(root, fn)
                    try:
                        if filecmp.cmp(local, candidate, shallow=False):
                            tz = os.path.relpath(candidate, zoneinfo_dir)
                            return tz
                    except Exception:
                        continue
    except Exception:
        pass
    return None


def detect_and_apply_system_timezone() -> Tuple[str, str, str]:
    """
    Detect system timezone name and apply it to the environment (TZ + time.tzset()).
    Returns (tzname_safe, offset_formatted, source).
    """
    tz_candidates = []

    tz = tz_from_timedatectl()
    if tz:
        tz_candidates.append(("timedatectl", tz))

    tz = tz_from_etc_timezone()
    if tz:
        tz_candidates.append(("/etc/timezone", tz))

    tz = tz_from_localtime_symlink()
    if tz:
        tz_candidates.append(("/etc/localtime-symlink", tz))

    tz = tz_from_localtime_filecmp()
    if tz:
        tz_candidates.append(("/etc/localtime-filecmp", tz))

    tz_env = os.environ.get("TZ")
    if tz_env:
        tz_candidates.append(("TZ_env", tz_env))

    for source, tzname in tz_candidates:
        try:
            os.environ['TZ'] = tzname
            try:
                time.tzset()
            except Exception:
                pass
            now = datetime.now().astimezone()
            offset = now.strftime("%z") or ""
            offset_formatted = offset[:3] + "-" + offset[3:] if offset and len(offset) == 5 else "UTC"
            tzname_safe = FILENAME_SAFE_RE.sub('_', tzname)
            return tzname_safe, offset_formatted, source
        except Exception:
            continue

    try:
        now = datetime.now().astimezone()
        tzname = now.tzname() or "local"
        offset = now.strftime("%z") or ""
        offset_formatted = offset[:3] + "-" + offset[3:] if offset and len(offset) == 5 else "UTC"
        tzname_safe = FILENAME_SAFE_RE.sub('_', tzname)
        return tzname_safe, offset_formatted, "astimezone-fallback"
    except Exception:
        return "local", "UTC", "unknown"


def run_traceroute(target: str) -> list[str]:
    print(Fore.CYAN + f"[+] Running traceroute for {target}...\n")
    try:
        proc = subprocess.run(["traceroute", "-n", target], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        print(Fore.RED + "[-] traceroute command not found. Install with: sudo apt install traceroute")
        return []
    except Exception as e:
        print(Fore.RED + f"[-] Error running traceroute: {e}")
        return []

    lines = proc.stdout.splitlines()
    ips: list[str] = []
    for line in lines[1:]:
        found = IPV4_RE.findall(line)
        for ip in found:
            if ip not in ips:
                ips.append(ip)
    return ips


def get_ip_info(ip: str) -> dict:
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=6)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_device_ip_local() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"


def get_public_ip() -> str:
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=6)
        if r.status_code == 200:
            return r.json().get("ip", "N/A")
    except Exception:
        return "N/A"


def main() -> None:
    target_input = input(Fore.YELLOW + "Enter website or link: " + Style.RESET_ALL).strip()
    if not target_input:
        print(Fore.RED + "[-] No target provided.")
        return

    hostname = sanitize_hostname(target_input)
    try:
        print(Fore.CYAN + f"[+] Resolving {hostname}...")
        target_ip = socket.gethostbyname(hostname)
        print(Fore.GREEN + f"[+] Target IP: {target_ip}")
    except Exception as e:
        print(Fore.RED + f"[-] Error resolving hostname: {e}")
        return

    device_ip_local = get_device_ip_local()
    device_ip_public = get_public_ip()
    print(Fore.RED + f"[+] Device IP (Local): {device_ip_local}")
    print(Fore.RED + f"[+] Device IP (Public): {device_ip_public}\n")

    # Detect and apply system timezone (this will set TZ and call time.tzset())
    tzname_safe, offset_formatted, _tz_source = detect_and_apply_system_timezone()

    # Build now using astimezone() so it reflects the applied TZ
    now = datetime.now().astimezone()

    # Run traceroute
    ips = run_traceroute(hostname)
    print(Fore.MAGENTA + f"[+] Found {len(ips)} IPs in route.\n")

    # Build filename
    date_part = now.strftime("%d-%m-%Y")
    time_part = now.strftime("%H-%M-%S")
    filename = f"{hostname}_{date_part}_{time_part}_{tzname_safe}_{offset_formatted}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(f"Traceroute results for {hostname} at {now.isoformat()}\n")
            fh.write(f"Target IP: {target_ip}\n")
            fh.write(f"Device IP (Local): {device_ip_local}\n")
            fh.write(f"Device IP (Public): {device_ip_public}\n")
            fh.write(f"Timestamp: {date_part} {time_part}\n")
            fh.write(f"Timezone: {tzname_safe} {offset_formatted}\n\n")

            for idx, ip in enumerate(ips, start=1):
                info = get_ip_info(ip)
                label = f"IP ({idx:02d}) : {ip}"
                print(GREEN_HEX + label + RESET)
                fh.write(label + "\n")

                if "error" in info:
                    err = info.get("error", "Unknown error")
                    print(Fore.RED + f"  Error: {err}")
                    fh.write(f"  Error: {err}\n")
                else:
                    country = info.get("country", "N/A")
                    region = info.get("regionName", "N/A")
                    city = info.get("city", "N/A")
                    isp = info.get("isp", "N/A")
                    org = info.get("org", "N/A")
                    asn = info.get("as", "N/A")
                    lat = info.get("lat", "N/A")
                    lon = info.get("lon", "N/A")
                    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat != "N/A" and lon != "N/A" else "N/A"

                    print(Fore.WHITE + f"  Country: {country}")
                    print(Fore.WHITE + f"  Region: {region}")
                    print(Fore.WHITE + f"  City: {city}")
                    print(Fore.YELLOW + f"  ISP: {isp}")
                    print(Fore.YELLOW + f"  Org: {org}")
                    print(Fore.YELLOW + f"  AS: {asn}")
                    print(Fore.GREEN + f"  Location: {lat}, {lon}")
                    print(Fore.BLUE + f"  Google Maps: {maps_link}")
                    print(PINK_HEX + f"  API/Website: ip-api.com (GeoIP Database)" + RESET)

                    fh.write(f"  Country: {country}\n")
                    fh.write(f"  Region: {region}\n")
                    fh.write(f"  City: {city}\n")
                    fh.write(f"  ISP: {isp}\n")
                    fh.write(f"  Org: {org}\n")
                    fh.write(f"  AS: {asn}\n")
                    fh.write(f"  Location: {lat}, {lon}\n")
                    fh.write(f"  Google Maps: {maps_link}\n")
                    fh.write(f"  API/Website: ip-api.com (GeoIP Database)\n")

                print(Style.DIM + "-" * 40)
                fh.write("-" * 40 + "\n")

        print(Fore.CYAN + f"\n[+] Results saved to {filename}")
    except Exception as e:
        print(Fore.RED + f"[-] Error writing file: {e}")


if __name__ == "__main__":
    main()
