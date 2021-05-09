#include <stdio.h>
#include <string.h>
#pragma pack(1)
#include "test.h"

#define PRINT(struct)				printf("sizeof(" #struct ")=%d\n", sizeof(struct))
#define PRINT_OFFSET(struct, var)	printf("offsetof(" #struct "." #var "=%d\n", (int)&(((struct *)(0))->var) )


static const char* file = "..\\parsec\\test.data";


static void make_file()
{

	FILE* fptr = fopen(file, "wb");
	if (fptr)
	{
		MY_STRUCT s;
		memset(&s, 0, sizeof(s));
		s.index = 0;
		for  ( int i = 0; i <sizeof(s.enum_sized); i++)
			s.enum_sized[i] = 100+i;
		strcpy(s.ms.simp1, "one");
		s.ms.simp2 = 2;
		s.mi = 3;
		strcpy(s.msa[0].simp1, "four");
		s.msa[0].simp2 = 5;
		strcpy(s.msa[1].simp1, "six");
		s.msa[1].simp2 = 7;
		strcpy(s.msa[2].simp1, "eight");
		s.msa[2].simp2 = 9;
		strcpy(s.msa[3].simp1, "ten");
		s.msa[3].simp2 = 11;
		strcpy(s.msa[4].simp1, "twelve");
		s.msa[4].simp2 = 13;
		s.e = 14;
		strcpy(s.sms.simp1, "fifteen");
		s.sms.simp2 = 16;
		s.why.a = 17;
		s.why.b = 18;
		s.why.c = 19;
		s.why2[0].a = 20;
		s.why2[0].b = 21;
		s.why2[0].c = 22;
		s.why2[1].a = 23;
		s.why2[2].b = 24;
		s.why2[3].c = 25;
		s.ch1 = 26;
		s.in1 = 27;
		s.l1 = 28;
		s.s1 = 29;
		s.us1 = 30;
		s.f1 = 31.31313131313131F;
		s.d1 = 32.32323232323232323232;
		s.ll1 = 100000000000033LL;
		printf("ll1 = %lld %llx\n", s.ll1, s.ll1);
#ifdef BITFIELDS
		s.bf00 = 20;
		s.bf01 = -20;
		s.bf1 = 0;
		s.bf2 = 2;
		s.bf3 = 1;
		s.bf4 = 0xF;
		s.bf5 = 0xF;
#endif
		s.ain1[0] = 34;
		s.ain1[1] = 35;
		s.ain1[2] = 36;
		s.ain1[3] = 37;
		s.ain1[4] = 38;
		s.ain1[5] = 39;
		s.ain1[6] = 40;
		s.ain1[7] = 41;
		s.ain1[8] = 42;
		s.ain1[9] = 43;
		strcpy(s.str, "Test");

		fwrite(&s, sizeof(s), 1, fptr);

		MY_STRUCT s2;
		memset(&s2, 0, sizeof(s2));
		s2.index = 1;
		fwrite(&s2, sizeof(s2), 1, fptr);

		s.index = 2;
		fwrite(&s, sizeof(s), 1, fptr);

		s2.index = 3;
		fwrite(&s2, sizeof(s2), 1, fptr);

		s.index = 4;
		fwrite(&s, sizeof(s), 1, fptr);

		s.index = 5;
		fwrite(&s, sizeof(s), 1, fptr);

		fclose(fptr);
	}

}


void main()
{
	MY_STRUCT x;

	PRINT(T1);
	PRINT(T2);
	PRINT(MY_STRUCT);
	PRINT(MY_SIMPLE);
	PRINT(MYINT);
	PRINT(MY_SIMPLE);
	PRINT(ENUM_DATA);
	//PRINT(x.bf);

	PRINT_OFFSET(MY_STRUCT, ll1);
	//PRINT_OFFSET(MY_STRUCT, bf1);
	PRINT_OFFSET(MY_STRUCT, ain1);

	make_file();
}