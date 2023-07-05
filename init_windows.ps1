$env:FLASK_APP = 'C:\Users\Master Projekt\Documents\GitHub\vr-passthrough\src\server\filetransfer\file_transfer.py'

# Open the first terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting Server'; cd src/server/ ; python socket_server.py"

# Open the second terminal
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting coordinates endpoint at http://127.0.0.1:5000/directionFile/'; cd src/server/filetransfer/  ; flask run"


# Open the third terminal
# Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Starting coordinates endpoint at http://127.0.0.1:5000/directionFile/'; cd src/cam/ ; python camera.py"