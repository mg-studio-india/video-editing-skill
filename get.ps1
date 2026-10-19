# get.ps1: one-line installer for video-editing-skill on Windows.
#
#   irm https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.ps1 | iex
#
# The pipeline runs in a bash environment: Git for Windows (Git Bash) or WSL. This finds one and runs get.sh in it,
# from the current folder (your creative workspace). Options: set $env:VIDEO_SKILLS_ARGS, e.g. "--project C:/Video --yes".
$ErrorActionPreference = "Stop"
$repo = if ($env:VIDEO_SKILLS_REPO) { $env:VIDEO_SKILLS_REPO } else { "mg-studio-india/video-editing-skill" }
$bash = $null
foreach ($c in @("$env:ProgramFiles\Git\bin\bash.exe", "${env:ProgramFiles(x86)}\Git\bin\bash.exe")) { if (Test-Path $c) { $bash = $c; break } }
if (-not $bash) { $cmd = Get-Command bash -ErrorAction SilentlyContinue; if ($cmd) { $bash = $cmd.Source } }
if (-not $bash) {
  Write-Host "video-skills needs a bash environment. Install Git for Windows (https://git-scm.com/download/win) or WSL (wsl --install), then run this line again."
  exit 1
}
$tmp = Join-Path $env:TEMP "video-skills-get.sh"
Invoke-RestMethod "https://raw.githubusercontent.com/$repo/main/get.sh" -OutFile $tmp
$args = if ($env:VIDEO_SKILLS_ARGS) { $env:VIDEO_SKILLS_ARGS.Split(" ") } else { @() }
& $bash $tmp @args
exit $LASTEXITCODE
