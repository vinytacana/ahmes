# ahmes_compacto.py
# Simulador Ahmes - Formato compacto estendido (corrigido)
# - Instruções básicas (LDA, STA, ADD, SUB, AND, OR, NOT, NOP) = 1 byte (opcode_hi + operand_lo)
# - Desvios (JMP, JN, JP, ...) = 2 bytes: [opcode_byte] [address (0..255)]
# - EXT_JMP (opcode 0xB) = 3 bytes: [0xB] [subcode] [address] -> subcodes: JV,JNV,JZ,JNZ,JC,JNC,JB,JNB
# - Shifts/Rotates: opcode 0xE (1 byte) com operand_lo definindo qual operação (00=SHR,01=SHL,10=ROR,11=ROL)
#
# mem.txt: decimal, 1 linha por byte. Linhas vazias e comentários com '#' são ignorados.
# Example jump: JMP 200 -> mem contains 128 then 200  (128 decimal == 0x80)

MAX_MEM = 256

# -------------------------
# Opcodes (4-bit)
# -------------------------
NOP_OP = 0x0
LDA_OP = 0x1
STA_OP = 0x2
ADD_OP = 0x3
SUB_OP = 0x4
OR_OP  = 0x5
AND_OP = 0x6
NOT_OP = 0x7

JMP_OP = 0x8   # 2 bytes: [opcode_byte] [addr_byte]
JN_OP  = 0x9   # 2 bytes: jump if negative
JP_OP  = 0xA   # 2 bytes: jump if positive
EXT_JMP_OP = 0xB  # 3 bytes: [0xB?] [subcode] [addr]
# 0xC reserved
JZ_OP  = 0xD   # 2 bytes (jump if zero) - convenience
SHF_OP = 0xE   # 1 byte, operand low 2 bits choose SHR/SHL/ROR/ROL
HLT_OP = 0xF

# EXT_JMP subcodes mapping (for second byte of EXT_JMP)
EXT_JV  = 0  # JV  - jump if V==1
EXT_JNV = 1  # JNV - jump if V==0
EXT_JZ  = 2  # JZ  - jump if Z==1
EXT_JNZ = 3  # JNZ - jump if Z==0
EXT_JC  = 4  # JC  - jump if C==1
EXT_JNC = 5  # JNC - jump if C==0
EXT_JB  = 6  # JB  - jump if B==1 (borrow)
EXT_JNB = 7  # JNB - jump if B==0

# -------------------------
# Registers / memory / flags
# -------------------------
mem = [0] * MAX_MEM
pc = 0
ac = 0

N = False  # negative (sign)
Z = False  # zero
V = False  # overflow
C = False  # carry
B = False  # borrow (from SUB)

# -------------------------
# Helpers
# -------------------------
def dump_state():
    print(f"PC={pc:03d} | AC={ac:4d} | N={int(N)} Z={int(Z)} V={int(V)} C={int(C)} B={int(B)}")

def update_flags(res):
    """
    Atualiza flags baseado no resultado 'res' (inteiro possivelmente fora do intervalo 0..255).
    Consideramos AC como 8-bit (0..255) para N/Z e C; V é uma aproximação de overflow de signed 8-bit.
    """
    global N, Z, V, C
    # res pode ser negativo; para N e Z consideramos a máscara 8-bit
    masked = res & 0xFF
    N = (masked & 0x80) != 0
    Z = masked == 0
    # Overflow: se res fora do intervalo -128..127
    V = (res > 127) or (res < -128)
    # Carry: se bit 8 (valor > 0xFF) estiver setado
    C = (res & 0x100) != 0

def load_memory(filename="mem.txt"):
    """Carrega mem a partir de arquivo decimal. Ignora linhas vazias e comentários (#)."""
    global mem
    try:
        with open(filename, "r") as f:
            lines = [ln.split('#',1)[0].strip() for ln in f.readlines()]
        values = []
        for ln in lines:
            if ln == "":
                continue
            try:
                val = int(ln, 10)
            except ValueError:
                print(f"Aviso: linha ignorada no mem.txt (não é decimal): '{ln}'")
                continue
            values.append(val & 0xFF)
        # carrega até MAX_MEM
        for i, v in enumerate(values[:MAX_MEM]):
            mem[i] = v
        print(f"Memória carregada com {len(values[:MAX_MEM])} posições.")
    except FileNotFoundError:
        print("Arquivo mem.txt não encontrado. Memória zerada.")

# -------------------------
# Shift / rotate ops
# -------------------------
def SHR():
    global ac, C
    old = ac & 0xFF
    C = (old & 0x01) != 0
    ac = (old >> 1) & 0xFF
    update_flags(ac)

def SHL():
    global ac, C
    old = ac & 0xFF
    C = (old & 0x80) != 0
    ac = ((old << 1) & 0xFF)
    update_flags(ac)

def ROR():
    global ac, C
    old = ac & 0xFF
    old_bit0 = old & 0x01
    new_ac = (old >> 1) | ((1 if C else 0) << 7)
    C = old_bit0 != 0
    ac = new_ac & 0xFF
    update_flags(ac)

def ROL():
    global ac, C
    old = ac & 0xFF
    old_bit7 = (old & 0x80) >> 7
    new_ac = ((old << 1) & 0xFF) | (1 if C else 0)
    C = old_bit7 != 0
    ac = new_ac & 0xFF
    update_flags(ac)

# -------------------------
# Execute one instruction
# -------------------------
def exec_instruction():
    """
    Executa a instrução em PC.
    Retorna True para HALT, False caso contrário.
    Atualiza PC dentro da função conforme o tamanho da instrução.
    """
    global pc, ac, mem, N, Z, V, C, B

    if pc < 0 or pc >= MAX_MEM:
        print(f"Erro: PC fora de faixa: {pc}")
        return True

    instr = mem[pc] & 0xFF
    opcode = (instr >> 4) & 0x0F
    operand_nibble = instr & 0x0F

    # 1-byte simples
    if opcode == NOP_OP:
        pc += 1
        return False

    if opcode == LDA_OP:
        # endereço 0..15 (nibble)
        addr = operand_nibble
        ac = mem[addr] & 0xFF
        update_flags(ac)
        pc += 1
        return False

    if opcode == STA_OP:
        addr = operand_nibble
        mem[addr] = ac & 0xFF
        pc += 1
        return False

    if opcode == ADD_OP:
        addr = operand_nibble
        res = (ac & 0xFF) + (mem[addr] & 0xFF)
        ac = res & 0xFF
        update_flags(res)
        pc += 1
        return False

    if opcode == SUB_OP:
        addr = operand_nibble
        res = (ac & 0xFF) - (mem[addr] & 0xFF)
        ac = res & 0xFF
        update_flags(res)
        B = (res < 0)
        pc += 1
        return False

    if opcode == OR_OP:
        addr = operand_nibble
        ac = (ac | mem[addr]) & 0xFF
        update_flags(ac)
        pc += 1
        return False

    if opcode == AND_OP:
        addr = operand_nibble
        ac = (ac & mem[addr]) & 0xFF
        update_flags(ac)
        pc += 1
        return False

    if opcode == NOT_OP:
        ac = (~ac) & 0xFF
        update_flags(ac)
        pc += 1
        return False

    if opcode == SHF_OP:
        sub = operand_nibble & 0x03
        if sub == 0:
            SHR()
        elif sub == 1:
            SHL()
        elif sub == 2:
            ROR()
        elif sub == 3:
            ROL()
        pc += 1
        return False

    if opcode == HLT_OP:
        pc += 1
        return True

    # Para instruções de salto precisamos de pelo menos mais um byte
    if pc + 1 >= MAX_MEM:
        print(f"Erro: instrução de salto em PC={pc} sem byte de endereço disponível.")
        return True

    addr = mem[pc + 1] & 0xFF  # endereço completo 0..255 (próximo byte)

    # JMP (incondicional) - 2 bytes
    if opcode == JMP_OP:
        pc = addr
        return False

    # JN (2 bytes) - jump if negative (N == 1)
    if opcode == JN_OP:
        if N:
            pc = addr
        else:
            pc += 2
        return False

    # JP (2 bytes) - jump if positive (definido como not negative and not zero)
    if opcode == JP_OP:
        if (not N) and (not Z):
            pc = addr
        else:
            pc += 2
        return False

    # JZ alias (2 bytes)
    if opcode == JZ_OP:
        if Z:
            pc = addr
        else:
            pc += 2
        return False

    # EXT_JMP (3 bytes): [0xB] [subcode] [addr]
    if opcode == EXT_JMP_OP:
        if pc + 2 >= MAX_MEM:
            print(f"Erro: EXT_JMP em PC={pc} sem bytes suficientes.")
            return True
        subcode = mem[pc + 1] & 0xFF
        target = mem[pc + 2] & 0xFF

        if subcode == EXT_JV:
            if V:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JNV:
            if not V:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JZ:
            if Z:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JNZ:
            if not Z:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JC:
            if C:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JNC:
            if not C:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JB:
            if B:
                pc = target
            else:
                pc += 3
            return False
        if subcode == EXT_JNB:
            if not B:
                pc = target
            else:
                pc += 3
            return False

        # unknown subcode: skip the 3 bytes
        pc += 3
        return False

    # opcode desconhecido/reservado para salto (quando chegou aqui)
    print(f"Erro: opcode de salto desconhecido {opcode:02X} em PC={pc}")
    return True

# -------------------------
# Run loop
# -------------------------
def execute():
    global pc, ac
    halted = False
    visited = set()

    print("=== Iniciando execução do programa ===")
    dump_state()

    # Limite de instruções executadas para evitar logs infinitos (proteção extra)
    instr_count = 0
    MAX_INSTR = 200000  # suficientemente grande

    while not halted and 0 <= pc < MAX_MEM:
        if pc in visited:
            print(f"\n⚠️ loop detectado em PC={pc:03d}. Encerrando execução para evitar travamento.")
            break
        visited.add(pc)

        instr_preview = mem[pc] & 0xFF
        opcode = (instr_preview >> 4) & 0x0F
        operand = instr_preview & 0x0F
        print(f"\nPC={pc:03d} | Instrução = {instr_preview:02X} (opcode={opcode:X}, operando={operand})")
        dump_state()

        halted = exec_instruction()

        instr_count += 1
        if instr_count >= MAX_INSTR:
            print("\n⚠️ limite de instruções atingido. Encerrando execução.")
            break

    print("\n=== Execução finalizada ===")
    dump_state()

    # Mostrar resultado de teste (endereço 3 é onde costumamos armazenar o resultado nos exemplos)
    print("\nResultado armazenado no endereço 6:", mem[6])
    print("Memória final (primeiros 32 bytes):")
    print(mem[:32])

# -------------------------
# Entry
# -------------------------
if __name__ == "__main__":
    load_memory("mem.txt")
    execute()
