.model small

crlf equ 0Dh, 0Ah

.code
.startup
	mov dx, offset hello_msg
	mov ah, 9
	int 21h
.exit 0

.data
hello_msg db 'Hello World!', crlf, '$'

.stack

end
