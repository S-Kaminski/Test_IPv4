#ifndef IPV4_H
#define IPV4_H


void init(void);

int add(unsigned int base, char mask);

int del(unsigned int base, char mask);

char check(unsigned int ip);

void clear(void);


#endif

