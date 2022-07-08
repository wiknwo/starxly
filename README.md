# What is Starxly 🌠🌌?

Starxly is an interpreted mini programming language based on BASIC. 
It offers features to do arithmetic with integers and floats and has 
a simple grammar that defines the language.

## Features of Starxly

- Simple syntax
- Supports floating point and integer numbers
- Additon: ```1 + 2 = 3```
- Subtraction: ```1 - 2 = -1```
- Multiplication: ```1 * 2 = 2```
- Division: ```1 / 2 = 0.5```
- Unary Operators: ```-1 + 2 = 1```
- Precedence Rules: ```(9 * 8) - (-4 * 5) + 47 = 139```

## Starxly's Grammar

Starxly's grammar is composed of expressions. Expressions are composed of terms and factors. 
Terms are composed of factors. Factors are the most fundamental elements in Starxly's grammar.
With expressions, terms and factors, we can define the starxly programming language in its 
entirety.

<table>
    <tr>
        <th>Concept</th>
        <th>Pattern</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>term ((PLUS|MINUS) term)*</td>
    </tr>
    <tr>
        <td>term</td>
        <td>factor ((MUL|DIV) factor)*</td>
    </tr>
    <tr>
        <td>factor</td>
        <td>INT|FLOAT</br>(PLUS|MINUS) factor</br>LPAREN expression RPAREN</td>
    </tr>
    
</table>
