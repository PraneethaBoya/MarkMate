# MarkMate GitHub Pages Deployment Script
# Run this in PowerShell

Write-Host "🚀 MarkMate Deployment to GitHub Pages" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit: MarkMate student performance platform"
} else {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
}

# Prompt for GitHub username
$username = Read-Host "Enter your GitHub username"
$reponame = Read-Host "Enter repository name (default: markmate)"
if ([string]::IsNullOrWhiteSpace($reponame)) {
    $reponame = "markmate"
}

# Check if remote exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "✓ Remote origin already configured: $remoteExists" -ForegroundColor Green
    $updateRemote = Read-Host "Update remote? (y/n)"
    if ($updateRemote -eq "y") {
        git remote set-url origin "https://github.com/$username/$reponame.git"
        Write-Host "✓ Remote updated" -ForegroundColor Green
    }
} else {
    Write-Host "Adding remote origin..." -ForegroundColor Yellow
    git remote add origin "https://github.com/$username/$reponame.git"
    Write-Host "✓ Remote added" -ForegroundColor Green
}

# Commit any changes
Write-Host ""
Write-Host "Committing changes..." -ForegroundColor Yellow
git add .
git commit -m "Deploy: Update MarkMate frontend"

# Push to GitHub
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "✅ Deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/$username/$reponame/settings/pages"
Write-Host "2. Under 'Source', select 'GitHub Actions'"
Write-Host "3. Wait 2 minutes for deployment"
Write-Host "4. Visit: https://$username.github.io/$reponame/"
Write-Host ""
