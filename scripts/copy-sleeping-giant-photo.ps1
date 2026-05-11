# One-shot helper: copy the sourced Sleeping Giant photograph into
# public/about/sleeping-giant.jpg. Run once from the project root.
#
# The image was fetched by the art-director dispatch on 2026-05-11 from
# Wikimedia Commons (photographer: D. Gordon E. Robertson, CC-BY-SA 3.0).
# WebFetch saved the binary to a Claude tool-results temp folder; this
# script moves it to the canonical asset path expected by about.astro.

$src = "C:\Users\jayzh\.claude\projects\C--Users-jayzh-projects-macro-research-department\63e74897-7417-49f5-8f39-1031f5e21841\tool-results\webfetch-1778514279971-id8kjg.jpg"
$dstDir = Join-Path $PSScriptRoot "..\public\about"
$dst = Join-Path $dstDir "sleeping-giant.jpg"

if (-not (Test-Path $src)) {
    Write-Error "Source file not found: $src"
    exit 1
}

if (-not (Test-Path $dstDir)) {
    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
}

Copy-Item -Path $src -Destination $dst -Force
Write-Host "Copied to $dst"
