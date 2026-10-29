
#include <stddef.h> 
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <stdint.h>

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
		printf("%f", film[base + i]);
	fflush(stdout);
}

void power(int a, int b, int dst)
{
	double base = film[a];
	double exp  = film[b];
	double res  = 0.0;

	if (fabs(exp) < FLT_EPSILON)
		res = 1.0;
	else if (base >= 0.0)
		res = pow(base, exp);
	else
	{
		uint64_t real_exp = 1.0 / exp;
		double res_pos = pow(-base, exp);
		double sign = (real_exp % 2 == 0) ? 1.0 : -1.0;
		res = res_pos * sign;
	}

	film[dst] = res;
}
void update_console()
{
	fflush(stdout);
}
void modulo(int a, int b, int dst)
{
	double num  = film[a];
	double base = film[b];

	double r = fmod(num, base);
	double res = 0.0;
	/**/ if (fabs(r) < FLT_EPSILON)    res = 0.0;
	else if ((r < 0.0) ^ (base < 0.0)) res = r + base;
	else                               res = r;

	film[dst] = res;
}

void main()
{
	extern void _compiled_entry();
	_compiled_entry();
}
