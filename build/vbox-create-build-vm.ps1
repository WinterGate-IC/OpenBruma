# Create OpenBruma build VM in VirtualBox (run on Windows host)
# Usage: .\build\vbox-create-build-vm.ps1
$VBox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$VMName = "OpenBruma-Build"
$VMFolder = "G:\OpenBruma-VMs"
$DiskPath = "$VMFolder\$VMName\$VMName.vdi"
$ISO = "$VMFolder\archlinux-latest-x86_64.iso"

if (-not (Test-Path $ISO)) {
    Write-Host "Arch ISO not found at $ISO. Download first: .\build\download-arch-iso.ps1"
    exit 1
}

& $VBox createvm --name $VMName --ostype "ArchLinux_64" --register --basefolder $VMFolder
& $VBox modifyvm $VMName --memory 8192 --cpus 4 --vram 128 --graphicscontroller vboxsvga
& $VBox modifyvm $VMName --firmware efi64 --boot1 dvd --boot2 disk --boot3 none --boot4 none
& $VBox modifyvm $VMName --nic1 nat --nictype1 82540EM
& $VBox modifyvm $VMName --clipboard-mode bidirectional --draganddrop bidirectional
& $VBox createmedium disk --filename $DiskPath --size 61440 --format VDI --variant Standard
& $VBox storagectl $VMName --name "SATA" --add sata --controller IntelAhci
& $VBox storageattach $VMName --storagectl "SATA" --port 0 --device 0 --type hdd --medium $DiskPath
& $VBox storagectl $VMName --name "IDE" --add ide
& $VBox storageattach $VMName --storagectl "IDE" --port 0 --device 0 --type dvddrive --medium $ISO

# Shared folder for repo + ISO exchange (keep builds inside VM disk)
& $VBox sharedfolder add $VMName --name "OpenBrumaRepo" --hostpath "C:\Users\zerop\OpenBruma" --automount --auto-mount-point /mnt/openbruma-repo
& $VBox sharedfolder add $VMName --name "OpenBrumaOut" --hostpath "G:\OpenBruma-VMs\out" --automount --auto-mount-point /mnt/openbruma-out

New-Item -ItemType Directory -Path "G:\OpenBruma-VMs\out" -Force | Out-Null

Write-Host "Build VM created: $VMName"
Write-Host "Start with: VBoxManage startvm $VMName"
