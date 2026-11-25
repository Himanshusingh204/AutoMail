# Runs draftbox at logon (dry-run unless you add --live). Run once in PowerShell from the repo root.
$exe = Join-Path $PSScriptRoot "..\.venv\Scripts\draftbox.exe"
$act = New-ScheduledTaskAction -Execute (Resolve-Path $exe) -Argument "run --accounts gmail --engine claude"
$trg = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "draftbox" -Action $act -Trigger $trg -Force
