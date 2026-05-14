"""
══════════════════════════════════════════════════════════════════
          ChargeGrid Intelligence — Simulador de Recarga
                         Sprint 1 — FIAP
══════════════════════════════════════════════════════════════════

Simula o ciclo completo de uma sessão de recarga comercial:
  • Início e fim de sessão
  • Controle básico de energia
  • Registro de dados da sessão
  • Aplicação de regras de cobrança dinâmica
"""

import time
import random
from datetime import datetime, timedelta


# ────────────────────────
#  CONSTANTES DE TARIFAÇÃO
# ────────────────────────
TARIFA_PADRAO_KWH   = 1.20   # R$/kWh — horário normal
TARIFA_PONTA_KWH    = 1.85   # R$/kWh — horário de pico (18h–21h)
TARIFA_OFF_PEAK_KWH = 0.90   # R$/kWh — madrugada (0h–6h)

DESCONTO_ASSINANTE  = 0.15   # 15% de desconto para assinantes
TAXA_SERVICO        = 2.50   # R$ taxa fixa de serviço por sessão

POTENCIA_MAX_KW     = 22.0   # kW — potência máxima do carregador (FIAP)
POTENCIA_MIN_KW     = 3.7    # kW — potência mínima válida

TIPOS_USUARIO = {
    "1": "Visitante",
    "2": "Assinante",
    "3": "Frota Corporativa",
}

TIPOS_VEICULO = {
    "1": {"nome": "Hatchback / Sedan",    "bateria_kwh": 40,  "potencia_max": 7.4},
    "2": {"nome": "SUV Elétrico",          "bateria_kwh": 77,  "potencia_max": 11.0},
    "3": {"nome": "Van / Utilitário",      "bateria_kwh": 90,  "potencia_max": 22.0},
    "4": {"nome": "Moto Elétrica",         "bateria_kwh": 5,   "potencia_max": 3.7},
}


# ───────────────────
#  FUNÇÕES AUXILIARES
# ───────────────────

def linha(char="─", largura=60):
    print(char * largura)


def cabecalho(titulo):
    linha("═")
    print(f"  {titulo}")
    linha("═")


def subcabecalho(titulo):
    linha("─")
    print(f"  {titulo}")
    linha("─")


def entrada_inteira(prompt, minimo, maximo):

    while True:
        try:
            valor = int(input(prompt))
            if minimo <= valor <= maximo:
                return valor
            print(f"Digite um número entre {minimo} e {maximo}.")
        except ValueError:
            print("Entrada inválida. Digite apenas números inteiros.")


def entrada_float(prompt, minimo, maximo):

    while True:
        try:
            valor = float(input(prompt))
            if minimo <= valor <= maximo:
                return valor
            print(f"Digite um valor entre {minimo:.1f} e {maximo:.1f}.")
        except ValueError:
            print("Entrada inválida. Use ponto como separador decimal.")


def escolher_opcao(prompt, opcoes: dict):

    for chave, descricao in opcoes.items():
        print(f"    [{chave}] {descricao}")
    while True:
        escolha = input(prompt).strip()
        if escolha in opcoes:
            return escolha
        print(f"Opção inválida. Escolha entre: {', '.join(opcoes.keys())}.")


def detectar_horario(hora: int):

    if 18 <= hora <= 20:
        return "ponta"
    elif 0 <= hora <= 5:
        return "off-peak"
    else:
        return "normal"


def calcular_tarifa(hora: int, tipo_usuario: str):

    periodo = detectar_horario(hora)

    if periodo == "ponta":
        tarifa = TARIFA_PONTA_KWH
    elif periodo == "off-peak":
        tarifa = TARIFA_OFF_PEAK_KWH
    else:
        tarifa = TARIFA_PADRAO_KWH


    if tipo_usuario == "Frota Corporativa":
        tarifa = min(tarifa, TARIFA_OFF_PEAK_KWH)

    return tarifa, periodo


def simular_recarga(potencia_kw: float, carga_inicial: float,
                    carga_alvo: float, capacidade_bateria: float):

    energia_necessaria = (carga_alvo - carga_inicial) / 100 * capacidade_bateria
    energia_carregada  = 0.0
    minuto             = 0
    registros          = []

    print()
    subcabecalho("Simulação em progresso...")
    print(f"  Energia a carregar: {energia_necessaria:.2f} kWh")
    print()

    while energia_carregada < energia_necessaria:
        # Potência varia +-5% por ciclo
        variacao       = random.uniform(-0.05, 0.05)
        potencia_atual = potencia_kw * (1 + variacao)
        potencia_atual = max(POTENCIA_MIN_KW, min(potencia_atual, POTENCIA_MAX_KW))

        energia_ciclo  = potencia_atual / 60
        restante       = energia_necessaria - energia_carregada
        energia_ciclo  = min(energia_ciclo, restante)

        energia_carregada += energia_ciclo
        soc_atual = carga_inicial + (energia_carregada / capacidade_bateria) * 100
        minuto   += 1

        registros.append({
            "minuto":       minuto,
            "potencia_kw":  round(potencia_atual, 2),
            "energia_kwh":  round(energia_ciclo, 4),
            "soc":          round(soc_atual, 1),
        })

        # Exibe progresso a cada 5 minutos
        if minuto % 5 == 0 or energia_carregada >= energia_necessaria:
            barra = int(soc_atual / 5)
            print(f"  t={minuto:>4}min │ {potencia_atual:>5.2f} kW │ "
                  f"SOC: {'█' * barra:<20} {soc_atual:>5.1f}%")

    return registros, energia_carregada


# ────────────────
#  FLUXO PRINCIPAL
# ────────────────

def coletar_dados_sessao():

    cabecalho("INÍCIO DE SESSÃO — ChargeGrid Intelligence")

    # Tipo de usuário
    print("\n  Tipo de usuário:")
    chave_usuario = escolher_opcao("\n  Escolha [1/2/3]: ", TIPOS_USUARIO)
    tipo_usuario  = TIPOS_USUARIO[chave_usuario]

    # Tipo de veículo
    print("\n  Tipo de veículo:")
    chave_veiculo = escolher_opcao("\n  Escolha [1/2/3/4]: ", {
        k: f"{v['nome']} (bateria: {v['bateria_kwh']} kWh)" for k, v in TIPOS_VEICULO.items()
    })
    veiculo = TIPOS_VEICULO[chave_veiculo]

    # Estado de carga atual e desejado
    print()
    carga_inicial = entrada_float(
        f"  Estado de carga atual (SOC) [%]  [0–99]: ", 0, 99
    )
    carga_alvo = entrada_float(
        f"  SOC desejado ao final       [%]  [{carga_inicial+1:.0f}–100]: ",
        carga_inicial + 1, 100
    )

    # Potência solicitada
    pot_max_veiculo = veiculo["potencia_max"]
    potencia_kw = entrada_float(
        f"  Potência de carga desejada  [kW] [{POTENCIA_MIN_KW}–{pot_max_veiculo}]: ",
        POTENCIA_MIN_KW, pot_max_veiculo
    )

    # Hora de início (para definir tarifa)
    hora_inicio = entrada_inteira(
        "  Hora de início da sessão    [h]  [0–23]: ", 0, 23
    )

    return {
        "tipo_usuario":   tipo_usuario,
        "veiculo":        veiculo,
        "carga_inicial":  carga_inicial,
        "carga_alvo":     carga_alvo,
        "potencia_kw":    potencia_kw,
        "hora_inicio":    hora_inicio,
    }


def processar_sessao(dados: dict):

    veiculo      = dados["veiculo"]
    tipo_usuario = dados["tipo_usuario"]
    hora_inicio  = dados["hora_inicio"]

    # Registros e energia total
    registros, energia_total = simular_recarga(
        potencia_kw       = dados["potencia_kw"],
        carga_inicial     = dados["carga_inicial"],
        carga_alvo        = dados["carga_alvo"],
        capacidade_bateria= veiculo["bateria_kwh"],
    )

    duracao_min = len(registros)

    # Timestamps simulados
    dt_inicio = datetime.now().replace(hour=hora_inicio, minute=0, second=0, microsecond=0)
    dt_fim    = dt_inicio + timedelta(minutes=duracao_min)

    # Tarifação
    tarifa_kwh, periodo = calcular_tarifa(hora_inicio, tipo_usuario)
    custo_energia       = energia_total * tarifa_kwh
    desconto            = custo_energia * DESCONTO_ASSINANTE if tipo_usuario == "Assinante" else 0.0
    total               = custo_energia - desconto + TAXA_SERVICO

    # Potência média dos registros
    potencia_media = sum(r["potencia_kw"] for r in registros) / len(registros)

    return {
        "registros":       registros,
        "energia_total":   round(energia_total, 3),
        "duracao_min":     duracao_min,
        "dt_inicio":       dt_inicio,
        "dt_fim":          dt_fim,
        "tarifa_kwh":      tarifa_kwh,
        "periodo":         periodo,
        "custo_energia":   round(custo_energia, 2),
        "desconto":        round(desconto, 2),
        "taxa_servico":    TAXA_SERVICO,
        "total":           round(total, 2),
        "potencia_media":  round(potencia_media, 2),
    }


def exibir_relatorio(dados: dict, sessao: dict):

    veiculo      = dados["veiculo"]
    tipo_usuario = dados["tipo_usuario"]

    cabecalho("RELATÓRIO DE SESSÃO — ChargeGrid Intelligence")

    # ── Identificação ──
    subcabecalho("Identificação")
    id_sessao = f"CG-{sessao['dt_inicio'].strftime('%Y%m%d')}-{random.randint(1000,9999)}"
    print(f"  ID da Sessão     : {id_sessao}")
    print(f"  Tipo de Usuário  : {tipo_usuario}")
    print(f"  Veículo          : {veiculo['nome']}")
    print(f"  Capacidade       : {veiculo['bateria_kwh']} kWh")

    # ── Período ──
    subcabecalho("Período")
    print(f"  Início           : {sessao['dt_inicio'].strftime('%d/%m/%Y %H:%M')}")
    print(f"  Fim              : {sessao['dt_fim'].strftime('%d/%m/%Y %H:%M')}")
    horas  = sessao["duracao_min"] // 60
    minutos= sessao["duracao_min"] %  60
    print(f"  Duração          : {horas}h {minutos:02d}min  ({sessao['duracao_min']} min)")

    # ── Energia ──
    subcabecalho("Energia")
    print(f"  SOC Inicial      : {dados['carga_inicial']:.1f}%")
    print(f"  SOC Final        : {dados['carga_alvo']:.1f}%")
    print(f"  Energia Total    : {sessao['energia_total']:.3f} kWh")
    print(f"  Potência Média   : {sessao['potencia_media']:.2f} kW")
    print(f"  Potência Máx.    : {dados['potencia_kw']:.2f} kW")

    # ── Tarifação ──
    subcabecalho("Tarifação")
    periodo_label = {
        "ponta":    "Horário de Ponta (18h–21h)",
        "off-peak": "Fora de Ponta / Madrugada (0h–6h)",
        "normal":   "Horário Normal",
    }[sessao["periodo"]]

    print(f"  Período Tarifário: {periodo_label}")
    print(f"  Tarifa Aplicada  : R$ {sessao['tarifa_kwh']:.2f}/kWh")

    # ── Cobrança ──
    subcabecalho("Cobrança")
    print(f"  Custo de Energia : R$ {sessao['custo_energia']:>8.2f}")
    if sessao["desconto"] > 0:
        print(f"  Desconto (15%)   : R$ {sessao['desconto']:>8.2f} –")
    print(f"  Taxa de Serviço  : R$ {sessao['taxa_servico']:>8.2f}")
    linha("─")
    print(f"  TOTAL A PAGAR    : R$ {sessao['total']:>8.2f}")

    # ── Resumo ambiental ──
    subcabecalho("Impacto Estimado")
    co2_evitado = sessao["energia_total"] * 0.233  # kg CO₂ por kWh (média BR)
    km_estimado = sessao["energia_total"] * 6      # ~6 km/kWh médio
    print(f"  CO₂ Evitado      : {co2_evitado:.2f} kg")
    print(f"  Autonomia Ganha  : ~{km_estimado:.0f} km")

    linha("═")
    print("  Sessão encerrada com sucesso. Protocolo OCPP 1.6 registrado.")
    linha("═")
    print()


# ────────────
#  ENTRY POINT
# ────────────

def main():
    print()
    cabecalho("ChargeGrid Intelligence v1.0 — FIAP Sprint 1")
    print("""
  Bem-vindo ao simulador de sessão de recarga comercial.
  Este programa simula o ciclo completo de recarga de um
  veículo elétrico em um eletroposto comercial, aplicando
  tarifação dinâmica conforme horário e perfil do usuário.
""")

    while True:
        # 1. Coleta de dados
        dados = coletar_dados_sessao()

        # 2. Simulação
        sessao = processar_sessao(dados)

        # 3. Relatório
        exibir_relatorio(dados, sessao)

        # 4. Nova sessão?
        resposta = input("  Simular nova sessão? [s/n]: ").strip().lower()

        while resposta != "s" and resposta != "n":
            print("Opção inválida. Escolha entre s/n.")
            resposta = input("  Simular nova sessão? [s/n]: ").strip().lower()

        if resposta != "s":
            print("\n  Encerrando ChargeGrid Intelligence. Até logo!\n")
            break
        print()


if __name__ == "__main__":
    main()
