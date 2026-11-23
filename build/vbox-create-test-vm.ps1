# Create OpenBruma test VM in VirtualBox (run on Windows host)
# Usage: .\build\vbox-create-test-vm.ps1
$VBox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$VMName = "OpenBruma-Test"
$VMFolder = "G:\OpenBruma-VMs"
$DiskPath = "$VMFolder\$VMName\$VMName.vdi"

& $VBox createvm --name $VMName --ostype "ArchLinux_64" --register --basefolder $VMFolder
& $VBox modifyvm $VMName --memory 4096 --cpus 2 --vram 128 --graphicscontroller vboxsvga
& $VBox modifyvm $VMName --firmware efi64 --boot1 dvd --boot2 disk --boot3 none --boot4 none
& $VBox modifyvm $VMName --nic1 nat --nictype1 82540EM
& $VBox createmedium disk --filename $DiskPath --size 20480 --format VDI --variant Standard
& $VBox storagectl $VMName --name "SATA" --add sata --controller IntelAhci
& $VBox storageattach $VMName --storagectl "SATA" --port 0 --device 0 --type hdd --medium $DiskPath
& $VBox storagectl $VMName --name "IDE" --add ide

Write-Host "Test VM created: $VMName"
Write-Host "Attach ISO before boot: VBoxManage storageattach $VMName --storagectl IDE --port 0 --device 0 --type dvddrive --medium <iso>"
