.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $8, %esp
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else1
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else2
movl $1, %eax
jmp ends1
else2:
movl $0, %eax
jmp ends1
else1:
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
andl $0xfffffffc, %esi
pushl %esi
andl $0xfffffffc, %edi
pushl %edi
call equal
ends1:
shl $2, %eax
or $1, %eax
movl %eax, %eax
movl %eax, %esi
pushl %eax
call is_true
cmpl $0, %eax
je else3
movl %esi, %eax
jmp ends2
else3:
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else4
movl %eax, %esi
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else5
movl $1, %eax
jmp ends3
else5:
movl $0, %eax
jmp ends3
else4:
movl %eax, %esi
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
andl $0xfffffffc, %esi
pushl %esi
andl $0xfffffffc, %edi
pushl %edi
call equal
ends3:
shl $2, %eax
or $1, %eax
movl %eax, %eax
ends2:
movl %eax, %esi
pushl %eax
call is_true
cmpl $0, %eax
je else6
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %ebx
shr $2, %ebx
movl $2, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
shr $2, %eax
addl %eax, %ebx
movl %ebx, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
jmp ends4
else6:
movl $1, %eax
shl $2, %eax
or $0, %eax
andl $0xfffffffc, %eax
movl %eax, %ebx
movl $2, %eax
shl $2, %eax
or $0, %eax
andl $0xfffffffc, %eax
pushl %eax
pushl %ebx
call add
or $3, %eax
movl %eax, %eax
ends4:
movl %eax, -4(%ebp)
movl -4(%ebp), %eax
movl %eax, -4(%ebp)
movl -4(%ebp), %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else7
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else8
movl $1, %eax
jmp ends5
else8:
movl $0, %eax
jmp ends5
else7:
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
andl $0xfffffffc, %esi
pushl %esi
andl $0xfffffffc, %edi
pushl %edi
call equal
ends5:
shl $2, %eax
or $1, %eax
movl %eax, %eax
movl %eax, %esi
pushl %eax
call is_true
cmpl $0, %eax
je else9
movl %esi, %eax
jmp ends6
else9:
movl -4(%ebp), %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else10
movl %eax, %esi
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else11
movl $1, %eax
jmp ends7
else11:
movl $0, %eax
jmp ends7
else10:
movl %eax, %esi
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
andl $0xfffffffc, %esi
pushl %esi
andl $0xfffffffc, %edi
pushl %edi
call equal
ends7:
shl $2, %eax
or $1, %eax
movl %eax, %eax
ends6:
movl %eax, %esi
pushl %eax
call is_true
cmpl $0, %eax
je else12
movl -4(%ebp), %ebx
shr $2, %ebx
movl $3, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
shr $2, %eax
addl %eax, %ebx
movl %ebx, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
jmp ends8
else12:
movl -4(%ebp), %eax
andl $0xfffffffc, %eax
movl %eax, %ebx
movl $3, %eax
shl $2, %eax
or $0, %eax
andl $0xfffffffc, %eax
pushl %eax
pushl %ebx
call add
or $3, %eax
movl %eax, %eax
ends8:
movl %eax, -8(%ebp)
movl -8(%ebp), %eax
movl %eax, -8(%ebp)
pushl -8(%ebp)
call print_any
addl $8, %esp
movl $0, %eax
leave
ret
