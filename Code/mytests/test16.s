.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $20, %esp
subl $12, %esp
movl $1, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -16(%ebp)
movl $0, %eax
shl $2, %eax
movl %eax, -20(%ebp)
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, -24(%ebp)
pushl -24(%ebp)
pushl -20(%ebp)
pushl -16(%ebp)
call set_subscript
addl $12, %esp
movl -16(%ebp), %eax
addl $12, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -4(%ebp)
subl $12, %esp
movl $1, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -20(%ebp)
movl $0, %eax
shl $2, %eax
movl %eax, -24(%ebp)
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, -28(%ebp)
pushl -28(%ebp)
pushl -24(%ebp)
pushl -20(%ebp)
call set_subscript
addl $12, %esp
movl -20(%ebp), %eax
addl $12, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -8(%ebp)
subl $12, %esp
movl $1, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -20(%ebp)
movl $0, %eax
shl $2, %eax
movl %eax, -24(%ebp)
movl -4(%ebp), %eax
movl %eax, -28(%ebp)
pushl -28(%ebp)
pushl -24(%ebp)
pushl -20(%ebp)
call set_subscript
addl $12, %esp
movl -20(%ebp), %eax
addl $12, %esp
movl %eax, %eax
pushl %eax
pushl $lambda_0
call create_closure
addl $8, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -8(%ebp)
subl $12, %esp
movl $1, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -20(%ebp)
movl $0, %eax
shl $2, %eax
movl %eax, -24(%ebp)
movl -8(%ebp), %eax
movl %eax, -28(%ebp)
pushl -28(%ebp)
pushl -24(%ebp)
pushl -20(%ebp)
call set_subscript
addl $12, %esp
movl -20(%ebp), %eax
addl $12, %esp
movl %eax, %eax
pushl %eax
pushl $lambda_1
call create_closure
addl $8, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -4(%ebp)
movl $10, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
pushl %eax
movl -8(%ebp), %eax
pushl %eax
call get_free_vars
addl $4, %esp
movl %eax, %eax
pushl %eax
movl -8(%ebp), %eax
pushl %eax
call get_fun_ptr
addl $4, %esp
movl %eax, %eax
call *%eax
addl $8, %esp
movl %eax, %eax
movl %eax, -12(%ebp)
addl $20, %esp
movl $0, %eax
leave
ret

lambda_0:
pushl %ebp
movl %esp, %ebp
subl $28, %esp
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
pushl %eax
movl 8(%ebp), %eax
pushl %eax
call get_subscript
addl $8, %esp
movl %eax, %eax
movl %eax, -4(%ebp)
subl $12, %esp
movl $1, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -20(%ebp)
movl $0, %eax
shl $2, %eax
movl %eax, -24(%ebp)
movl -4(%ebp), %eax
movl %eax, -28(%ebp)
pushl -28(%ebp)
pushl -24(%ebp)
pushl -20(%ebp)
call set_subscript
addl $12, %esp
movl -20(%ebp), %eax
addl $12, %esp
movl %eax, %eax
pushl %eax
pushl $lambda_0
call create_closure
addl $8, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -8(%ebp)
movl 12(%ebp), %eax
pushl %eax
call print_any
addl $4, %esp
movl 12(%ebp), %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else0
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else1
movl $1, %eax
jmp ends0
else1:
movl $0, %eax
jmp ends0
else0:
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
addl $8, %esp
ends0:
shl $2, %eax
or $1, %eax
movl %eax, %eax
movl %eax, -12(%ebp)
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
shr $2, %eax
negl %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, -16(%ebp)
movl -16(%ebp), %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else2
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else3
movl $1, %eax
jmp ends1
else3:
movl $0, %eax
jmp ends1
else2:
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
addl $8, %esp
ends1:
shl $2, %eax
or $1, %eax
movl %eax, %eax
movl %eax, %esi
pushl %eax
call is_true
addl $4, %esp
cmpl $0, %eax
je else4
movl %esi, %eax
jmp ends2
else4:
movl -16(%ebp), %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else5
movl %eax, %esi
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else6
movl $1, %eax
jmp ends3
else6:
movl $0, %eax
jmp ends3
else5:
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
addl $8, %esp
ends3:
shl $2, %eax
or $1, %eax
movl %eax, %eax
ends2:
movl %eax, %eax
movl %eax, %esi
pushl %eax
call is_true
addl $4, %esp
cmpl $0, %eax
je else7
movl -16(%ebp), %ebx
shr $2, %ebx
movl 12(%ebp), %eax
shr $2, %eax
addl %ebx, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
jmp ends4
else7:
movl -16(%ebp), %eax
andl $0xfffffffc, %eax
movl %eax, %ebx
movl 12(%ebp), %eax
andl $0xfffffffc, %eax
pushl %eax
pushl %ebx
call add
addl $8, %esp
or $0x3, %eax
or $3, %eax
movl %eax, %eax
ends4:
movl %eax, %eax
movl %eax, -20(%ebp)
movl -12(%ebp), %eax
movl %eax, %esi
pushl %eax
call is_true
addl $4, %esp
cmpl $0, %eax
je else8
movl $10, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
jmp ends5
else8:
movl -20(%ebp), %eax
pushl %eax
movl -4(%ebp), %eax
pushl %eax
call get_free_vars
addl $4, %esp
movl %eax, %eax
pushl %eax
movl -4(%ebp), %eax
pushl %eax
call get_fun_ptr
addl $4, %esp
movl %eax, %eax
call *%eax
addl $8, %esp
movl %eax, %eax
ends5:
movl %eax, %eax
movl %eax, -24(%ebp)
movl -24(%ebp), %eax
addl $28, %esp
leave
ret

lambda_1:
pushl %ebp
movl %esp, %ebp
subl $28, %esp
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
pushl %eax
movl 8(%ebp), %eax
pushl %eax
call get_subscript
addl $8, %esp
movl %eax, %eax
movl %eax, -4(%ebp)
subl $12, %esp
movl $1, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -20(%ebp)
movl $0, %eax
shl $2, %eax
movl %eax, -24(%ebp)
movl -4(%ebp), %eax
movl %eax, -28(%ebp)
pushl -28(%ebp)
pushl -24(%ebp)
pushl -20(%ebp)
call set_subscript
addl $12, %esp
movl -20(%ebp), %eax
addl $12, %esp
movl %eax, %eax
pushl %eax
pushl $lambda_1
call create_closure
addl $8, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -8(%ebp)
movl 12(%ebp), %eax
pushl %eax
call print_any
addl $4, %esp
movl 12(%ebp), %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else9
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else10
movl $1, %eax
jmp ends6
else10:
movl $0, %eax
jmp ends6
else9:
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
addl $8, %esp
ends6:
shl $2, %eax
or $1, %eax
movl %eax, %eax
movl %eax, -12(%ebp)
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
shr $2, %eax
negl %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, -16(%ebp)
movl -16(%ebp), %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else11
movl %eax, %esi
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else12
movl $1, %eax
jmp ends7
else12:
movl $0, %eax
jmp ends7
else11:
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
addl $8, %esp
ends7:
shl $2, %eax
or $1, %eax
movl %eax, %eax
movl %eax, %esi
pushl %eax
call is_true
addl $4, %esp
cmpl $0, %eax
je else13
movl %esi, %eax
jmp ends8
else13:
movl -16(%ebp), %eax
andl $3, %eax
shl $2, %eax
movl %eax, %eax
movl %eax, %esi
andl $0x3, %esi
cmpl $2, %esi
jg else14
movl %eax, %esi
movl $1, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
movl %eax, %edi
shr $2, %esi
shr $2, %edi
cmpl %esi, %edi
jne else15
movl $1, %eax
jmp ends9
else15:
movl $0, %eax
jmp ends9
else14:
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
addl $8, %esp
ends9:
shl $2, %eax
or $1, %eax
movl %eax, %eax
ends8:
movl %eax, %eax
movl %eax, %esi
pushl %eax
call is_true
addl $4, %esp
cmpl $0, %eax
je else16
movl -16(%ebp), %ebx
shr $2, %ebx
movl 12(%ebp), %eax
shr $2, %eax
addl %ebx, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
jmp ends10
else16:
movl -16(%ebp), %eax
andl $0xfffffffc, %eax
movl %eax, %ebx
movl 12(%ebp), %eax
andl $0xfffffffc, %eax
pushl %eax
pushl %ebx
call add
addl $8, %esp
or $0x3, %eax
or $3, %eax
movl %eax, %eax
ends10:
movl %eax, %eax
movl %eax, -20(%ebp)
movl -12(%ebp), %eax
movl %eax, %esi
pushl %eax
call is_true
addl $4, %esp
cmpl $0, %eax
je else17
movl $0, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
jmp ends11
else17:
movl -20(%ebp), %eax
pushl %eax
movl -4(%ebp), %eax
pushl %eax
call get_free_vars
addl $4, %esp
movl %eax, %eax
pushl %eax
movl -4(%ebp), %eax
pushl %eax
call get_fun_ptr
addl $4, %esp
movl %eax, %eax
call *%eax
addl $8, %esp
movl %eax, %eax
ends11:
movl %eax, %eax
movl %eax, -24(%ebp)
movl -24(%ebp), %eax
addl $28, %esp
leave
ret

