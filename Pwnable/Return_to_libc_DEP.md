# 「Return-to-libcでDEPを回避してみる」を再現(未完成)

ももいろテクノロジーさんの以下の記事を再現してみたというメモです
http://inaz2.hatenablog.com/entry/2014/03/23/233759

64bitでもできないか試したくてやってみました.

`DEP(Data Execution Prevention)`とは
>DEP（Data Execution Prevention）は、その名前の通りデータエリアでのプログラムの実行を防止するという、ハードウェアで実装された機能です.<br>
(中略)DEPは、スタックエリアやヒープエリア、つまりコードエリア以外の領域でプログラムが実行されると、プログラムを異常終了させます。<br>
出典元: DEPの仕組みとその回避手法 (1/3)https://www.atmarkit.co.jp/ait/articles/1410/15/news004.html


## 環境

```
$ uname -a
Linux vagrant 4.15.0-29-generic #31-Ubuntu SMP Tue Jul 17 15:39:52 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux

$ gcc --version
gcc (Ubuntu 7.4.0-1ubuntu1~18.04) 7.4.0
Copyright (C) 2017 Free Software Foundation, Inc.
```

## 脆弱性のあるプログラムを用意

次は, バッファサイズ300で、第一引数の入力によりスタックバッファオーバーフローが起こるコード.
```
#include<stdio.h>
#include<stdlib.h>
#include<string.h>

//buffer size: 300
//stack over flow

int main(int argc, char *argv[]) {
  char buf[300] = {}; // set all bytes to zero
  printf("buf = %p\n", buf);
  printf("puts = %p\n", puts); // puts func
  printf("system = %p\n", system); // system func

  strcpy(buf, argv[1]);
  puts(buf);
  return 0;
}
```

以下実行例
```
$./bof
buf = 0x7ffd61feb6f0
puts = 0x7f06845859c0
system = 0x7f0684554440
Segmentation fault (core dumped)
```
ASLR, SSPを無効にして`DEP(Data Execution Prevention)`のみ有効にする.

```
$ sudo sysctl -w kernel.randomize_va_space=0
kernel.randomize_va_space = 0
$ gcc -fno-stack-protector -o bof bof.c
```

objdumpコマンドで実行ファイルのプログラムヘッダを調べると、STACKのところにxビットが立っていない(flags rw-)、つまりスタック領域のデータが実行不可になっていることが確認できる。
```
$ objdump -x bof
bof:     file format elf64-x86-64
bof
architecture: i386:x86-64, flags 0x00000150:
HAS_SYMS, DYNAMIC, D_PAGED
start address 0x00000000000005f0

Program Header:
    PHDR off    0x0000000000000040 vaddr 0x0000000000000040 paddr 0x0000000000000040 align 2**3
         filesz 0x00000000000001f8 memsz 0x00000000000001f8 flags r--
  INTERP off    0x0000000000000238 vaddr 0x0000000000000238 paddr 0x0000000000000238 align 2**0
         filesz 0x000000000000001c memsz 0x000000000000001c flags r--
    LOAD off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**21
         filesz 0x00000000000009b0 memsz 0x00000000000009b0 flags r-x
    LOAD off    0x0000000000000da0 vaddr 0x0000000000200da0 paddr 0x0000000000200da0 align 2**21
         filesz 0x0000000000000270 memsz 0x0000000000000278 flags rw-
 DYNAMIC off    0x0000000000000db0 vaddr 0x0000000000200db0 paddr 0x0000000000200db0 align 2**3
         filesz 0x00000000000001f0 memsz 0x00000000000001f0 flags rw-
    NOTE off    0x0000000000000254 vaddr 0x0000000000000254 paddr 0x0000000000000254 align 2**2
         filesz 0x0000000000000044 memsz 0x0000000000000044 flags r--
EH_FRAME off    0x0000000000000868 vaddr 0x0000000000000868 paddr 0x0000000000000868 align 2**2
         filesz 0x000000000000003c memsz 0x000000000000003c flags r--
   STACK off    0x0000000000000000 vaddr 0x0000000000000000 paddr 0x0000000000000000 align 2**4
         filesz 0x0000000000000000 memsz 0x0000000000000000 flags rw-
   RELRO off    0x0000000000000da0 vaddr 0x0000000000200da0 paddr 0x0000000000200da0 align 2**0
         filesz 0x0000000000000260 memsz 0x0000000000000260 flags r--
...
```

`ldd`コマンドで共有ライブラリを調べたら, libcがリンクされていることが分かりました.
```
$ ldd bof
	linux-vdso.so.1 (0x00007ffc177c1000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f6952ea9000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f695349c000)
```

```
$ gdb -q system
Reading symbols from system...(no debugging symbols found)...done.
gdb-peda$ b main
Breakpoint 1 at 0x64e
gdb-peda$ r
Starting program: /home/vagrant/momoiro/system
[----------------------------------registers-----------------------------------]
RAX: 0x55555555464a (<main>:	push   rbp)
RBX: 0x0
RCX: 0x555555554670 (<__libc_csu_init>:	push   r15)
RDX: 0x7fffffffe2b8 --> 0x7fffffffe511 ("LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc"...)
RSI: 0x7fffffffe2a8 --> 0x7fffffffe4f4 ("/home/vagrant/momoiro/system")
RDI: 0x1
RBP: 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
RIP: 0x55555555464e (<main+4>:	lea    rdi,[rip+0x9f]        # 0x5555555546f4)
R8 : 0x7ffff7dd0d80 --> 0x0
R9 : 0x7ffff7dd0d80 --> 0x0
R10: 0x0
R11: 0x0
R12: 0x555555554540 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffe2a0 --> 0x1
R14: 0x0
R15: 0x0
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x555555554645 <frame_dummy+5>:	jmp    0x5555555545b0 <register_tm_clones>
   0x55555555464a <main>:	push   rbp
   0x55555555464b <main+1>:	mov    rbp,rsp
=> 0x55555555464e <main+4>:	lea    rdi,[rip+0x9f]        # 0x5555555546f4
   0x555555554655 <main+11>:	call   0x555555554520 <system@plt>
   0x55555555465a <main+16>:	mov    eax,0x0
   0x55555555465f <main+21>:	pop    rbp
   0x555555554660 <main+22>:	ret
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
0008| 0x7fffffffe1c8 --> 0x7ffff7a05b97 (<__libc_start_main+231>:	mov    edi,eax)
0016| 0x7fffffffe1d0 --> 0x1
0024| 0x7fffffffe1d8 --> 0x7fffffffe2a8 --> 0x7fffffffe4f4 ("/home/vagrant/momoiro/system")
0032| 0x7fffffffe1e0 --> 0x100008000
0040| 0x7fffffffe1e8 --> 0x55555555464a (<main>:	push   rbp)
0048| 0x7fffffffe1f0 --> 0x0
0056| 0x7fffffffe1f8 --> 0x3884e47b9cc204a2
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x000055555555464e in main ()

gdb-peda$ pdisass main
Dump of assembler code for function main:
   0x000055555555464a <+0>:	push   rbp
   0x000055555555464b <+1>:	mov    rbp,rsp
   0x000055555555464e <+4>:	lea    rdi,[rip+0x9f]        # 0x5555555546f4
   0x0000555555554655 <+11>:	call   0x555555554520 <system@plt>
   0x000055555555465a <+16>:	mov    eax,0x0
   0x000055555555465f <+21>:	pop    rbp
   0x0000555555554660 <+22>:	ret
End of assembler dump.

gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x55555555464a (<main>:	push   rbp)
RBX: 0x0
RCX: 0x555555554670 (<__libc_csu_init>:	push   r15)
RDX: 0x7fffffffe2b8 --> 0x7fffffffe511 ("LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc"...)
RSI: 0x7fffffffe2a8 --> 0x7fffffffe4f4 ("/home/vagrant/momoiro/system")
RDI: 0x5555555546f4 --> 0x68732f6e69622f ('/bin/sh')
RBP: 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
RIP: 0x555555554655 (<main+11>:	call   0x555555554520 <system@plt>)
R8 : 0x7ffff7dd0d80 --> 0x0
R9 : 0x7ffff7dd0d80 --> 0x0
R10: 0x0
R11: 0x0
R12: 0x555555554540 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffe2a0 --> 0x1
R14: 0x0
R15: 0x0
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x55555555464a <main>:	push   rbp
   0x55555555464b <main+1>:	mov    rbp,rsp
   0x55555555464e <main+4>:	lea    rdi,[rip+0x9f]        # 0x5555555546f4
=> 0x555555554655 <main+11>:	call   0x555555554520 <system@plt>
   0x55555555465a <main+16>:	mov    eax,0x0
   0x55555555465f <main+21>:	pop    rbp
   0x555555554660 <main+22>:	ret
   0x555555554661:	nop    WORD PTR cs:[rax+rax*1+0x0]
Guessed arguments:
arg[0]: 0x5555555546f4 --> 0x68732f6e69622f ('/bin/sh')
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
0008| 0x7fffffffe1c8 --> 0x7ffff7a05b97 (<__libc_start_main+231>:	mov    edi,eax)
0016| 0x7fffffffe1d0 --> 0x1
0024| 0x7fffffffe1d8 --> 0x7fffffffe2a8 --> 0x7fffffffe4f4 ("/home/vagrant/momoiro/system")
0032| 0x7fffffffe1e0 --> 0x100008000
0040| 0x7fffffffe1e8 --> 0x55555555464a (<main>:	push   rbp)
0048| 0x7fffffffe1f0 --> 0x0
0056| 0x7fffffffe1f8 --> 0x3884e47b9cc204a2
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x0000555555554655 in main ()
gdb-peda$ si
[----------------------------------registers-----------------------------------]
RAX: 0x55555555464a (<main>:	push   rbp)
RBX: 0x0
RCX: 0x555555554670 (<__libc_csu_init>:	push   r15)
RDX: 0x7fffffffe2b8 --> 0x7fffffffe511 ("LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc"...)
RSI: 0x7fffffffe2a8 --> 0x7fffffffe4f4 ("/home/vagrant/momoiro/system")
RDI: 0x5555555546f4 --> 0x68732f6e69622f ('/bin/sh')
RBP: 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffe1b8 --> 0x55555555465a (<main+16>:	mov    eax,0x0)
RIP: 0x555555554520 (<system@plt>:	jmp    QWORD PTR [rip+0x200aaa]        # 0x555555754fd0)
R8 : 0x7ffff7dd0d80 --> 0x0
R9 : 0x7ffff7dd0d80 --> 0x0
R10: 0x0
R11: 0x0
R12: 0x555555554540 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffe2a0 --> 0x1
R14: 0x0
R15: 0x0
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x555555554511:	xor    eax,0x200aaa
   0x555555554516:	jmp    QWORD PTR [rip+0x200aac]        # 0x555555754fc8
   0x55555555451c:	nop    DWORD PTR [rax+0x0]
=> 0x555555554520 <system@plt>:	jmp    QWORD PTR [rip+0x200aaa]        # 0x555555754fd0
 | 0x555555554526 <system@plt+6>:	push   0x0
 | 0x55555555452b <system@plt+11>:	jmp    0x555555554510
 | 0x555555554530 <__cxa_finalize@plt>:	jmp    QWORD PTR [rip+0x200ac2]        # 0x555555754ff8
 | 0x555555554536 <__cxa_finalize@plt+6>:	xchg   ax,ax
 |->   0x7ffff7a33440 <__libc_system>:	test   rdi,rdi
       0x7ffff7a33443 <__libc_system+3>:	je     0x7ffff7a33450 <__libc_system+16>
       0x7ffff7a33445 <__libc_system+5>:	jmp    0x7ffff7a32eb0 <do_system>
       0x7ffff7a3344a <__libc_system+10>:	nop    WORD PTR [rax+rax*1+0x0]
                                                                  JUMP is taken
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffe1b8 --> 0x55555555465a (<main+16>:	mov    eax,0x0)
0008| 0x7fffffffe1c0 --> 0x555555554670 (<__libc_csu_init>:	push   r15)
0016| 0x7fffffffe1c8 --> 0x7ffff7a05b97 (<__libc_start_main+231>:	mov    edi,eax)
0024| 0x7fffffffe1d0 --> 0x1
0032| 0x7fffffffe1d8 --> 0x7fffffffe2a8 --> 0x7fffffffe4f4 ("/home/vagrant/momoiro/system")
0040| 0x7fffffffe1e0 --> 0x100008000
0048| 0x7fffffffe1e8 --> 0x55555555464a (<main>:	push   rbp)
0056| 0x7fffffffe1f0 --> 0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x0000555555554520 in system@plt ()
gdb-peda$ x/gx 0x7fffffffe1b8
0x7fffffffe1b8:	0x000055555555465a
gdb-peda$ x/i 0x000055555555465a
   0x55555555465a <main+16>:	mov    eax,0x0
gdb-peda$ x/20wx 0x7fffffffe1b8
0x7fffffffe1b8:	0x5555465a	0x00005555	0x55554670	0x00005555
0x7fffffffe1c8:	0xf7a05b97	0x00007fff	0x00000001	0x00000000
0x7fffffffe1d8:	0xffffe2a8	0x00007fff	0x00008000	0x00000001
0x7fffffffe1e8:	0x5555464a	0x00005555	0x00000000	0x00000000
0x7fffffffe1f8:	0x9cc204a2	0x3884e47b	0x55554540	0x00005555
```


pedaの見方についてですが, リトルエンディアンに気をつけ, ASCIIコード表をみて変換すると
```
68 -> h
73 -> s
2f -> /
6e -> n
69 -> i
62 -> b
2f -> /
```
となります, つまり, メモリアドレス --> その中身 というわけです.
```
0x5555555546f4 --> 0x68732f6e69622f ('/bin/sh')
```

整理すると以下のようになってます.
```
0x7fffffffe1b8:
  0x55555555465a // <main+16>: mov eax,0x0 (return address from system)
  ...
0x7fffffffe1c0:
  0x555555554670
```