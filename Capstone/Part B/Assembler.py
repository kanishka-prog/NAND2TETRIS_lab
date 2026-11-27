
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101"
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576
}

for i in range(16):
    PREDEFINED["R" + str(i)] = i


def clean_lines(filename):
    lines = []
    with open(filename, "r") as file:
        for line_number, line in enumerate(file, 1):
            line = line.split("//")[0].strip()
            if line:
                lines.append((line, line_number))
    return lines


def assemble(filename):
    lines = clean_lines(filename)
    symbols = PREDEFINED.copy()
    instructions = []
    rom_address = 0

    # FIRST PASS: labels
    for line, line_number in lines:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]

            if label in symbols:
                print("Warning: Duplicate label:", label,
                      "at line", line_number)
            else:
                symbols[label] = rom_address
        else:
            instructions.append((line, line_number))
            rom_address += 1

    # SECOND PASS: convert instructions
    result = []
    next_variable = 16

    for line, line_number in instructions:
        try:
            if line.startswith("@"):
                value = line[1:]

                if value.isdigit():
                    address = int(value)
                else:
                    if value not in symbols:
                        symbols[value] = next_variable
                        next_variable += 1
                    address = symbols[value]

                if address < 0 or address > 32767:
                    raise ValueError("Address out of range")

                binary = format(address, "016b")

            else:
                dest = ""
                jump = ""
                comp = line

                if "=" in comp:
                    dest, comp = comp.split("=")

                if ";" in comp:
                    comp, jump = comp.split(";")

                if comp not in COMP:
                    raise ValueError("Invalid comp")

                if dest not in DEST:
                    raise ValueError("Invalid dest")

                if jump not in JUMP:
                    raise ValueError("Invalid jump")

                binary = "111" + COMP[comp] + DEST[dest] + JUMP[jump]

            result.append(binary)

        except Exception as error:
            print("Line", line_number, ":", error)
            return

    output_file = filename.rsplit(".", 1)[0] + ".hack"

    with open(output_file, "w") as file:
        file.write("\n".join(result) + "\n")

    print("Assembly successful!")
    print("Output saved in:", output_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py filename.asm")
    else:
        assemble(sys.argv[1])
