### Simulador Ahmes
Este projeto consiste em um simulador de arquitetura de CPU de 8 bits desenvolvido em Python. O objetivo é emular o ciclo de vida da instrução (Fetch-Decode-Execute), o gerenciamento de registradores e a manipulação de flags de estado (N, Z, V, C, B) de um processador hipotético denominado Ahmes.

O simulador utiliza um formato de instrução compacto e estendido, permitindo a execução de programas escritos em um formato de código de máquina simples (decimal) carregado de um arquivo de texto (mem.txt).

---
### Alunos
- Vinícius dos Santos Tacaná
- Matheus Leonardo
- Lucas Nunes

---
Características Principais

1. Arquitetura de Memória e Registradores

    Memória (mem): 256 bytes (0 a 255) simulados por uma lista Python.

    Registradores Principais:

        ac (Accumulator): Registrador de 8 bits (0-255) onde as operações aritméticas e lógicas são realizadas.

        pc (Program Counter): Aponta para o endereço da próxima instrução a ser executada.

    Flags de Estado (N, Z, V, C, B): Usadas para controlar desvios condicionais e indicar o resultado de operações (ex: negativo, zero, carry, overflow, borrow).

---

### Como usar
O simulador requer apenas dois arquivos no mesmo diretório:

1. ahmes_compacto.py

- Contém toda a lógica da CPU, incluindo o loader de memória, o decoder de instruções e o loop de execução.

2. mem.txt (O Programa)
- Este arquivo define o conteúdo da memória, linha por linha, em formato decimal.

Linha,Decimal,Hex (Opcode),Instrução,Explicação
0,20,0x14,LDA 4,Carrega o valor 10 (do Endereço 4) no AC.
1,69,0x45,SUB 5,Subtrai o valor 4 (do Endereço 5) do AC.
2,38,0x26,STA 6,Armazena o resultado (6) no Endereço 6.
3,240,0xF0,HLT,Encerra a execução.
4,10,0x0A,Dado,Valor 10 (Minuendo).
5,4,0x04,Dado,Valor 4 (Subtraendo).
6,0,0x00,Resultado,Posição de destino.