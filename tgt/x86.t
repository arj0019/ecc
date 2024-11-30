.map CALL ::= CALL *tgt
.fmt CALL :: \tcall $tgt\n

.map LOC ::= LOC *tgt
.fmt LOC ::= $tgt:\n
             \tpush rbp\n
             \tmov rbp, rsp\n

.map MOV ::= MOV *tgt, &src
           | MOV *tgt, #src
.fmt MOV ::= &src
             \tmov rbp-!tgt, rax\n
           | \tmov rbp-!tgt, $src\n

.map ADD ::= ADD *tgt, *src
           | ADD *tgt, &src
           | ADD *tgt, #src
           | ADD #tgt, *src
           | ADD #tgt, &src
           | ADD #tgt, #src
.fmt ADD ::= \tmov rax, rbp-&tgt\n
             \tadd rax, rbp-&src\n
           | &src
             \tadd rax, rbp-&tgt\n
           | \tmov rax, rbp-&tgt\n
             \tadd rax, $src\n
           | \tmov rax, $tgt\n
             \tadd rax, rbp-&src\n
           | &src
             \tadd rax, $tgt\n
           | \tmov rax, $src\n
             \tadd rax, $tgt\n

.map SUB ::= SUB *tgt, *src
           | SUB *tgt, &src
           | SUB *tgt, #src
           | SUB #tgt, *src
           | SUB #tgt, &src
           | SUB #tgt, #src
.fmt SUB ::= \tmov rax, rbp-&tgt\n
             \tsub rax, rbp-&src\n
           | &src
             \tmov rbx, rax\n
             \tmov rax, rbp-&tgt\n
             \tsub rax, rbx\n
           | \tmov rax, rbp-&tgt\n
             \tsub rax, $src\n
           | \tmov rax, $tgt\n
             \tsub rax, rbp-&src\n
           | &src
             \tmov rbx, rax\n
             \tmov rax, $tgt\n
             \tsub rax, rbx\n
           | \tmov rax, $tgt\n
             \tsub rax, $src\n

.map RET ::= RET *tgt
           | RET &tgt
           | RET #tgt
.fmt RET ::= \tmov rax, rbp-&tgt\n
             \tpop rbp\n
             \tret\n
           | &tgt
             \tpop rbp\n
             \tret\n
           | \tmov rax, $tgt\n
             \tpop rbp\n
             \tret\n

.del \tpush rax\n
     \tpop rax\n
.del \tadd [^\n]*, 0\n
.del \tsub [^\n]*, 0\n

.sub \tmov ([^\n]*), ([^\n]*)\n\tmov \2, \1\n;\tmov \1, \2\n
