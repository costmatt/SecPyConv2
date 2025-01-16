import re
import sys

# Assembly instructions to C/C++ equivalents
instruction_map = {
    "mov": " = ",
    "add": " += ",
    "sub": " -= ",
    "push": "// push ",
    "pop": "// pop ",
    "call": "// call ",
    "ret": "return",
    "cmp": "// compare ",
    "jnz": "// jump if not zero ",
    # Add more mappings as needed
}

def detect_language(assembly_code):
    """Detect whether to convert to C or C++ based on assembly code."""
    for line in assembly_code.split('\n'):
        if "malloc" in line:
            return "C++"
    return "C"

def convert_assembly_to_c_cpp(assembly_code, language):
    c_code = []
    if language == "C++":
        c_code.append("#include <iostream>")
        c_code.append("#include <cstdlib>")
        c_code.append("using namespace std;")
    else:
        c_code.append("#include <stdio.h>")
        c_code.append("#include <stdlib.h>")
    
    c_code.append("\nint main() {")
    c_code.append("    int* head = nullptr; // var_8")
    c_code.append("    int counter = 1; // var_C")

    while_loop_started = False

    for line in assembly_code.split('\n'):
        # Remove comments and unnecessary whitespace
        line = line.split(';')[0].strip()
        if not line:
            continue

        # Match assembly instruction and operands
        match = re.match(r"(\w+)\s+(.*)", line)
        if match:
            instr, operands = match.groups()
            if instr in instruction_map:
                c_instr = instruction_map[instr]
                if instr == "mov":
                    dst, src = operands.split(', ')
                    c_line = f"    {dst} {c_instr} {src};"
                elif instr in {"add", "sub"}:
                    dst, src = operands.split(', ')
                    c_line = f"    {dst} {c_instr} {src};"
                elif instr == "cmp":
                    c_line = f"    if ({operands}) // compare"
                elif instr == "jnz":
                    c_line = f"    if ({operands} != 0) // jump if not zero"
                elif instr == "push" or instr == "call":
                    c_line = f"    {c_instr} {operands};"
                else:
                    c_line = f"    {c_instr}{operands};"
                c_code.append(c_line)
            else:
                c_code.append(f"    // Unknown instruction: {line}")
        else:
            c_code.append(f"    // Cannot parse: {line}")

        if "jmp" in line and not while_loop_started:
            c_code.append("    while (counter <= 10) {")
            while_loop_started = True

    if while_loop_started:
        c_code.append("    }")

    # Add checks for memory leaks and buffer overflows
    c_code.append("    // Free allocated memory")
    c_code.append("    int* currentNode = head;")
    c_code.append("    while (currentNode != nullptr) {")
    c_code.append("        int* nextNode = reinterpret_cast<int*>(*(currentNode + 1));")
    c_code.append("        free(currentNode);")
    c_code.append("        currentNode = nextNode;")
    c_code.append("    }")

    c_code.append("    return 0;")
    c_code.append("}\n")
    return '\n'.join(c_code)

def main():
    if len(sys.argv) != 2:
        print("Usage: python SecPyConv2.py <assembly_code.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r') as file:
            assembly_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)

    language = detect_language(assembly_code)
    c_code = convert_assembly_to_c_cpp(assembly_code, language)

    # Print converted code to terminal
    print("Converted C/C++ Code:")
    print(c_code)

    # Save converted code to a file
    output_file = f"converted_code.{language.lower()}"
    with open(output_file, 'w') as file:
        file.write(c_code)
    print(f"Converted code has been saved to '{output_file}'")

if __name__ == "__main__":
    main()
