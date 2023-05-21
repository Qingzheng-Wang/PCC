	.text
	.section	.rodata
	.comm	T0,4,4
	.text
	.globl	main
	.type	main, @function
main:

	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$12, %rsp
	movl	$0, -4(%rbp)
.W1:
	movl	-4(%rbp), %eax
	cmpl	$10, %eax
	jle	.begin3
	jmp	.end3
.begin3:
	movl	-4(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T0(%rip)
	movl	T0(%rip), %ecx
	movl	%ecx, -4(%rbp)
	jmp	.W1
.end3:

	movl	$0, %eax
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"PCC: 1.0.0"
