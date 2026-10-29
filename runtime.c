
#define _GNU_SOURCE
#include <stddef.h> 
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

extern double film[];

void print(int base, int len)
{
	char buf[len + 1];
	buf[len] = '\0';
	for (int i = 0; i < len; i++)
		buf[i] = film[base + i];

	printf("%s", buf);
}
void print_numbers(int base, int len)
{
	for (int i = 0; i < len; i++)
		printf("%f", film[base + i]);
}
void update_console()
{
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
void _sin(int src, int dst) { film[dst] = sin(film[src]); }
void _cos(int src, int dst) { film[dst] = cos(film[src]); }
void _tan(int src, int dst) { film[dst] = tan(film[src]); }
void _floor(int src, int dst) { film[dst] = floor(film[src]); }
void _ceil (int src, int dst) { film[dst] = ceil (film[src]); }
void _sqrt (int src, int dst) { film[dst] = sqrt (film[src]); }

typedef struct
{
	size_t len;
	size_t cap;
	double* buf;
} list_t;

list_t matrix[1 << 16] = { 0 };
int matrix_bump = 0;
#define _list_get(idx) (&matrix[(int)film[idx]])

void new_list  (int idx) { film[idx] = (double)(matrix_bump++); }
void empty_list(int idx) { _list_get(idx)->len = 0; }

void _inc_len(list_t* l)
{
	if (l->len >= l->cap)
		if (l->cap == 0) {
			l->cap = 100000;
			l->buf = malloc(sizeof(double) * 100000);
		} else {
			double* old = l->buf;
			l->cap *= 2;
			size_t s = sizeof(double) * l->cap;
			free(l->buf);
			l->buf = malloc(s);
			memcpy(l->buf, old, s);
		}

	l->len += 1;
}

void add_list(int idx, int src)
{
	list_t* l = _list_get(idx);
	_inc_len(l);
	l->buf[l->len - 1] = film[src];
}
void print_list(int idx)
{
	list_t* l = _list_get(idx);
	size_t len = l->len;

	char buf[len + 1];
	buf[len] = '\0';
	for (int i = 0; i < len; i++)
		buf[i] = l->buf[i];

	printf("%s", buf);
}
void print_list_numbers(int idx)
{
	list_t* l = _list_get(idx);
	size_t len = l->len;

	printf("[");
	for (int i = 0; i < len; i++)
		printf(
			i < (len - 1) ? "%f, " : "%f", 
			l->buf[i]
		);
	printf("]\n");
}

void sort_list(int idx, bool order)
{
	int _cmp(const void* _a, const void* _b, void* _order)
	{
		const double* a = _a;
		const double* b = _b;
		bool order = _order;
		return (*a < *b) ^ order;
	}

	list_t* l = _list_get(idx);
	qsort_r(l->buf, l->len, sizeof(double), _cmp, (void*)order);
}
void copy_from_list(int idx, int src, int dst)
{
	list_t* l = _list_get(idx);
	film[dst] = l->buf[src];
}
void list_set(int idx, int dst, int src)
{
	list_t* l = _list_get(idx);
	l->buf[dst] = film[src];
}
void list_length(int idx, int len)
{
	film[len] = (double)(_list_get(idx)->len);
}


void main()
{
	extern void _compiled_entry();
	_compiled_entry();
}
