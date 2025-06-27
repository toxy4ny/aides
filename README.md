# AIDES
A S Y N C   I D   B R U T E F I L E   S C A N N E R

# IDEA:
# IDOR in **GetFile.aspx**  
_Asynchronous enumeration of `id` parameter reveals confidential documents_

![risk](https://img.shields.io/badge/Risk-Critical-red) ![cvss](https://img.shields.io/badge/CVSS-9.4%2F10-important)

> “A single predictable integer turned an internal file-store into an open library.”

---

## 1 Executive summary
The endpoint  

/.../GetFile.aspx?id=


suffers from a classic **Insecure Direct Object Reference (IDOR)**: the numeric identifier is neither authorised nor randomised.  
An attacker can brute-force the parameter and harvest sensitive PDFs/DOCX stored in the database.

---

## 2 Proof-of-concept

### 2.1 Python async scanner  
```python
# PoC: find valid ids and log working URLs
# ⋯ full code omitted – see asyn_brutefile.py in repo

2.2 Result sample
https://target/…/GetFile.aspx?id=32978   BoardMinutes_StaffCuts.pdf
https://target/…/GetFile.aspx?id=33025   Salary_Spreadsheet_Q3.xlsx

3 Technical root cause
The id is a direct primary-key reference to the Files table.
Endpoint lacks:
• Session/role verification
• Owner/resource mapping
• Unpredictable identifiers (e.g. UUID, GUID)

Server returns 200/206 with full binary payload + descriptive Content-Type.
4 Business impact (why it is critical)
Asset disclosed	Possible damage
HR documents (salary, layoffs)	Labour disputes, brand reputation, insider trade
Legal drafts & board minutes	Loss of competitive leverage, compliance fines
PII of students/employees	GDPR/CCPA penalties, identity theft
Embedded credentials inside docs	Expands foothold, lateral movement
High-sensitivity data flows directly to unauthenticated users, resulting in:

Regulatory non-compliance – potential fines up to 4 % of global turnover.
Breach notification costs, PR crisis, shareholder lawsuits.
Facilitation of spear-phishing and BEC via leaked org charts and e-mails.

5 Extended attack surface
IDOR

Sensitive docs

Embedded creds

VPN / DB login

M&A leaks

Metadata reveal

Usernames

Credential pivoting
• Extract hard-coded passwords from Word/PDF comments → RDP / SQL login.
Version disclosure
• Document properties show Office version & OS build → targeted exploit matching.
S3 / Azure Blob links
• Files often contain pre-signed URLs; attacker reuses before expiry.
Watermark removal / tampering
• Re-upload modified docs if PUT or POST misconfigured (stored XSS, malware).

6 Mitigation
Control	Description
Authorisation gate	Validate that requester owns/needs file.
Indirect identifiers	Replace sequential IDs with UUID v4.
Rate limiting & anomaly detection	Block high-velocity enumeration.
Audit & purge	Remove legacy documents, rotate keys.
Quick patch (C# ASP.NET):

csharp

if(!User.Identity.IsAuthenticated) { return Unauthorized(); }
var file = db.Files.FirstOrDefault(f => f.Guid == requestedGuid
                                      && f.OwnerId == User.Id);
7 References
OWASP Top 10 – A01:2021 Broken Access Control
CWE-639: Authorization Bypass Through User-Controlled Key
