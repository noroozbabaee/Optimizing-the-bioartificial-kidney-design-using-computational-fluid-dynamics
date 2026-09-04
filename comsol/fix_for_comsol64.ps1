# One-shot COMSOL 6.4 sanitizer for Desktop\BAK (no GitHub).
# Removes every line pattern that has caused Unknown parameter/feature on this build.

$ErrorActionPreference = "Stop"
$files = @("BAK_IO.java", "BAK_OI.java", "BAK_OI_fair.java")

$bad = @(
  'setIndex\("Dc"',
  'setIndex\("D_c"',
  'setIndex\("c0"',
  'setIndex\("N0"',
  'minput_velocity_src',
  'ConvectionDiffusion',
  'cdm_mem',
  'ReactingFlowDilutedSpecies',
  'rfd_blood',
  'rfd_dial',
  '\.set\("FluidFlow"',
  '\.set\("DilutedSpecies"',
  '\.set\("is"',
  '\.set\("isc"',
  '\.set\("isd"',
  'field\("concentration"\)\.field',
  'field\("concentration"\)\.component'
)
$rx = [string]::Join('|', $bad)

foreach ($f in $files) {
  if (-not (Test-Path $f)) { Write-Host "SKIP $f"; continue }
  $t = Get-Content $f -Raw
  # Point flux expressions at default species names c / c2
  $t = $t -replace 'Vmax_A\*\(is/\(Km_bl\+is\)-isc/\(Km_bl\+isc\)\)', 'Vmax_A*(c/(Km_bl+c)-c2/(Km_bl+c2))'
  $t = $t -replace 'Vmax_ap\*isc/\(Km_ap\+isc\)', 'Vmax_ap*c2/(Km_ap+c2)'
  $t = $t -replace 'tds\.ndflux_is', 'tds.ndflux_c'
  $t = $t -replace 'set\("expr", "is"\)', 'set("expr", "c")'
  $t = $t -replace 'set\("expr", "isc"\)', 'set("expr", "c2")'
  $lines = $t -split "`r?`n"
  $kept = $lines | Where-Object { $_ -notmatch $rx }
  Set-Content $f $kept
  Write-Host "OK $f  removed $($lines.Count - $kept.Count) lines"
}

Write-Host "`nLeftover bad API (should be empty):"
Select-String -Path $files -Pattern 'setIndex\("c0"|setIndex\("Dc"|setIndex\("N0"|ConvectionDiffusion|\.set\("is"|ReactingFlowDilutedSpecies|field\("concentration"\)\.field' -ErrorAction SilentlyContinue
Write-Host "Done. del *.class then comsolcompile."
