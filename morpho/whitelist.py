
# These are the only multi-character words (except digits)
# that are allowed to appear in any expression.
# It also contains all allowable punctuation symbols.
whitelist = {
"zeta",

"acos",
"acosh",
"asin",
"asinh",
"atan",
"atanh",
"cos",
"cosh",
"exp",
"isfinite",
"isinf",
"isnan",
"log",
"log10",
"phase",
"sin",
"sinh",
"sqrt",
"tan",
"tanh",
"pi",

"atan2",
"ceil",
"degrees",
"erf",
"erfc",
"expm1",
"fabs",
"factorial",
"floor",
"fmod",
"gamma",
"hypot",
"ldexp",
"lgamma",
"log1p",
"log2",
"pow",
"radians",
"trunc",

"isbadnum",
"ln",
"tau",
"fact",

"1j",
"real",
"imag",
"re",
"im",
"arg",
"angle",
"phase",
"abs",
"norm",
"conj",
"mod",

"mat",
"inv",
"det",

"sum",
"prod",
"product",
"range",
"seq",
"inf",
"nan",

"for",
"in",
"if",
"else",
"and",
"or",
"not",
"min",
"max",

"disk",

"+", "-", "*", "/", "%", "^",
"=", "!", "<", ">",
"(", ")", "[", "]",
",", "."
}

# Extracts all "words" from a string.
# i.e. all isolated substrings of alphanumeric characters
# (including underscores).
def getWords(st):
    words = set()
    word = ""
    for ch in st:
        if ch.isalnum() or ch == "_":
            word += ch
        elif len(word) > 0:
            words.add(word)
            word = ""
    if len(word) > 0:  # If the string ENDS with a word
        words.add(word)
    return words

# Extract all non-alphanumeric characters
# (except spaces and underscores)
def getSymbols(st):
    symbols = set()
    for ch in st:
        if not ch.isalnum() and ch != "_" and ch != " ":
            symbols.add(ch)
    return symbols

# Returns True iff all the words are either single letters,
# strings of pure digits (e.g. 12345), or are in the whitelist,
# AND all the symbols are in the whitelist.
# NOTE: This function is NOT case-sensitive.
def safeExpr(expr, whitelist=whitelist):
    # Check all words
    words = getWords(expr.lower())
    for word in words:
        if len(word) > 1 and (not word.isdigit()) and word not in whitelist:
            return False
        if word == "_":  # No single underscores
            return False

    # Now check symbols
    return (getSymbols(expr).issubset(whitelist))

# Given a list of frames, checks that all of the function formulas
# are safe according to safeExpr().
def checkFramelist(frames, whitelist=whitelist):
    for frm in frames:
        # If there's no "function" attribute (e.g. in the Domain frame)
        # then there's nothing to check. Continue.
        if "function" not in frm.__dict__:
            continue
        if not safeExpr(frm.function, whitelist):
            return False
    return True
