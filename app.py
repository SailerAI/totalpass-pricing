import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Configurações da Página ---
st.set_page_config(
    page_title="Proposta TotalPass | Sailer AI", page_icon="🚀", layout="wide"
)

# --- Configuração de Edição de Tabelas de Preços ---
# Altere para False para desabilitar a edição das tabelas de preços
ENABLE_PRICE_EDITING = True

# --- Dados do Cliente TotalPass ---
TOTALPASS_DATA = {
    "volume_leads_mes": 5000,
    "leads_abandonados_pct": 0.85,
    "ticket_medio": 566.50,
    "ltv_dias": 173,
    "taxa_conversao_atual": 0.166,
    "num_vendedores": 10,
    "comp_total_medio": 9000.0,  # Salário base + comissão média
    "multiplicador_encargos": 1.6,
    "comissao_min": 0.03,
    "comissao_max": 0.05,
}

# --- Funções de Cálculo ---


def calculate_tiered_cost(quantity, tiers_df):
    """
    Calcula o custo total com base em uma tabela de preços escalonada (por faixas).
    A tabela deve ter as colunas 'Mínimo', 'Máximo', 'Valor'.
    """
    if quantity == 0:
        return 0

    # Garante que os tipos de dados estão corretos
    tiers_df["Mínimo"] = tiers_df["Mínimo"].astype(float)
    tiers_df["Máximo"] = tiers_df["Máximo"].astype(float)
    tiers_df["Valor"] = tiers_df["Valor"].astype(float)

    tiers_df = tiers_df.sort_values(by="Mínimo").reset_index(drop=True)

    total_cost = 0

    for _, row in tiers_df.iterrows():
        min_val, max_val, price = row["Mínimo"], row["Máximo"], row["Valor"]

        if quantity > min_val:
            # Calcula a quantidade dentro desta faixa
            items_in_tier = min(quantity, max_val) - min_val
            cost_in_tier = items_in_tier * price
            total_cost += cost_in_tier

    return total_cost


def run_simulation(
    total_leads,
    rates,
    pricing_tables,
    minimum_billing=0.0,
    ticket_medio=0.0,
    taxa_conversao_vendas=0.0,
    comissao_vendas=0.0,
):
    """
    Executa uma simulação completa para um dado cenário.
    """
    # 1. Calcular a quantidade de eventos em cada etapa do funil
    num_replies = total_leads * rates["response"]
    num_no_replies = total_leads - num_replies
    num_qualified = num_replies * rates["qualification"]
    num_booked = num_qualified * rates["booking"]

    # 2. Calcular o custo de cada componente
    # Custo base: leads que não responderam
    cost_no_reply = num_no_replies * pricing_tables["no_reply"].iloc[0]["Valor"]

    # Custo dos leads que responderam (substitui o custo de R$0,20)
    cost_replies = calculate_tiered_cost(num_replies, pricing_tables["leads"])

    # Custos adicionais para eventos de sucesso
    cost_qualified = calculate_tiered_cost(num_qualified, pricing_tables["qualified"])
    cost_booked = calculate_tiered_cost(num_booked, pricing_tables["booked"])

    # 3. Calcular comissão de vendas
    # Número de vendas = reuniões agendadas * taxa de conversão de vendas
    num_vendas = num_booked * taxa_conversao_vendas
    # Comissão = número de vendas * ticket médio * taxa de comissão
    cost_comissao = num_vendas * ticket_medio * comissao_vendas

    # 4. Calcular o custo total e métricas
    calculated_cost = (
        cost_no_reply + cost_replies + cost_qualified + cost_booked + cost_comissao
    )

    # Aplicar consumo mínimo
    total_cost = max(calculated_cost, minimum_billing)

    cpl = total_cost / total_leads if total_leads > 0 else 0
    cpa = total_cost / num_booked if num_booked > 0 else 0

    return {
        "total_leads": total_leads,
        "num_no_replies": num_no_replies,
        "num_replies": num_replies,
        "num_qualified": num_qualified,
        "num_booked": num_booked,
        "num_vendas": num_vendas,
        "cost_no_reply": cost_no_reply,
        "cost_replies": cost_replies,
        "cost_qualified": cost_qualified,
        "cost_booked": cost_booked,
        "cost_comissao": cost_comissao,
        "calculated_cost": calculated_cost,
        "total_cost": total_cost,
        "cpl": cpl,
        "cpa": cpa,
    }


# --- Paleta de Cores ---
BRAND_COLOR = "#39B5FF"  # Cor principal da marca
LIGHT_BLUE_1 = "#A8DAFF"  # Azul claro 1
LIGHT_BLUE_2 = "#70C7FF"  # Azul claro 2
LIGHT_BLUE_3 = "#D4EDFF"  # Azul muito claro
GRAY_1 = "#9E9E9E"  # Cinza médio
GRAY_2 = "#BDBDBD"  # Cinza claro
GRAY_3 = "#E0E0E0"  # Cinza muito claro
GRAY_4 = "#424242"  # Cinza escuro

# --- Interface do Usuário (UI) ---

st.title("🚀 Proposta Comercial | TotalPass + Sailer AI")

# Business Case Hero Section
st.markdown(
    """
    ### Transforme leads abandonados em oportunidades reais com a **Tamires** — sua agente de IA no WhatsApp
    
    ---
    """
)

# Business Case Columns
hero_col1, hero_col2, hero_col3 = st.columns(3)

with hero_col1:
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #39B5FF 0%, #1E88E5 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 2.5rem;">~4.250</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">leads/mês abandonados antes da cotação</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_col2:
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 2.5rem;">85%</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">dos leads abandonam antes de receber cotação</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_col3:
    custo_vendedor = (
        TOTALPASS_DATA["comp_total_medio"] * TOTALPASS_DATA["multiplicador_encargos"]
    )
    custo_time = custo_vendedor * TOTALPASS_DATA["num_vendedores"]
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 2.5rem;">R$ {custo_time/1000:.0f}k</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">custo mensal do time de vendas (10 pessoas)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# Value Proposition
with st.expander("📋 **O Problema & Nossa Solução**", expanded=True):
    prob_col1, prob_col2 = st.columns(2)

    with prob_col1:
        st.markdown(
            """
            #### 😰 O Cenário Atual
            
            O time **TPWeb** da TotalPass recebe aproximadamente **5.000 leads/mês** através do formulário "Simule" no site. 
            No entanto, **85% desses leads abandonam o fluxo antes de receberem a cotação final**.
            
            Isso significa que:
            - **~4.250 leads/mês** estão "parados" sem atenção adequada
            - Vendedores focam apenas nos **750 leads quentes**
            - Oportunidades de SMBs (5-20 vidas) são perdidas
            - Custo de aquisição desperdiçado em leads não trabalhados
            """
        )

    with prob_col2:
        st.markdown(
            """
            #### 🤖 A Solução: Tamires AI
            
            A **Tamires** é uma agente de IA que trabalha 24/7 via WhatsApp para:
            
            ✅ **Reativar** leads que abandonaram o fluxo  
            ✅ **Qualificar** e tirar dúvidas automaticamente  
            ✅ **Conduzir** a venda até o aceite da cotação  
            ✅ **Agendar** reuniões ou transbordar quando necessário
            
            > *"Seus vendedores focam em fechar negócios complexos, enquanto a Tamires cuida da repescagem e vendas SMB."*
            """
        )

# Segmentation by Company Size
with st.expander("🎯 **Fluxo por Segmento de Cliente**", expanded=True):
    seg_col1, seg_col2 = st.columns(2)

    with seg_col1:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #39B5FF 0%, #1E88E5 100%); padding: 20px; border-radius: 12px; color: white;">
                <h4 style="margin: 0 0 15px 0;">👥 SMB: 5 a 20 vidas</h4>
                <p style="margin: 0 0 10px 0;"><strong>Tamires conduz a venda completa</strong></p>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Reativa o lead abandonado</li>
                    <li>Qualifica e tira dúvidas</li>
                    <li>Apresenta cotação e negocia</li>
                    <li>Conduz até o aceite</li>
                    <li>Transborda apenas para validação final (documentos, facial, fraude)</li>
                </ul>
                <p style="margin: 15px 0 0 0; opacity: 0.9; font-size: 0.9rem;">💡 <em>Libera vendedores para contas maiores</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with seg_col2:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%); padding: 20px; border-radius: 12px; color: white;">
                <h4 style="margin: 0 0 15px 0;">🏢 Mid-Market: +20 vidas</h4>
                <p style="margin: 0 0 10px 0;"><strong>Tamires qualifica e agenda reunião</strong></p>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Reativa o lead abandonado</li>
                    <li>Qualifica e coleta informações</li>
                    <li>Identifica necessidades específicas</li>
                    <li>Agenda reunião com vendedor</li>
                    <li>Transborda com contexto completo</li>
                </ul>
                <p style="margin: 15px 0 0 0; opacity: 0.9; font-size: 0.9rem;">💡 <em>Vendedor recebe lead quente e qualificado</em></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Billing Model Explanation
with st.expander(
    "💰 **Modelo de Cobrança & Alinhamento de Incentivos**", expanded=True
):
    st.markdown("### Por que nosso modelo funciona para você")
    st.markdown(
        "Nosso modelo de precificação foi desenhado para **alinhar nossos incentivos com os seus resultados**:"
    )

    # Tabela de preços usando HTML para evitar problemas com R$
    st.markdown(
        """
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                    <th style="padding: 12px; text-align: left; font-weight: 600;">Componente</th>
                    <th style="padding: 12px; text-align: left; font-weight: 600;">Como funciona</th>
                    <th style="padding: 12px; text-align: left; font-weight: 600;">Por que é justo</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 12px;"><strong>Custo por Disparo</strong></td>
                    <td style="padding: 12px;">R&#36; 0,20 por lead sem resposta</td>
                    <td style="padding: 12px;">Você só paga pelo alcance real</td>
                </tr>
                <tr style="border-bottom: 1px solid #dee2e6; background: #f8f9fa;">
                    <td style="padding: 12px;"><strong>Custo por Resposta</strong></td>
                    <td style="padding: 12px;">R&#36; 2,50 a R&#36; 5,00 (escalonado)</td>
                    <td style="padding: 12px;">Quanto mais engajamento, menor o custo</td>
                </tr>
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 12px;"><strong>Custo por Lead Qualificado</strong></td>
                    <td style="padding: 12px;">R&#36; 5,00 a R&#36; 15,00 por qualificado</td>
                    <td style="padding: 12px;">Pagamento por resultado real</td>
                </tr>
                <tr style="border-bottom: 1px solid #dee2e6; background: #f8f9fa;">
                    <td style="padding: 12px;"><strong>Custo por Lead Avançado</strong></td>
                    <td style="padding: 12px;">R&#36; 40,00 a R&#36; 80,00 por avanço</td>
                    <td style="padding: 12px;">Só cobra quando o lead avança</td>
                </tr>
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 12px;"><strong>Comissão sobre Vendas</strong></td>
                    <td style="padding: 12px;">3% do <strong>LTV</strong> por venda</td>
                    <td style="padding: 12px;">Ganhamos juntos com o valor total</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ---
        
        #### 🎯 Incentivos Alinhados
        
        - **Sem resultado = baixo custo**: Se a IA não conseguir engajar, você paga apenas o mínimo
        - **Com resultado = custo proporcional**: Quanto mais leads qualificados e avançados, maior o investimento — mas também maior o retorno
        - **Comissão sobre vendas (SMB)**: Participamos do seu sucesso nas vendas que a Tamires conduziu
        - **Reunião qualificada (+20 vidas)**: Seu vendedor recebe o lead pronto para fechar
        
        > *"Não vendemos horas ou licenças. Vendemos resultados."*
        """
    )

st.divider()

# --- Barra Lateral de Configurações ---
st.sidebar.image("LOGO-COR.png", width=200)
st.sidebar.header("⚙️ Configure a Simulação")

st.sidebar.subheader("🎯 Cenário de Simulação")

# Informação contextual
st.sidebar.caption(
    f"📊 **Dados TotalPass:** {TOTALPASS_DATA['volume_leads_mes']:,} leads/mês | "
    f"~{int(TOTALPASS_DATA['volume_leads_mes'] * TOTALPASS_DATA['leads_abandonados_pct']):,} abandonados"
)

target_total_leads = st.sidebar.slider(
    "Quantidade de Leads a serem processados",
    min_value=0,
    max_value=5000,
    value=2000,
    step=100,
    help="Recomendamos iniciar com 1.000-2.000 leads para a POC",
)

# Colunas para organizar as taxas de conversão
col1, col2 = st.sidebar.columns(2)
target_response_rate = (
    col1.slider(
        "Taxa de Resposta (%)",
        min_value=0.0,
        max_value=100.0,
        value=45.0,
        step=0.5,
        format="%.1f%%",
        help="Expectativa conservadora para WhatsApp",
    )
    / 100.0
)

target_qualification_rate = (
    col2.slider(
        "Taxa de Qualificação (% de Respostas)",
        min_value=0.0,
        max_value=100.0,
        value=25.0,
        step=0.5,
        format="%.1f%%",
        help="Leads que avançam para qualificação",
    )
    / 100.0
)

target_booking_rate = (
    st.sidebar.slider(
        "Taxa de Avanço/Agendamento (%)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=0.5,
        format="%.1f%%",
        help="SMB: avanço para cotação | +20 vidas: agendamento de reunião",
    )
    / 100.0
)

# Consumo mínimo mensal
st.sidebar.subheader("💳 Cobrança Mínima")
minimum_billing = st.sidebar.number_input(
    "Consumo Mínimo Mensal (R$)",
    min_value=0.0,
    max_value=50000.0,
    value=2997.0,
    step=100.0,
    help="Valor mínimo mensal garantido para manter a operação",
)

# Comissão de Vendas
st.sidebar.subheader("💵 Comissão de Vendas")
st.sidebar.caption("Comissão sobre o LTV das vendas fechadas")

ticket_medio_mensal = st.sidebar.number_input(
    "Ticket Médio Mensal (R$)",
    min_value=0.0,
    max_value=10000.0,
    value=TOTALPASS_DATA["ticket_medio"],
    step=50.0,
    help="Valor médio mensal de cada venda TotalPass (SMB 5-20 vidas)",
)

ltv_dias = st.sidebar.number_input(
    "LTV (dias)",
    min_value=30,
    max_value=730,
    value=int(TOTALPASS_DATA["ltv_dias"]),
    step=10,
    help="Lifetime Value médio do cliente em dias",
)

# Calcular LTV em valor monetário
ltv_meses = ltv_dias / 30
ltv_valor = ticket_medio_mensal * ltv_meses

st.sidebar.metric(
    label="💰 LTV Estimado",
    value=f"R$ {ltv_valor:,.2f}",
    delta=f"{ltv_meses:.1f} meses × R$ {ticket_medio_mensal:,.2f}",
)

taxa_conversao_vendas = (
    st.sidebar.slider(
        "Taxa de Conversão de Vendas (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(TOTALPASS_DATA["taxa_conversao_atual"] * 100),
        step=1.0,
        format="%.0f%%",
        help=f"Taxa atual TotalPass: {TOTALPASS_DATA['taxa_conversao_atual']*100:.1f}%",
    )
    / 100.0
)

comissao_vendas = (
    st.sidebar.slider(
        "Comissão de Vendas (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.5,
        format="%.1f%%",
        help="Porcentagem do LTV por venda fechada (alinhado com comissão atual: 3-5%)",
    )
    / 100.0
)

# Para cálculos, usamos o LTV como base da comissão
ticket_medio = ltv_valor  # Comissão é sobre o LTV, não apenas o ticket mensal

# Taxa de Setup (única vez)
st.sidebar.subheader("🚀 Taxa de Setup (Única Vez)")
st.sidebar.markdown(
    """
    **R$ 14.470,00**
    
    ✅ Criação da **Tamires** (Agente IA)  
    ✅ Suporte total durante implantação  
    ✅ Treinamento da equipe TPWeb  
    ✅ Integração com Salesforce
    """
)
setup_fee = 14470.0


# --- Função para formatar tabelas de preços ---
def format_price_table(df, show_ranges=True):
    """Formata a tabela de preços para melhor visualização"""
    if show_ranges and "Mínimo" in df.columns and "Máximo" in df.columns:
        # Criar coluna de faixa
        df_display = df.copy()
        faixas = []
        for _, row in df_display.iterrows():
            if row["Máximo"] >= 99999:
                faixa = f"{int(row['Mínimo']):,}+"
            else:
                faixa = f"{int(row['Mínimo']):,} - {int(row['Máximo']):,}"
            faixas.append(faixa)
        df_display.insert(0, "Faixa", faixas)
        df_display = df_display[["Faixa", "Valor"]].copy()
        df_display["Valor"] = df_display["Valor"].apply(lambda x: f"R$ {x:,.2f}")
        return df_display
    else:
        df_display = df.copy()
        if "Valor" in df_display.columns:
            df_display["Valor"] = df_display["Valor"].apply(lambda x: f"R$ {x:,.2f}")
        return df_display


# --- Tabelas de Preços Configuráveis ---
st.sidebar.subheader("💰 Tabelas de Preços")
st.sidebar.caption("Configure as faixas de preço por volume (preços escalonados)")

with st.sidebar.expander("📧 Custo por Envio (Sem Resposta)", expanded=False):
    st.caption("Custo fixo por lead que não respondeu")
    df_no_reply = pd.DataFrame([{"Valor": 0.20}])
    df_no_reply_display = format_price_table(df_no_reply, show_ranges=False)
    st.dataframe(
        df_no_reply_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Valor": st.column_config.TextColumn("Custo por Lead", width="medium")
        },
    )


with st.sidebar.expander("💬 Custo por Lead (com Resposta)", expanded=False):
    st.caption("Preço por lead que respondeu, escalonado por volume de respostas")
    df_leads = pd.DataFrame(
        [
            {"Mínimo": 0, "Máximo": 300, "Valor": 5.00},
            {"Mínimo": 300, "Máximo": 800, "Valor": 4.00},
            {"Mínimo": 800, "Máximo": 1500, "Valor": 3.50},
            {"Mínimo": 1500, "Máximo": 2500, "Valor": 3.00},
            {
                "Mínimo": 2500,
                "Máximo": 99999,
                "Valor": 2.50,
            },  # Máximo alto para pegar todos os excedentes
        ]
    )
    if ENABLE_PRICE_EDITING:
        edited_df_leads = st.data_editor(
            df_leads,
            key="leads_editor",
            num_rows="dynamic",
            column_config={
                "Mínimo": st.column_config.NumberColumn(
                    "Mínimo", format="%d", width="small"
                ),
                "Máximo": st.column_config.NumberColumn(
                    "Máximo", format="%d", width="small"
                ),
                "Valor": st.column_config.NumberColumn(
                    "Preço (R$)", format="%.2f", width="small"
                ),
            },
            hide_index=True,
        )
    else:
        df_leads_display = format_price_table(df_leads, show_ranges=True)
        st.dataframe(
            df_leads_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Faixa": st.column_config.TextColumn("Volume", width="medium"),
                "Valor": st.column_config.TextColumn("Preço por Lead", width="medium"),
            },
        )
        edited_df_leads = df_leads

with st.sidebar.expander("✅ Custo por Lead Qualificado", expanded=False):
    st.caption("Preço por lead qualificado, escalonado por volume de qualificados")
    df_qualified = pd.DataFrame(
        [
            {"Mínimo": 0, "Máximo": 75, "Valor": 15.00},
            {"Mínimo": 75, "Máximo": 150, "Valor": 12.00},
            {"Mínimo": 150, "Máximo": 300, "Valor": 8.00},
            {"Mínimo": 300, "Máximo": 99999, "Valor": 5.00},
        ]
    )
    if ENABLE_PRICE_EDITING:
        edited_df_qualified = st.data_editor(
            df_qualified,
            key="qualified_editor",
            num_rows="dynamic",
            column_config={
                "Mínimo": st.column_config.NumberColumn(
                    "Mínimo", format="%d", width="small"
                ),
                "Máximo": st.column_config.NumberColumn(
                    "Máximo", format="%d", width="small"
                ),
                "Valor": st.column_config.NumberColumn(
                    "Preço (R$)", format="%.2f", width="small"
                ),
            },
            hide_index=True,
        )
    else:
        df_qualified_display = format_price_table(df_qualified, show_ranges=True)
        st.dataframe(
            df_qualified_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Faixa": st.column_config.TextColumn("Volume", width="medium"),
                "Valor": st.column_config.TextColumn("Preço por Lead", width="medium"),
            },
        )
        edited_df_qualified = df_qualified

with st.sidebar.expander("📈 Custo por Lead Avançado", expanded=False):
    st.caption("Preço por lead que avançou para cotação/oportunidade")
    df_booked = pd.DataFrame(
        [
            {"Mínimo": 0, "Máximo": 30, "Valor": 80.00},
            {"Mínimo": 30, "Máximo": 60, "Valor": 60.00},
            {"Mínimo": 60, "Máximo": 100, "Valor": 50.00},
            {"Mínimo": 100, "Máximo": 99999, "Valor": 40.00},
        ]
    )
    if ENABLE_PRICE_EDITING:
        edited_df_booked = st.data_editor(
            df_booked,
            key="booked_editor",
            num_rows="dynamic",
            column_config={
                "Mínimo": st.column_config.NumberColumn(
                    "Mínimo", format="%d", width="small"
                ),
                "Máximo": st.column_config.NumberColumn(
                    "Máximo", format="%d", width="small"
                ),
                "Valor": st.column_config.NumberColumn(
                    "Preço (R$)", format="%.2f", width="small"
                ),
            },
            hide_index=True,
        )
    else:
        df_booked_display = format_price_table(df_booked, show_ranges=True)
        st.dataframe(
            df_booked_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Faixa": st.column_config.TextColumn("Volume", width="medium"),
                "Valor": st.column_config.TextColumn(
                    "Preço por Lead Avançado", width="medium"
                ),
            },
        )
        edited_df_booked = df_booked


# --- Coleta dos dados para a simulação ---
rates = {
    "response": target_response_rate,
    "qualification": target_qualification_rate,
    "booking": target_booking_rate,
}
pricing_tables = {
    "no_reply": df_no_reply,
    "leads": edited_df_leads,
    "qualified": edited_df_qualified,
    "booked": edited_df_booked,
}

# --- Execução e Exibição dos Resultados ---
if target_total_leads > 0:
    # Simulação para o cenário target
    target_results = run_simulation(
        target_total_leads,
        rates,
        pricing_tables,
        minimum_billing,
        ticket_medio,
        taxa_conversao_vendas,
        comissao_vendas,
    )

    st.header("📊 Resultados da Simulação")
    st.markdown(
        f"Análise para **{target_total_leads:,} disparos** processados com as taxas de conversão configuradas."
    )

    # Verificar se o consumo mínimo foi aplicado
    calculated_cost = target_results["calculated_cost"]
    final_cost = target_results["total_cost"]
    has_minimum_charge = final_cost > calculated_cost

    # Funil de conversão - Métricas principais
    funnel_col1, funnel_col2, funnel_col3, funnel_col4 = st.columns(4)

    with funnel_col1:
        st.metric(
            label="📨 Respostas",
            value=f"{int(target_results['num_replies']):,}",
            delta=f"{target_response_rate * 100:.1f}% dos disparos",
        )

    with funnel_col2:
        st.metric(
            label="✅ Leads Qualificados",
            value=f"{int(target_results['num_qualified']):,}",
            delta=f"{target_qualification_rate * 100:.1f}% das respostas",
        )

    with funnel_col3:
        st.metric(
            label="📈 Leads Avançados / Reuniões",
            value=f"{int(target_results['num_booked']):,}",
            delta=f"{target_booking_rate * 100:.1f}% dos qualificados",
            help="SMB: leads avançados para cotação | +20 vidas: reuniões agendadas",
        )

    with funnel_col4:
        if has_minimum_charge:
            st.metric(
                label="💵 Custo Mensal",
                value=f"R$ {final_cost:,.2f}",
                delta="Consumo mínimo aplicado",
                delta_color="off",
            )
            st.caption(f"💡 Custo calculado: R$ {calculated_cost:,.2f}")
        else:
            st.metric(
                label="💵 Custo Mensal",
                value=f"R$ {final_cost:,.2f}",
                delta=None,
            )

    # Métricas de vendas e comissão
    st.divider()

    sales_col1, sales_col2, sales_col3, sales_col4 = st.columns(4)

    with sales_col1:
        st.metric(
            label="💰 Vendas Estimadas",
            value=f"{target_results['num_vendas']:.1f}",
            delta=f"{taxa_conversao_vendas * 100:.0f}% dos avançados",
        )

    with sales_col2:
        # Receita mensal real (cash flow)
        receita_mensal = target_results["num_vendas"] * ticket_medio_mensal
        # LTV total (valor completo do cliente)
        receita_ltv = target_results["num_vendas"] * ticket_medio  # ticket_medio = LTV
        st.metric(
            label="📈 Receita Mensal",
            value=f"R$ {receita_mensal:,.2f}",
            delta=f"LTV total: R$ {receita_ltv:,.0f}",
            help=f"Mensal: {target_results['num_vendas']:.1f} vendas × R$ {ticket_medio_mensal:,.2f} | LTV ({ltv_meses:.1f} meses): R$ {receita_ltv:,.2f}",
        )

    with sales_col3:
        st.metric(
            label="🤝 Comissão de Vendas",
            value=f"R$ {target_results['cost_comissao']:,.2f}",
            delta=f"{comissao_vendas * 100:.1f}% do LTV",
            help="Comissão calculada sobre o Lifetime Value completo",
        )

    with sales_col4:
        # ROI considerando o LTV completo (valor real gerado pelos clientes)
        roi_ltv = (receita_ltv - final_cost) / final_cost * 100 if final_cost > 0 else 0
        st.metric(
            label="📊 ROI sobre LTV",
            value=f"{roi_ltv:.1f}%",
            delta=f"LTV gerado vs Custo Sailer",
            delta_color="normal" if roi_ltv > 0 else "inverse",
            help="Retorno considerando o valor total que os clientes trarão ao longo do tempo",
        )

    # Projeção 12 meses - Receita Acumulada vs Custo Sailer
    st.divider()

    st.subheader("📈 Projeção 12 Meses: Receita Acumulada vs Investimento")
    st.markdown(
        """
        Estes leads **seriam perdidos sem a Tamires**. A receita gerada é **100% incremental**.
        Veja como o valor acumula ao longo do tempo:
        """
    )

    # Calcular projeção mês a mês
    # Cada mês gera novas vendas que pagam mensalidades durante o LTV
    vendas_por_mes = target_results["num_vendas"]
    meses_ltv = int(ltv_meses)

    projecao_data = []
    clientes_ativos = 0
    receita_acumulada = 0
    custo_sailer_acumulado = setup_fee  # Começa com o setup

    for mes in range(1, 13):
        # Novos clientes entram
        clientes_ativos += vendas_por_mes

        # Clientes saem após o LTV (simplificado)
        if mes > meses_ltv:
            clientes_ativos -= vendas_por_mes

        # Limita ao máximo de clientes ativos baseado no LTV
        clientes_ativos = min(clientes_ativos, vendas_por_mes * meses_ltv)

        # Receita do mês = clientes ativos × ticket mensal
        receita_mes = clientes_ativos * ticket_medio_mensal
        receita_acumulada += receita_mes

        # Custo Sailer acumulado
        custo_sailer_acumulado += final_cost

        projecao_data.append(
            {
                "Mês": mes,
                "Clientes Ativos": clientes_ativos,
                "Receita Mensal": receita_mes,
                "Receita Acumulada": receita_acumulada,
                "Custo Sailer Acumulado": custo_sailer_acumulado,
                "Lucro Acumulado": receita_acumulada - custo_sailer_acumulado,
            }
        )

    projecao_df = pd.DataFrame(projecao_data)

    # Gráfico de linha comparando receita acumulada vs custo Sailer
    fig_projecao = go.Figure()

    fig_projecao.add_trace(
        go.Scatter(
            x=projecao_df["Mês"],
            y=projecao_df["Receita Acumulada"],
            mode="lines+markers",
            name="Receita Acumulada",
            line=dict(color="#26de81", width=3),
            fill="tozeroy",
            fillcolor="rgba(38, 222, 129, 0.1)",
        )
    )

    fig_projecao.add_trace(
        go.Scatter(
            x=projecao_df["Mês"],
            y=projecao_df["Custo Sailer Acumulado"],
            mode="lines+markers",
            name="Investimento Sailer",
            line=dict(color="#39B5FF", width=3),
        )
    )

    # Encontrar ponto de break-even
    breakeven_mes = None
    for _, row in projecao_df.iterrows():
        if float(row["Lucro Acumulado"]) > 0:
            breakeven_mes = int(row["Mês"])
            break

    if breakeven_mes is not None:
        fig_projecao.add_vline(
            x=breakeven_mes,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Break-even: Mês {breakeven_mes}",
            annotation_position="top",
        )

    fig_projecao.update_layout(
        title="Receita Acumulada vs Investimento Sailer (12 meses)",
        xaxis_title="Mês",
        yaxis_title="Valor (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    proj_col1, proj_col2 = st.columns([0.65, 0.35])

    with proj_col1:
        st.plotly_chart(fig_projecao, use_container_width=True)

    with proj_col2:
        lucro_12_meses = projecao_df.iloc[-1]["Lucro Acumulado"]
        receita_12_meses = projecao_df.iloc[-1]["Receita Acumulada"]
        custo_12_meses = projecao_df.iloc[-1]["Custo Sailer Acumulado"]
        roi_12_meses = (
            (lucro_12_meses / custo_12_meses * 100) if custo_12_meses > 0 else 0
        )

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%); padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 15px;">
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Lucro Acumulado em 12 meses</p>
                <h2 style="margin: 10px 0;">R$ {lucro_12_meses:,.2f}</h2>
                <p style="margin: 0; opacity: 0.8; font-size: 0.8rem;">ROI: {roi_12_meses:.0f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        breakeven_text = f"Mês {breakeven_mes}" if breakeven_mes is not None else "N/A"
        st.markdown(
            f"""
            **Resumo 12 meses:**
            - 📈 Receita total: **R$ {receita_12_meses:,.2f}**
            - 💳 Investimento Sailer: **R$ {custo_12_meses:,.2f}**
            - 🎯 Break-even: **{breakeven_text}**
            - 💰 Lucro: **R$ {lucro_12_meses:,.2f}**
            
            > *Receita de leads que seriam perdidos sem a Tamires*
            """
        )

    # Taxa de Setup
    st.divider()

    st.subheader("🚀 Investimento Inicial (Única Vez)")
    setup_col1, setup_col2 = st.columns([0.6, 0.4])

    with setup_col1:
        st.info(
            f"""
            **Taxa de Setup: R$ {setup_fee:,.2f}**
            
            O investimento inicial inclui:
            - ✅ **Criação do Agente de IA** - Configuração completa e personalizada
            - ✅ **Suporte Total** - Acompanhamento dedicado durante implantação
            - ✅ **Treinamento** - Capacitação da equipe para uso da plataforma
            - ✅ **Integração com Salesforce** - Conexão completa com seu CRM
            """
        )

    with setup_col2:
        st.metric(
            label="💳 Taxa de Setup",
            value=f"R$ {setup_fee:,.2f}",
        )
        # Payback em meses baseado na receita mensal real (não LTV)
        if receita_mensal > final_cost and receita_mensal > 0:
            lucro_mensal = receita_mensal - final_cost
            payback_meses = (
                setup_fee / lucro_mensal if lucro_mensal > 0 else float("inf")
            )
            if payback_meses < 36:
                st.metric(
                    label="⏱️ Payback do Setup",
                    value=f"{payback_meses:.1f} meses",
                    delta=f"Lucro mensal: R$ {lucro_mensal:,.0f}",
                    delta_color="off",
                )
        elif receita_mensal > 0:
            st.caption(f"💡 Receita mensal: R$ {receita_mensal:,.2f}")

    # Separador visual
    st.divider()

    # Comparativo de Custos
    st.subheader("📊 Comparativo: Sailer AI vs. Operação Atual")

    # Calcular custos da operação atual baseado nos dados reais
    # 10 vendedores × R$ 9.000 (comp total) × 1.6 (encargos) = R$ 144.000/mês para 5.000 leads
    custo_vendedor_total = (
        TOTALPASS_DATA["comp_total_medio"] * TOTALPASS_DATA["multiplicador_encargos"]
    )
    custo_time_total = custo_vendedor_total * TOTALPASS_DATA["num_vendedores"]
    volume_leads_atual = TOTALPASS_DATA["volume_leads_mes"]

    # Custo por lead no modelo atual
    custo_por_lead_atual = custo_time_total / volume_leads_atual

    # Custo proporcional para os leads que a Sailer vai trabalhar
    custo_operacao_manual = target_total_leads * custo_por_lead_atual
    pct_capacidade = (target_total_leads / volume_leads_atual) * 100

    comp_col1, comp_col2, comp_col3 = st.columns(3)

    with comp_col1:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;">
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Custo Proporcional do Time Atual</p>
                <h2 style="margin: 10px 0;">R$ {custo_operacao_manual:,.2f}</h2>
                <p style="margin: 0; opacity: 0.8; font-size: 0.8rem;">{pct_capacidade:.0f}% da capacidade × R$ {custo_time_total:,.0f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with comp_col2:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #39B5FF 0%, #1E88E5 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;">
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Sailer AI (Tamires)</p>
                <h2 style="margin: 10px 0;">R$ {final_cost:,.2f}</h2>
                <p style="margin: 0; opacity: 0.8; font-size: 0.8rem;">Custo variável por resultado</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with comp_col3:
        economia = custo_operacao_manual - final_cost
        economia_pct = (
            (economia / custo_operacao_manual * 100) if custo_operacao_manual > 0 else 0
        )
        cor_economia = "#26de81" if economia >= 0 else "#FF6B6B"
        cor_economia_fim = "#20bf6b" if economia >= 0 else "#EE5A24"
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, {cor_economia} 0%, {cor_economia_fim} 100%); padding: 20px; border-radius: 12px; text-align: center; color: white;">
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{"Economia" if economia >= 0 else "Investimento Adicional"}</p>
                <h2 style="margin: 10px 0;">R$ {abs(economia):,.2f}</h2>
                <p style="margin: 0; opacity: 0.8; font-size: 0.8rem;">{abs(economia_pct):.0f}% {"de economia" if economia >= 0 else "a mais"}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        f"💡 *Base: 10 vendedores × R$ 9.000 (comp média) × 1.6 (encargos) = R$ {custo_time_total:,.0f}/mês para {volume_leads_atual:,} leads = R$ {custo_por_lead_atual:.2f}/lead*"
    )

    st.divider()

    # Detalhamento dos custos
    st.subheader("💰 Composição do Custo Mensal")
    cost_data = {
        "Componente": [
            "Sem Resposta",
            "Leads (com Resposta)",
            "Leads Qualificados",
            "Leads Avançados / Reuniões",
            "Comissão de Vendas",
        ],
        "Quantidade": [
            f"{int(target_results['num_no_replies']):,}",
            f"{int(target_results['num_replies']):,}",
            f"{int(target_results['num_qualified']):,}",
            f"{int(target_results['num_booked']):,}",
            f"{target_results['num_vendas']:.1f} vendas",
        ],
        "Custo (R$)": [
            target_results["cost_no_reply"],
            target_results["cost_replies"],
            target_results["cost_qualified"],
            target_results["cost_booked"],
            target_results["cost_comissao"],
        ],
    }

    # Adicionar linha de consumo mínimo se aplicável
    if has_minimum_charge:
        cost_data["Componente"].append("Ajuste Consumo Mínimo")
        cost_data["Quantidade"].append("-")
        cost_data["Custo (R$)"].append(final_cost - calculated_cost)

    cost_df = pd.DataFrame(cost_data)
    cost_df["% do Total"] = (cost_df["Custo (R$)"] / final_cost * 100).fillna(0)

    # Formatação para exibição
    formatted_cost_df = cost_df.style.format(
        {"Custo (R$)": "R$ {:,.2f}", "% do Total": "{:.1f}%"}
    )

    col_detail, col_pie = st.columns([0.6, 0.4])
    with col_detail:
        st.dataframe(formatted_cost_df, use_container_width=True)

    with col_pie:
        # Cores do gráfico de pizza (incluindo cor para comissão e consumo mínimo se aplicável)
        pie_colors = [
            GRAY_3,
            LIGHT_BLUE_3,
            LIGHT_BLUE_2,
            BRAND_COLOR,
            "#FFB347",
        ]  # Laranja para comissão
        if has_minimum_charge:
            pie_colors.append(GRAY_1)  # Cor para ajuste de consumo mínimo

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=cost_df["Componente"],
                    values=cost_df["Custo (R$)"],
                    hole=0.3,
                    textinfo="label+percent",
                    marker_colors=pie_colors,
                )
            ]
        )
        fig_pie.update_layout(
            title_text="Distribuição do Custo Total",
            margin=dict(t=40, b=10, l=10, r=10),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Separador visual
    st.divider()

    # --- Gráficos de Simulação e Variação ---
    st.header("📈 Análise de Sensibilidade por Volume")
    st.markdown(
        "Explore como diferentes taxas de conversão impactam os custos em diversos volumes de leads (0 a 5.000)."
    )

    # Criar abas para os três gráficos de volume
    tab_resp, tab_qual, tab_book = st.tabs(
        ["Taxa de Resposta", "Taxa de Qualificação", "Taxa de Avanço"]
    )

    # Gráfico 1: Custo Total vs. Quantidade de Leads (Variando Taxa de Resposta)
    with tab_resp:
        lead_volumes = list(range(0, 5001, 100))

        # Variações de taxa de resposta baseadas no target
        response_step = 0.10  # 10 pontos percentuais
        response_rate_variations = {}

        # Duas abaixo do target
        if target_response_rate - 2 * response_step >= 0:
            response_rate_variations[
                f"-20pp ({(target_response_rate - 2 * response_step) * 100:.1f}%)"
            ] = target_response_rate - 2 * response_step
        if target_response_rate - response_step >= 0:
            response_rate_variations[
                f"-10pp ({(target_response_rate - response_step) * 100:.1f}%)"
            ] = target_response_rate - response_step

        # Target
        response_rate_variations[f"Target ({target_response_rate * 100:.1f}%)"] = (
            target_response_rate
        )

        # Duas acima do target
        if target_response_rate + response_step <= 1.0:
            response_rate_variations[
                f"+10pp ({(target_response_rate + response_step) * 100:.1f}%)"
            ] = target_response_rate + response_step
        if target_response_rate + 2 * response_step <= 1.0:
            response_rate_variations[
                f"+20pp ({(target_response_rate + 2 * response_step) * 100:.1f}%)"
            ] = target_response_rate + 2 * response_step

        fig_volume_response = go.Figure()

        # Define colors for each scenario
        scenario_colors = {
            0: GRAY_2,  # -10pp
            1: GRAY_1,  # -5pp
            2: BRAND_COLOR,  # Target
            3: LIGHT_BLUE_2,  # +5pp
            4: LIGHT_BLUE_1,  # +10pp
        }

        for idx, (scenario_name, response_rate) in enumerate(
            response_rate_variations.items()
        ):
            costs = []
            scenario_rates = rates.copy()
            scenario_rates["response"] = response_rate
            for volume in lead_volumes:
                sim_result = run_simulation(
                    volume,
                    scenario_rates,
                    pricing_tables,
                    minimum_billing,
                    ticket_medio,
                    taxa_conversao_vendas,
                    comissao_vendas,
                )
                costs.append(sim_result["total_cost"])

            is_target = "Target" in scenario_name
            fig_volume_response.add_trace(
                go.Scatter(
                    x=lead_volumes,
                    y=costs,
                    mode="lines",
                    name=scenario_name,
                    line=dict(
                        width=4 if is_target else 2.5,
                        dash="solid" if is_target else "dot",
                        color=scenario_colors.get(idx, BRAND_COLOR),
                    ),
                )
            )

        # Adicionar ponto do cenário target
        fig_volume_response.add_trace(
            go.Scatter(
                x=[target_total_leads],
                y=[target_results["total_cost"]],
                mode="markers",
                marker=dict(size=12, color="red", symbol="star"),
                name="Seu Cenário Atual",
            )
        )

        fig_volume_response.update_layout(
            xaxis_title="Quantidade de Leads Processados",
            yaxis_title="Custo Total (R$)",
            legend_title="Taxa de Resposta",
            hovermode="x unified",
        )
        st.plotly_chart(fig_volume_response, use_container_width=True)

    # Gráfico 2: Custo Total vs. Quantidade de Leads (Variando Taxa de Qualificação)
    with tab_qual:
        # Variações de taxa de qualificação baseadas no target
        qualification_step = 0.10  # 10 pontos percentuais
        qualification_rate_variations = {}

        # Duas abaixo do target
        if target_qualification_rate - 2 * qualification_step >= 0:
            qualification_rate_variations[
                f"-20pp ({(target_qualification_rate - 2 * qualification_step) * 100:.1f}%)"
            ] = target_qualification_rate - 2 * qualification_step
        if target_qualification_rate - qualification_step >= 0:
            qualification_rate_variations[
                f"-10pp ({(target_qualification_rate - qualification_step) * 100:.1f}%)"
            ] = target_qualification_rate - qualification_step

        # Target
        qualification_rate_variations[
            f"Target ({target_qualification_rate * 100:.1f}%)"
        ] = target_qualification_rate

        # Duas acima do target
        if target_qualification_rate + qualification_step <= 1.0:
            qualification_rate_variations[
                f"+10pp ({(target_qualification_rate + qualification_step) * 100:.1f}%)"
            ] = target_qualification_rate + qualification_step
        if target_qualification_rate + 2 * qualification_step <= 1.0:
            qualification_rate_variations[
                f"+20pp ({(target_qualification_rate + 2 * qualification_step) * 100:.1f}%)"
            ] = target_qualification_rate + 2 * qualification_step

        fig_volume_qualification = go.Figure()

        # Define colors for each scenario
        scenario_colors_qual = {
            0: GRAY_2,  # -20pp
            1: GRAY_1,  # -10pp
            2: BRAND_COLOR,  # Target
            3: LIGHT_BLUE_2,  # +10pp
            4: LIGHT_BLUE_1,  # +20pp
        }

        for idx, (scenario_name, qual_rate) in enumerate(
            qualification_rate_variations.items()
        ):
            costs = []
            scenario_rates = rates.copy()
            scenario_rates["qualification"] = qual_rate
            for volume in lead_volumes:
                sim_result = run_simulation(
                    volume,
                    scenario_rates,
                    pricing_tables,
                    minimum_billing,
                    ticket_medio,
                    taxa_conversao_vendas,
                    comissao_vendas,
                )
                costs.append(sim_result["total_cost"])

            is_target = "Target" in scenario_name
            fig_volume_qualification.add_trace(
                go.Scatter(
                    x=lead_volumes,
                    y=costs,
                    mode="lines",
                    name=scenario_name,
                    line=dict(
                        width=4 if is_target else 2.5,
                        dash="solid" if is_target else "dot",
                        color=scenario_colors_qual.get(idx, BRAND_COLOR),
                    ),
                )
            )

        # Adicionar ponto do cenário target
        fig_volume_qualification.add_trace(
            go.Scatter(
                x=[target_total_leads],
                y=[target_results["total_cost"]],
                mode="markers",
                marker=dict(size=12, color="red", symbol="star"),
                name="Seu Cenário Atual",
            )
        )

        fig_volume_qualification.update_layout(
            xaxis_title="Quantidade de Leads Processados",
            yaxis_title="Custo Total (R$)",
            legend_title="Taxa de Qualificação",
            hovermode="x unified",
        )
        st.plotly_chart(fig_volume_qualification, use_container_width=True)

    # Gráfico 3: Custo Total vs. Quantidade de Leads (Variando Taxa de Avanço)
    with tab_book:
        # Variações de taxa de agendamento baseadas no target
        booking_step = 0.15  # 15 pontos percentuais
        booking_rate_variations = {}

        # Duas abaixo do target
        if target_booking_rate - 2 * booking_step >= 0:
            booking_rate_variations[
                f"-30pp ({(target_booking_rate - 2 * booking_step) * 100:.1f}%)"
            ] = target_booking_rate - 2 * booking_step
        if target_booking_rate - booking_step >= 0:
            booking_rate_variations[
                f"-15pp ({(target_booking_rate - booking_step) * 100:.1f}%)"
            ] = target_booking_rate - booking_step

        # Target
        booking_rate_variations[f"Target ({target_booking_rate * 100:.1f}%)"] = (
            target_booking_rate
        )

        # Duas acima do target
        if target_booking_rate + booking_step <= 1.0:
            booking_rate_variations[
                f"+15pp ({(target_booking_rate + booking_step) * 100:.1f}%)"
            ] = target_booking_rate + booking_step
        if target_booking_rate + 2 * booking_step <= 1.0:
            booking_rate_variations[
                f"+30pp ({(target_booking_rate + 2 * booking_step) * 100:.1f}%)"
            ] = target_booking_rate + 2 * booking_step

        fig_volume_booking = go.Figure()

        # Define colors for each scenario
        scenario_colors_booking = {
            0: GRAY_2,  # -30pp
            1: GRAY_1,  # -15pp
            2: BRAND_COLOR,  # Target
            3: LIGHT_BLUE_2,  # +15pp
            4: LIGHT_BLUE_1,  # +30pp
        }

        for idx, (scenario_name, book_rate) in enumerate(
            booking_rate_variations.items()
        ):
            costs = []
            scenario_rates = rates.copy()
            scenario_rates["booking"] = book_rate
            for volume in lead_volumes:
                sim_result = run_simulation(
                    volume,
                    scenario_rates,
                    pricing_tables,
                    minimum_billing,
                    ticket_medio,
                    taxa_conversao_vendas,
                    comissao_vendas,
                )
                costs.append(sim_result["total_cost"])

            is_target = "Target" in scenario_name
            fig_volume_booking.add_trace(
                go.Scatter(
                    x=lead_volumes,
                    y=costs,
                    mode="lines",
                    name=scenario_name,
                    line=dict(
                        width=4 if is_target else 2.5,
                        dash="solid" if is_target else "dot",
                        color=scenario_colors_booking.get(idx, BRAND_COLOR),
                    ),
                )
            )

        # Adicionar ponto do cenário target
        fig_volume_booking.add_trace(
            go.Scatter(
                x=[target_total_leads],
                y=[target_results["total_cost"]],
                mode="markers",
                marker=dict(size=12, color="red", symbol="star"),
                name="Seu Cenário Atual",
            )
        )

        fig_volume_booking.update_layout(
            xaxis_title="Quantidade de Leads Processados",
            yaxis_title="Custo Total (R$)",
            legend_title="Taxa de Avanço",
            hovermode="x unified",
        )
        st.plotly_chart(fig_volume_booking, use_container_width=True)

    # Separador visual
    st.divider()

    # Heatmap de Taxa de Qualificação vs Taxa de Avanço
    st.header("🔥 Matriz de Sensibilidade: Qualificação vs Avanço")
    st.markdown(
        """
        Visualize como diferentes combinações de taxas de qualificação e agendamento impactam o custo total.
        
        **📊 Referência POC:** Em um teste real, foram alcançados: **22,6% de qualificação** e **33,3% de agendamento**.  
        Os limites abaixo refletem cenários realistas baseados nesta performance.
        """
    )

    # Criar ranges para o heatmap (baseado em dados reais de POC)
    # POC: Qualificação 22.6%, Agendamento 33.3%
    qual_rates_heatmap = [i / 100.0 for i in range(0, 36, 5)]  # De 0% a 35%, passo 5%
    booking_rates_heatmap = [
        i / 100.0 for i in range(0, 51, 5)
    ]  # De 0% a 50%, passo 5%

    # Matriz para armazenar os custos
    cost_matrix = []
    cpa_matrix = []
    meetings_matrix = []

    for qual_rate in qual_rates_heatmap:
        cost_row = []
        cpa_row = []
        meetings_row = []
        for book_rate in booking_rates_heatmap:
            temp_rates = rates.copy()
            temp_rates["qualification"] = qual_rate
            temp_rates["booking"] = book_rate
            sim_result = run_simulation(
                target_total_leads,
                temp_rates,
                pricing_tables,
                minimum_billing,
                ticket_medio,
                taxa_conversao_vendas,
                comissao_vendas,
            )
            cost_row.append(sim_result["total_cost"])
            cpa_row.append(sim_result["cpa"] if sim_result["cpa"] > 0 else 0)
            meetings_row.append(sim_result["num_booked"])
        cost_matrix.append(cost_row)
        cpa_matrix.append(cpa_row)
        meetings_matrix.append(meetings_row)

    # Criar abas para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(
        ["Custo Total", "Custo por Reunião (CPA)", "Reuniões Agendadas"]
    )

    # Custom colorscale para os heatmaps
    custom_colorscale = [
        [0.0, BRAND_COLOR],  # Menor custo = azul da marca
        [0.5, LIGHT_BLUE_3],  # Médio = azul claro
        [1.0, GRAY_2],  # Maior custo = cinza
    ]

    with tab1:
        fig_heatmap_cost = go.Figure(
            data=go.Heatmap(
                z=cost_matrix,
                x=[f"{r * 100:.0f}%" for r in booking_rates_heatmap],
                y=[f"{q * 100:.0f}%" for q in qual_rates_heatmap],
                colorscale=custom_colorscale,
                text=[[f"R$ {val:,.0f}" for val in row] for row in cost_matrix],
                texttemplate="%{text}",
                textfont={"size": 9},
                colorbar=dict(title="Custo Total (R$)"),
                hovertemplate="Qualificação: %{y}<br>Agendamento: %{x}<br>Custo: R$ %{z:,.2f}<extra></extra>",
            )
        )

        # Adicionar marcador para o cenário target
        target_qual_idx = min(
            range(len(qual_rates_heatmap)),
            key=lambda i: abs(qual_rates_heatmap[i] - target_qualification_rate),
        )
        target_book_idx = min(
            range(len(booking_rates_heatmap)),
            key=lambda i: abs(booking_rates_heatmap[i] - target_booking_rate),
        )

        fig_heatmap_cost.add_trace(
            go.Scatter(
                x=[f"{booking_rates_heatmap[target_book_idx] * 100:.0f}%"],
                y=[f"{qual_rates_heatmap[target_qual_idx] * 100:.0f}%"],
                mode="markers",
                marker=dict(
                    size=20,
                    color=GRAY_4,
                    symbol="star",
                    line=dict(color="white", width=2),
                ),
                name="Seu Target",
                showlegend=True,
            )
        )

        fig_heatmap_cost.update_layout(
            title="Custo Total por Combinação de Taxas",
            xaxis_title="Taxa de Agendamento (% de Qualificados)",
            yaxis_title="Taxa de Qualificação (% de Respostas)",
            height=600,
        )
        st.plotly_chart(fig_heatmap_cost, use_container_width=True)

    with tab2:
        fig_heatmap_cpa = go.Figure(
            data=go.Heatmap(
                z=cpa_matrix,
                x=[f"{r * 100:.0f}%" for r in booking_rates_heatmap],
                y=[f"{q * 100:.0f}%" for q in qual_rates_heatmap],
                colorscale=custom_colorscale,
                text=[[f"R$ {val:,.0f}" for val in row] for row in cpa_matrix],
                texttemplate="%{text}",
                textfont={"size": 9},
                colorbar=dict(title="CPA (R$)"),
                hovertemplate="Qualificação: %{y}<br>Agendamento: %{x}<br>CPA: R$ %{z:,.2f}<extra></extra>",
            )
        )

        fig_heatmap_cpa.add_trace(
            go.Scatter(
                x=[f"{booking_rates_heatmap[target_book_idx] * 100:.0f}%"],
                y=[f"{qual_rates_heatmap[target_qual_idx] * 100:.0f}%"],
                mode="markers",
                marker=dict(
                    size=20,
                    color=GRAY_4,
                    symbol="star",
                    line=dict(color="white", width=2),
                ),
                name="Seu Target",
                showlegend=True,
            )
        )

        fig_heatmap_cpa.update_layout(
            title="Custo por Reunião (CPA) por Combinação de Taxas",
            xaxis_title="Taxa de Agendamento (% de Qualificados)",
            yaxis_title="Taxa de Qualificação (% de Respostas)",
            height=600,
        )
        st.plotly_chart(fig_heatmap_cpa, use_container_width=True)

    # Colorscale invertido para reuniões (mais = melhor)
    meetings_colorscale = [
        [0.0, GRAY_3],  # Menos reuniões = cinza claro
        [0.5, LIGHT_BLUE_2],  # Médio = azul claro
        [1.0, BRAND_COLOR],  # Mais reuniões = azul da marca
    ]

    with tab3:
        fig_heatmap_meetings = go.Figure(
            data=go.Heatmap(
                z=meetings_matrix,
                x=[f"{r * 100:.0f}%" for r in booking_rates_heatmap],
                y=[f"{q * 100:.0f}%" for q in qual_rates_heatmap],
                colorscale=meetings_colorscale,
                text=[[f"{int(val)}" for val in row] for row in meetings_matrix],
                texttemplate="%{text}",
                textfont={"size": 9},
                colorbar=dict(title="Reuniões"),
                hovertemplate="Qualificação: %{y}<br>Agendamento: %{x}<br>Reuniões: %{z:.0f}<extra></extra>",
            )
        )

        fig_heatmap_meetings.add_trace(
            go.Scatter(
                x=[f"{booking_rates_heatmap[target_book_idx] * 100:.0f}%"],
                y=[f"{qual_rates_heatmap[target_qual_idx] * 100:.0f}%"],
                mode="markers",
                marker=dict(
                    size=20,
                    color=GRAY_4,
                    symbol="star",
                    line=dict(color="white", width=2),
                ),
                name="Seu Target",
                showlegend=True,
            )
        )

        fig_heatmap_meetings.update_layout(
            title="Reuniões Agendadas por Combinação de Taxas",
            xaxis_title="Taxa de Agendamento (% de Qualificados)",
            yaxis_title="Taxa de Qualificação (% de Respostas)",
            height=600,
        )
        st.plotly_chart(fig_heatmap_meetings, use_container_width=True)

    # Insights adicionais
    st.subheader("💡 Insights da Matriz de Sensibilidade")
    col_ins1, col_ins2, col_ins3 = st.columns(3)

    # Encontrar o melhor e pior cenário
    flat_costs = [cost for row in cost_matrix for cost in row]
    flat_cpas = [cpa for row in cpa_matrix for cpa in row if cpa > 0]
    flat_meetings = [meeting for row in meetings_matrix for meeting in row]

    col_ins1.metric(
        "Custo Mínimo Possível",
        f"R$ {min(flat_costs):,.2f}",
        delta=f"{((min(flat_costs) - target_results['total_cost']) / target_results['total_cost'] * 100):.1f}% vs Target",
        delta_color="inverse",
    )

    col_ins2.metric(
        "Custo Máximo Possível",
        f"R$ {max(flat_costs):,.2f}",
        delta=f"{((max(flat_costs) - target_results['total_cost']) / target_results['total_cost'] * 100):.1f}% vs Target",
        delta_color="inverse",
    )

    col_ins3.metric(
        "Máximo de Reuniões Possível",
        f"{int(max(flat_meetings))}",
        delta=f"{int(max(flat_meetings) - target_results['num_booked'])} vs Target",
    )

else:
    st.info("Ajuste a quantidade de leads na barra lateral para iniciar a simulação.")
