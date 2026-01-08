# Clean up files that should be ignored by git
# This removes them from git tracking but keeps them on disk

Write-Host "Cleaning up git-tracked files that should be ignored..." -ForegroundColor Cyan

# Remove node_modules from git tracking if they exist
if (Test-Path "apps/frontend/node_modules") {
    Write-Host "Removing apps/frontend/node_modules from git tracking..." -ForegroundColor Yellow
    git rm -r --cached apps/frontend/node_modules 2>$null
}

if (Test-Path "apps/signaling/node_modules") {
    Write-Host "Removing apps/signaling/node_modules from git tracking..." -ForegroundColor Yellow
    git rm -r --cached apps/signaling/node_modules 2>$null
}

# Remove venv from git tracking if it exists
if (Test-Path "venv") {
    Write-Host "Removing venv from git tracking..." -ForegroundColor Yellow
    git rm -r --cached venv 2>$null
}

# Remove .env if it was tracked
if (Test-Path ".env") {
    Write-Host "Removing .env from git tracking..." -ForegroundColor Yellow
    git rm --cached .env 2>$null
}

Write-Host "`nDone! Review changes with 'git status' and commit if needed." -ForegroundColor Green

