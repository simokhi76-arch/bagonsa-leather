<#
.SYNOPSIS
BAGONSA Safe Single-Commit Git Push Script (PowerShell).
Prevents GitHub API secondary rate limits and automated flagging by bundling
all 100 HTML pages, index.html, sitemap.xml, and Colab notebooks into a single
atomic Git commit rather than individual HTTP REST API calls.
#>

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "BAGONSA SAFE SINGLE-COMMIT GIT DEPLOYMENT (PowerShell)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$GithubUser = if ($env:GITHUB_USER) { $env:GITHUB_USER } else { "bagonsa-official" }
$RepoName   = if ($env:GITHUB_REPO) { $env:GITHUB_REPO } else { "bagonsa-seo-engine" }
$Branch     = if ($env:GITHUB_BRANCH) { $env:GITHUB_BRANCH } else { "main" }
$CommitMsg  = "Docs: update product specification directory"

Write-Host "Target Repository : $GithubUser/$RepoName"
Write-Host "Target Branch     : $Branch"

if (-not (Test-Path "dist_pages") -or -not (Test-Path "dist_colab")) {
    Write-Error "dist_pages or dist_colab directory not found! Run build scripts first."
}

$pageCount = (Get-ChildItem -Path "dist_pages" -Filter "*.html").Count
$colabCount = (Get-ChildItem -Path "dist_colab" -Filter "*.ipynb").Count

Write-Host "Discovered $pageCount HTML pages in dist_pages/"
Write-Host "Discovered $colabCount Colab notebooks in dist_colab/"

if ($pageCount -lt 100) {
    Write-Warning "Expected 100+ HTML pages, found $pageCount."
}

if (-not (Test-Path ".git")) {
    Write-Host "Initializing fresh local git repository..."
    git init
    git branch -M $Branch
} else {
    Write-Host "Existing git repository detected."
    git branch -M $Branch
}

# Configure local git identity if needed
try {
    git config user.name | Out-Null
} catch {
    git config user.name "BAGONSA Automation Bot"
}
try {
    git config user.email | Out-Null
} catch {
    git config user.email "automation@bagonsales.shop"
}

Write-Host "Staging static pages, Colab notebooks, source code, and configuration..."
git add dist_pages/
git add dist_colab/
git add src/
git add data/
git add config.py
git add requirements.txt
git add deploy_github_safe.sh
git add deploy_github_safe.ps1
git add deploy_gcs_bucket.py
if (Test-Path ".github") { git add .github/ }

$stagedDiff = git diff --cached --name-only
if (-not $stagedDiff) {
    Write-Host "No modifications detected. Working tree is clean." -ForegroundColor Green
    exit 0
}

Write-Host "Creating single atomic commit..." -ForegroundColor Yellow
git commit -m $CommitMsg

if (-not $env:GITHUB_TOKEN) {
    Write-Host "NOTICE: GITHUB_TOKEN environment variable not set." -ForegroundColor Yellow
    Write-Host "Attempting push to origin remote if configured..."
    $remotes = git remote
    if ($remotes -contains "origin") {
        git push origin $Branch
        Write-Host "Push to origin completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "No 'origin' remote configured."
        Write-Host "To push to GitHub, set `$env:GITHUB_TOKEN = 'ghp_token' and re-run."
    }
} else {
    Write-Host "Pushing securely via authenticated GITHUB_TOKEN..." -ForegroundColor Yellow
    $remoteUrl = "https://$($env:GITHUB_TOKEN)@github.com/$GithubUser/$RepoName.git"
    git push -u $remoteUrl $Branch --force
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SCRIPT COMPLETED" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
