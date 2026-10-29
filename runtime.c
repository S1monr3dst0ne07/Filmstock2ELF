
#include <stddef.h> 
#include <stdio.h>
#include <stdlib.h>

extern double film[];

void print(int base, int len)
{
	char buf[len + 1];
	buf[len] = '\0';
	for (int i = 0; i < len; i++)
		buf[i] = film[base + i];

	printf("%s", buf);
	fflush(stdout);
}
void print_numbers(int base, int len)
{
	for (int i = 0; i < len; i++)
		printf("%f\n", film[base + i]);
	fflush(stdout);
}

void power(int a, int b, int dst)
{
}

void main()
{
	extern void _compiled_entry();
	_compiled_entry();
}
