.globl main
main:
    pushl %ebp
    movl %esp, %ebp









    subl $12, %esp

    // Below creates list
    movl $2, %eax
    shl $2, %eax
    or $0, %eax

    pushl %eax
    call create_list

    or $3, %eax

    movl %eax, -4(%ebp)
    // Above creates list


    // Below gets and tags index
    movl $1, %eax
    shl $2, %eax
    or $0, %eax

    movl %eax, -8(%ebp)
    // Above gets and tags index


    // Below gets value and inserts into list at index
    movl $42, %eax
    shl $2, %eax
    or $0, %eax

    movl %eax, -12(%ebp)

    pushl -12(%ebp)
    pushl -8(%ebp)
    pushl -4(%ebp)

    call set_subscript
    // Above gets value and inserts into list at index


    movl -4(%ebp), %eax
    //andl $0xfffffffc, %eax

    addl $12, %esp













    pushl %eax
    call print_any
    addl $12, %esp
    movl $0, %eax
    leave
    ret
