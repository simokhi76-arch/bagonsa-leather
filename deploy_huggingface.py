"""
Hugging Face Deployment Automation for BAGONSA.
Uploads the compiled interactive Space & Dataset bundle from dist_huggingface/
to Hugging Face Hub (huggingface.co/spaces/{user}/{space_name}) using huggingface_hub.
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config

try:
    from huggingface_hub import HfApi, create_repo, upload_folder
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False


DIST_HF_DIR = config.BASE_DIR / "dist_huggingface"


def deploy_to_huggingface(
    token: str,
    repo_name: str = "bagonsa-leather-goods",
    repo_type: str = "space",
    space_sdk: str = "gradio",
    private: bool = False
):
    """Uploads the dist_huggingface directory to Hugging Face Spaces or Datasets."""
    print("=" * 65)
    print("BAGONSA HUGGING FACE DEPLOYMENT ENGINE")
    print("=" * 65)

    if not HF_HUB_AVAILABLE:
        print("ERROR: huggingface_hub is not installed.")
        print("Please install via: pip install huggingface_hub")
        sys.exit(1)

    if not token:
        print("ERROR: Hugging Face token (HF_TOKEN) is required.")
        print("Get your free write token at: https://huggingface.co/settings/tokens")
        sys.exit(1)

    if not DIST_HF_DIR.exists():
        print(f"ERROR: {DIST_HF_DIR} not found. Running build_huggingface_repo.py first...")
        from src.build_huggingface_repo import build_huggingface_bundle
        build_huggingface_bundle()

    api = HfApi(token=token)
    user_info = api.whoami()
    username = user_info.get("name")
    print(f"Authenticated as Hugging Face user: @{username}")

    full_repo_id = f"{username}/{repo_name}"
    print(f"Target Repository : {full_repo_id} ({repo_type.capitalize()})")

    # 1. Create Repository if it doesn't exist
    try:
        print(f"\nEnsuring repository '{full_repo_id}' exists on Hugging Face...")
        if repo_type == "space":
            create_repo(
                repo_id=full_repo_id,
                repo_type="space",
                space_sdk=space_sdk,
                private=private,
                token=token,
                exist_ok=True
            )
        else:
            create_repo(
                repo_id=full_repo_id,
                repo_type=repo_type,
                private=private,
                token=token,
                exist_ok=True
            )
        print(f"[OK] Repository verified: https://huggingface.co/{'spaces/' if repo_type == 'space' else ''}{full_repo_id}")
    except Exception as e:
        print(f"Notice during repository verification: {e}")

    # 2. Upload Files to Hugging Face
    print(f"\nUploading all assets from {DIST_HF_DIR} to Hugging Face...")
    try:
        commit_info = upload_folder(
            folder_path=str(DIST_HF_DIR),
            repo_id=full_repo_id,
            repo_type=repo_type,
            token=token,
            commit_message="Initial deploy: BAGONSA full-grain leather catalog & interactive guide"
        )
        print("[OK] Upload successful!")

        live_url = f"https://huggingface.co/spaces/{full_repo_id}" if repo_type == "space" else f"https://huggingface.co/datasets/{full_repo_id}"
        print("\n" + "=" * 65)
        print(f"SUCCESS: Your Hugging Face Parasite Space is live at:")
        print(live_url)
        print("=" * 65)
        return live_url

    except Exception as ex:
        print(f"Deployment error: {ex}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Deploy BAGONSA SEO engine to Hugging Face.")
    parser.add_argument(
        "--token",
        default=os.getenv("HF_TOKEN", ""),
        help="Hugging Face User Access Token (write permission)"
    )
    parser.add_argument(
        "--repo-name",
        default=os.getenv("HF_REPO_NAME", "bagonsa-leather-goods"),
        help="Repository name on Hugging Face (default: bagonsa-leather-goods)"
    )
    parser.add_argument(
        "--type",
        choices=["space", "dataset"],
        default="space",
        help="Deploy as an interactive Space or Dataset"
    )

    args = parser.parse_args()
    deploy_to_huggingface(
        token=args.token,
        repo_name=args.repo_name,
        repo_type=args.type
    )


if __name__ == "__main__":
    main()
