import pulp
import tempfile

def resolver_distribuicao():
    try:
        # Ler os parâmetros iniciais do usuário
        n, m, t = map(int, input().strip().split())

        # Verificar se os valores são válidos
        if n <= 0 or m <= 0 or t <= 0:
            return -1


        # Ler os dados das fábricas
        fabricas = []
        for _ in range(n):
            fi, pj, fmax = map(int, input().strip().split())
            fabricas.append((fi, pj, fmax))

        # Ler os dados dos países
        paises = []
        for _ in range(m):
            pj, pmaxj, pminj = map(int, input().strip().split())
            paises.append((pj, pmaxj, pminj))

        # Ler os pedidos das crianças
        pedidos = []
        for _ in range(t):
            dados = list(map(int, input().strip().split()))
            ck, pj, *fabricas_ck = dados
            print(fabricas_ck)
            pedidos.append((ck, pj, fabricas_ck))

    

        # Variaveis sao do tipo:
        # fabricas = numero_fabrica, numero_pais, stock_maximo
        # paises = numero_pais, lim max export, lim min export
        # pedidos = numero_pedido, numero_pais, fabricas_possiveis

        # Create the optimization problem
        # Verificado [X]
        problema = pulp.LpProblem("Distribuicao_de_Brinquedos", pulp.LpMaximize)
        
        # Decision variables: x[k, f] indicates if request k is fulfilled by factory f (1) or not (0)
        # x é um dicionário onde a chave é uma tupla (k, f) e o valor é uma variável binária
        x = {(k, f): pulp.LpVariable(f"x_{k}_{f}", cat="Binary") for k, _, fabricas_ck in pedidos for f in fabricas_ck}

        # Objective function: maximize the number of requests fulfilled
        problema += pulp.lpSum(x[k, f] for k, _, fabricas_ck in pedidos for f in fabricas_ck), "Maximizar_pedidos_atendidos"

        # Factory capacity constraints
        for fi, pi, fmax in fabricas:
            problema += (
                pulp.lpSum(
                    x[k, f] 
                    for k, _, fabricas_ck in pedidos 
                    for f in fabricas_ck if f == fi
                ) <= fmax,
                f"Capacidade_fabrica_{fi}"
            )

        # Export and import constraints per country
        for pj, pmaxj, pminj in paises:
            # Maximum export constraint (excluding intra-country distribution)
            problema += (
                pulp.lpSum(
                    x[k, f] 
                    for k, pais, fabricas_ck in pedidos 
                    for f in fabricas_ck 
                    if pais == pj and any(fi == f and pais_fabrica != pj for fi, pais_fabrica, _ in fabricas)
                ) <= pmaxj,
                f"Exportacao_maxima_{pj}"
            )
            # Minimum import constraint
            problema += (
                pulp.lpSum(
                    x[k, f] 
                    for k, pais, fabricas_ck in pedidos 
                    for f in fabricas_ck if pais == pj
                ) >= pminj,
                f"Exportacao_minima_{pj}"
            )

        # Each request can only be fulfilled by one factory
        for k, _, fabricas_ck in pedidos:
            problema += (
                pulp.lpSum(x[k, f] for f in fabricas_ck) <= 1,
                f"Pedido_{k}_unico"
            )

        
        # Resolver o problema
        try:
            status = problema.solve(pulp.PULP_CBC_CMD(msg=False))
        except Exception as e:
            print(f"Erro durante a resolução do problema: {e}")
            

        # Verificar o status do solver
        if pulp.LpStatus[status] not in ["Optimal", "Feasible"]:
            print("return not feasible")
            print({"status": "optimal", "fulfilled_requests": resultado})
            return -1

        # Calcular o número de pedidos atendidos
        try:
            resultado = sum(
                1 for k, _, fabricas_ck in pedidos
                if any(pulp.value(x[k, f]) == 1 for f in fabricas_ck)
            )
        except Exception as e:
            print(f"Erro ao calcular o resultado: {e}")
            print(3)
            return -1

        # Garantir que todos os pedidos foram atendidos, se necessário
        

        return resultado

    except Exception as e:
        print(f"Erro geral na função: {e}")
        return -1


# Solve the problem and suppress CBC solver output


# Exemplo de uso:
print(resolver_distribuicao())
