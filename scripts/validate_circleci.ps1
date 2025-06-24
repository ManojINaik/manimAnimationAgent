# CircleCI Configuration Validation Script (PowerShell)
# This script validates the CircleCI configuration file

$ErrorActionPreference = "Stop"

Write-Host "🔍 Validating CircleCI configuration..." -ForegroundColor Cyan

# Check if CircleCI CLI is installed
try {
    circleci version | Out-Null
    Write-Host "✅ CircleCI CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ CircleCI CLI not found. Please install it:" -ForegroundColor Red
    Write-Host "   Visit: https://circleci.com/docs/local-cli/" -ForegroundColor Yellow
    Write-Host "   Or run: choco install circleci-cli" -ForegroundColor Yellow
    exit 1
}

# Check if configuration file exists
if (-not (Test-Path ".circleci/config.yml")) {
    Write-Host "❌ .circleci/config.yml not found!" -ForegroundColor Red
    exit 1
}

# Validate the configuration
Write-Host "📋 Validating .circleci/config.yml..." -ForegroundColor Cyan

try {
    circleci config validate .circleci/config.yml
    Write-Host "✅ CircleCI configuration is valid!" -ForegroundColor Green
} catch {
    Write-Host "❌ CircleCI configuration has errors. Please fix them before proceeding." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Process the configuration
Write-Host "🔧 Processing configuration..." -ForegroundColor Cyan
try {
    circleci config process .circleci/config.yml > .circleci/processed-config.yml
    Write-Host "📄 Processed configuration saved to .circleci/processed-config.yml" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not process configuration" -ForegroundColor Yellow
}

# Check for common issues
Write-Host "🔍 Checking for common issues..." -ForegroundColor Cyan

$configContent = Get-Content ".circleci/config.yml" -Raw

# Check if required environment variables are documented
if ($configContent -match "APPWRITE_ENDPOINT" -and $configContent -match "GEMINI_API_KEY") {
    Write-Host "✅ Required environment variables are referenced" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some required environment variables might be missing" -ForegroundColor Yellow
}

# Check for caching
if ($configContent -match "restore_cache" -and $configContent -match "save_cache") {
    Write-Host "✅ Caching is configured" -ForegroundColor Green
} else {
    Write-Host "⚠️  Caching might not be properly configured" -ForegroundColor Yellow
}

# Check for workflows
$workflowMatches = [regex]::Matches($configContent, "workflows:")
if ($workflowMatches.Count -gt 0) {
    Write-Host "✅ Workflows are configured ($($workflowMatches.Count) found)" -ForegroundColor Green
} else {
    Write-Host "⚠️  No workflows found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 CircleCI configuration validation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Commit the configuration to your repository" -ForegroundColor White
Write-Host "2. Set up environment variables in CircleCI project settings" -ForegroundColor White
Write-Host "3. Trigger your first build" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: CIRCLECI_SETUP.md" -ForegroundColor Yellow 