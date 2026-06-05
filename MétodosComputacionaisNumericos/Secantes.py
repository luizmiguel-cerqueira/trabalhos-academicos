def f(x):
    # Altere aqui a função do problema
    # Exemplo: x² - 25 = 0
    return x**2 - 25


def metodo_secantes(x0, x1, max_iteracoes, proximidade):
    for i in range(max_iteracoes):
        fx0 = f(x0)
        fx1 = f(x1)

        if fx1 - fx0 == 0:
            print("Erro: divisão por zero.")
            return None

        x2 = x1 - (fx1 * (x1 - x0)) / (fx1 - fx0)

        diferenca = abs(x2 - x1)

        print(f"Iteração {i + 1}: x = {x2}, f(x) = {f(x2)}, diferença = {diferenca}")

        if diferenca <= proximidade or abs(f(x2)) <= proximidade:
            return x2

        x0 = x1
        x1 = x2

    return x1


x0 = float(input("Digite o primeiro chute inicial x0: "))
x1 = float(input("Digite o segundo chute inicial x1: "))
max_iteracoes = int(input("Digite o máximo de interações: "))
proximidade = float(input("Digite a proximidade desejada: "))

resposta = metodo_secantes(x0, x1, max_iteracoes, proximidade)

print("\nResposta aproximada:")
print(resposta)