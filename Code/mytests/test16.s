.globl main
main:
    pushl %ebp
    movl %esp, %ebp
    subl $0, %esp
    movl $1, %eax
    shl $2, %eax
    or $1, %eax
    pushl %eax
    call print_any
    addl $0, %esp
    movl $0, %eax
    leave
    ret
