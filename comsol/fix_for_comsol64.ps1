# Sanitizes BAK_IO.java / BAK_OI.java / BAK_OI_fair.java for university COMSOL 6.4.
# Removes ALL known File>Open killers in one pass (no GitHub needed).

$ErrorActionPreference = "Stop"
$files = @("BAK_IO.java", "BAK_OI.java", "BAK_OI_fair.java")

# Line patterns that break COMSOL 6.4 File>Open of compiled .class
$bad = @(
  'setIndex\("Dc"',
  'setIndex\("D_c"',
  'minput_velocity_src',
  'ConvectionDiffusion',
  'cdm_mem',
  'ReactingFlowDilutedSpecies',
  'rfd_blood',
  'rfd_dial',
  '\.set\("FluidFlow"',
  '\.set\("DilutedSpecies"'
)
$rx = [string]::Join('|', $bad)

foreach ($f in $files) {
  if (-not (Test-Path $f)) {
    Write-Host "SKIP missing $f"
    continue
  }
  $lines = Get-Content $f
  $kept = $lines | Where-Object { $_ -notmatch $rx }
  $removed = $lines.Count - $kept.Count
  Set-Content -Path $f -Value $kept
  Write-Host "OK $f  (removed $removed lines)"
}

Write-Host ""
Write-Host "Verify (should be empty except possible comments):"
Select-String -Path $files -Pattern 'ConvectionDiffusion|setIndex\("Dc"|setIndex\("D_c"|ReactingFlowDilutedSpecies|minput_velocity_src' -ErrorAction SilentlyContinue
Write-Host "Done."
