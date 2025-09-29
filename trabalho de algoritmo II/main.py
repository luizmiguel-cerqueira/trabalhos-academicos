#Elementos do grupo: Luiz Miguel Costa Cerqueira
class MercadoCesta:
    mercado: str = ""
    valor: list[float] = list()
    soma: float = 0

    def __init__(self, mercado="", valor=None, soma = None) -> None:
        self.mercado = mercado
        self.valor = valor if valor is not None else []
        self.soma = soma if soma is not None else 0

def main():
   tabela = tabelainicial()
   continua = True
   while continua :
    print("digite 1 para mostrar a tabela com valores(ja existem valores predefinidos)")
    print("digite 2 para adicionar um supermercado e itens na tabela")
    print("digite 3 ou qualquer outra coisa para sair")
    escolha = input("")
    if escolha == "1":
        mostrartabela(tabela)
    elif escolha == "2":
       tabela.append(adicionarmercados())
    else:
        continua = False

#não existe adicionar produtos por conta do tamanha da tela, iria quebrar a tabela se tivesse muitos produtos
def adicionarmercados()-> MercadoCesta:

    produtos = ["arroz", "feijão", "leite", "açúcar", "café"]
    mercado = input("Digite o nome do mercado: ")
    valores = []
    for produto in produtos:
        continua = True      #para entrar sempre no while
        while continua :     #loop para caso escreva valor não numerico repita a mesma pergunta
            continua = False #para que se ele acertar não entre no while denovo
            precostr = (input(f"digite o preço do {produto} (usando '.' como vírgula)"))
            try:
                precofloat = float(precostr)
                valores.append(precofloat)
            except ValueError:
                print("valor invalido, coloque um valor numero(utilizando'.' como vírgula)\n")
                continua = True

    print("\n")#para fazer quebra de linha
    return MercadoCesta(mercado, valores)

def tabelainicial() -> list[MercadoCesta]:
    # montagem de tabela
    tabela = [
        MercadoCesta("Guanabara", [6.00, 5.20, 8.10, 5.30, 72.00]),
        MercadoCesta("Carrefour", [6.40, 5.60, 8.50, 5.70, 75.00]),
        MercadoCesta("Assaí Atacadista", [6.20, 5.40, 8.20, 5.50, 73.00]),
        MercadoCesta("SuperMarket", [6.10, 5.30, 8.30, 5.40, 73.50])
        #menor = min(tabela, key=lambda x: x.soma)
    ]
    return tabela

def mostrartabela(tabela):
    # espaços antes de produto para centralizar
    print(f"                                 produtos[{len(tabela[0].valor)}]")
    print("-----------------------------------------------------------------------")
    print(f"supermercados[{len(tabela)}]     | arroz  | feijão| leite | açúcar|  café  | Soma")  # infelizmente não consegui deixar perfeito

    # loop para escrever cada linha da tabela
    for i in range(len(tabela)):
        #print("-----------------------------------------------------------------------")
        print(tabela[i].mercado.ljust(20, ' ')[0:20], "|", mostrarvalores(tabela, i, 0) + " " + somacesta(tabela, i))

    # traço em baixo + linha "Média"
    print("-----------------------------------------------------------------------")
    print("Média".ljust(20, ' ')[0:20] + " | " + mostrarmedia(tabela)+ "\n")
    # a string de espaços entre a "média" e a função a fim de ficar alinhado
    menor = min(tabela, key=lambda x: x.soma)
    print(f"O mercado com a menor cesta {menor.mercado} é com o valor de {menor.soma}\n")

# função de recursividade para montar os valores dos produtos
def mostrarvalores(tabela, i: int, j: int):
    if j > len(tabela[i].valor) - 1:
        return f""
    else:
        return f"  {tabela[i].valor[j]}  |" + mostrarvalores(tabela, i, j + 1)

    # forma de fazer sem recursividade

    # a = ""
    # for k in range(0,j):
    #    a += tabela[i].valor[k]

def mostrarmedia(tabela):
    s = ""#forçar os valores para string
    for i in range(0, len(tabela[0].valor)):
        s += somaitem(tabela, i)
    return s

# função para somar o total da "cesta básica"
def somacesta(tabela, i: int) -> str:
    soma = 0
    for j in range(0, len(tabela[0].valor)):
        soma += float(tabela[i].valor[j])
    tabela[i].soma = soma #<- pra facilitar na mensagem de qual o mercado mais barato
    return str(soma)

def somaitem(tabela, i: int) -> str:
    soma = 0
    for j in range(0, len(tabela[0].valor)-1):
        soma += float(tabela[j].valor[i])
    return media(soma, len(tabela))

def media(soma, i: int) -> str:
    return f" {soma /i:.3f} |"

if __name__ == "__main__":
    main()