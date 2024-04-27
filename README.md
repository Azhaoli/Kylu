# Kylu
A minimalistic scripting language written in python3

RAW FILE IS SIGNIFICANTLY MORE LEGIBLE
#### ################################################################################################################
#### #                                             _---___                                                          #
#### #                                        __  /       \                                                         #
#### #                                       /  \ \       / __                                                      #
#### #   KYLU PROJECT DOCUMENTATION         /___| |______/ /  \                                                     #
#### #   release build alpha 1.7             ___| |______ |   |                                                     #
#### #                                      \   | |      \ \__/                                                     #
#### #   Azhaoli c2024                       \__/ /       \                                                        ##
#### #                                            \_    __/                                                      ##
#### #                                               ~~~                                                       ##
#### #                                                                                                       ##
#### ########################################################################################################

########################################################################################################################
########    1- Intro (numbers, strings, symbols, lists, booleans, basic operations)    #################################
############################################################################################################

########    1.1- Numbers    ############################################################################################

Numbers are any string of the characters 0, 1, 2, 3, 4, 5, 6, 7, 8, and 9, containing an optional decimal point (.).
They can be used in numerical expressions or compared with logical operators.
Unlike in python, floats and integers are treated exactly the same by the interpreter. If a float is within the rounding
tolerance of an integer, it will be rounded to that integer. The rounding tolerance setting can be set in the Node.__init__
function, Node.RoundingTolerance is set to 0.00001 by default. This feature can be disabled by setting the rounding
tolerance to 0.

examples:
1.2
34.002

illegal:
.0112
0.233.401
10e5


########    1.2- Strings    ############################################################################################

Strings can be any set of characters enclosed by single ('') or double ("") quotes representing words and phrases, or literals.
They are the only data type that can be read out to the Kylu terminal via the 'write' built in function (read more
about functions in section 3).
Anything passed into 'write' must be able to be converted to a string otherwise, the interpreter will return the raw parsetree
data via Node.__repr__.

exmple:
"hello!"
'Goodbye'

illegal:
'str
"string'
"abc"def"


########    1.3- Symbols    ############################################################################################

Symbols can be any set of alphanumeric characters, but the first character must be alphabetic. They are used to name or
encapsulate values (numbers, strings, bools, etc) or pieces of code.
Symbols are the only data type that can be used as function arguments or indeces in iterator loops (see section 2.2a).
Symbols are used by the interpreter to keep track of stored data, and are the only data type that can be linked to another
value.
Any expression that accesses the interpreter's stored memory must evaluate to a symbol.

examples:
arg__
v4ri4b13

illegal:
23number
_value


########    1.4- Lists    ##############################################################################################

Lists are any set of values enclosed by square brackets separated by commas. They are a way to concisely organize and
store several values for later access.
Any valid syntax expression including loops, objects and if statements can be elements in a list (see details in section 2 and 3.5).
Lists can be indexed or sliced using the 'getitem' (:) operator with another list.
When slicing a list, the first number indicates the start index, the second indicates the end index, and the third number
specifies how many indeces to move along the list between each value (step). Unlike in python, the value at the stop index is also
included in the slice unless it is out of the array's range.

examples:
[1, 2, "string", [12, 5], True, loop iter(a, [1, 3, 5]){ [a+3] }, 5]

indexing:
list <- [1, 3, 5, 7, 9]
a <- list:[3]  <--- 'a' has a value of of 7

slicing:
list <- [1, 3, 5, 7, 9]
list:[1, 3, 1] <--- this expression has a value of [3, 5, 7]

########    builtin list operations
linear algebra
- dot(list1, list2) will take the dot product of 2 vectors or matrices
- det(list) will take the determinant of a square matrix
- adj(matrix) gives the adjoint/ adjunction of a matrix
- T(matrix) transposes a matrix
- product(list) will multiply all elements in a list together, and return a number
- inverse(list) will return the inverse of a square matrix such that list * invert(list) gives the identity matrix
logic
- span(list1, list2) will return all ordered sets of values between 2 points (python range() but multidimensional)
- in(elem, list) will return 'True' if elem occurs within list
- similar(list1, list2) returns another list of all elements list1 and list2 have in common
- different(list1, list2) returns another list of all elements list1 and list2 do not have in common
basic arithmetic
- list + elem will append a new element to the end of list
- list - elem will remove elem from a list


########    1.5- The assignment operator    ############################################################################

Any expression or value can be assigned to a symbol using the assignment operator '<-'. The values assigned to symbols will
be retrieved from the current variable cache whenever their names are referenced elsewhere in the code.
Values can also be added to the variable space directly outside where the code is currently working using the attrubute
operator (@) (read section 3.4).
The assignment operator cannot add new elements to a list, but can mutate currently existing values at a specific index.
The assignment operator can add new attributes to object instances.
An expression using the assignment operator returns the value being assigned, this allows chaining assignments to quickly set multiple
variables to a single value, as well as enabling assignment operations to be placed inside other expressions.
In Kylu a1.7 elements can only be passed and retrieved by value, never by reference, so read and write operations to the interpeter's
stored memory will always be declared directly.

examples:
n <- 1.25
var <- "bonjour" = "hello"
list:[5] <- obj(a, b, c)( out(a+b*c) )
@Object:property <- w <- 2

illegal:
"var" <- 12
22 <- a


########    1.6- Algebraic and Logical Operators    ####################################################################

#### NUMBER/ other objects -> NUMBER/ other objects
Numbers, symbols, and strings can be combined into expressions using arithmetic operators.
Each allowed type pairing is manually programmed into the Interpreter.operTable dictionary.

+ add, append
- subtract, remove
* multiply
/ divide
^ exponent
% modulus
#### each of the above operators has a self-assign equivalent
example: 
a <- 3   <--- initialize variable 'a'
a <-+ 2   <--- add 2 to 'a' and assign the result to 'a', same as a <- a+2, variable must be initialized first

other examples:
a + b
"hel" + "lo"
2 * "w"
1 + 2

Illegal:
"w" + 3
True * 5

#### NUMBER -> BOOL
Numbers can be compared, and combined into boolean expressions using logical operators.
When a logical operation is performed on two elements, the result is a boolean.

> greater than
< less than
= equal to
>= greater than or equal to
<= less than or equal to

examples:
1 > 3
a = 2

illegal:
"s" > 2
True > "hello world"

#### BOOL -> BOOL
Booleans can be compared using logic gate operators, which will return another boolean.

<!> not returns the inverse of the value to the right
<:> or True if one or both values are True
<!:> nor True if or both values are False
<+> and True if both values are True
<!+> nand True if one or both values are False
<^> xor True if only one value is True
<!^> xnor True if both or neither values are True

operations such as <->, <-=, and <-<^> are not yet supported, but I am planning to add them in future versions


########    1.7- How to Use the Interpreter Interface    ###############################################################

Currently, the Kylu interpreter does not fuction as a standalone program, and must be run using the python interpreter.
All files run by the kylu interpreter must have the .kylu extention.
Type '/kyedit' into the terminal to write programs with multiple lines, then type '/done' on a seperate line to complete
and run the program.
The terminal editor may have additional features similar to the nano text editor in later versions.
Typing '/exit' will quit the terminal.
pressing ctrl+c will halt the terminal immediately

example:
(on your terminal)
user@computer:~/ProjectDir$ python3 Kylu_a1.7.py --file testfile.kylu
#### output from testfile will be seen here

user@computer:~/ProjectDir$ python3 Kylu_a1.7.py
#### system welcome message
                                             _---___
                                        __  /       \
                                       /  \ \       / __
   KYLU PROJECT TERMINAL              /___| |______/ /  \
   release build alpha 1.7             ___| |______ |   |
                                      \   | |      \ \__/
   Azhaoli c2024                       \__/ /       \
                                            \_    __/
                                               ~~~

(kylu)->


########################################################################################################################
########    2- Basic Programming (if statements, while/ for loops)    ##################################################
############################################################################################################

########    2.1- If statements    ######################################################################################

If statements are invoked using the 'if' keyword, the statement contains two required fields, and an optional third field.
The first contains a boolean expression, and the second contains an action to perform if the condition in the first field 
is true.
The user can specify an action to perform if the condition is false, or chain another 'if' statement on the end with a comma (,).
If another statement is chained onto the first, the expression behaves like a traditional 'elif' statement.

examples:
if (2 < 4){ write("4 is greater!") }{ write("2 is greater!") }
     action if true ^^^^^     action if false ^^^^^

a <- 2
if ( a < 5 ){ write("less than 5") }, if ( a < 10 ){ write("less than 10") }{ write("10 or greater!") }
        comma to connect statements ^

when an if statement is evaluated, it will return the result of the last expression in whatever field is run
q <- 3
var <- if (q > 5){ write("q is more than 5")  4 }{  write("q is less than 5")  9 }   <--- 'var' has a value of 9


########    2.2- Loop statements    ####################################################################################

Loop statements are invoked using the 'loop' keyword, and followed by a loop type keyword, either 'iter' or 'cond'
in both cases, the statement contains two required fields.

########    2.2a- While loops    ########
In the case of conditional loops, the first field contains a boolean expression, while the second contains an action to
perform repeatedly as long as the expression in the first field evaluates to true.

examples:
a <- 0
loop cond (a < 5){ write(a)  a <-+ 1 }   <--- add 1 to 'a' until it is greater than 4


########    2.2b- For loops    ########
In the case of iterator loops, the first field contains an index to name each element in an iterator, and an iterable object.
For loops can iterate over multiple iterators at once in an embedded loop, each index/ iterator combination is in a separate
field with the outermost loop being first.
the last field is an action to be performed for each element in the iterable object(s).

examples:
loop iter (a, [0, 1, 2, 3, 4]){ write(a) }

the repeated block can be used to generate a list that the loop statement will return
similar to if statements, the result of the last statement in the action field will be added to the generated list
list1 <- [1, 2, 3]
list2 <- [4, 5, 6]

list3 <- loop iter(a, list1){ a+1 }   <--- list3 has a value of [2, 3, 4]

list4 <- loop iter(a, list1)(b, list2){ [a, b] }   <--- list4 has a value of [[[1, 4], [1, 5], [1, 6]], [[2, 4], [2, 5], [2, 6]], [[3, 4], [3, 5], [3, 6]]]

if the repeated block contains more than one expression, both expressions will be added to the list
list1 <- [1, 2, 3]
list2 <- [4, 5, 6]

w <- loop iter (x, list1)(y, list2){ x  y }   <--- w has a value of [[1, 4, 1, 5, 1, 6], [2, 4, 2, 5, 2, 6], [3, 4, 3, 5, 3, 6]]


########    2.3- Importing Variables From Other Programs    ############################################################

Users can add the variables from other files in the current directory using the 'ext' function.
The 'ext' function opens and runs the specified file, then appends all the variables to the current variable cache as an object
instance with the same name as the imported file.
Variables added with the 'ext' function can be accessed from any scope in the code similar to standard library functions.


examples:
in file file1.kylu

var1 <- 1
var2 <- 2

in file file2.kylu

ext(file1)   <--- add an object instance named file1 to the current variable space

write( file1:var1 + 3 )   <--- display a value of 4
write( file1:var2 + 6 )   <--- display a value of 8


########################################################################################################################
########    3- Objects and Object Properties (getitem statements, obj/subobj declarations)    ##########################
############################################################################################################

########    3.1- Defining callable objects    ###########################################################################

Objects are created using the 'obj' keyword, and followed by two required fields
The first field contains a list of symbols, or arguments that will be assigned values in the local scope when the object is
instantiated, the second is an action, or set of actions to take when the object is called.
Objects are anonymous like every other syntax expression, and can only be accessed later if they are assigned to a variable
or placed in another data structure during declaration.
Objects will return an object instance when called if no return value is specified with the 'out' function, this will cause
them to behave similarly to python's classes.


examples:
func <- obj(arg1, arg2, arg3)(
   c <- arg1 + arg2
   e <- c + arg3
   out(e)
)


########    3.2- Calling objects     ###################################################################################

Objects can be called using the name of the symbol they were assigned to during declaration, and a field containing values
to be assigned to the object's arguments.
The arguments are assigned values based on the values listed in the call, and each action will be run sequentially until
the function ends, or the 'out' function is called.

example:
func <- obj(a, b, c){
   write(a, b, c)
   out(a+b*c)
}

'func' is called with arguments 1, 4, and 2
var <- func(1, 4, 2)   <--- a value of 9 will be assigned to 'var'


########    3.3- Object properties    ##################################################################################

Properties are variables that are assigned a value inside the context of an object. These variables are added to the
object's internal data along with the arguments passed into it.
Properties can be accessed from outside the function using the 'getitem' (:) operator.
Currently, only object instances and lists support the getitem operation since the properties inside an object are not
valid until the context of the object is created during calling/ instancing.
Properties can also be accessed from inside sub-objects using the 'attribute' (@) operator (see next section).

examples:
defining the object
object <- obj(a, b, c){
   d <- "w"
}
objects are abstract structures, so object:a does not represent a valid property

instancing the object
inst <- object("x", "y", "z")

accessing the instance's properties
write(inst:a, inst:b)   <--- writes values "x", and "y" to the console


########    3.4- Sub objects    ########################################################################################

Objects can contain other objects as their properties, these sub-objects have exactly the same behavior as standalone objects
and can be instanced by other sub objects. Internal objects can be instanced from outside the base object as long as they are 
properties of a valid object instance.

examples:
the inner object has access to the properties of the object containing it
incr, and decr can access the 'a' attribute, but not the 'arg1', 'arg2', and 'arg3' attributes

struct <- obj( arg1, arg2, arg3 ){
 arg4 <- "hello"
 substruct <- obj( a ){
     incr <- obj(){ @a <-+ 1  write(@a) }
     decr <- obj(){ @a <-- 1  write(@a) }
}}

'struct' is instanced, then it's property 'substruct' is retrieved and instanced
the instance of 'substruct' is assigned to 'foo'
foo <- struct( 2, 5, 6 ):substruct(3)

foo:incr()   <--- this gives a value of 4 for @a
foo:decr()   <--- this gives a value of 3 for @a


########    3.5- Indirect object calls    ##############################################################################

Objects are the only data type in kylu that is callable as of version a1.7, but any expression that evaluates to an object
is also callable.

list <- [1, "e", True, obj(a, b, c){ out(a+b-c) }, [], 12]
result <- (list:[3])(1, 3, 5)   <--- result has a value of -1

num1 <- 4
num2 <- 5

( if(num1 > num2){ obj(x, y, z){write(x+y-z)} }{ obj(a, b, c){write("hello!")} } )(5, 8, 13)

since the call brackets will be applied to the closest valid expression (the list) parentheses need to be added to the indexing
expression to ensure it is evaluated first


########    3.6- Monadic design patterns    ############################################################################

Monads help keep code concise in many circumstances when a value needs to have several consecutive checks or operations applied 
to it. if a value or piece of code needs multiple errors to be caught, the nested if statements can get out of control quickly.
This is a crude early example of how the macro system could be used to enable procedural code expansion at parse time in
future versions.

Example of a basic monad object:

monad <- obj(val, self){
    bind <- obj(func){   <--- monadic bind function
        @val <- func(@val)   <--- apply specified function (takes exactly 1 parameter, returns 1 value)
        out(@self(@val, @self))   <--- set the stored value to the result of the function
    }
}
The above code is inserted directly into the local variable cache at runtime in the a1.7 proof of concept build

h <- obj(val){ out(val*5) }

f <- monad(7, monad)
g <- f:bind(h):bind(h):bind(h)
write(g:val)   <--- g:val has a value of 875 or 7*5*5*5

This is an incredibly useful design pattern, so the code can be abbreviated:

h <- obj(val){ out(val*5) }   <--- obejct that takes 1 argument, and returns a value

f <- monad(7)   <--- instance of builtin monad object
g <- f:bind(h):bind(h):bind(h)
write(g:val)


########################################################################################################################
########    4- Misc features I don't have enough content to make sections on individually    ###########################
############################################################################################################

########    4.1- Error Handling    #####################################################################################

The builtin 'Error' function allows the user to reproduce any error that can be raised by the interpreter.
The Error function takes in 1 to 4 arguments, the first is the type of the error represented as a string
ex: "INVALIDOPERATION", the other arguments incude any additional data neccessary to throw the error

example:
Error("INVALIDOPERATION", "+", "a", "b")

#### will show the message if uncaught:
INVALIDOPERATION: OPERATION '+' IS NOT SUPPORTED FOR TYPES a, b
[!] [0, 40] CALL --- Error("INVALIDOPERATION", "+", "a", "b")

The 'expect' object can be used to catch errors of a specified type, and perform a set of actions.
If the code targeted by the expect block generates an error of a different type from the type being caught, or no error
is produced, the expression will have no effect on the execution of the targeted code, returning whatever the target
code eveluated to.

(a:b):expect(NULLREFERENCE){ write("object a has no valid property b") }

Expect expressions can be chained together to catch multiple types of errors

(a:b - c):expect(NULLREFERENCE){
    write("object a has no valid property b")
}:expect(INVALIDOPERATION){
    write("subtract operation failed")
}

########    4.2- Builtin operator overloading    #######################################################################

If an object contains an overloading method, the method will replace the builtin method for the overloaded operation
whenever an instance of the object is used in that operation.
Functionality will be added later to allow object instances to be callable, iterable, assignable, or represented by
the write function in a customizable way.
Currently, overloading only allows object instances to be used in algebreic expressions

Length <- obj(cm){
    extend <- obj(length){
        @cm += length  write("measurment extended by", length)
    }
    ADD <- obj(other){
        Length(out(@cm + other:cm))
    }
    DISPLAY <- obj(){ out("Length measurment: " + toInt(@cm/100) + " meters, " + @cm%100 + " centimeters") }
}
l1 <- Length(300)
l2 <- Length(422)

write( l1 + l2 )   <--- writes "Length measurment: 7 meters, 22 centimeters" to the screen

Currently implemented functions:
ADD, SUB, MULTIPLY, DIVIDE, MODULUS, GREATER, LESS

Functions currently planned for next version, changes to standard operator handling required:
DISPLAY, CALL, ITERATE, ASSIGNVALUE, GETITEM


