import subprocess
import sys
import os
import urllib.request
import urllib.error

def check_command(cmd, name):
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[OK] {name} is installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[ERROR] {name} is not installed or not in PATH.")
        return False

def check_env_file():
    if os.path.exists(".env"):
        print("[OK] .env file exists.")
        return True
    else:
        print("[ERROR] .env file is missing. Run setup-dev.ps1 first.")
        return False

def check_port(port, service_name):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"[OK] Port {port} is open ({service_name} is running).")
        sock.close()
        return True
    else:
        print(f"[ERROR] Port {port} is closed ({service_name} might not be running).")
        return False

def check_http_service(url, name):
    try:
        urllib.request.urlopen(url, timeout=2)
        print(f"[OK] {name} is reachable at {url}.")
        return True
    except urllib.error.URLError:
        print(f"[ERROR] {name} is NOT reachable at {url}.")
        return False

def main():
    print("=== AutoSOC Environment Validation ===")
    
    # 1. Check tools
    has_docker = check_command(["docker", "--version"], "Docker")
    has_python = check_command([sys.executable, "--version"], "Python")
    
    # 2. Check config
    has_env = check_env_file()
    
    # 3. Check services (assuming default ports)
    if has_docker:
        print("\nChecking Infrastructure Ports...")
        check_port(5432, "PostgreSQL")
        check_port(6379, "Redis")
        check_port(9092, "Redpanda")
        check_port(9000, "MinIO")
        check_port(9200, "OpenSearch")
        check_port(8080, "Keycloak")
        check_port(5000, "MLflow")
        
        print("\nChecking Service Endpoints...")
        check_http_service("http://localhost:8080/health/ready", "Keycloak")
        check_http_service("http://localhost:9200", "OpenSearch")
        
    print("\nValidation Complete.")

if __name__ == "__main__":
    main()
