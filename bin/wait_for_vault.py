# wait_for_vault.py
import requests
import time
import sys


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
                time.sleep(2)
        except requests.RequestException:
            print("Vault not yet ready... waiting...")
            time.sleep(2)


if __name__ == "__main__":
    # Check if an address was provided
    if len(sys.argv) != 2:
        print("Usage: python wait_for_vault.py <vault_address>")
        sys.exit(1)

    vault_address = sys.argv[1]
    health_url = f"{vault_address}/v1/sys/health"

    wait_for_vault(health_url)
