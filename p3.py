import pulp
import tempfile

def resolver_distribuicao(input_file):
    try:
        # Ler os dados do arquivo de entrada
        with open(input_file, 'r') as f:
            linhas = f.readlines()

        # Verificar se há linhas suficientes no arquivo
        if not linhas or len(linhas) < 2:
            return -1

        # Processar os parâmetros iniciais
        try:
            n, m, t = map(int, linhas[0].strip().split())  # n = fábricas, m = países, t = pedidos
        except ValueError:
            return -1

        # Ler os dados das fábricas
        fabricas = []
        for i in range(1, n + 1):
            try:
                fi, pj, fmax = map(int, linhas[i].strip().split())
                fabricas.append((fi, pj, fmax))
            except ValueError:
                return -1

        # Ler os dados dos países
        paises = []
        for i in range(n + 1, n + 1 + m):
            try:
                pj, pmaxj, pminj = map(int, linhas[i].strip().split())
                paises.append((pj, pmaxj, pminj))
            except ValueError:
                return -1

        # Ler os pedidos das crianças
        pedidos = []
        for i in range(n + 1 + m, len(linhas)):
            try:
                dados = list(map(int, linhas[i].strip().split()))
                ck, pj, *fabricas_ck = dados
                pedidos.append((ck, pj, fabricas_ck))
            except ValueError:
                return -1

        # Criar o modelo de otimização
        problema = pulp.LpProblem("Distribuicao_de_Brinquedos", pulp.LpMaximize)

        # Variáveis de decisão: x[k, f] indica se o pedido k será atendido pela fábrica f (1) ou não (0)
        x = {(k, f): pulp.LpVariable(f"x_{k}_{f}", cat="Binary") for k, _, fabricas_ck in pedidos for f in fabricas_ck}

        # Função objetivo: maximizar o número de pedidos atendidos
        problema += pulp.lpSum(x[k, f] for k, _, fabricas_ck in pedidos for f in fabricas_ck), "Maximizar_pedidos_atendidos"

        # Restrições de capacidade das fábricas
        for fi, _, fmax in fabricas:
            problema += (
                pulp.lpSum(x[k, f] for k, _, fabricas_ck in pedidos for f in fabricas_ck if f == fi) <= fmax,
                f"Capacidade_fabrica_{fi}"
            )

        # Restrições de exportação e importação dos países
        for pj, pmaxj, pminj in paises:
            # Máximo de exportação
            problema += (
                pulp.lpSum(x[k, f] for k, pais, fabricas_ck in pedidos for f in fabricas_ck if pais == pj) <= pmaxj,
                f"Exportacao_maxima_{pj}"
            )
            # Mínimo de exportação
            problema += (
                pulp.lpSum(x[k, f] for k, pais, fabricas_ck in pedidos for f in fabricas_ck if pais == pj) >= pminj,
                f"Exportacao_minima_{pj}"
            )

        # Cada pedido só pode ser atendido por uma única fábrica
        for k, _, fabricas_ck in pedidos:
            problema += (
                pulp.lpSum(x[k, f] for f in fabricas_ck) <= 1,
                f"Pedido_{k}_unico"
            )

        # Resolver o problema
        try:
            status = problema.solve()
        except Exception as e:
            print(f"Erro durante a resolução do problema: {e}")
            return -1

        # Verificar o status do solver
        if pulp.LpStatus[status] not in ["Optimal", "Feasible"]:
            print(f"Status do solver: {pulp.LpStatus[status]}")
            return -1

        # Calcular o número de pedidos atendidos
        try:
            resultado = sum(
                1 for k, _, fabricas_ck in pedidos
                if any(pulp.value(x[k, f]) == 1 for f in fabricas_ck)
            )
        except Exception as e:
            print(f"Erro ao calcular o resultado: {e}")
            return -1

        # Garantir que todos os pedidos foram atendidos, se necessário
        if resultado < len(pedidos):
            return -1

        return resultado

    except Exception as e:
        print(f"Erro geral na função: {e}")
        return -1

if __name__ == "__main__":
    try:
        arquivo_entrada = "input.txt"  # Substitua pelo caminho do seu arquivo de entrada
        resultado = resolver_distribuicao(arquivo_entrada)
        print(resultado)
    except Exception as e:
        print(f"Erro no programa principal: {e}")

def testar_resolver_distribuicao(func):
    """Função para testar casos customizados."""
    casos_de_teste = [
        # Caso 1: Exemplo do enunciado, simples e funcional
        {
            "input": """3 2 3
1 1 1
2 1 1
3 2 1
1 2 1
2 2 1
1 1 2 3
2 1 2 1
3 2 1
""",
            "output": 3  # Esperado: Todos os pedidos podem ser atendidos
        },
        # Caso 2: Fábricas sem capacidade suficiente
        {
            "input": """2 1 3
1 1 1
2 1 1
1 2 1
1 2 1
2 1 2
""",
            "output": -1  # Esperado: Não é possível atender todos os pedidos
        },
        # Caso 3: Restrições mínimas de exportação não atendidas
        {
            "input": """3 1 3
1 1 2
2 1 2
3 1 2
1 3 3
""",
            "output": -1  # Esperado: Não há como cumprir pminj
        },
        # Caso 4: Apenas um pedido atendido
        {
            "input": """2 2 2
1 1 1
2 2 1
1 2 1
2 2 1
""",
            "output": 1  # Esperado: Apenas um pedido pode ser atendido
        },
        # Caso 5: Pedido impossível de ser atendido (nenhuma fábrica válida)
        {
            "input": """1 1 1
1 1 1
1 2 2
""",
            "output": -1  # Esperado: Pedido não pode ser atendido
        },
    ]

    # Loop pelos casos de teste
    for i, caso in enumerate(casos_de_teste, start=1):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(caso["input"])
            tmp.seek(0)
            resultado = func(tmp.name)

        esperado = caso["output"]
        print(f"Caso de Teste {i}:")
        print(f"Resultado Obtido: {resultado}")
        print(f"Resultado Esperado: {esperado}")
        print("Passou!\n" if resultado == esperado else "Falhou!\n")

# Exemplo de uso:
testar_resolver_distribuicao(resolver_distribuicao)
