# CircleCI Configuration Validation Script (PowerShell)
# This script validates the CircleCI setup and dependencies on Windows

param(
    [switch]$Detailed = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🔍 CircleCI Configuration Validation" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Function to print colored output
function Write-Status {
    param(
        [string]$Status,
        [string]$Message
    )
    
    switch ($Status) {
        "SUCCESS" { Write-Host "✅ $Message" -ForegroundColor Green }
        "WARNING" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "❌ $Message" -ForegroundColor Red }
        default { Write-Host "ℹ️  $Message" -ForegroundColor White }
    }
}

# Check if CircleCI config exists
Write-Host "🔧 Checking CircleCI Configuration..." -ForegroundColor Blue
if (Test-Path ".circleci/config.yml") {
    Write-Status "SUCCESS" "CircleCI config file found"
} else {
    Write-Status "ERROR" "CircleCI config file not found at .circleci/config.yml"
    exit 1
}

# Validate YAML syntax
Write-Host "📝 Validating YAML syntax..." -ForegroundColor Blue
try {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $yamlCheck = python -c "import yaml; yaml.safe_load(open('.circleci/config.yml'))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "SUCCESS" "YAML syntax is valid"
        } else {
            Write-Status "ERROR" "YAML syntax is invalid"
            exit 1
        }
    } else {
        Write-Status "WARNING" "Python not available - skipping YAML validation"
    }
} catch {
    Write-Status "WARNING" "Could not validate YAML syntax"
}

# Check for required files
Write-Host "📁 Checking required files..." -ForegroundColor Blue
$requiredFiles = @(
    "requirements-github-actions.txt",
    "scripts/check_video_queue.py",
    "scripts/github_video_renderer.py",
    "test_simple_manim.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Status "SUCCESS" "Required file found: $file"
    } else {
        Write-Status "ERROR" "Required file missing: $file"
    }
}

# Check environment variables
Write-Host "🌍 Checking environment variables..." -ForegroundColor Blue
$requiredEnvVars = @(
    "APPWRITE_ENDPOINT",
    "APPWRITE_PROJECT_ID", 
    "APPWRITE_API_KEY",
    "GEMINI_API_KEY"
)

$optionalEnvVars = @(
    "OPENAI_API_KEY",
    "MEM0_API_KEY", 
    "TAVILY_API_KEY",
    "ELEVENLABS_API_KEY"
)

foreach ($var in $requiredEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Status "SUCCESS" "Required environment variable set: $var"
    } else {
        Write-Status "ERROR" "Required environment variable missing: $var"
    }
}

foreach ($var in $optionalEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Status "SUCCESS" "Optional environment variable set: $var"
    } else {
        Write-Status "WARNING" "Optional environment variable missing: $var"
    }
}

# Check Python and pip
Write-Host "🐍 Checking Python environment..." -ForegroundColor Blue
try {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonVersion = python --version 2>&1
        Write-Status "SUCCESS" "Python found: $pythonVersion"
    } else {
        Write-Status "ERROR" "Python not found"
    }
} catch {
    Write-Status "ERROR" "Python check failed"
}

try {
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        $pipVersion = pip --version 2>&1
        Write-Status "SUCCESS" "pip found: $pipVersion"
    } else {
        Write-Status "ERROR" "pip not found"
    }
} catch {
    Write-Status "ERROR" "pip check failed"
}

# Test CircleCI CLI if available
Write-Host "🔄 Checking CircleCI CLI..." -ForegroundColor Blue
try {
    if (Get-Command circleci -ErrorAction SilentlyContinue) {
        $circleciVersion = circleci version 2>&1
        Write-Status "SUCCESS" "CircleCI CLI found: $circleciVersion"
        
        Write-Host "🧪 Validating CircleCI config with CLI..." -ForegroundColor Blue
        $configValidation = circleci config validate .circleci/config.yml 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "SUCCESS" "CircleCI configuration is valid"
        } else {
            Write-Status "ERROR" "CircleCI configuration validation failed"
            if ($Detailed) {
                Write-Host $configValidation -ForegroundColor Red
            }
        }
    } else {
        Write-Status "WARNING" "CircleCI CLI not found - install from: https://circleci.com/docs/local-cli/"
    }
} catch {
    Write-Status "WARNING" "CircleCI CLI check failed"
}

# Check for common issues
Write-Host "🔍 Checking for common issues..." -ForegroundColor Blue

# Check if using correct requirements file
$configContent = Get-Content ".circleci/config.yml" -Raw
if ($configContent -match "requirements-github-actions\.txt") {
    Write-Status "SUCCESS" "Using correct requirements file (requirements-github-actions.txt)"
} else {
    Write-Status "ERROR" "Not using requirements-github-actions.txt in CircleCI config"
}

# Check for GraphViz dependencies
if ($configContent -match "graphviz-dev") {
    Write-Status "SUCCESS" "GraphViz development headers included"
} else {
    Write-Status "ERROR" "GraphViz development headers missing (needed for pygraphviz)"
}

# Check for timeout configurations
if ($configContent -match "no_output_timeout") {
    Write-Status "SUCCESS" "Timeout configurations found"
} else {
    Write-Status "WARNING" "No timeout configurations found"
}

# Check Docker availability (for local testing)
Write-Host "🐳 Checking Docker..." -ForegroundColor Blue
try {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        $dockerVersion = docker --version 2>&1
        Write-Status "SUCCESS" "Docker found: $dockerVersion"
    } else {
        Write-Status "WARNING" "Docker not found (optional for local testing)"
    }
} catch {
    Write-Status "WARNING" "Docker check failed"
}

Write-Host ""
Write-Host "🎯 Validation Summary" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "✅ Check the output above for any ERROR messages" -ForegroundColor Green
Write-Host "⚠️  WARNING messages are optional but recommended to address" -ForegroundColor Yellow
Write-Host "💡 Install missing dependencies before running CircleCI jobs" -ForegroundColor Blue
Write-Host ""
Write-Host "📚 For setup instructions, see: CIRCLECI_SETUP.md" -ForegroundColor White
Write-Host "🔧 For API triggers, see: scripts/circleci_api_examples.md" -ForegroundColor White

# Additional Windows-specific tips
Write-Host ""
Write-Host "🪟 Windows-specific tips:" -ForegroundColor Magenta
Write-Host "- Use PowerShell as Administrator for environment variable changes" -ForegroundColor White
Write-Host "- Install Python from python.org or Microsoft Store" -ForegroundColor White
Write-Host "- Consider using Windows Subsystem for Linux (WSL) for better compatibility" -ForegroundColor White 