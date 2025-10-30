# Bulk register users against the deployed backend
# Usage:
#   1) Edit scripts\users.csv
#   2) Run in PowerShell from project root:
#        .\scripts\bulk-register.ps1 -BackendUrl "https://markmate-api-vbm1.onrender.com" [-AdminSetupKey "YOUR_KEY"]
#   3) Optional: provide -AdminSetupKey to promote users where role=administrator
param(
    [Parameter(Mandatory=$true)][string]$BackendUrl,
    [Parameter(Mandatory=$false)][string]$AdminSetupKey
)

$ErrorActionPreference = 'Stop'

$csvPath = Join-Path $PSScriptRoot 'users.csv'
if (-not (Test-Path $csvPath)) {
    Write-Host "CSV not found: $csvPath" -ForegroundColor Red
    Write-Host "Create scripts/users.csv with headers: username,password,role,full_name" -ForegroundColor Yellow
    exit 1
}

# Normalize URL (no trailing slash)
$BackendUrl = $BackendUrl.TrimEnd('/')
$api = "$BackendUrl/api"

function Register-User($username, $password) {
    try {
        $uri = "$api/auth/register?username=$([System.Web.HttpUtility]::UrlEncode($username))&password=$([System.Web.HttpUtility]::UrlEncode($password))"
        $null = Invoke-RestMethod -Method POST -Uri $uri -ErrorAction Stop
        Write-Host "✓ Registered: $username" -ForegroundColor Green
        return $true
    }
    catch {
        $msg = $_.Exception.Message
        if ($msg -match '400' -or $msg -match 'exists') {
            Write-Host "• Exists: $username" -ForegroundColor Yellow
            return $false
        }
        else {
            Write-Host "✗ Failed to register $username : $msg" -ForegroundColor Red
            return $false
        }
    }
}

function Promote-Admin($username) {
    if (-not $AdminSetupKey) { return }
    try {
        $uri = "$api/setup/promote?username=$([System.Web.HttpUtility]::UrlEncode($username))&key=$([System.Web.HttpUtility]::UrlEncode($AdminSetupKey))"
        $null = Invoke-RestMethod -Method POST -Uri $uri -ErrorAction Stop
        Write-Host "★ Promoted to admin: $username" -ForegroundColor Cyan
    }
    catch {
        Write-Host ("! Promote failed for {0} : {1}" -f $username, $_.Exception.Message) -ForegroundColor Red
    }
}

try {
    $rows = Import-Csv -Path $csvPath
    $created = 0
    $total = $rows.Count
    $current = 0

    foreach ($row in $rows) {
        $current++
        $username = $row.username.Trim()
        $password = $row.password.Trim()
        
        if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($password)) {
            Write-Host "Skipping row $current - missing username or password" -ForegroundColor Yellow
            continue
        }
        
        $role = ($row.role | ForEach-Object { $_.ToString().Trim().ToLowerInvariant() })
        
        Write-Host "[$current/$total] Processing: $username" -ForegroundColor Cyan
        
        $ok = Register-User -username $username -password $password
        if ($ok) { 
            $created++ 
        }
        
        if ($role -eq 'administrator') { 
            Promote-Admin -username $username 
        }
        
        # Small delay to avoid rate limiting
        Start-Sleep -Milliseconds 200
    }

    Write-Host "`nRegistration complete!" -ForegroundColor Green
    Write-Host "Total users processed: $total" -ForegroundColor White
    Write-Host "New users created: $created" -ForegroundColor Green
    Write-Host "Existing users skipped: $($total - $created)" -ForegroundColor Yellow
}
catch {
    Write-Host "`nAn error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Script execution aborted." -ForegroundColor Red
    exit 1
}

# Add this line to keep the window open after completion
Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
