$ssh = New-SSHSession -ComputerName "192.168.137.13" -Credential pi
$ssh | Enter-SSHPassword -Password "vrpass123"