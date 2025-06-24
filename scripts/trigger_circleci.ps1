# CircleCI API Trigger Script (PowerShell)
param(
    [string]$Token = $env:CIRCLECI_TOKEN,
    [string]$Org = "gh/your-username",
    [string]$Project = "manimAnimationAgent", 
    [string]$Branch = "main",
    [ValidateSet("ci-cd", "video-rendering")]
    [string]$Workflow = "ci-cd",
    [string]$VideoId = "",
    [switch]$ForceDeploy,
    [string]$Status = "",
    [switch]$List,
    [switch]$Help
)

if ($Help) {
    Write-Host "CircleCI API Trigger Script" -ForegroundColor Cyan
    Write-Host "Usage: .\trigger_circleci.ps1 -Token YOUR_TOKEN [options]"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\trigger_circleci.ps1 -Token abc123 -Workflow ci-cd"
    Write-Host "  .\trigger_circleci.ps1 -Token abc123 -Workflow video-rendering -VideoId vid123"
    exit 0
}

if (-not $Token) {
    Write-Host "❌ Token required. Use -Token parameter or set CIRCLECI_TOKEN env var" -ForegroundColor Red
    exit 1
}

$url = "https://circleci.com/api/v2/project/$Org/$Project/pipeline"
$headers = @{ "Content-Type" = "application/json"; "Circle-Token" = $Token }

if ($Status) {
    $statusUrl = "https://circleci.com/api/v2/pipeline/$Status"
    $response = Invoke-RestMethod -Uri $statusUrl -Headers $headers
    $response | ConvertTo-Json -Depth 3
    exit 0
}

if ($List) {
    $listUrl = "https://circleci.com/api/v2/project/$Org/$Project/pipeline?limit=10"
    $response = Invoke-RestMethod -Uri $listUrl -Headers $headers
    $response | ConvertTo-Json -Depth 3
    exit 0
}

$params = @{ workflow = $Workflow; force_deploy = $ForceDeploy.IsPresent }
if ($VideoId) { $params.video_id = $VideoId }

$body = @{ branch = $Branch; parameters = $params } | ConvertTo-Json -Depth 3

Write-Host "🚀 Triggering $Workflow workflow..." -ForegroundColor Blue
$response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body

Write-Host "✅ Pipeline triggered!" -ForegroundColor Green
Write-Host "Pipeline ID: $($response.id)"
Write-Host "Dashboard: https://app.circleci.com/pipelines/$Org/$Project/$($response.number)" 