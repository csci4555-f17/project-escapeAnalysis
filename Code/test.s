.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $16, %esp
subl $12, %esp
movl $0, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -16(%ebp)
movl -16(%ebp), %eax
addl $12, %esp
movl %eax, %eax
pushl %eax
pushl $lambda_0
call create_closure
addl $8, %esp
or $3, %eax
movl %eax, %eax
movl %eax, -4(%ebp)
subl $12, %esp
movl $0, %eax
shl $2, %eax
pushl %eax
call create_list
addl $4, %esp
or $3, %eax
movl %eax, -20(%ebp)
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
movl $5, %eax
shl $2, %eax
or $0, %eax
movl %eax, %eax
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
movl %eax, -12(%ebp)
movl -12(%ebp), %eax
pushl %eax
call print_any
addl $4, %esp
movl $5, %eax
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
movl %eax, -16(%ebp)
movl -16(%ebp), %eax
pushl %eax
call print_any
addl $4, %esp
addl $16, %esp
movl $0, %eax
leave
ret

lambda_0:
pushl %ebp
movl %esp, %ebp
subl $4, %esp
addl $4, %esp
leave
ret

lambda_1:
pushl %ebp
movl %esp, %ebp
subl $4, %esp
addl $4, %esp
leave
ret

