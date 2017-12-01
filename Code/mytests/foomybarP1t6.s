.globl main
main:
    pushl %ebp
    movl %esp, %ebp
    subl $28, %esp
    call input
    shl $2, %eax
    movl %eax, -4(%ebp)
    call input
    shl $2, %eax
    movl %eax, -8(%ebp)
    subl $12, %esp
    movl $7, %eax
    shl $2, %eax
    pushl %eax
    call create_list
    or $3, %eax
    movl %eax, -32(%ebp)
    movl $0, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $1, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $1, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $2, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $2, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $3, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $3, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $4, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $4, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $5, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $5, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $6, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $6, %eax
    shl $2, %eax
    movl %eax, -36(%ebp)
    movl $7, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl -32(%ebp), %eax
    addl $12, %esp
    or $3, %eax
    movl %eax, -12(%ebp)
    movl $1, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, %eax
    shr $2, %eax
    negl %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -16(%ebp)
    movl $1, %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, %eax
    shr $2, %eax
    negl %eax
    shl $2, %eax
    or $0, %eax
    movl %eax, -20(%ebp)
    subl $12, %esp
    call create_dict
    or $0x3, %eax
    movl %eax, -32(%ebp)
    movl -16(%ebp), %eax
    movl %eax, -36(%ebp)
    movl -20(%ebp), %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl -4(%ebp), %eax
    movl %eax, -36(%ebp)
    movl -8(%ebp), %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl $1, %eax
    shl $2, %eax
    or $1, %eax
    movl %eax, -36(%ebp)
    movl -12(%ebp), %eax
    movl %eax, -40(%ebp)
    pushl -40(%ebp)
    pushl -36(%ebp)
    pushl -32(%ebp)
    call set_subscript
    movl -32(%ebp), %eax
    addl $12, %esp
    or $3, %eax
    movl %eax, -24(%ebp)
    movl -24(%ebp), %eax
    movl %eax, -28(%ebp)
    pushl -28(%ebp)
    call print_any
    addl $28, %esp
    movl $0, %eax
    leave
    ret
