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
                print("Erro: existem valores de x muito próximos ou repetidos.")
                return False

    return True


def interpolacao_lagrange(pontos, valor_x):
    resultado = 0

    for i in range(len(pontos)):
        xi, yi = pontos[i]
        termo = yi

        for j in range(len(pontos)):
            if i != j:
                xj, yj = pontos[j]
                termo *= (valor_x - xj) / (xi - xj)

        resultado += termo

    return resultado


pontos = ler_pontos()

proximidade = float(input("Digite a proximidade/tolerância: "))

if validar_pontos(pontos, proximidade):
    valor_x = float(input("Digite o valor de x que deseja calcular: "))

    resultado = interpolacao_lagrange(pontos, valor_x)

    print("\nResultado:")
    print(f"P({valor_x}) = {resultado}")