def f(x):
    # Altere aqui a função do problema
    # Exemplo: x² - 25 = 0
    return x**2 - 25


def derivada_f(x):
    # Altere aqui a derivada da função
    # Derivada de x² - 25 é 2x
    return 2 * x


def metodo_newton(chute_inicial, max_iteracoes, proximidade):
    x = chute_inicial

    for i in range(max_iteracoes):
        fx = f(x)
        dfx = derivada_f(x)

        if dfx == 0:
            print("Erro: derivada igual a zero.")
            return None

        novo_x = x - fx / dfx
        diferenca = abs(novo_x - x)

        print(f"Iteração {i + 1}: x = {novo_x}, f(x) = {f(novo_x)}, diferença = {diferenca}")

        if diferenca <= proximidade or abs(f(novo_x)) <= proximidade:
            return novo_x

        x = novo_x

    return x


chute_inicial = float(input("Digite o chute inicial: "))
max_iteracoes = int(input("Digite o máximo de interações: "))
proximidade = float(input("Digite a proximidade desejada: "))

resposta = metodo_newton(chute_inicial, max_iteracoes, proximidade)

print("\nResposta aproximada:")
print(resposta)