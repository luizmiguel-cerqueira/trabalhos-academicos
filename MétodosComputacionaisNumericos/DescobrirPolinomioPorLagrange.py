def multiplicar_polinomio_por_binomio(polinomio, termo):
    # Multiplica o polinômio atual por (x - termo)
    novo = [0.0] * (len(polinomio) + 1)

    for i in range(len(polinomio)):
        novo[i] += -termo * polinomio[i]
        novo[i + 1] += polinomio[i]

    return novo


def somar_polinomios(p1, p2):
    tamanho = max(len(p1), len(p2))
    resultado = [0.0] * tamanho

    for i in range(tamanho):
        if i < len(p1):
            resultado[i] += p1[i]
        if i < len(p2):
            resultado[i] += p2[i]

    return resultado


def multiplicar_por_constante(polinomio, constante):
    return [coef * constante for coef in polinomio]


def lagrange_polinomio(pontos, proximidade):
    n = len(pontos)
    polinomio_final = [0.0]

    for i in range(n):
        xi, yi = pontos[i]

        numerador = [1.0]
        denominador = 1.0

        for j in range(n):
            if i != j:
                xj, _ = pontos[j]

                if abs(xi - xj) <= proximidade:
                    print("Erro: existem valores de x repetidos ou muito próximos.")
                    return None

                numerador = multiplicar_polinomio_por_binomio(numerador, xj)
                denominador *= xi - xj

        termo = multiplicar_por_constante(numerador, yi / denominador)
        polinomio_final = somar_polinomios(polinomio_final, termo)

    return polinomio_final


def formatar_polinomio(coeficientes, proximidade):
    partes = []

    for grau in range(len(coeficientes) - 1, -1, -1):
        coef = coeficientes[grau]

        if abs(coef) <= proximidade:
            continue

        if grau == 0:
            parte = f"{coef:.6g}"
        elif grau == 1:
            parte = f"{coef:.6g}x"
        else:
            parte = f"{coef:.6g}x^{grau}"

        partes.append(parte)

    if not partes:
        return "0"

    return " + ".join(partes).replace("+ -", "- ")


qtd = int(input("Digite a quantidade de pontos: "))
pontos = []

for i in range(qtd):
    x = float(input(f"Digite x{i}: "))
    y = float(input(f"Digite y{i}: "))
    pontos.append((x, y))

proximidade = float(input("Digite a proximidade/tolerância: "))

coeficientes = lagrange_polinomio(pontos, proximidade)

if coeficientes is not None:
    print("\nCoeficientes do polinômio:")
    for grau, coef in enumerate(coeficientes):
        print(f"x^{grau}: {coef}")

    print("\nPolinômio interpolador:")
    print("P(x) =", formatar_polinomio(coeficientes, proximidade))