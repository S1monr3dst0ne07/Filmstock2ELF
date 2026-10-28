
#include <asm/unistd.h> 
#include <stddef.h> 

void sys_write(char* buf, size_t len)
{
    asm volatile(
        "syscall"
        : : "a"(__NR_write), "D"(1), "S"(buf), "d"(len)
        : "rcx", "r11", "memory"
    );
}
void outchar(char c)
{
	sys_write(&c, 1);
}
void print_number(double x)
{
	int    real =  x > 0.0 ? (int)x : -(int)x;
	double frac = (x > 0.0 ? x : -x) - (double)real;

	if (x < 0) outchar('-');

	char   buf[256] = { 0 };
	size_t len      =   1  ;
	do
		buf[255 - (len++)] = 
		(real % 10) + '0';
	while((real /= 10));
	sys_write(buf + 255 - len, len);

	outchar('.');

	for(int i = 0; i < 4; i++)
		outchar(((int)(frac *= 10.0) % 10) + '0');

}


extern double film[];

void print(int base, int len)
{
	for (int i = 0; i < len; i++)
		outchar(film[base + i]);
}
void print_numbers(int base, int len)
{
	for (int i = 0; i < len; i++)
		print_number(film[base + i]);
}

void power(int a, int b, int dst)
{
}


