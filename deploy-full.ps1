# Complete MarkMate Deployment Script
# Deploys both frontend (GitHub Pages) and backend (Railway)

Write-Host "🚀 MarkMate Full Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Initialize Git
Write-Host "Step 1: Git Setup" -ForegroundColor Yellow
Write-Host "----------------" -ForegroundColor Yellow

if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Gray
    git init
    git add .
    git commit -m "Initial commit: MarkMate platform"
    Write-Host "✓ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git already initialized" -ForegroundColor Green
}

Write-Host ""

# Step 2: GitHub Setup
Write-Host "Step 2: GitHub Repository" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow

$username = Read-Host "Enter your GitHub username"
$reponame = Read-Host "Enter repository name (default: markmate)"
if ([string]::IsNullOrWhiteSpace($reponame)) {
    $reponame = "markmate"
}

$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "✓ Remote already configured: $remoteExists" -ForegroundColor Green
} else {
    git remote add origin "https://github.com/$username/$reponame.git"
    Write-Host "✓ Remote added" -ForegroundColor Green
}

Write-Host ""

# Step 3: Push to GitHub
Write-Host "Step 3: Push to GitHub" -ForegroundColor Yellow
Write-Host "---------------------" -ForegroundColor Yellow

git add .
git commit -m "Deploy: MarkMate platform" --allow-empty
git branch -M main

Write-Host "Pushing to GitHub..." -ForegroundColor Gray
git push -u origin main 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pushed to GitHub" -ForegroundColor Green
} else {
    Write-Host "⚠ Push failed. You may need to authenticate or create the repo first." -ForegroundColor Yellow
    Write-Host "  Visit: https://github.com/new" -ForegroundColor Gray
    Write-Host "  Create repo named: $reponame" -ForegroundColor Gray
    Write-Host "  Then run: git push -u origin main" -ForegroundColor Gray
}

Write-Host ""

# Step 4: Deployment Instructions
Write-Host "Step 4: Deploy Backend to Render" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://render.com" -ForegroundColor White
Write-Host "2. Sign in with GitHub" -ForegroundColor White
Write-Host "3. Click 'New +' → 'Web Service'" -ForegroundColor White
Write-Host "4. Select 'Build and deploy from a Git repository'" -ForegroundColor White
Write-Host "5. Choose: $username/$reponame" -ForegroundColor White
Write-Host "6. Configure: Name=markmate-api, Environment=Python 3" -ForegroundColor White
Write-Host "7. Build Command: pip install -r requirements.txt" -ForegroundColor White
Write-Host "8. Start Command: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" -ForegroundColor White
Write-Host "9. Wait 3-5 minutes for deployment" -ForegroundColor White
Write-Host "10. Copy your backend URL (e.g., https://markmate-api.onrender.com)" -ForegroundColor White
Write-Host ""

$backendUrl = Read-Host "Enter your Render backend URL (or press Enter to skip for now)"

if (-not [string]::IsNullOrWhiteSpace($backendUrl)) {
    Write-Host ""
    Write-Host "Updating frontend API URLs..." -ForegroundColor Gray
    
    $backendUrl = $backendUrl.TrimEnd('/')
    $files = @(
        "frontend/index.html",
        "frontend/login.html",
        "frontend/student.html",
        "frontend/admin.html",
        "frontend/predict.html",
        "frontend/charts.html"
    )
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            $newContent = $content -replace 'const API = "/api";', "const API = `"$backendUrl/api`";"
            Set-Content $file -Value $newContent -NoNewline
        }
    }
    
    Write-Host "✓ Frontend API URLs updated" -ForegroundColor Green
    
    # Commit and push changes
    git add .
    git commit -m "Update API URLs for production"
    git push
    
    Write-Host "✓ Changes pushed to GitHub" -ForegroundColor Green
}

Write-Host ""

# Step 5: Enable GitHub Pages
Write-Host "Step 5: Enable GitHub Pages" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://github.com/$username/$reponame/settings/pages" -ForegroundColor White
Write-Host "2. Under 'Source', select: GitHub Actions" -ForegroundColor White
Write-Host "3. Wait 2 minutes for deployment" -ForegroundColor White
Write-Host ""

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your URLs:" -ForegroundColor Cyan
Write-Host "  Frontend: https://$username.github.io/$reponame/" -ForegroundColor White
if (-not [string]::IsNullOrWhiteSpace($backendUrl)) {
    Write-Host "  Backend:  $backendUrl" -ForegroundColor White
    Write-Host "  API Docs: $backendUrl/docs" -ForegroundColor White
}
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  - DEPLOY.md (Frontend deployment)" -ForegroundColor Gray
Write-Host "  - DEPLOY_BACKEND.md (Backend deployment)" -ForegroundColor Gray
Write-Host ""
