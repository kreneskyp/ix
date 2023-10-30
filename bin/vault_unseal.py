import subprocess
import json
import sys
import os
import argparse


def unseal_vault(vault_address, unseal_file_path):
    print("Unsealing Vault...")

    # Load unseal data to get the unseal key
    with open(unseal_file_path, "r") as f:
        unseal_data = json.load(f)

    unseal_key = unseal_data["unseal_keys_b64"][0]

    # Set Vault address for the environment
    env = {**os.environ, "VAULT_ADDR": vault_address}

    try:
        result = subprocess.run(
            ["vault", "operator", "unseal", unseal_key],
            capture_output=True,
            check=True,
            text=True,
            env=env,
        )

        print("Vault unsealed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while unsealing Vault: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Unseal HashiCorp Vault.")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help="Vault server address (e.g., 'https://127.0.0.1:8200').",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Path to the JSON file containing the unseal key.",
    )

    args = parser.parse_args()

    unseal_vault(args.address, args.file)


if __name__ == "__main__":
    main()
