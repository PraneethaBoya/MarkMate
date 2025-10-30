# Update Frontend API URLs for Production
# Run this after deploying backend to Railway/Render

Write-Host "🔧 MarkMate API URL Updater" -ForegroundColor Cyan
Write-Host ""

$backendUrl = Read-Host "Enter your backend URL (e.g., https://markmate-production.up.railway.app)"

if ([string]::IsNullOrWhiteSpace($backendUrl)) {
    Write-Host "❌ Backend URL is required" -ForegroundColor Red
    exit 1
}

# Remove trailing slash if present
$backendUrl = $backendUrl.TrimEnd('/')

Write-Host ""
Write-Host "Updating API base to: $backendUrl/api" -ForegroundColor Yellow
Write-Host ""

$files = @(
    "frontend/index.html",
    "frontend/login.html",
    "frontend/student.html",
    "frontend/admin.html",
    "frontend/predict.html",
    "frontend/charts.html"
)

$updated = 0
foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        # Update API base URL
        $newContent = $content -replace 'const API = "/api";', "const API = `"$backendUrl/api`";"
        
        if ($content -ne $newContent) {
            Set-Content $file -Value $newContent -NoNewline
            Write-Host "✓ Updated: $file" -ForegroundColor Green
            $updated++
        } else {
            Write-Host "- Skipped: $file (no changes needed)" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠ Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
if ($updated -gt 0) {
    Write-Host "✅ Updated $updated file(s)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test locally: Open frontend/index.html in browser"
    Write-Host "2. Commit changes: git add . && git commit -m 'Update API URL'"
    Write-Host "3. Push to GitHub: git push"
    Write-Host "4. GitHub Pages will auto-deploy in ~2 minutes"
} else {
    Write-Host "ℹ No files were updated" -ForegroundColor Blue
}
Write-Host ""
