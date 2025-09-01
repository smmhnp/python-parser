import re
import sys
import os

# ...................... Language Definitions ......................

def is_in_l1(s):
    if not re.match(r'^a+b*$', s):
        return False
    n = s.count('a')
    m = s.count('b')
    if m == 0:
        return n > 0
    return m < n and n <= 3 * m

def is_in_l2(s):
    if not re.match(r'^a*b*c*$', s):
        return False
    n_a = s.count('a')
    n_b = s.count('b')
    return n_a == n_b

def is_in_l3(s):
    if not re.match(r'^a*b*c*$', s):
        return False
    n_b = s.count('b')
    n_c = s.count('c')
    return n_b == n_c

def is_in_l4(s):
    if not re.match(r'^[ab]*$', s):
        return False
    n_a = s.count('a')
    n_b = s.count('b')
    return n_a == n_b

# ...................... Operation Handlers ......................

def handle_union(lang1, lang2):
    def union_checker(s):
        return lang1(s) or lang2(s)
    return union_checker

def handle_concat(lang1, lang2):
    def concat_checker(s):
        for i in range(len(s) + 1):
            part1 = s[:i]
            part2 = s[i:]
            if lang1(part1) and lang2(part2):
                return True
        return False
    return concat_checker

def handle_star(lang):
    def star_checker(s):
        if s == '':
            return True
        for i in range(1, len(s) + 1):
            part = s[:i]
            if lang(part):
                remaining = s[i:]
                if handle_star(lang)(remaining):
                    return True
        return False
    return star_checker

# ...................... Parser ......................

def parse_language_expression(expr):
    lang_map = {
        'L1': is_in_l1,
        'L2': is_in_l2,
        'L3': is_in_l3,
        'L4': is_in_l4
    }
    temp = 100
    expr = re.sub(r'\s+', '', expr)

    # Handle parentheses with nested expressions
    def find_innermost_paren(expr):
        stack = []
        start = -1
        for i, char in enumerate(expr):
            if char == '(':
                stack.append(i)
                if start == -1:
                    start = i
            elif char == ')':
                if stack:
                    start_idx = stack.pop()
                    if not stack:  # Found the innermost pair
                        return start_idx, i
        return None, None

    # Process parentheses
    while True:
        start, end = find_innermost_paren(expr)
        if start is None:
            break
        sub_expr = expr[start + 1:end]
        parsed = parse_language_expression(sub_expr)  # Recursively parse the subexpression
        temp_key = f"L{temp}"
        lang_map[temp_key] = parsed
        expr = expr[:start] + temp_key + expr[end + 1:]
        temp += 1

    # Handle Kleene Star
    while re.search(r'(L\d+)\*', expr):
        match = re.search(r'(L\d+)\*', expr)
        lang_key = match.group(1)
        if lang_key not in lang_map:
            print(f"Error: Language {lang_key} not defined")
            sys.exit(1)
        temp_key = f"L{temp}"
        lang_map[temp_key] = handle_star(lang_map[lang_key])
        expr = expr.replace(f"{lang_key}*", temp_key)
        temp += 1

    # Handle Concatenation (.)
    while re.search(r'(L\d+)\.(L\d+)', expr):
        match = re.search(r'(L\d+)\.(L\d+)', expr)
        lang1, lang2 = match.group(1), match.group(2)
        if lang1 not in lang_map or lang2 not in lang_map:
            print(f"Error: Language {lang1} or {lang2} not defined")
            sys.exit(1)
        temp_key = f"L{temp}"
        lang_map[temp_key] = handle_concat(lang_map[lang1], lang_map[lang2])
        expr = expr.replace(f"{lang1}.{lang2}", temp_key)
        temp += 1

    # Handle Union (+)
    while re.search(r'(L\d+)\+(L\d+)', expr):
        match = re.search(r'(L\d+)\+(L\d+)', expr)
        lang1, lang2 = match.group(1), match.group(2)
        if lang1 not in lang_map or lang2 not in lang_map:
            print(f"Error: Language {lang1} or {lang2} not defined")
            sys.exit(1)
        temp_key = f"L{temp}"
        lang_map[temp_key] = handle_union(lang_map[lang1], lang_map[lang2])
        expr = expr.replace(f"{lang1}+{lang2}", temp_key)
        temp += 1

    if expr not in lang_map:
        print(f"Error: Invalid expression '{expr}'")
        sys.exit(1)

    return lang_map[expr]

# ...................... Main Program ......................

def process_file(expression, file_path):
    if not os.path.exists(file_path):
        print("Error: File not found")
        sys.exit(1)

    checker = parse_language_expression(expression)
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    for i, line in enumerate(lines, 1):
        result = '✅ Yes' if checker(line) else '❌ No'
        print(f"Line {i}: {line} => {result}")

# Command-line execution
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python lang_checker.py \"<expression>\" <file_path>")
        sys.exit(1)
    
    expression = sys.argv[1]
    file_path = sys.argv[2]
    process_file(expression, file_path)