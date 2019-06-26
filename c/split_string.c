#include <string.h>
#include <stdio.h>
#include <stdlib.h>


int str2tok(const char *text, char ***buf, const char *delim) {
    char str[strlen(text)];
    strcpy(str, text);

    int count = 1;
    char *p = str;
    while (*p != '\0') {
        if (*p == *delim) count++;
        p++;
    }

    *buf = (char**)malloc(sizeof(char*)*count);
    char *tok = strtok(str, delim);;

    int i = 0;
    while( tok != NULL ) {
        (*buf)[i] = malloc(sizeof(char*)*strlen(tok));
        strcpy((*buf)[i], tok);
        tok = strtok(NULL, delim);
        i++;
    }

    return i;
}

void usage(const char *name) {
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "\t%s <string> <delimiter>\n", name);
}


// Exercise on string splitting in C.
int main(int argc, char **argv) {
    
    char * text; 
    char * delim;

    if (argv[1] != NULL && strlen(argv[1]) > 0) {
        text = argv[1];
    } else {
        usage(argv[0]);
        return(1);
    }

    if (argv[2] != NULL && strlen(argv[2]) == 1) {
        delim = argv[2];
    } else {
        usage(argv[0]);
        return(1);
    }

    char **tokens = NULL;
    int n = str2tok(text, &tokens, delim);

    int i = 0;
    while (tokens[i] != NULL) {
        printf("%s\n", tokens[i++]);
    }
    return(0);
}
