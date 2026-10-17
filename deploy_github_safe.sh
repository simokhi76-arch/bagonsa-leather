#!/usr/bin/env bash
# ==============================================================================
# BAGONSA Safe Single-Commit Git Push Script
# Prevents GitHub API secondary rate limits and automated flagging by bundling
# all 100 HTML pages, index.html, sitemap.xml, and Colab notebooks into a single
# atomic Git commit rather than individual HTTP REST API calls.
# ==============================================================================

set -euo pipefail

echo "================================================================="
echo "BAGONSA SAFE SINGLE-COMMIT GIT DEPLOYMENT"
echo "================================================================="

# 1. Environment & Parameter Extraction
GITHUB_USER="${GITHUB_USER:-simokhi76-arch}"
REPO_NAME="${GITHUB_REPO:-bagonsa-leather}"
BRANCH="${GITHUB_BRANCH:-main}"
COMMIT_MSG="Docs: update product specification directory"

echo "Target Repository : ${GITHUB_USER}/${REPO_NAME}"
echo "Target Branch     : ${BRANCH}"

# 2. Check Prerequisites
if [ ! -d "dist_pages" ] || [ ! -d "dist_colab" ]; then
    echo "ERROR: dist_pages or dist_colab directory not found!"
    echo "Please run: python src/build_html_pages.py && python src/build_colab_notebooks.py"
    exit 1
fi

PAGE_COUNT=$(find dist_pages -name "*.html" | wc -l)
COLAB_COUNT=$(find dist_colab -name "*.ipynb" | wc -l)

echo "Discovered ${PAGE_COUNT} HTML pages in dist_pages/"
echo "Discovered ${COLAB_COUNT} Colab notebooks in dist_colab/"

if [ "${PAGE_COUNT}" -lt 100 ]; then
    echo "WARNING: Expected 100+ HTML pages, found ${PAGE_COUNT}."
fi

# 3. Initialize Git if not already a repository
if [ ! -d ".git" ]; then
    echo "Initializing fresh local git repository..."
    git init
    git checkout -b "${BRANCH}" 2>/dev/null || git branch -M "${BRANCH}"
else
    echo "Existing git repository detected."
    git checkout "${BRANCH}" 2>/dev/null || git checkout -b "${BRANCH}"
fi

# Set local git identity if not configured
if ! git config user.name >/dev/null 2>&1; then
    git config user.name "BAGONSA Automation Bot"
fi
if ! git config user.email >/dev/null 2>&1; then
    git config user.email "automation@bagonsales.shop"
fi

# 4. Stage all necessary files atomically
echo "Staging static pages, Colab parasite notebooks, source code, and configuration..."
git add dist_pages/
git add dist_colab/
git add src/
git add data/
git add config.py
git add requirements.txt
git add deploy_github_safe.sh
git add deploy_gcs_bucket.py
git add .github/ 2>/dev/null || true

# Check if there are staged changes
if git diff --cached --quiet; then
    echo "No modifications detected. Working tree is clean."
    exit 0
fi

# 5. Create Single Atomic Commit
echo "Creating single atomic commit..."
git commit -m "${COMMIT_MSG}"

# 6. Push to GitHub Remote
if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "NOTICE: GITHUB_TOKEN environment variable not set."
    echo "Attempting standard push to origin remote..."
    if git remote | grep -q "^origin$"; then
        git push origin "${BRANCH}"
        echo "Push successful!"
    else
        echo "No 'origin' remote configured."
        echo "To push with a personal access token or CI token, run:"
        echo "  export GITHUB_TOKEN=ghp_your_secret_token"
        echo "  ./deploy_github_safe.sh"
    fi
else
    echo "Pushing securely via authenticated GITHUB_TOKEN remote..."
    REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
    git push -u "${REMOTE_URL}" "${BRANCH}" --force
    echo "Deployment to ${GITHUB_USER}/${REPO_NAME} completed successfully!"
fi

echo "================================================================="
echo "SAFE COMMIT & DEPLOYMENT SCRIPT COMPLETED"
echo "================================================================="
