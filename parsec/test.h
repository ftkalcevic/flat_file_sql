#define BITFIELDS

typedef enum _enum_data
{
	e1 = 1, e2, e3
} ENUM_DATA;

enum
{
	E1,
	E2 = 3,
	E4,
	E5,
	E6 = E4+ 5,
	EMAX
};

enum
{
	ER = 1 << E4,
	ES = -1,
	ET = 'I'
};

typedef struct _my_simple
{
	char simp1[(12*2)/2 + 1 - 2];
	int  simp2;
} MY_SIMPLE;

struct _plain_struct
{
	double a1;
	long   a2[5];
};

typedef union _test_union
{
	char simp1[12];
	int  simp2;
} TEST_UNION;

typedef int MYINT;

typedef struct _my_struct
{
	int index;

	int enum_sized[EMAX + 1];
	MY_SIMPLE ms;
	MYINT mi;
	MY_SIMPLE msa[5];
	ENUM_DATA e;

	struct _my_simple sms;


	struct _inline_struct
	{
		int a, b, c;
	} why;
	struct _inline_struct2
	{
		int a, b, c;
	} why2[2];
	int union1_type;
	TEST_UNION union1;
	int union2_type;
	union
	{
		int type1;
		char type2[45];
		double type3;
	} union2;
	char ch1;
	int bf00 : 6;
	int bf01 : 6;
	int  in1;
	long l1;
	short s1;
	unsigned short us1;
	float f1;
	double d1;
	long long ll1;
#ifdef BITFIELDS
	unsigned int bf1 : 1;
	int bf2 : 2;
	int bf3 : 1;
	unsigned int bf4 : 4;
	int bf5 : 4;
#endif
	int ain1[10];
	char str[10 + 1];

} MY_STRUCT;

typedef struct _t2
{
	int t2int;
} T2;

typedef struct _t1
{
	int i1;
	T2 t2_array[5];
} T1;

void x(void);
