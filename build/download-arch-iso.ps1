# Download current Arch Linux ISO (run on Windows host)
$OutDir = "G:\OpenBruma-VMs"
$Mirror = "https://geo.mirror.pkgbuild.com/iso/latest"
$Html = (Invoke-WebRequest -Uri $Mirror/ -UseBasicParsing).Content
# find iso filename
if ($Html -match 'archlinux-[\d.]+-x86_64\.iso') { $Iso = $Matches[0] } else { Write-Error "Could not find ISO filename"; exit 1 }
$Url = "$Mirror/$Iso"
$Dest = "$OutDir\$Iso"
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
Write-Host "Downloading $Url"
# disable proxy env
$env:all_proxy=""; $env:ALL_PROXY=""
curl.exe -L -o $Dest $Url
# checksum
$ShaUrl = "$Mirror/sha256sums.txt"
curl.exe -L -o "$OutDir\sha256sums.txt" $ShaUrl
Write-Host "Saved to $Dest"
Get-FileHash $Dest -Algorithm SHA256
