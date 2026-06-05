def ler_matriz(n):
    matriz = []

    for i in range(n):
        linha = []
        for j in range(n):
            valor = float(input(f"A[{i+1}][{j+1}]: "))
            linha.append(valor)
        matriz.append(linha)

    return matriz


def ler_vetor(n):
    vetor = []

    for i in range(n):
        valor = float(input(f"b[{i+1}]: "))
        vetor.append(valor)

    return vetor


def decomposicao_lu(A, proximidade):
    n = len(A)

    L = [[0.0 for _ in range(n)] for _ in range(n)]
    U = [[0.0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        L[i][i] = 1.0

    for k in range(n):
        for j in range(k, n):
            soma = 0
            for s in range(k):
                soma += L[k][s] * U[s][j]

            U[k][j] = A[k][j] - soma

        if abs(U[k][k]) <= proximidade:
            print("Erro: pivô muito próximo de zero.")
            return None, None

        for i in range(k + 1, n):
            soma = 0
            for s in range(k):
                soma += L[i][s] * U[s][k]

            L[i][k] = (A[i][k] - soma) / U[k][k]

    return L, U


def resolver_y(L, b):
    n = len(L)
    y = [0.0 for _ in range(n)]

    for i in range(n):
        soma = 0
        for j in range(i):
            soma += L[i][j] * y[j]

        y[i] = b[i] - soma

    return y


def resolver_x(U, y, proximidade):
    n = len(U)
    x = [0.0 for _ in range(n)]

    for i in range(n - 1, -1, -1):
        soma = 0
        for j in range(i + 1, n):
            soma += U[i][j] * x[j]

        if abs(U[i][i]) <= proximidade:
            print("Erro: divisão por valor muito próximo de zero.")
            return None

        x[i] = (y[i] - soma) / U[i][i]

    return x


n = int(input("Digite a ordem da matriz: "))
proximidade = float(input("Digite a proximidade/tolerância: "))

print("\nDigite os valores da matriz A:")
A = ler_matriz(n)

print("\nDigite os valores do vetor b:")
b = ler_vetor(n)

L, U = decomposicao_lu(A, proximidade)

if L is not None:
    y = resolver_y(L, b)
    x = resolver_x(U, y, proximidade)

    print("\nMatriz L:")
    for linha in L:
        print(linha)

    print("\nMatriz U:")
    for linha in U:
        print(linha)

    print("\nSolução do sistema:")
    for i, valor in enumerate(x):
        print(f"x{i+1} = {valor}")