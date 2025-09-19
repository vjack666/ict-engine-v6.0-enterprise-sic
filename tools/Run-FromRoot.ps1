param(
  [Parameter(Mandatory=$true)][string]$ScriptPath,
  [Parameter(Mandatory=$false)][string]$Args
)
Push-Location $PSScriptRoot/..
try {
  python -X utf8 $ScriptPath $Args
} finally {
  Pop-Location
}
