param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$TraceSolPython = $null
$TraceSolArgs = @()
if (Test-Path -LiteralPath (Join-Path $PSScriptRoot '.venv\Scripts\python.exe')) {
    $TraceSolPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
} elseif (Get-Command py.exe -ErrorAction SilentlyContinue) {
    $TraceSolPython = (Get-Command py.exe).Source
    $TraceSolArgs = @('-3')
} else {
    $TraceSolCandidates = @('python.exe','python3.exe')
    foreach ($TraceSolCandidate in $TraceSolCandidates) {
        $TraceSolCommand = Get-Command $TraceSolCandidate -ErrorAction SilentlyContinue
        if ($TraceSolCommand -and $TraceSolCommand.Source -notlike '*\Microsoft\WindowsApps\*') {
            $TraceSolPython = $TraceSolCommand.Source
            break
        }
    }
}
# Also support the Python runtime bundled with the Codex desktop application.
if (-not $TraceSolPython) {
    $TraceSolRuntime = Get-ChildItem -Path (Join-Path $env:ProgramFiles 'WindowsApps\OpenAI.CodexPrimaryRuntime.*\dependencies\python\python.exe') -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
    if ($TraceSolRuntime) { $TraceSolPython = $TraceSolRuntime.FullName }
}
if (-not $TraceSolPython) {
    Write-Host 'Python 3.10 or later is needed. Install it from https://www.python.org/downloads/ and run this launcher again.'
    exit 1
}
Write-Host "Open http://127.0.0.1:$Port in your browser after the ready message. Keep this window open while using TraceSol."
& $TraceSolPython @TraceSolArgs (Join-Path $PSScriptRoot 'app.py') --port $Port
exit $LASTEXITCODE
