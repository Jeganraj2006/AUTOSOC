export const MITRE_DICTIONARY: Record<string, string> = {
  // Initial Access
  "T1190": "Exploit Public-Facing Application",
  "T1566": "Phishing Attack Vector",
  "T1566.001": "Spearphishing Attachment",
  "T1566.002": "Spearphishing Link",
  "T1078": "Valid Account Access",

  // Execution
  "T1059": "Command & Script Interpreter",
  "T1059.001": "PowerShell Script Execution",
  "T1059.003": "Windows Command Shell (cmd.exe)",
  "T1059.004": "Unix Shell Scripting (bash/sh)",
  "T1053": "Scheduled Task / Cron Job",
  "T1053.005": "Scheduled Task: Systemd Service",
  "T1204": "User Execution of Malicious File",

  // Persistence & Privilege Escalation
  "T1547": "Boot / Logon Autostart Execution",
  "T1055": "Process Injection",
  "T1068": "Exploitation for Privilege Escalation",
  "T1134": "Access Token Manipulation",

  // Defense Evasion
  "T1027": "Obfuscated & Encrypted Payloads",
  "T1027.001": "Binary Padding",
  "T1027.002": "Software Packing & Compression",
  "T1070": "Indicator Removal / Clearing Logs",
  "T1140": "Deobfuscate / Decode Executable Files",
  "T1218": "System Binary Proxy Execution (LOLBins)",

  // Credential Access
  "T1003": "OS Credential Dumping",
  "T1003.001": "LSASS Password Memory Dumping",
  "T1003.002": "Security Account Manager (SAM) Registry",
  "T1003.003": "NTDS.dit Active Directory Database",
  "T1110": "Brute Force Credential Access",
  "T1110.001": "Password Guessing",
  "T1110.003": "Password Spraying",
  "T1555": "Credentials from Password Stores",

  // Discovery
  "T1046": "Network Service Discovery & Scanning",
  "T1082": "System Information Discovery",
  "T1083": "File & Directory Discovery",
  "T1018": "Remote System Discovery",
  "T1069": "Permission Group Discovery",

  // Lateral Movement
  "T1021": "Remote Desktop & Network Services",
  "T1021.001": "Remote Desktop Protocol (RDP) Access",
  "T1021.002": "SMB / Admin Remote Share Execution",
  "T1021.004": "SSH Remote Session Access",
  "T1570": "Lateral Tool Transfer",

  // Command & Control
  "T1071": "Application Layer C2 Protocol",
  "T1090": "Proxy & Tunneling Connection",
  "T1105": "Ingress Tool Transfer / File Download",
  "T1573": "Encrypted C2 Channel",

  // Exfiltration & Impact
  "T1041": "Exfiltration Over C2 Channel",
  "T1005": "Data Ingestion from Local System",
  "T1485": "Data Destruction",
  "T1486": "Ransomware Data Encryption",
  "T1490": "Inhibit System Recovery / Delete Shadows",
};

/**
 * Dynamically resolves any MITRE Technique ID into a human-readable title.
 * Handles exact matches, sub-technique fallbacks, and unknown custom IDs gracefully.
 */
export function getMitreTitle(id: string): string {
  if (!id) return "Security Event";
  
  const cleanId = id.trim().toUpperCase();
  
  // 1. Direct dictionary match
  if (MITRE_DICTIONARY[cleanId]) {
    return MITRE_DICTIONARY[cleanId];
  }

  // 2. Base technique fallback (e.g. T1059.009 -> T1059)
  const baseId = cleanId.split(".")[0];
  if (MITRE_DICTIONARY[baseId]) {
    return `${MITRE_DICTIONARY[baseId]} (${cleanId})`;
  }

  // 3. General dynamic fallback for any unlisted MITRE ID
  return `Security Technique (${cleanId})`;
}
