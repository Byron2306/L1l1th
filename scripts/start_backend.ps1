# Start LuciferOS backend (Windows PowerShell)
$VenvPython = "C:\LuciferOS_FULL\.venv\Scripts\python.exe"
$Backend = "c:\LuciferOS_FULL\tools\lilith_complete.py"
Start-Process -NoNewWindow -FilePath $VenvPython -ArgumentList $Backend
Write-Host "Started backend (detached)."