# get.ps1: one-line installer for video-editing-skill on Windows.
#
#   irm https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.ps1 | iex
#
# The pipeline runs in Git Bash (Git for Windows). This checks the Windows prerequisites, then runs get.sh in Git Bash
# from the current folder (your creative workspace). Options: set $env:VIDEO_SKILLS_ARGS, e.g. "--project C:/Video --yes".
# Wrapped in a script block so that `iex` never closes your PowerShell window when something is missing.
& {
  $ErrorActionPreference = "Stop"
  $repo = if ($env:VIDEO_SKILLS_REPO) { $env:VIDEO_SKILLS_REPO } else { "mg-studio-india/video-editing-skill" }

  # Git Bash, never System32\bash.exe (WSL cannot read this session's C:\ paths)
  $bash = $null
  foreach ($c in @("$env:ProgramFiles\Git\bin\bash.exe", "${env:ProgramFiles(x86)}\Git\bin\bash.exe", "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe")) {
    if ($c -and (Test-Path $c)) { $bash = $c; break }
  }
  if (-not $bash) {
    $cmd = Get-Command bash -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch "(?i)system32") { $bash = $cmd.Source }
  }

  # What is missing, with the winget line that installs it
  $missing = @()
  if (-not $bash) { $missing += "Git.Git" }
  $py = Get-Command python -ErrorAction SilentlyContinue
  if ((-not $py -or $py.Source -match "(?i)WindowsApps") -and -not (Get-Command py -ErrorAction SilentlyContinue)) { $missing += "Python.Python.3.12" }
  if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { $missing += "Gyan.FFmpeg" }
  if (-not (Get-Command sox -ErrorAction SilentlyContinue)) { $missing += "ChrisBagwell.SoX" }
  if ($missing.Count -gt 0) {
    Write-Host "video-skills needs: $($missing -join ', ')"
    Write-Host "Install them, open a NEW terminal, and run the one-liner again:"
    foreach ($m in $missing) { Write-Host "  winget install --id $m -e" }
    if (-not $bash) { return }
    Write-Host "(continuing: Git Bash is present, the installer will say what is still missing)"
  }

  $tmp = Join-Path $env:TEMP "video-skills-get.sh"
  Invoke-RestMethod "https://raw.githubusercontent.com/$repo/main/get.sh" -OutFile $tmp
  $pass = @(if ($env:VIDEO_SKILLS_ARGS) { $env:VIDEO_SKILLS_ARGS -split "\s+" | Where-Object { $_ } })
  & $bash $tmp @pass
  if ($LASTEXITCODE -ne 0) { Write-Host "video-skills: the installer stopped (exit $LASTEXITCODE); see the message above." }
}
