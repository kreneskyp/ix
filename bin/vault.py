import os
import sys
import time
import json
import requests
import subprocess
import argparse


def check_vault_status(vault_address):
    try:
        response = requests.get(f"{vault_address}/v1/sys/health", verify=False)
        return response.status_code, response.json()
    except requests.RequestException as e:
        print(f"Error checking Vault status ({vault_address}): {e}", file=sys.stderr)
        return None, None


def initialize_vault(vault_address, unseal_file_path, token_file_path):
    print("Initializing Vault...")
    try:
        result = subprocess.run(
            [
                "vault",
                "operator",
                "init",
                f"-address={vault_address}",
                "-key-shares=1",
                "-key-threshold=1",
                "-format=json",
            ],
            capture_output=True,
            check=True,
            text=True,
        )

        vault_output = json.loads(result.stdout)

        with open(unseal_file_path, "w") as unseal_file:
            json.dump(vault_output, unseal_file, indent=2)

        root_token = vault_output["root_token"]
        with open(token_file_path, "w") as token_file:
            token_file.write(f"VAULT_DEV_ROOT_TOKEN_ID={root_token}")

        print("Vault initialized.")
        return vault_output["unseal_keys_b64"]

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while initializing Vault: {e}", file=sys.stderr)
        sys.exit(1)


def unseal_vault(vault_address, unseal_keys):
    print("Unsealing Vault...")
    headers = {"Content-Type": "application/json"}
    for key in unseal_keys:
        payload = {"key": key}
        response = requests.put(
            f"{vault_address}/v1/sys/unseal",
            headers=headers,
            data=json.dumps(payload),
            verify=False,
        )
        if response.status_code != 200:
            print(f"Error unsealing Vault: {response.content}", file=sys.stderr)
            sys.exit(1)

    print("Vault unsealed.")


def manage_vault(vault_address, vault_dir, unseal_file, token_file):
    unseal_file_path = os.path.join(vault_dir, unseal_file)
    token_file_path = os.path.join(vault_dir, token_file)

    # Check Vault status and wait if necessary
    for _ in range(10):
        status_code, vault_status = check_vault_status(vault_address)
        if status_code is not None:
            break
        print("Vault is not responding. Waiting...")
        time.sleep(2)
    else:
        print("Vault did not respond after several attempts. Exiting.")
        sys.exit(1)

    if vault_status["initialized"]:
        print("Vault is already initialized.")
        if vault_status["sealed"]:
            with open(unseal_file_path, "r") as unseal_file:
                vault_data = json.load(unseal_file)
                unseal_keys = vault_data["unseal_keys_b64"]
            unseal_vault(vault_address, unseal_keys)
    else:
        unseal_keys = initialize_vault(vault_address, unseal_file_path, token_file_path)
        unseal_vault(vault_address, unseal_keys)
    enable_kv_secrets_engine(vault_address, unseal_file_path)


def enable_kv_secrets_engine(vault_address, unseal_file_path):
    print("Checking if KV secrets engine is enabled...")

    # Load unseal data to get the root token
    with open(unseal_file_path, "r") as f:
        unseal_data = json.load(f)
    root_token = unseal_data["root_token"]

    # Set Vault address and token for the environment
    env = {**os.environ, "VAULT_ADDR": vault_address, "VAULT_TOKEN": root_token}

    try:
        # List enabled secrets engines
        result = subprocess.run(
            [
                "vault",
                "secrets",
                "list",
                "-format=json",
            ],
            capture_output=True,
            check=True,
            text=True,
            env=env,
        )

        engines = json.loads(result.stdout)
        if engines.get("secret/", {}).get("type", None) == "kv":
            print("KV secrets engine is already enabled.")
            return

        print("Enabling KV secrets engine...")

        result = subprocess.run(
            [
                "vault",
                "secrets",
                "enable",
                "-path=secret",
                "-version=2",
                "kv",
            ],
            capture_output=True,
            check=True,
            text=True,
            env=env,
        )

        print("KV secrets engine enabled.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage Vault initialization and unsealing process"
    )
    parser.add_argument("--vault-addr", required=True, help="Vault server address")
    parser.add_argument(
        "--vault-dir", default=".vault/", help="Directory to store Vault files"
    )
    parser.add_argument(
        "--unseal-file",
        default="keys",
        help="File to store the unseal keys and other related data",
    )
    parser.add_argument(
        "--token-file", default=".client.env", help="File to store the root token"
    )
    args = parser.parse_args()

    if not os.path.exists(args.vault_dir):
        os.makedirs(args.vault_dir)

    manage_vault(args.vault_addr, args.vault_dir, args.unseal_file, args.token_file)


if __name__ == "__main__":
    main()
