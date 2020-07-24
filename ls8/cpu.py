"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0x0] * 0x8
        self.ram =[0x0] * 0x100
        self.pc = 0x0
        self.fl = 0b00000000 #LGE L: 0b00000100/0x04 G:0b00000010/0x02 E:0b00000001/0x01
        self.SP = 0x7
        self.reg[self.SP] = 0xf4

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        return self.ram[MAR]

    def load(self):
        """Load a program into memory."""

        address = 0x0
        if len(sys.argv) != 0x2:
            print("usage: ls8.py filename")
            sys.exit(0x1)

        try:
            with open(sys.argv[0x1]) as f:
                for line in f:
                    try:
                        line = line.split("#",0x1)[0x0]
                        line = int(line, 0x2)  # int() is base 10 by default
                        self.ram[address] = line
                        address += 0x1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[0x1]}")
            sys.exit(0x1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        #todo Add the ALU operations: AND OR XOR NOT SHL SHR MOD
        if op == "ADD":
            return self.reg[reg_a] + self.reg[reg_b]

        elif op == "SUB":
            return self.reg[reg_a] - self.reg[reg_b]

        elif op == "MUL":
            return self.reg[reg_a] * self.reg[reg_b]

        elif op == "DIV":
            return self.reg[reg_a] / self.reg[reg_b]

        elif op == "MOD":
            return self.reg[reg_a] % self.reg[reg_b]

        elif op == "AND":
            return self.reg[reg_a] & self.reg[reg_b]

        elif op == "OR":
            return self.reg[reg_a] | self.reg[reg_b]

        elif op == "XOR":
            return self.reg[reg_a] ^ self.reg[reg_b]

        elif op == "NOT":
            return ~self.reg[reg_a]

        elif op == "SHL":
            return self.reg[reg_a] << self.reg[reg_b]

        elif op == "SHR":
            return self.reg[reg_a] >> self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 0x1),
            self.ram_read(self.pc + 0x2)
        ), end='')

        for i in range(0x8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            IR = self.ram[self.pc]
            operand_a = self.ram[self.pc + 0x1]
            operand_b = self.ram[self.pc + 0x2]

            if IR == 0x0:  # NOP
                pass

            if IR == 0x1:  # HALT
                running = False

            elif IR == 0x11:  # RET
                # Get return address from the top of the stack
                address_to_pop_from = self.reg[self.SP]
                return_addr = self.ram[address_to_pop_from]
                self.reg[self.SP] += 1

                # Set the PC to the return address
                self.pc = return_addr
                print(f"0x11/17: {return_addr}\n")


            # elif IR == 0x13:  # IRET
            #     print(f"0x13/19: {IR}\n")

            #     # self.pc += 0x1

            elif IR == 0x45:  # Push
                # Decrement stack pointer           
                self.reg[self.SP] -= 1

                self.reg[self.SP] &= 0xff  # keep R7 in the range 00-FF

                # get register value
                value = self.reg[operand_a]

                # Store in memory
                address_to_push_to = self.reg[self.SP]
                self.ram[address_to_push_to] = value

                print(f"0x45/69: {value}\n")

                self.pc += 0x2

            elif IR == 0x46:  # Pop
                # Get value from RAM
                address_to_pop_from = self.reg[self.SP]
                value = self.ram[address_to_pop_from]

                # Store in the given register
                self.reg[operand_a] = value

                print(f"0x46/70: {value}\n")

                # Increment SP
                self.reg[self.SP] += 1

                self.pc += 0x2

            elif IR == 0x47:  # PRN Register pseudo-instruction
                print(f"0x47/71: {self.reg[operand_a]}\n")

                self.pc += 0x2

            # elif IR == 0x48:  # PRA
            #     print(f"0x48/72: {operand_a}\n")

            #     self.pc += 0x2

            elif IR == 0x50:  #Call
                # Get address of the next instruction
                # return_addr = self.pc + 0x2
                return_addr = operand_b

                # Push that on the stack
                self.reg[self.SP] -= 1
                address_to_push_to = self.reg[self.SP]
                self.ram[address_to_push_to] = return_addr

                # Set the PC to the subroutine address
                subroutine_addr = self.reg[operand_a]

                self.pc = subroutine_addr
                print(f"0x50/80: {subroutine_addr}\n")


            elif IR == 0x54:  #JMP
                addr = self.reg[operand_a]

                self.pc = addr
                print(f"0x54/84: {addr}\n")

            elif IR == 0x55:  #JEQ
                if self.fl == 0x1:
                    addr = self.reg[operand_a]
                    self.pc = addr
                    print(f"0x55/85: {addr}\n")
                else:
                    print(f"0x55/85: No go\n")
                    self.pc += 0x2

            elif IR == 0x56:  #JNE
                if self.fl is not 0b1 or self.fl is not 0b11 or self.fl is not 0b111:
                    addr = self.reg[operand_a]
                    self.pc = addr
                    print(f"0x56/86: {addr}\n")
                else:
                    print(f"0x56/86: No go\n")
                    self.pc += 0x2

            elif IR == 0x82:  # LDI Load Immediate
                self.reg[operand_a] = operand_b
                print(f"0x82/130: {self.reg[operand_a]}\n")

                self.pc += 0x3

            # elif IR == 0x83:  # LD
            #     print(f"0x83/131: {operand_b}\n")

            #     self.pc += 0x3

            # elif IR == 0x84:  # ST
            #     print(f"0x84/132: {operand_b}\n")

            #     self.pc += 0x3

            #todo Add the ALU operations: AND OR XOR NOT SHL SHR MOD
            elif IR == 0xA0:  #ADD A and B
                operand_c = self.alu("ADD",operand_a, operand_b)
                print(f"0xA0/160: {operand_c}\n")

                self.pc += 0x3
            
            elif IR == 0xA1:  #SUB A and B
                operand_c = self.alu("SUB",operand_a, operand_b)
                print(f"0xA1/161: {operand_c}\n")

                self.pc += 0x3

            elif IR == 0xA2:  #MUL Multiply A and B
                operand_c = self.alu("MUL",operand_a, operand_b)
                print(f"0xA2/162: {operand_c}\n")

                self.pc += 0x3

            elif IR == 0xA3:  #DIV A and B
                operand_c = self.alu("DIV",operand_a, operand_b)
                print(f"0xA3/163: {operand_c}\n")

                self.pc += 0x3

            elif IR == 0xA4:  #MOD A and B
                operand_c = self.alu("MOD",operand_a, operand_b)
                print(f"0xA4/164: {operand_c}\n")

                self.pc += 0x3

            elif IR == 0xA7:  # CMP
                if operand_a == operand_b:
                    self.fl = 0x01 # E in LGE flag
                elif operand_a < operand_b:
                    self.fl = 0x04 # L in LGE flag
                elif operand_a > operand_b:
                    self.fl = 0x02 # G in LGE flag
                
                print(f"0xA7/167: {self.fl}\n")

                self.pc += 0x3

            else:
                 print(f"Unknown instruction...\nInt:{IR}/ Bin:{bin(IR)}/ Hex: {hex(IR)}")
                 running = False