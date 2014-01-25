#include <stdio.h>
#include <stdlib.h>
#include <static_test.h>

int main()
{
	signed int c, d;
	printf("Enter two numbers: ");
	fflush(stdout);
	scanf("%d%d", &c, &d);
	printf("The static lib test reports these results:\n");
	printf("add(c, d): %d\n" \
		"sub(c, d): %d\n" \
		"mul(c, d): %d\n" \
		"div2(c, d): %d\n" \
		"mod(c, d): %d\n", add(c, d), sub(c, d), mul(c, d), div2(c, d), mod(c, d));
	return EXIT_SUCCESS;	
}
	
