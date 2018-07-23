#include <mpfr.h>
#include <gmp.h>

int main()
{
    mpfr_printf("Pass (direct test of mpfr)\n");
    gmp_printf("Pass (inherited dependency on gmp)\n");
    return 0;
}
