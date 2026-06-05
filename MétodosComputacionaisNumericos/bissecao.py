def funcao_tema_4(x):
    # Altere aqui a regra do Tema 4
    # Exemplo: encontrar x onde x² seja próximo de 25
    return x ** 2


def algoritmo_aproximacao(valor_esperado, chute_inicial, passo, max_iteracoes, proximidade):
    x = chute_inicial

    for i in range(max_iteracoes):
        resultado = funcao_tema_4(x)
        diferenca = abs(valor_esperado - resultado)

        print(f"Iteração {i + 1}: x={x}, resultado={resultado}, diferença={diferenca}")

        if diferenca <= proximidade:
            return x, resultado, i + 1

        if resultado < valor_esperado:
            x += passo
        else:
            x -= passo

        passo = passo / 2  # deixa o algoritmo mais preciso aos poucos

    return x, funcao_tema_4(x), max_iteracoes


valor_esperado = float(input("Digite o valor esperado: "))
chute_inicial = float(input("Digite o chute inicial: "))
passo = float(input("Digite o passo inicial: "))
max_iteracoes = int(input("Digite o máximo de interações: "))
proximidade = float(input("Digite a proximidade aceita: "))

x, resultado, iteracoes = algoritmo_aproximacao(
    valor_esperado,
    chute_inicial,
    passo,
    max_iteracoes,
    proximidade
)

print("\nResposta encontrada:")
print(f"x = {x}")
print(f"resultado = {resultado}")
print(f"iterações usadas = {iteracoes}")