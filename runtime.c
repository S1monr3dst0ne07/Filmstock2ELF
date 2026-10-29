
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
#include <unistd.h>

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
	film[dst] = l->buf[(int)film[src]];
}
void rt_list_set(int idx, int dst, int src)
{
	list_t* l = _list_get(idx);
	l->buf[(int)film[dst]] = film[src];
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
	static bool need_init = true;
	if (need_init)
	{
		SetConfigFlags(FLAG_WINDOW_RESIZABLE);
    	InitWindow(800, 600, "Filmstock");
		need_init = false;
	}

	if (WindowShouldClose()) exit(0);
	BeginDrawing();
}

Color color;

void rt_draw_triangles(int idx)
{
	void draw_triangle_auto_wind(Vector2 v1, Vector2 v2, Vector2 v3, Color color)
	{
		if ((v2.x - v1.x) * (v3.y - v1.y) - (v2.y - v1.y) * (v3.x - v1.x) > 0)
			DrawTriangle(v1, v3, v2, color);
		else
			DrawTriangle(v1, v2, v3, color);
	}

    list_t* l = _list_get(idx);
    double* points = l->buf;

	Vector2 v1, v2, v3;

	double cursorX = 0;
	double cursorY = 0;
    for (int i = 0; i < l->len;) 
    {
    	v1.x = points[i++] + cursorX; v1.y = points[i++] + cursorY;
    	v2.x = points[i++] + cursorX; v2.y = points[i++] + cursorY;
    	v3.x = points[i++] + cursorX; v3.y = points[i++] + cursorY;

        draw_triangle_auto_wind(v1, v2, v3, color);
    }
}


void rt_end_drawing()          { EndDrawing(); }
void rt_get_scroll()           {}
void rt_get_mouse_x(int idx)   { film[idx] = GetMousePosition().x; }
void rt_get_mouse_y(int idx)   { film[idx] = GetMousePosition().y; }
void rt_sleep(int idx)         { if (film[idx] > 0) usleep(film[idx] * 1000.0); }
void rt_set_color(int idx)     { uint64_t tmp = film[idx]; memcpy(&color, &tmp, 4); }
void rt_mouse_pressed(int btn, int idx) 
{ 
	int raybtn;
	switch (btn)
	{
		case 0: raybtn = MOUSE_LEFT_BUTTON;   break;
		case 1: raybtn = MOUSE_RIGHT_BUTTON;  break;
		case 2: raybtn = MOUSE_MIDDLE_BUTTON; break;
	}
	film[idx] = (double)IsMouseButtonDown(raybtn); 
}




