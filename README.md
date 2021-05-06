# flat_file_sql
Basic sql queries over a flat binary file based on a C structure definition

For example, a flat C binary file with records like...

```c
typedef struct _my_simple
{
	char simp1[(12*2)/2 + 1 - 2];
	int  simp2;
} MY_SIMPLE;
```
can be queried using...

```sql
select * from MY_SIMPLE where simp2 > 7
```

`char[]` is treated as a string.

arrays (including arrays of structures) are supported.

No joins.

LIKE expressions use Regex expression.