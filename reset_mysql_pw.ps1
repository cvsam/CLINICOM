# MySQL 9.1 Root Password Reset Script (Robust Method)
# Run as Administrator

$mysqlBin = "C:\Program Files\MySQL\MySQL Server 9.1\bin"
$mysqlIni = "C:\ProgramData\MySQL\MySQL Server 9.1\my.ini"

Write-Host "=== MySQL 9.1 Root Password Reset ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop MySQL service
Write-Host "[1/5] Stopping MySQL91 service..." -ForegroundColor Yellow
net stop MySQL91 2>$null
Start-Sleep -Seconds 3

# Ensure no mysqld processes remain
Write-Host "[2/5] Cleaning up any remaining mysqld processes..." -ForegroundColor Yellow
Get-Process mysqld -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Step 3: Start MySQL with --skip-grant-tables
Write-Host "[3/5] Starting MySQL in safe mode (skip-grant-tables)..." -ForegroundColor Yellow
$proc = Start-Process -FilePath "$mysqlBin\mysqld.exe" `
    -ArgumentList "--defaults-file=`"$mysqlIni`"", "--skip-grant-tables", "--shared-memory" `
    -PassThru -WindowStyle Hidden

# Wait for MySQL to be ready
Write-Host "  Waiting for MySQL to start..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Step 4: Reset password using UPDATE (more compatible with skip-grant-tables)
Write-Host "[4/5] Resetting root password..." -ForegroundColor Yellow

# First flush privileges, then alter user
$resetSql = @"
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'Kanyoro193#';
FLUSH PRIVILEGES;
SELECT 'PASSWORD_RESET_OK' AS result;
"@

$resetSql | & "$mysqlBin\mysql.exe" -u root --connect-expired-password 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Password reset SUCCESSFUL!" -ForegroundColor Green
} else {
    Write-Host "  First method failed. Trying alternative..." -ForegroundColor Yellow
    
    # Alternative: direct update to mysql.user table
    $altSql = @"
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Kanyoro193#';
FLUSH PRIVILEGES;
SELECT 'PASSWORD_RESET_OK' AS result;
"@
    $altSql | & "$mysqlBin\mysql.exe" -u root 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Password reset SUCCESSFUL (alt method)!" -ForegroundColor Green
    } else {
        Write-Host "  Password reset FAILED!" -ForegroundColor Red
    }
}

# Step 5: Stop safe-mode MySQL and restart service
Write-Host "[5/5] Restarting MySQL normally..." -ForegroundColor Yellow
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 4

# Make sure mysqld is fully stopped
Get-Process mysqld -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

net start MySQL91
Start-Sleep -Seconds 3

# Verify
Write-Host ""
Write-Host "=== Verifying Connection ===" -ForegroundColor Cyan
& "$mysqlBin\mysql.exe" -u root -p"Kanyoro193#" -e "SELECT 'CONNECTION_VERIFIED' AS status;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! MySQL root password has been reset to: Kanyoro193#" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Connection test failed. Check the output above for errors." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
