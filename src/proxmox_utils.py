from proxmoxer import ProxmoxAPI
from tabulate import tabulate
import os
import datetime
from logger import setup_logging
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path="/app/.env")
setup_logging()


def _format_uptime(seconds):
    """Formats uptime in seconds into a human-readable string (e.g., 2d 3h 4m)."""
    seconds = int(seconds)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if days > 0 or hours > 0:
        parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
    elif minutes > 0:
        parts.append(f"{minutes}m")

    if not parts:
        return "0m"

    return " ".join(parts)


def _get_pve_report(proxmox):
    """Fetches and formats the Proxmox VE node status report."""
    pve_rows = []
    for node in proxmox.nodes.get():
        name = node["node"]
        try:
            summary = proxmox.nodes(name).status.get()
            cpu = summary.get("cpu")
            mem = summary.get("memory", {})
            mem_used = mem.get("used")
            mem_total = mem.get("total")
            disk = summary.get("rootfs", {})
            disk_used = disk.get("used")
            disk_total = disk.get("total")
            uptime = _format_uptime(summary.get("uptime", 0))

            if all(val is not None for val in [cpu, mem_used, mem_total, disk_used, disk_total]):
                pve_rows.append([
                    name,
                    f"{cpu * 100:.1f}%",
                    f"{mem_used / 1e9:.1f}/{mem_total / 1e9:.1f} GB",
                    f"{disk_used / 1e9:.1f}/{disk_total / 1e9:.1f} GB",
                    uptime
                ])
            else:
                pve_rows.append([name, "N/A", "N/A", "N/A", "Missing metrics"])
        except Exception as inner:
            pve_rows.append([name, "N/A", "N/A", "N/A", f"Error: {inner}"])

    pve_table = tabulate(pve_rows, headers=["Node", "CPU", "RAM", "Disk", "Uptime"], tablefmt="github")
    return "PVE Node Status:\n```\n" + pve_table + "\n```"


def _get_pbs_report(pbs):
    """Fetches and formats the Proxmox Backup Server datastore status report."""
    pbs_rows = []
    try:
        datastores = pbs.admin.datastore.get()
        logging.info(f"Raw datastores response: {datastores}")
    except Exception as e:
        logging.error(f"Failed to get datastores: {e}")
        datastores = []

    for store in datastores:
        name = store.get("store")
        if not name:
            continue

        store_status = pbs.admin.datastore(name).status.get()
        used = store_status.get("used")
        total = store_status.get("total")
        last = "N/A"

        try:
            snapshots = pbs.admin.datastore(name).snapshots.get()
            if snapshots:
                latest = max(snapshots, key=lambda s: s.get("backup-time", 0))
                backup_time = latest.get("backup-time")
                if backup_time:
                    backup_id = f"{latest.get('backup-type', 'unknown')}/{latest.get('backup-id', 'unknown')}"
                    last = f"{backup_id} @ {datetime.datetime.fromtimestamp(backup_time).strftime('%Y-%m-%d %H:%M')}"
        except Exception as e:
            logging.error(f"Error getting snapshots for {name}: {e}")

        if used is not None and total is not None:
            pbs_rows.append([name, f"{used / 1e9:.1f} GB", f"{total / 1e9:.1f} GB", last])
        else:
            pbs_rows.append([name, "N/A", "N/A", last])

    pbs_table = tabulate(pbs_rows, headers=["Datastore", "Used", "Total", "Last Backup"], tablefmt="github")
    return "PBS Datastore Status:\n```\n" + pbs_table + "\n```"


def get_proxmox_report():
    """
    Generates a combined report for Proxmox VE and Proxmox Backup Server.
    """
    report_sections = []

    # Proxmox VE Node Status
    try:
        proxmox = ProxmoxAPI(
            os.getenv("PROXMOX_HOST"),
            user=os.getenv("PROXMOX_USER"),
            token_name=os.getenv("PROXMOX_TOKEN_ID"),
            token_value=os.getenv("PROXMOX_TOKEN_SECRET"),
            verify_ssl=False
        )
        report_sections.append(_get_pve_report(proxmox))
    except Exception as e:
        report_sections.append(f"❌ Failed to fetch PVE data: {e}")

    # Proxmox Backup Server
    try:
        pbs = ProxmoxAPI(
            os.getenv("PBS_HOST"),
            user=os.getenv("PBS_USER"),
            token_name=os.getenv("PBS_TOKEN_ID"),
            token_value=os.getenv("PBS_TOKEN_SECRET"),
            verify_ssl=False,
            port=8007,
            service='pbs'
        )
        report_sections.append(_get_pbs_report(pbs))
    except Exception as e:
        report_sections.append(f"❌ Failed to fetch PBS data: {e}")

    return "\n\n".join(report_sections)
