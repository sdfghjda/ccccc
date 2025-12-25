import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# 设置页面标题
st.set_page_config(page_title="企业数字化转型指数查询系统", layout="wide")

# 应用标题
st.title("企业数字化转型指数查询系统")

# 读取数据
@st.cache_data

def load_data():
    file_path = '两版合并后的年报数据_完整版.xlsx'
    df = pd.read_excel(file_path)
    # 将股票代码格式化为6位字符串
    df['股票代码'] = df['股票代码'].astype(str).str.zfill(6)
    return df

# 加载数据
df = load_data()

# 创建左侧查询面板
with st.sidebar:
    st.header("查询面板")
    st.write("请选择以下参数进行查询")
    
    # 股票代码查询
    stock_codes = sorted(df['股票代码'].unique())
    selected_stock = st.selectbox("股票代码", stock_codes)
    
    # 年份查询
    min_year = int(df['年份'].min())
    max_year = int(df['年份'].max())
    selected_year = st.selectbox("年份", sorted(df['年份'].unique()))
    
    # 查询按钮
    if st.button("查询"):
        st.session_state['query_executed'] = True

# 确保会话状态存在
if 'query_executed' not in st.session_state:
    st.session_state['query_executed'] = False

# 过滤数据
filtered_data = df[(df['股票代码'] == selected_stock)]
selected_year_data = df[(df['股票代码'] == selected_stock) & (df['年份'] == selected_year)]

# 按照年份排序
filtered_data = filtered_data.sort_values('年份')

# 获取企业名称
company_name = filtered_data['企业名称'].iloc[0] if not filtered_data.empty else "未知企业"

# 第一部分：统计概览
st.header("统计概览")

# 创建统计卡片
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("总记录数", len(df))

with col2:
    st.metric("企业数量", df['股票代码'].nunique())

with col3:
    st.metric("年份范围", f"{int(df['年份'].min())}-{int(df['年份'].max())}")

with col4:
    avg_index = df['数字化转型指数'].mean()
    st.metric("平均指数", f"{avg_index:.2f}")

with col5:
    max_index = df['数字化转型指数'].max()
    st.metric("最高指数", f"{max_index:.2f}")

with col6:
    min_index = df['数字化转型指数'].min()
    st.metric("最低指数", f"{min_index:.2f}")

# 第二部分：数据概览
st.header("数据概览")

# 显示数据预览
st.subheader("数据预览")
st.dataframe(df.sample(10), use_container_width=True)



# 第四部分：数字化转型指数详细统计
st.header("数字化转型指数详细统计")

# 计算详细统计信息
detailed_stats = {
    "平均值": filtered_data['数字化转型指数'].mean(),
    "中位数": filtered_data['数字化转型指数'].median(),
    "最大值": filtered_data['数字化转型指数'].max(),
    "最小值": filtered_data['数字化转型指数'].min(),
    "标准差": filtered_data['数字化转型指数'].std(),
    "25%分位数": filtered_data['数字化转型指数'].quantile(0.25),
    "75%分位数": filtered_data['数字化转型指数'].quantile(0.75)
}

# 显示详细统计
col1, col2, col3, col4 = st.columns(4)

for i, (key, value) in enumerate(detailed_stats.items()):
    if i % 4 == 0:
        with col1:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")
    elif i % 4 == 1:
        with col2:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")
    elif i % 4 == 2:
        with col3:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")
    else:
        with col4:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")

# 第五部分：数字化转型指数折线图
st.header("数字化转型指数趋势")

if not filtered_data.empty:
    # 创建多指标折线图
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 添加数字化转型指数
    fig_line.add_trace(
        go.Scatter(x=filtered_data['年份'], y=filtered_data['数字化转型指数'], 
                  name="数字化转型指数", line=dict(color="#1f77b4", width=3)),
        secondary_y=False,
    )
    
    # 添加技术维度
    fig_line.add_trace(
        go.Scatter(x=filtered_data['年份'], y=filtered_data['技术维度'], 
                  name="技术维度", line=dict(color="#ff7f0e", width=2, dash="dash")),
        secondary_y=False,
    )
    
    # 添加应用维度
    fig_line.add_trace(
        go.Scatter(x=filtered_data['年份'], y=filtered_data['应用维度'], 
                  name="应用维度", line=dict(color="#2ca02c", width=2, dash="dot")),
        secondary_y=False,
    )
    
    # 为选中的年份添加特殊标识
    try:
        # 检查选中年份是否在数据中
        if not selected_year_data.empty:
            # 获取选中年份的数据
            selected_year_index = float(selected_year_data['数字化转型指数'].iloc[0])
            selected_year_tech = float(selected_year_data['技术维度'].iloc[0])
            selected_year_app = float(selected_year_data['应用维度'].iloc[0])
            
            # 添加选中年份的特殊标记（数字化转型指数）
            fig_line.add_trace(
                go.Scatter(
                    x=[int(selected_year)], 
                    y=[selected_year_index],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color='red',
                        symbol='star',
                        line=dict(width=3, color='darkred')
                    ),
                    text=[f'{int(selected_year)}'],
                    textposition='top center',
                    name=f'选中年份 {int(selected_year)}',
                    showlegend=True,
                    hovertemplate=f'<b>选中年份 {int(selected_year)}</b><br>' +
                                 f'数字化转型指数: {selected_year_index}<br>' +
                                 '<extra></extra>'
                ),
                secondary_y=False,
            )
            
            # 添加选中年份的技术维度标记
            fig_line.add_trace(
                go.Scatter(
                    x=[int(selected_year)], 
                    y=[selected_year_tech],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='orange',
                        symbol='diamond',
                        line=dict(width=2, color='darkorange')
                    ),
                    name=f'{int(selected_year)} 技术维度',
                    showlegend=False,
                    hovertemplate=f'<b>选中年份 {int(selected_year)}</b><br>' +
                                 f'技术维度: {selected_year_tech}<br>' +
                                 '<extra></extra>'
                ),
                secondary_y=False,
            )
            
            # 添加选中年份的应用维度标记
            fig_line.add_trace(
                go.Scatter(
                    x=[int(selected_year)], 
                    y=[selected_year_app],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='green',
                        symbol='square',
                        line=dict(width=2, color='darkgreen')
                    ),
                    name=f'{int(selected_year)} 应用维度',
                    showlegend=False,
                    hovertemplate=f'<b>选中年份 {int(selected_year)}</b><br>' +
                                 f'应用维度: {selected_year_app}<br>' +
                                 '<extra></extra>'
                ),
                secondary_y=False,
            )
        else:
            # 如果选中年份没有数据，也要显示标识
            fig_line.add_trace(
                go.Scatter(
                    x=[int(selected_year)], 
                    y=[0],
                    mode='markers+text',
                    marker=dict(
                        size=15,
                        color='red',
                        symbol='star',
                        line=dict(width=3, color='darkred')
                    ),
                    text=[f'{int(selected_year)}'],
                    textposition='top center',
                    name=f'选中年份 {int(selected_year)} (无数据)',
                    showlegend=True,
                    hovertemplate=f'<b>选中年份 {int(selected_year)}</b><br>' +
                                 '该年份无数据<br>' +
                                 '<extra></extra>'
                ),
                secondary_y=False,
            )
    except Exception as e:
        # 如果添加标识失败，至少显示基本信息
        st.warning(f"年份标识显示异常: {str(e)}")
    
    # 更新布局
    fig_line.update_layout(
        title=f"{company_name} ({selected_stock}) 数字化转型指数趋势 - 选中年份: {int(selected_year)}",
        xaxis_title="年份",
        yaxis_title="指数值",
        legend_title="指标类型",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.write("没有找到相关数据")

