"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.fl = 0
        self.sp = 7

    def load(self):
        """Load a program into memory."""

        address = 0

        with open(sys.argv[1]) as f: #python ls8.py examples/py print8.ls8
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == '':
                    continue
                v = int(string_val, 2)
                #print(v)
                self.ram[address] = v
                address += 1
        

        # For now, we've just hardcoded a program: 

        # program = [
        #     # From print8.ls8
        #     0b10000010, #(this is the opcode,the machine code value of the instruction,stored in RAM) # LDI R0,8)
        #     0b00000000, #(operand for R0)
        #     0b00001000, #(operand for the value 8 )
        #     0b01000111, # PRN R0 (psuedo instruction that prints the numeric value stored in a register)
        #     0b00000000,
        #     0b00000001, # HLT (halt the CPU and exit the emulator)
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        
        
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = self.fl | 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = self.fl | 2
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = self.fl | 4


        else:
            raise Exception("Unsupported ALU operation")
    
    def ram_read(self, mar):
        return self.ram[mar]
    
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

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
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        HLT = 0b00000001
        LDI = 0b10000010# (load immediate) takes a constant value and stores it in a register
        PRN = 0b01000111
        ADD = 0b10100000
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110


         
        running = True
         

        while running:
        #read the bytes at PC, PC+1 and PC+2 from RAM and store into variables
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == PRN:
                print(self.reg[operand_a])
                #it's a 2 byte instruction so add 2 to the pc
                self.pc += 2
                
            elif ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            
            elif ir == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3

            elif ir == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            
            elif ir == HLT:
                running = False
                sys.exit()
            

            elif ir == PUSH:
                #decrement the stack pointer (SP)
                self.reg[self.sp] -= 1
                
                #get the value out of the register
                val = self.reg[operand_a]
            
                #store value in memory at SP
                self.ram[self.reg[self.sp]] = val
                
                #it's a 2 byte instruction so add 2 to the pc
                self.pc += 2
                
                 
            elif ir == POP:
                top_stack = operand_a
                val = self.ram[self.reg[self.sp]]
                self.reg[top_stack] = val
                self.reg[self.sp] += 1
                #this is a 2 byte instruction
                self.pc += 2
                

               
            elif ir == CALL:
                #decrement
                self.reg[self.sp] -=1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[operand_a]
                
                # top_of_stack_add = registers[self.sp]
                # self.ram[top_of_stack_add] = return_add   
                # #Set the PC to the subroutine add
                # reg_num = self.ram[pc + 1]
                # subroutine_add = self.reg[reg_num]  
                # pc = subroutine_add

            
            elif ir == RET:
                val = self.ram[self.reg[self.sp]]
                self.pc = val
                self.reg[self.sp] += 1
                # top_of_stack_add = registers[self.pc]
                # return_add = self.ram[top_of_stack_add]
                # registers[self.sp] += 1

                # #store it in the PC
                # self.pc = return_add

            elif ir == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
            
            elif ir == JMP:
                #decrement
                self.reg[self.sp] -=1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[operand_a]

            
            elif ir == JEQ:
                if self.fl == 1 or self.fl == 3 or self.fl == 5 or self.fl == 7:
                    self.reg[self.sp] -=1
                    self.ram[self.reg[self.sp]] = self.pc + 2
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            
            elif ir == JNE:
                if self.fl == 0 or self.fl == 2 or self.fl == 3 or self.fl == 4:
                    self.reg[self.sp] -= 1
                    self.ram[self.reg[self.sp]] = self.pc + 2
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2