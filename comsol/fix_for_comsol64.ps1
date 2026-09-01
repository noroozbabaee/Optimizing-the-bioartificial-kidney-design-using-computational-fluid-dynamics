# Sanitizes BAK_*.java for university COMSOL 6.4 (no GitHub needed).
# 1) Removes known bad lines
# 2) Rewrites init/Concentration .set("is"/"isc"/"isd") -> setIndex("c0", ...)

$ErrorActionPreference = "Stop"
$files = @("BAK_IO.java", "BAK_OI.java", "BAK_OI_fair.java")

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
  $text = Get-Content $f -Raw

  # Concentration / initial values: species name is NOT a property on COMSOL 6.4
  $text = $text -replace '\.feature\("init1"\)\.set\("is",\s*"C_in"\)', '.feature("init1").setIndex("c0", "C_in", 0)'
  $text = $text -replace '\.feature\("conc_b"\)\.set\("is",\s*"C_in"\)', '.feature("conc_b").setIndex("c0", "C_in", 0)'
  $text = $text -replace '\.feature\("init1"\)\.set\("isc",\s*"0"\)', '.feature("init1").setIndex("c0", "0", 0)'
  $text = $text -replace '\.feature\("init1"\)\.set\("isd",\s*"0"\)', '.feature("init1").setIndex("c0", "0", 0)'
  $text = $text -replace '\.feature\("conc_d"\)\.set\("isd",\s*"0"\)', '.feature("conc_d").setIndex("c0", "0", 0)'

  $lines = $text -split "`r?`n"
  $kept = $lines | Where-Object { $_ -notmatch $rx }
  Set-Content -Path $f -Value $kept
  Write-Host "OK $f"
}

Write-Host ""
Write-Host "Bad leftover checks (should be empty):"
Select-String -Path $files -Pattern 'ConvectionDiffusion|setIndex\("Dc"|setIndex\("D_c"|ReactingFlowDilutedSpecies|\.set\("is"|\.set\("isc"|\.set\("isd"' -ErrorAction SilentlyContinue
Write-Host "Done."
