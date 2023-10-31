import os
import requests
import time
import sys


import subprocess


def print_docker_logs():
    if os.environ.get("WAIT_FOR_VAULT_ECHO_LOGS", 1) in [1, True, "1", "true", "True"]:
        try:
            output = subprocess.check_output(["docker-compose", "logs", "vault"])
            print(output.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
    else:
        pass



def wait_for_vault(health_url):
    while True:
        try:
            print("Checking Vault health...")
            response = requests.get(health_url)
            if response.status_code == 200:
                print("Vault is up and running!")
                break
            else:
                print(response.status_code, response.content)
                print("Vault not yet ready... waiting...")
                print_docker_logs()
                time.sleep(2)
        except requests.RequestException:
            print("Vault not yet ready... waiting...")
            print_docker_logs()
            time.sleep(2)


if __name__ == "__main__":
    # Check if an address was provided
    if len(sys.argv) != 2:
        print("Usage: python wait_for_vault.py <vault_address>")
        sys.exit(1)

    vault_address = sys.argv[1]
    health_url = f"{vault_address}/v1/sys/health"

    wait_for_vault(health_url)
