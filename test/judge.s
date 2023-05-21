	.text
	.section	.rodata
	.comm	T0,4,4
	.comm	T1,4,4
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
	movl	$1, -4(%rbp)
	movl	-4(%rbp), %eax
	cmpl	$0, %eax
	je	.begin2
	jmp	.end2
.begin2:
	movl	-4(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T0(%rip)
	movl	T0(%rip), %ecx
	movl	%ecx, -4(%rbp)
.end2:
	movl	-4(%rbp), %eax
	cmpl	$1, %eax
	je	.begin8
	jmp	.end8
.begin8:
	movl	-4(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T1(%rip)
	movl	T1(%rip), %ecx
	movl	%ecx, -4(%rbp)
.end8:

	movl	$0, %eax
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"PCC: 1.0.0"
