while worcking:
https://www.youtube.com/shorts/YP1jf1zOvU4

# Mustek-1200-UB-Plus-on-win10-11
Use the Mustek 1200 UB Plus scanner 
on Windows 10/11 via WSL and Linux SANE. 
Windows handles USB forwarding, 
Ubuntu WSL runs SANE with the gt68xx backend and firmware. 
This guide provides simple, repeatable steps for beginners to set up, 
test, and automate scanning without !MODERN! drivers.

Windows 10/11
   └─ usbipd-win (USB forwarding)
       └─ WSL (Ubuntu)
           └─ SANE (gt68xx backend)
               └─ Mustek 1200 UB Plus


README.txt
==========

Mustek 1200 UB Plus Scanner on Windows 10 / 11
(using WSL + Linux SANE)

Last tested: Windows 10/11, usbipd-win 5.x, Ubuntu WSL

------------------------------------------------------------
IMPORTANT – PLEASE READ FIRST
------------------------------------------------------------

• The Mustek 1200 UB Plus has NO working Windows 10/11 driver.
• It CANNOT be used directly by Windows scan programs.
• The ONLY reliable method is:

  Windows → WSL (Ubuntu) → Linux SANE → Scanner

This guide explains EXACTLY how to do that.

------------------------------------------------------------
WHAT YOU WILL NEED
------------------------------------------------------------

1. Windows 10 or Windows 11 (64-bit)
2. Internet connection
3. Mustek 1200 UB Plus scanner
4. Firmware file named:

   SBfw.usb   (this is NORMAL and correct)

------------------------------------------------------------
STEP 1 – ENABLE WSL ON WINDOWS
------------------------------------------------------------

1. Open PowerShell AS ADMINISTRATOR
2. Run:

   wsl --install

3. Restart Windows when asked

After restart, verify:

   wsl --status

------------------------------------------------------------
STEP 2 – INSTALL UBUNTU (WSL)
------------------------------------------------------------

In PowerShell:

   wsl --install -d Ubuntu

Open Ubuntu once from the Start Menu and finish setup
(username and password).

------------------------------------------------------------
STEP 3 – INSTALL usbipd-win (USB SUPPORT)
------------------------------------------------------------

1. Download from:
   https://github.com/dorssel/usbipd-win/releases

2. Install:
   usbipd-win-5.x.x-x64.msi

3. Restart Windows

Verify in PowerShell:

   usbipd --version

------------------------------------------------------------
STEP 4 – CONNECT THE SCANNER TO WSL
------------------------------------------------------------

1. Plug in the Mustek scanner
2. Open PowerShell AS ADMINISTRATOR
3. Run:

   usbipd list

4. Note the BUSID (example: 2-1)

5. Attach it to Ubuntu:

   usbipd attach --busid 2-1 --wsl Ubuntu

------------------------------------------------------------
STEP 5 – CHECK USB INSIDE UBUNTU
------------------------------------------------------------

Open Ubuntu (WSL):

   lsusb

You must see the Mustek scanner listed.
If not, STOP – USB is not attached.

------------------------------------------------------------
STEP 6 – INSTALL SANE (SCANNER SOFTWARE)
------------------------------------------------------------

In Ubuntu:

   sudo apt update
   sudo apt install sane sane-utils libsane-common

------------------------------------------------------------
STEP 7 – ENABLE THE CORRECT BACKEND
------------------------------------------------------------

Edit this file:

   sudo nano /etc/sane.d/dll.conf

Make sure this line exists and is NOT commented:

   gt68xx

Save and exit:
CTRL+O → Enter → CTRL+X

------------------------------------------------------------
STEP 8 – PREPARE THE FIRMWARE (VERY IMPORTANT)
------------------------------------------------------------

Your firmware file is named:

   SBfw.usb

This is CORRECT.

Windows side:
1. Create folder:
   C:\Temp
2. Copy:
   SBfw.usb
   into:
   C:\Temp\SBfw.usb

------------------------------------------------------------
STEP 9 – INSTALL THE FIRMWARE INTO LINUX
------------------------------------------------------------

In Ubuntu (copy-paste exactly):

1. Create firmware folder:

   sudo mkdir -p /usr/share/sane/gt68xx

2. Copy and RENAME the firmware in one step:

   sudo cp /mnt/c/Temp/SBfw.usb /usr/share/sane/gt68xx/PS1fw.usb

3. Set permissions:

   sudo chmod 644 /usr/share/sane/gt68xx/PS1fw.usb

------------------------------------------------------------
STEP 10 – TELL SANE WHERE THE FIRMWARE IS
------------------------------------------------------------

Open config file:

   sudo nano /etc/sane.d/gt68xx.conf

Add this line at the END:

   firmware /usr/share/sane/gt68xx/PS1fw.usb

Save and exit:
CTRL+O → Enter → CTRL+X

------------------------------------------------------------
STEP 11 – TEST THE SCANNER
------------------------------------------------------------

In Ubuntu:

   scanimage -L

Expected result:
Mustek 1200 UB Plus is detected.

------------------------------------------------------------
STEP 12 – TEST A SCAN
------------------------------------------------------------

In Ubuntu:

   scanimage --resolution 300 --mode Color > test_scan.pnm

Open from Windows:

   \\wsl$\Ubuntu\home\<your-username>\test_scan.pnm

------------------------------------------------------------
FINAL NOTES
------------------------------------------------------------

• This setup WORKS on Windows 10 and 11
• No unsigned drivers are used
• The scanner works via command line and scripts
• This setup is stable and repeatable
• WSL can be backed up using:

   wsl --export Ubuntu ubuntu_backup.tar

------------------------------------------------------------
END OF README
------------------------------------------------------------
