# Start LuciferOS dashboard (Windows PowerShell)
$VenvPython = "C:\LuciferOS_FULL\.venv\Scripts\python.exe"
$Dashboard = "c:\LuciferOS_FULL\ui\dashboard_complete.py"
Start-Process -NoNewWindow -FilePath $VenvPython -ArgumentList $Dashboard
Write-Host "Started dashboard (detached)."