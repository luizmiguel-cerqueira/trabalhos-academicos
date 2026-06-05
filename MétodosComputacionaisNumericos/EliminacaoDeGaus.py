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


def eliminacao_gauss(A, b, proximidade):
    n = len(A)

    # Monta a matriz aumentada [A | b]
    matriz = []
    for i in range(n):
        matriz.append(A[i] + [b[i]])

    # Etapa de eliminação
    for k in range(n - 1):

        # Pivoteamento parcial
        maior_linha = k
        for i in range(k + 1, n):
            if abs(matriz[i][k]) > abs(matriz[maior_linha][k]):
                maior_linha = i

        if maior_linha != k:
            matriz[k], matriz[maior_linha] = matriz[maior_linha], matriz[k]

        if abs(matriz[k][k]) <= proximidade:
            print("Erro: pivô muito próximo de zero.")
            return None

        for i in range(k + 1, n):
            fator = matriz[i][k] / matriz[k][k]

            for j in range(k, n + 1):
                matriz[i][j] = matriz[i][j] - fator * matriz[k][j]

    # Verifica o último pivô
    if abs(matriz[n - 1][n - 1]) <= proximidade:
        print("Erro: sistema sem solução única.")
        return None

    # Retrosubstituição
    x = [0.0 for _ in range(n)]

    for i in range(n - 1, -1, -1):
        soma = 0

        for j in range(i + 1, n):
            soma += matriz[i][j] * x[j]

        x[i] = (matriz[i][n] - soma) / matriz[i][i]

    return x


n = int(input("Digite a ordem da matriz: "))
proximidade = float(input("Digite a proximidade/tolerância: "))

print("\nDigite os valores da matriz A:")
A = ler_matriz(n)

print("\nDigite os valores do vetor b:")
b = ler_vetor(n)

resultado = eliminacao_gauss(A, b, proximidade)

if resultado is not None:
    print("\nSolução do sistema:")

    for i, valor in enumerate(resultado):
        print(f"x{i+1} = {valor}")