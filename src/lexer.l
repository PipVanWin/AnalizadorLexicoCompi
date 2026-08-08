%option noyywrap
%option yylineno

%{
#include <stdio.h>
#include <string.h>

#define FS "\x01"

/* Imprime un lexema con su token y categoria, separados por FS */
#define EMIT(categoria, token) \
    printf("%s" FS "%d" FS "%s" FS "%s\n", yytext, yylineno, (token), (categoria))

/* Cuenta saltos de linea dentro de un lexema multi-linea (comentarios de
 * bloque, strings triples) y ajusta yylineno manualmente */
static void contar_saltos_linea(const char *texto) {
    for (const char *p = texto; *p; p++) {
        if (*p == '\n') yylineno++;
    }
}
%}

DIGITO      [0-9]
LETRA       [a-zA-Z_]

%%

    /* Comentarios se ignoran, no son lexemas */
"//".*                              { /* comentario de linea, se descarta */ }
"/*"([^*]|\*+[^*/])*\*+"/"          { contar_saltos_linea(yytext); /* comentario de bloque */ }

    /*Espacios en blanco se ignoran*/
[ \t\r]+                            { /* se ignora */ }
\n                                   { /* yylineno se incrementa automaticamente con %option yylineno */ }

    /* Valores booleanos categoria propia, no cuentan como palabra reservada */
"true"                              { EMIT("BOOLEANO", "BOOL_TRUE"); }
"false"                             { EMIT("BOOLEANO", "BOOL_FALSE"); }

    /*Palabras reservadas de Kotlin*/
"as"            { EMIT("RESERVADA", "RES_AS"); }
"break"         { EMIT("RESERVADA", "RES_BREAK"); }
"class"         { EMIT("RESERVADA", "RES_CLASS"); }
"continue"      { EMIT("RESERVADA", "RES_CONTINUE"); }
"do"            { EMIT("RESERVADA", "RES_DO"); }
"else"          { EMIT("RESERVADA", "RES_ELSE"); }
"for"           { EMIT("RESERVADA", "RES_FOR"); }
"fun"           { EMIT("RESERVADA", "RES_FUN"); }
"if"            { EMIT("RESERVADA", "RES_IF"); }
"in"            { EMIT("RESERVADA", "RES_IN"); }
"interface"     { EMIT("RESERVADA", "RES_INTERFACE"); }
"is"            { EMIT("RESERVADA", "RES_IS"); }
"null"          { EMIT("RESERVADA", "RES_NULL"); }
"object"        { EMIT("RESERVADA", "RES_OBJECT"); }
"package"       { EMIT("RESERVADA", "RES_PACKAGE"); }
"return"        { EMIT("RESERVADA", "RES_RETURN"); }
"super"         { EMIT("RESERVADA", "RES_SUPER"); }
"this"          { EMIT("RESERVADA", "RES_THIS"); }
"throw"         { EMIT("RESERVADA", "RES_THROW"); }
"try"           { EMIT("RESERVADA", "RES_TRY"); }
"typealias"     { EMIT("RESERVADA", "RES_TYPEALIAS"); }
"typeof"        { EMIT("RESERVADA", "RES_TYPEOF"); }
"val"           { EMIT("RESERVADA", "RES_VAL"); }
"var"           { EMIT("RESERVADA", "RES_VAR"); }
"when"          { EMIT("RESERVADA", "RES_WHEN"); }
"while"         { EMIT("RESERVADA", "RES_WHILE"); }
"by"            { EMIT("RESERVADA", "RES_BY"); }
"catch"         { EMIT("RESERVADA", "RES_CATCH"); }
"constructor"   { EMIT("RESERVADA", "RES_CONSTRUCTOR"); }
"delegate"      { EMIT("RESERVADA", "RES_DELEGATE"); }
"dynamic"       { EMIT("RESERVADA", "RES_DYNAMIC"); }
"field"         { EMIT("RESERVADA", "RES_FIELD"); }
"file"          { EMIT("RESERVADA", "RES_FILE"); }
"finally"       { EMIT("RESERVADA", "RES_FINALLY"); }
"get"           { EMIT("RESERVADA", "RES_GET"); }
"import"        { EMIT("RESERVADA", "RES_IMPORT"); }
"init"          { EMIT("RESERVADA", "RES_INIT"); }
"param"         { EMIT("RESERVADA", "RES_PARAM"); }
"property"      { EMIT("RESERVADA", "RES_PROPERTY"); }
"receiver"      { EMIT("RESERVADA", "RES_RECEIVER"); }
"set"           { EMIT("RESERVADA", "RES_SET"); }
"setparam"      { EMIT("RESERVADA", "RES_SETPARAM"); }
"where"         { EMIT("RESERVADA", "RES_WHERE"); }
"actual"        { EMIT("RESERVADA", "RES_ACTUAL"); }
"abstract"      { EMIT("RESERVADA", "RES_ABSTRACT"); }
"annotation"    { EMIT("RESERVADA", "RES_ANNOTATION"); }
"companion"     { EMIT("RESERVADA", "RES_COMPANION"); }
"const"         { EMIT("RESERVADA", "RES_CONST"); }
"crossinline"   { EMIT("RESERVADA", "RES_CROSSINLINE"); }
"data"          { EMIT("RESERVADA", "RES_DATA"); }
"enum"          { EMIT("RESERVADA", "RES_ENUM"); }
"expect"        { EMIT("RESERVADA", "RES_EXPECT"); }
"external"      { EMIT("RESERVADA", "RES_EXTERNAL"); }
"final"         { EMIT("RESERVADA", "RES_FINAL"); }
"infix"         { EMIT("RESERVADA", "RES_INFIX"); }
"inline"        { EMIT("RESERVADA", "RES_INLINE"); }
"inner"         { EMIT("RESERVADA", "RES_INNER"); }
"internal"      { EMIT("RESERVADA", "RES_INTERNAL"); }
"lateinit"      { EMIT("RESERVADA", "RES_LATEINIT"); }
"noinline"      { EMIT("RESERVADA", "RES_NOINLINE"); }
"open"          { EMIT("RESERVADA", "RES_OPEN"); }
"operator"      { EMIT("RESERVADA", "RES_OPERATOR"); }
"out"           { EMIT("RESERVADA", "RES_OUT"); }
"override"      { EMIT("RESERVADA", "RES_OVERRIDE"); }
"private"       { EMIT("RESERVADA", "RES_PRIVATE"); }
"protected"     { EMIT("RESERVADA", "RES_PROTECTED"); }
"public"        { EMIT("RESERVADA", "RES_PUBLIC"); }
"reified"       { EMIT("RESERVADA", "RES_REIFIED"); }
"sealed"        { EMIT("RESERVADA", "RES_SEALED"); }
"suspend"       { EMIT("RESERVADA", "RES_SUSPEND"); }
"tailrec"       { EMIT("RESERVADA", "RES_TAILREC"); }
"vararg"        { EMIT("RESERVADA", "RES_VARARG"); }

 /* Cadenas (strings)*/
\"\"\"([^\"]|\"[^\"]|\"\"[^\"])*\"\"\"   { contar_saltos_linea(yytext); EMIT("CADENA", "STRING_TRIPLE"); }
\"([^\"\\\n]|\\.)*\"                    { EMIT("CADENA", "STRING"); }

    /* Numeros flotantes (antes que enteros)*/
{DIGITO}+"."{DIGITO}+([eE][+-]?{DIGITO}+)?[fF]?   { EMIT("FLOTANTE", "NUM_FLOTANTE"); }
{DIGITO}+[eE][+-]?{DIGITO}+[fF]?                  { EMIT("FLOTANTE", "NUM_FLOTANTE"); }
{DIGITO}+[fF]                                     { EMIT("FLOTANTE", "NUM_FLOTANTE"); }

    /*  Numeros enteros  */
{DIGITO}({DIGITO}|"_")*[lL]?                      { EMIT("ENTERO", "NUM_ENTERO"); }

    /* Identificadores  */
{LETRA}({LETRA}|{DIGITO})*          { EMIT("IDENTIFICADOR", "ID"); }

    /* Operadores (mas de 10 distintos, con token especifico cada uno) */
"=="        { EMIT("OPERADOR", "OP_IGUAL"); }
"!="        { EMIT("OPERADOR", "OP_DIFERENTE"); }
"<="        { EMIT("OPERADOR", "OP_MENORIGUAL"); }
">="        { EMIT("OPERADOR", "OP_MAYORIGUAL"); }
"&&"        { EMIT("OPERADOR", "OP_AND"); }
"||"        { EMIT("OPERADOR", "OP_OR"); }
"++"        { EMIT("OPERADOR", "OP_INCREMENTO"); }
"--"        { EMIT("OPERADOR", "OP_DECREMENTO"); }
"+="        { EMIT("OPERADOR", "OP_SUMA_ASIGNA"); }
"-="        { EMIT("OPERADOR", "OP_RESTA_ASIGNA"); }
"*="        { EMIT("OPERADOR", "OP_MULT_ASIGNA"); }
"/="        { EMIT("OPERADOR", "OP_DIV_ASIGNA"); }
"->"        { EMIT("OPERADOR", "OP_FLECHA"); }
"?:"        { EMIT("OPERADOR", "OP_ELVIS"); }
"?."        { EMIT("OPERADOR", "OP_SAFECALL"); }
".."        { EMIT("OPERADOR", "OP_RANGO"); }
"<"         { EMIT("OPERADOR", "OP_MENOR"); }
">"         { EMIT("OPERADOR", "OP_MAYOR"); }
"+"         { EMIT("OPERADOR", "OP_SUMA"); }
"-"         { EMIT("OPERADOR", "OP_RESTA"); }
"*"         { EMIT("OPERADOR", "OP_MULT"); }
"/"         { EMIT("OPERADOR", "OP_DIV"); }
"%"         { EMIT("OPERADOR", "OP_MOD"); }
"="         { EMIT("OPERADOR", "OP_ASIGNA"); }
"!"         { EMIT("OPERADOR", "OP_NOT"); }
"."         { EMIT("OPERADOR", "OP_PUNTO"); }
","         { EMIT("OPERADOR", "OP_COMA"); }
":"         { EMIT("OPERADOR", "OP_DOSPUNTOS"); }
";"         { EMIT("OPERADOR", "OP_PUNTOCOMA"); }
"("         { EMIT("OPERADOR", "OP_PARENIZQ"); }
")"         { EMIT("OPERADOR", "OP_PARENDER"); }
"{"         { EMIT("OPERADOR", "OP_LLAVEIZQ"); }
"}"         { EMIT("OPERADOR", "OP_LLAVEDER"); }
"["         { EMIT("OPERADOR", "OP_CORCHETEIZQ"); }
"]"         { EMIT("OPERADOR", "OP_CORCHETEDER"); }

    /* Cualquier otro caracter no reconocido */
.           { fprintf(stderr, "Advertencia: caracter no reconocido '%s' en linea %d\n", yytext, yylineno); }

%%

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <archivo_fuente.kt>\n", argv[0]);
        return 1;
    }
    FILE *entrada = fopen(argv[1], "r");
    if (!entrada) {
        fprintf(stderr, "No se pudo abrir el archivo: %s\n", argv[1]);
        return 1;
    }
    yyin = entrada;
    yylex();
    fclose(entrada);
    return 0;
}