#  Smart Campus Resource Hub & Three-Node Security Lab

A self-hosted, multi-node virtualized Linux infrastructure hosting a live campus facility availability portal (`Campus Resource Hub`) paired with an independent Python health-monitoring daemon, real-time Telegram incident alerts, and a Purple Team auditing node.

---

##  System Architecture & Topology

| Node | OS | IP Address | Role |
| :--- | :--- | :--- | :--- |
| **Host Machine** | macOS (Apple Silicon) | `192.168.64.1` | UTM Hypervisor host, browser client, SSH admin |
| **`VM1-Server`** | Ubuntu Server 24.04 ARM64 | `192.168.64.2` | Nginx web host (`:80`), UFW default-deny firewall, OpenSSH (`:22`) |
| **`VM2-Monitor`** | Ubuntu Server 24.04 ARM64 | `192.168.64.4` | Independent Python watchdog daemon & Telegram Bot REST API alerting |
| **`VM3-Auditor`** | Kali Linux ARM64 | `192.168.65.2` | External attack-surface enumeration (`nmap`) & HTTP header auditing (`curl`) |

---

##  Key Features

* **Two-Node Fault Isolation:** Decouples monitoring (`VM2-Monitor`) from the web host (`VM1-Server`) so alerts fire even when the primary server goes down.
* **Least-Privilege Security (UFW):** Blocks all unsolicited inbound connections by default, permitting only `22/tcp` (SSH) and `80/tcp` (HTTP).
* **Human-Centered Alert Design:** Translates raw connection errors into plain-English Telegram alerts specifying **Student Impact** and **Recovery Commands**, using boolean state-tracking (`server_is_up`) to prevent alert spam.
* **Purple Team Log Forensics:** Validated firewall filtering via `nmap -sV -Pn` from `VM3-Auditor` and verified real-time traffic attribution in `/var/log/nginx/access.log`.

---

## 🏗️ Visual Architecture Diagram

```mermaid
flowchart LR
    subgraph Host["macOS Host (192.168.64.1)"]
        Browser["Safari / Chrome<br/>(Admin & Client)"]
    end

    subgraph VirtualNet["UTM Virtual Network Bridge"]
        VM1["VM1-Server (192.168.64.2)<br/>Ubuntu 24.04 ARM64<br/>- Nginx (:80)<br/>- UFW Default-Deny (:22, :80)<br/>- /var/log/nginx/access.log"]
        VM2["VM2-Monitor (192.168.64.4)<br/>Ubuntu 24.04 ARM64<br/>- Python watchdog.py<br/>- State-Tracking Logic"]
        VM3["VM3-Auditor (192.168.65.2)<br/>Kali Linux ARM64<br/>- Nmap (-sV -Pn)<br/>- Curl Header Audits"]
    end

    Telegram["Telegram Bot REST API<br/>(Mobile Incident Alerts)"]

    Browser -- "HTTP GET (:80) / SSH (:22)" --> VM1
    VM3 -- "Port Scan & Header Audit" --> VM1
    VM2 -- "Health Poll Every 10s" --> VM1
    VM2 -- "HTTPS POST /sendMessage<br/>(Outage & Resolved Alerts)" --> Telegram
```

---

##  Visual Proof & Lab Validation

### 1. Live Web Portal & Firewall Hardening
![Campus Portal](screenshots/02-campus-portal.png)
![UFW Status](screenshots/03-ufw-status.png)

### 2. Real-Time Telegram Outage & Recovery Alerts
![Telegram Alerts](screenshots/04-telegram-alerts.png)

### 3. Forensic Nginx Access Log (`VM3-Auditor` Probes)
![Nginx Access Log](screenshots/05-nginx-access-log.png)

---

##  Engineering Challenges & Solutions

* **x86 vs. ARM64 Architecture:** Resolved VirtualBox Guru Meditation and EFI boot failures on Apple Silicon by migrating to native ARM64 images in UTM.
* **VM Cloning Isolation:** Prevented IP collisions and hostname conflicts after cloning by regenerating virtual MAC addresses and updating `/etc/hostname` and `/etc/hosts`.
* **Security & Credential Hygiene:** Removed hardcoded API tokens in favor of environment variables (`os.getenv`) and rotated exposed bot credentials.
