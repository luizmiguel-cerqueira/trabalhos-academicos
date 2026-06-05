def ler_pontos():
    pontos = []

    quantidade = int(input("Digite a quantidade de pontos: "))

    for i in range(quantidade):
        x = float(input(f"Digite x{i}: "))
        y = float(input(f"Digite y{i}: "))
        pontos.append((x, y))

    return pontos


def validar_pontos(pontos, proximidade):
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            if abs(pontos[i][0] - pontos[j][0]) <= proximidade:
                print("Erro: existem valores de x repetidos ou muito próximos.")
                return False

    return True


def calcular_diferencas_divididas(pontos):
    n = len(pontos)

    tabela = [[0.0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        tabela[i][0] = pontos[i][1]

    for j in range(1, n):
        for i in range(n - j):
            xi = pontos[i][0]
            xj = pontos[i + j][0]

            tabela[i][j] = (tabela[i + 1][j - 1] - tabela[i][j - 1]) / (xj - xi)

    coeficientes = tabela[0]

    return coeficientes, tabela


def calcular_newton(pontos, coeficientes, valor_x):
    resultado = coeficientes[0]
    produto = 1.0

    for i in range(1, len(coeficientes)):
        produto *= valor_x - pontos[i - 1][0]
        resultado += coeficientes[i] * produto

    return resultado


pontos = ler_pontos()

proximidade = float(input("Digite a proximidade/tolerância: "))

if validar_pontos(pontos, proximidade):
    coeficientes, tabela = calcular_diferencas_divididas(pontos)

    valor_x = float(input("Digite o valor de x que deseja calcular: "))

    resultado = calcular_newton(pontos, coeficientes, valor_x)

    print("\nTabela de diferenças divididas:")
    for linha in tabela:
        print(linha)

    print("\nCoeficientes do polinômio:")
    for i, coef in enumerate(coeficientes):
        print(f"a{i} = {coef}")

    print("\nResultado:")
    print(f"P({valor_x}) = {resultado}")