typedef enum _enum_data
{
	e1 = 1, e2, e3
} ENUM_DATA;

typedef enum
{
	E1,
	E2 = 3,
	E4,
	E5,
	E6 = E4+ 5,
	EMAX
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
	char ch1;
	int  in1;
	long l1;
	short s1;
	unsigned short us1;
	float f1;
	double d1;
	long long ll1;

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