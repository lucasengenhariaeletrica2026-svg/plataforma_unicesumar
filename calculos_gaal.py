import math

def processar_vetores_3d(x1, y1, z1, x2, y2, z2):
    """
    Realiza os principais cálculos analíticos entre dois vetores u e v no espaço R3.
    Retorna um dicionário com os resultados e strings explicativas.
    """
    # Vetores representados como tuplas
    u = (x1, y1, z1)
    v = (x2, y2, z2)
    
    # 1. Soma de Vetores: u + v = (u1+v1, u2+v2, u3+v3)
    soma = (u[0] + v[0], u[1] + v[1], u[2] + v[2])
    
    # 2. Subtração de Vetores: u - v = (u1-v1, u2-v2, u3-v3)
    subtracao = (u[0] - v[0], u[1] - v[1], u[2] - v[2])
    
    # 3. Produto Escalar (Scalar Product): u . v = u1*v1 + u2*v2 + u3*v3
    prod_escalar = (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])
    
    # 4. Magnitudes (Módulos / Normas)
    norma_u = math.sqrt(u[0]**2 + u[1]**2 + u[2]**2)
    norma_v = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    
    # 5. Ângulo entre os vetores (usando a fórmula do cosseno)
    if norma_u > 0 and norma_v > 0:
        cosseno_teta = prod_escalar / (norma_u * norma_v)
        # Força o cosseno a ficar no intervalo [-1, 1] para evitar erros numéricos
        cosseno_teta = max(-1.0, min(1.0, cosseno_teta))
        angulo_radianos = math.acos(cosseno_teta)
        angulo_graus = math.degrees(angulo_radianos)
    else:
        angulo_graus = 0.0
        
    return {
        "vetor_u": u,
        "vetor_v": v,
        "soma": soma,
        "subtracao": subtracao,
        "produto_escalar": prod_escalar,
        "norma_u": round(norma_u, 4),
        "norma_v": round(norma_v, 4),
        "angulo_graus": round(angulo_graus, 2)
    }
