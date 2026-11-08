# Run with: .\run-lab.ps1 -IncludeSoak
# Each run uses no more than 5 VUs. The only run longer than 3 minutes is
# the 2-VU soak test explicitly allowed by the lab.
param(
    [switch]$IncludeSoak
)

$ErrorActionPreference = 'Stop'
if (-not (Get-Command k6 -ErrorAction SilentlyContinue)) {
    throw 'k6 is missing. Install it with: winget install k6 --source winget'
}

Set-Location $PSScriptRoot
foreach ($dir in @('reports', 'reports/metrics', 'reports/logs', 'reports/samples')) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

$exitCodes = [ordered]@{}

function Run-Test {
    param(
        [string]$Id,
        [string]$File,
        [string[]]$Extra = @(),
        [switch]$Html,
        [switch]$RawSamples
    )

    Write-Host "`n=== $Id / $File ===" -ForegroundColor Cyan
    $params = @(
        'run',
        '--summary-trend-stats', 'avg,min,med,max,p(90),p(95),p(99)',
        '--summary-export', "reports/metrics/$Id.json"
    )
    if ($Html) {
        $params += @('--out', "web-dashboard=export=reports/$Id.html")
    }
    if ($RawSamples) {
        $params += @('--out', "json=reports/samples/$Id.json")
    }
    $params += $Extra
    $params += $File

    # The run may exit with 99 when a strict performance threshold fails.
    # Continue to the next test and save the actual exit code.
    & k6 @params
    $status = $LASTEXITCODE
    $exitCodes[$Id] = $status
    Write-Host "Exit code ($Id): $status" -ForegroundColor Yellow
}

Run-Test '0.1-first' '01-first-test.js'
Run-Test '0.2-five-vus' '01-first-test.js' -Extra @('--vus','5','--duration','20s')
Run-Test '0.3-iterations' '01-first-test.js' -Extra @('--vus','5','--iterations','20')
Run-Test '0.4-pizza' '04-pizza-api.js'
Run-Test '0.5-no-token' '05-no-token.js'
Run-Test '0.6-normal' '06-thresholds.js'
Run-Test '0.6-p95-300' '06-thresholds.js' -Extra @('-e','P95=300')
Run-Test '0.7-requirement' '07-requirement.js'
Run-Test '0.7-tightened' '07-requirement.js' -Extra @('-e','REQ_P95=1')
Run-Test '0.8-original' '08-bug-hunt-original.js' -Extra @('--vus','5','--duration','20s')
Run-Test '0.8-explore' 'explore.js'
Run-Test '0.8-fixed' '08-bug-hunt.js' -Extra @('--vus','5','--duration','20s')

Run-Test 'a1-smoke' 'a1-smoke.js'
Run-Test 'a2-average' 'a2-average.js' -Html
Run-Test 'a3-stress' 'a3-stress.js' -Html
Run-Test 'a4-spike' 'a4-spike.js' -Html -RawSamples

if ($IncludeSoak) {
    Run-Test 'a5-soak' 'a5-soak.js' -Html -RawSamples
} else {
    Write-Host "`nSoak was skipped. Run '.\run-lab.ps1 -IncludeSoak' to include it." -ForegroundColor Yellow
    Write-Host 'You may also run just: k6 run --out web-dashboard=export=reports/a5-soak.html a5-soak.js'
}

$exitCodes | ConvertTo-Json | Set-Content 'reports/exit_codes.json' -Encoding UTF8
python tools/build_results.py
Write-Host "`nRESULTS.md updated using available measured metrics." -ForegroundColor Green
Write-Host 'IMPORTANT: Review the Part B spike and soak answers before submitting.'
