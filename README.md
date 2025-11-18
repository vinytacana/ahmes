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
