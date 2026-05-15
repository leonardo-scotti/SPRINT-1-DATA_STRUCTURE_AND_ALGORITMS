# ChargeGrid Intelligence — Sprint 1

## Integrantes
| NOME | RM |
| ---- | -- |
| LEONARDO SCOTTI TOBIAS | 573305 |
| NATAN SILVA DA COSTA | 573100 |
| ENZO SEIJI DELGADO TABUCHI | 573156 |
| LUCA ALMEIDA LUCARELI | 569061 |
| HENRIQUE ALMEIDA LUCARELI | 569183 |

## Documento de Lógica do Simulador de Sessão de Recarga

---

## 1. Visão Geral

O simulador implementa o ciclo completo de uma sessão de recarga comercial de veículo elétrico, cobrindo:

- Coleta e validação de dados de entrada
- Simulação minuto a minuto do carregamento
- Aplicação de tarifação dinâmica
- Geração de relatório formatado

---

## 2. Estrutura do Código

O programa está organizado em funções com responsabilidade única:

| Função | Responsabilidade |
|---|---|
| `entrada_inteira()` | Lê e valida inteiros dentro de um intervalo |
| `entrada_float()` | Lê e valida números decimais dentro de um intervalo |
| `escolher_opcao()` | Exibe menu e valida escolha do usuário |
| `detectar_horario()` | Classifica a hora em período tarifário |
| `calcular_tarifa()` | Retorna R$/kWh conforme horário e tipo de usuário |
| `simular_recarga()` | Loop principal da simulação física |
| `coletar_dados_sessao()` | Coleta todas as entradas do usuário |
| `processar_sessao()` | Orquestra simulação + cálculo financeiro |
| `exibir_relatorio()` | Formata e imprime o relatório final |
| `main()` | Ponto de entrada; controla loop de sessões |

---

## 3. Estruturas Condicionais (if / elif / else)

### 3.1 Detecção de Período Tarifário

```python
def detectar_horario(hora: int):
    if 18 <= hora <= 20:
        return "ponta"       # R$ 1,85/kWh
    elif 0 <= hora <= 5:
        return "off-peak"    # R$ 0,90/kWh
    else:
        return "normal"      # R$ 1,20/kWh
```

Três faixas de preço reproduzem a estrutura tarifária da ANEEL:
- **Ponta**: 18h–20h — maior demanda na rede
- **Off-peak**: 0h–5h — menor demanda, tarifa reduzida
- **Normal**: demais horários

### 3.2 Desconto para Assinante

```python
if tipo_usuario == "Assinante":
    desconto = custo_energia * DESCONTO_ASSINANTE  # 15%

if tipo_usuario == "Frota Corporativa":
    tarifa = min(tarifa, TARIFA_OFF_PEAK_KWH)  # tarifa negociada
```

### 3.3 Validação de Entrada

```python
if minimo <= valor <= maximo:
    return valor
else:
    print(f"⚠ Digite um valor entre {minimo} e {maximo}.")
```

---

## 4. Estruturas de Repetição

### 4.1 Loop de Validação de Entrada (`while True`)

Todas as funções de entrada (`entrada_inteira`, `entrada_float`, `escolher_opcao`) usam `while True` com `return` ao validar, garantindo que o programa não avance com dados inválidos:

```python
def entrada_inteira(prompt, minimo, maximo):
    while True:
        try:
            valor = int(input(prompt))
            if minimo <= valor <= maximo:
                return valor          # sai do loop apenas com dado válido
            print("⚠ Valor fora do intervalo.")
        except ValueError:
            print("⚠ Apenas números inteiros.")
```

### 4.2 Loop de Simulação da Recarga (`while`)

A simulação física usa `while` controlado pela energia carregada, não por tempo fixo — refletindo o comportamento real de um carregador:

```python
while energia_carregada < energia_necessaria:
    potencia_atual = potencia_kw * (1 + random.uniform(-0.05, 0.05))
    energia_ciclo  = potencia_atual / 60          # 1 minuto em horas
    energia_ciclo  = min(energia_ciclo, restante) # não ultrapassa o alvo
    energia_carregada += energia_ciclo
    minuto += 1
```

**Controle de fluxo**: o `min()` garante que a última iteração não ultrapasse a energia necessária, encerrando o loop de forma precisa.

### 4.3 Loop de Sessões Múltiplas (`while True` no `main`)

```python
while True:
    dados  = coletar_dados_sessao()
    sessao = processar_sessao(dados)
    exibir_relatorio(dados, sessao)
    if input("Simular nova sessão? [s/n]: ").lower() != "s":
        break
```

---

## 5. Lógica da Sessão de Recarga

### 5.1 Parâmetros físicos

| Parâmetro | Valor |
|---|---|
| Potência máxima do carregador | 22,0 kW (AC Tipo 2, FIAP) |
| Potência mínima válida | 3,7 kW |
| Variação de potência por ciclo | ±5% aleatório (realismo) |
| Passo de simulação | 1 minuto |

### 5.2 Cálculo de energia por ciclo

```
energia_ciclo [kWh] = potencia_atual [kW] × (1 min / 60 min)
```

A cada minuto, a potência varia levemente para simular flutuações reais da rede e do BMS (Battery Management System) do veículo.

### 5.3 Estado de Carga (SOC)

```
energia_necessaria = (SOC_alvo − SOC_inicial) / 100 × capacidade_bateria
SOC_atual = SOC_inicial + (energia_carregada / capacidade_bateria) × 100
```

---

## 6. Cálculo de Tarifação

### 6.1 Tabela de tarifas

| Período | Horário | Tarifa |
|---|---|---|
| Normal | 6h–17h / 21h–23h | R$ 1,20/kWh |
| Ponta | 18h–20h | R$ 1,85/kWh |
| Off-peak | 0h–5h | R$ 0,90/kWh |

### 6.2 Regras diferenciadas por tipo de usuário

| Tipo | Regra |
|---|---|
| Visitante | Tarifa cheia conforme horário |
| Assinante | Tarifa cheia − 15% de desconto |
| Frota Corporativa | min(tarifa_horário, tarifa_off-peak) — tarifa negociada |

### 6.3 Fórmula final

```
custo_energia = energia_total × tarifa_kWh
desconto      = custo_energia × 0,15   (apenas Assinante)
TOTAL         = custo_energia − desconto + R$ 2,50 (taxa de serviço)
```

---

## 7. Entrada e Saída de Dados

### 7.1 Entradas coletadas

| Campo | Tipo | Validação |
|---|---|---|
| Tipo de usuário | Opção [1–3] | Menu com re-entrada |
| Tipo de veículo | Opção [1–4] | Menu com re-entrada |
| SOC inicial | Float [0–99%] | Intervalo numérico |
| SOC desejado | Float [SOC+1–100%] | Limite dinâmico |
| Potência kW | Float [3,7–max veículo] | Limite por veículo |
| Hora de início | Inteiro [0–23] | Intervalo numérico |

### 7.2 Saída — Relatório de sessão

O relatório é dividido em 5 seções:
1. **Identificação** — ID único, usuário, veículo
2. **Período** — Timestamps de início/fim e duração
3. **Energia** — SOC inicial/final, kWh, potência média
4. **Tarifação** — Período tarifário e tarifa aplicada
5. **Cobrança** — Detalhamento de custos e total
6. **Impacto Estimado** — CO₂ evitado e autonomia ganha

---

## 8. Relação com o Projeto ChargeGrid

| Componente simulado | Equivalente real |
|---|---|
| Loop minuto a minuto | Telemetria OCPP `MeterValues` |
| Variação de potência ±5% | Controle de demanda / Power Management |
| SOC e energia carregada | Leitura MODBUS do inversor GoodWe |
| Tarifas por horário | Regras de Dynamic Load Management |
| ID de sessão | `transactionId` no protocolo OCPP 1.6 |
| Relatório final | `StopTransaction` + `MeterStop` |

---

## 9. Execução

```bash
python chargegrid_simulador.py
```

Não requer instalação de bibliotecas externas. Utiliza apenas módulos da biblioteca padrão do Python (`time`, `random`, `datetime`).
