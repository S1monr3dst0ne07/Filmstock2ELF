
#define _GNU_SOURCE
#include <stddef.h> 
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#include <raylib.h>

extern double film[];

void rt_print(int base, int len)
{
	char buf[len + 1];
	buf[len] = '\0';
	for (int i = 0; i < len; i++)
		buf[i] = film[base + i];

	printf("%s", buf);
}
void rt_print_numbers(int base, int len)
{
	for (int i = 0; i < len; i++)
		printf("%f", film[base + i]);
}
void rt_update_console()
{
	fflush(stdout);
}

void rt_power(int a, int b, int dst)
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
void rt_modulo(int a, int b, int dst)
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
void rt_sin(int src, int dst) { film[dst] = sin(film[src]); }
void rt_cos(int src, int dst) { film[dst] = cos(film[src]); }
void rt_tan(int src, int dst) { film[dst] = tan(film[src]); }
void rt_floor(int src, int dst) { film[dst] = floor(film[src]); }
void rt_ceil (int src, int dst) { film[dst] = ceil (film[src]); }
void rt_square_root (int src, int dst) { film[dst] = sqrt (film[src]); }

typedef struct
{
	size_t len;
	size_t cap;
	double* buf;
} list_t;

list_t matrix[1 << 16] = { 0 };
int matrix_bump = 0;
#define _list_get(idx) (&matrix[(int)film[idx]])

void rt_new_list  (int idx) { film[idx] = (double)(matrix_bump++); }
void rt_empty_list(int idx) { _list_get(idx)->len = 0; }

void _inc_len(list_t* l)
{
	if (l->len >= l->cap)
		if (l->cap == 0) {
			l->cap = 1;
			l->buf = malloc(sizeof(double));
		} else {
			double* old = l->buf;
			l->cap *= 2;
			l->buf = malloc(sizeof(double) * l->cap);
			memcpy(l->buf, old, sizeof(double) * l->len);
			free(old);
		}

	l->len += 1;
}

void rt_add_list(int idx, int src)
{
	list_t* l = _list_get(idx);
	_inc_len(l);
	l->buf[l->len - 1] = film[src];
}
void rt_print_list(int idx)
{
	list_t* l = _list_get(idx);
	size_t len = l->len;

	char buf[len + 1];
	buf[len] = '\0';
	for (int i = 0; i < len; i++)
		buf[i] = l->buf[i];

	printf("%s", buf);
}
void rt_print_list_numbers(int idx)
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

void rt_sort_list(int idx, bool order)
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
void rt_copy_from_list(int idx, int src, int dst)
{
	list_t* l = _list_get(idx);
	film[dst] = l->buf[src];
}
void rt_list_set(int idx, int dst, int src)
{
	list_t* l = _list_get(idx);
	l->buf[dst] = film[src];
}
void rt_length_of_list(int idx, int len)
{
	film[len] = (double)(_list_get(idx)->len);
}


void rt_time(int dst)
{
	struct timespec ts;
	clock_gettime(CLOCK_REALTIME, &ts);
	film[dst] = ((double)ts.tv_sec * 1000.0) + ((double)ts.tv_nsec / 1000000.0);
}

void main()
{
	extern void _compiled_entry();
	_compiled_entry();
}





// --- raylib stuff from here on out ---

void rt_get_width (int idx) { film[idx] = GetScreenWidth (); }
void rt_get_height(int idx) { film[idx] = GetScreenHeight(); }

void rt_begin_drawing()
{
	if (WindowShouldClose()) exit(0);

	static bool need_init = true;
	printf("INIT\n");
	if (need_init)
	{
		SetConfigFlags(FLAG_WINDOW_RESIZABLE);
    	InitWindow(800, 600, "Filmstock");
	}

	BeginDrawing();
}
void rt_end_drawing()
{
	EndDrawing();
}

void rt_draw_triangles()  {}
void rt_set_color()       {}
void rt_get_scroll()      {}
void rt_get_mouse_x()     {}
void rt_get_mouse_y()     {}
void rt_sleep()           {}
void rt_mouse_pressed()   {}




