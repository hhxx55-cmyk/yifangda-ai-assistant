# -*- coding: utf-8 -*-
"""
标的交收AI助手 - Streamlit演示界面
提供交互式的交收分析和可视化
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from settlement_ai.data_loader import SettlementDataLoader
from settlement_ai.ai_analyzer import SettlementAIAnalyzer


# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """初始化系统（缓存）"""
    loader = SettlementDataLoader()
    analyzer = SettlementAIAnalyzer()
    return loader, analyzer


@st.cache_data
def load_data(_loader):
    """加载数据（缓存）"""
    accounts, dates = _loader.scan_available_data()
    df = _loader.load_all_trades()
    return accounts, dates, df


def main():
    """主函数"""
    
    # 标题
    st.markdown('<div class="main-header">🔄 标的交收AI助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    loader, analyzer = initialize_system()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("# 🔄 交收助手")
        st.markdown("**标的交收智能系统**")
        st.markdown("---")
        st.markdown("### 📊 系统功能")
        
        page = st.radio(
            "选择功能模块",
            ["🏠 首页概览", "📊 匹配监控", "🔍 重复检测", "⏱️ 延迟预警", "💡 智能建议"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📌 数据选择")
        
        # 加载数据
        accounts, dates, df = load_data(loader)
        
        if df is not None and not df.empty:
            st.metric("总交易数", len(df))
            st.metric("账户数", len(accounts))
            st.metric("交易日期", len(dates))
        
        st.markdown("---")
        st.markdown("### ℹ️ 关于")
        st.info("**版本**: v1.0\n\n**更新**: 2024-12-26")
    
    # 主内容区
    if df is None or df.empty:
        st.error("未能加载交易数据，请检查数据路径配置")
        return
    
    if page == "🏠 首页概览":
        show_home_page(df, analyzer, accounts, dates)
    
    elif page == "📊 匹配监控":
        show_match_monitoring_page(df, analyzer)
    
    elif page == "🔍 重复检测":
        show_duplicate_detection_page(df, analyzer)
    
    elif page == "⏱️ 延迟预警":
        show_delay_prediction_page(df, analyzer)
    
    elif page == "💡 智能建议":
        show_recommendations_page(df, analyzer)


def show_home_page(df, analyzer, accounts, dates):
    """显示首页"""
    
    st.markdown("## 📊 系统概览")
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="总交易数",
            value=len(df),
            delta=f"{len(accounts)} 个账户"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        matched = (df['Matched?'] == 'Y').sum()
        match_rate = (matched / len(df) * 100) if len(df) > 0 else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="匹配率",
            value=f"{match_rate:.1f}%",
            delta=f"{matched} 已匹配"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        duplicated = (df['Duplicated?'] == 'Y').sum()
        dup_rate = (duplicated / len(df) * 100) if len(df) > 0 else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="重复率",
            value=f"{dup_rate:.1f}%",
            delta=f"{duplicated} 条重复"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="交易日期",
            value=len(dates),
            delta=f"{dates[0]} - {dates[-1]}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 图表展示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 匹配状态分布")
        # 计算已匹配和未匹配的数量
        matched_count = (df['Matched?'] == 'Y').sum()
        unmatched_count = len(df) - matched_count
        
        # 创建饼图数据
        match_data = pd.DataFrame({
            '状态': ['已匹配', '未匹配'],
            '数量': [matched_count, unmatched_count]
        })
        
        fig = px.pie(
            match_data,
            values='数量',
            names='状态',
            title="匹配状态占比",
            color='状态',
            color_discrete_map={'已匹配': '#2ecc71', '未匹配': '#e74c3c'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 交易类型分布")
        if 'Blotter Transaction Type' in df.columns:
            type_dist = df['Blotter Transaction Type'].value_counts().head(10)
            fig = px.bar(
                x=type_dist.index,
                y=type_dist.values,
                title="Top 10 交易类型",
                labels={'x': '交易类型', 'y': '数量'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少'Blotter Transaction Type'列")
    
    # 账户统计
    st.markdown("### 📈 账户交易统计")
    account_stats = df.groupby('Account').agg({
        'Matched?': lambda x: (x == 'Y').sum(),
        'Duplicated?': lambda x: (x == 'Y').sum()
    }).reset_index()
    account_stats['交易数'] = df.groupby('Account').size().values
    account_stats.columns = ['账户', '已匹配', '重复数', '交易数']
    account_stats = account_stats[['账户', '交易数', '已匹配', '重复数']]
    account_stats['匹配率%'] = (account_stats['已匹配'] / account_stats['交易数'] * 100).round(2)
    account_stats = account_stats.sort_values('交易数', ascending=False).head(10)
    
    st.dataframe(account_stats, use_container_width=True)
    
    # 日期趋势
    st.markdown("### 📅 日期趋势分析")
    date_stats = df.groupby('Date').agg({
        'Matched?': lambda x: (x == 'Y').sum()
    }).reset_index()
    date_stats['交易数'] = df.groupby('Date').size().values
    date_stats.columns = ['日期', '已匹配', '交易数']
    date_stats = date_stats[['日期', '交易数', '已匹配']]
    date_stats['匹配率'] = (date_stats['已匹配'] / date_stats['交易数'] * 100).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=date_stats['日期'],
        y=date_stats['交易数'],
        name='交易数',
        yaxis='y'
    ))
    fig.add_trace(go.Scatter(
        x=date_stats['日期'],
        y=date_stats['匹配率'],
        name='匹配率(%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title="每日交易数与匹配率",
        xaxis_title="日期",
        yaxis_title="交易数",
        yaxis2=dict(title="匹配率(%)", overlaying='y', side='right'),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)


def show_match_monitoring_page(df, analyzer):
    """显示匹配监控页面"""
    
    st.markdown("## 📊 交易匹配监控")
    
    # 分析匹配状态
    with st.spinner("正在分析匹配状态..."):
        match_results = analyzer.analyze_match_status(df)
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总交易数", match_results['total'])
    with col2:
        st.metric("已匹配", match_results['matched'], 
                 delta=f"{match_results['match_rate']:.1f}%")
    with col3:
        st.metric("未匹配", match_results['unmatched'],
                 delta=f"{100-match_results['match_rate']:.1f}%",
                 delta_color="inverse")
    with col4:
        status = "优秀" if match_results['match_rate'] >= 95 else "良好" if match_results['match_rate'] >= 90 else "需改进"
        st.metric("匹配状态", status)
    
    st.markdown("---")
    
    # 详细分析
    tab1, tab2, tab3 = st.tabs(["📊 按账户统计", "📅 按日期统计", "🔍 未匹配详情"])
    
    with tab1:
        st.markdown("#### 各账户匹配情况")
        account_stats = match_results['account_stats']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=account_stats['Account'],
            y=account_stats['Total'],
            name='总交易',
            marker_color='lightblue'
        ))
        fig.add_trace(go.Bar(
            x=account_stats['Account'],
            y=account_stats['Matched'],
            name='已匹配',
            marker_color='green'
        ))
        fig.update_layout(
            title="各账户交易匹配情况",
            xaxis_title="账户",
            yaxis_title="交易数",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(account_stats, use_container_width=True)
    
    with tab2:
        st.markdown("#### 各日期匹配情况")
        date_stats = match_results['date_stats']
        
        fig = px.line(
            date_stats,
            x='Date',
            y='Match_Rate',
            title="匹配率趋势",
            markers=True
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", 
                     annotation_text="目标: 95%")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(date_stats, use_container_width=True)
    
    with tab3:
        st.markdown("#### 未匹配交易详情")
        unmatched = match_results['unmatched_trades']
        
        if len(unmatched) > 0:
            st.warning(f"发现 {len(unmatched)} 条未匹配交易")
            
            # 显示前20条
            display_cols = ['Account', 'Date']
            optional_cols = ['Ticket Number', 'Security', 'Blotter Transaction Type', 'Amount (Pennies)', 'Currency']
            for col in optional_cols:
                if col in unmatched.columns:
                    display_cols.append(col)
            display_df = unmatched[display_cols].head(20)
            st.dataframe(display_df, use_container_width=True)
            
            # 下载按钮
            csv = unmatched.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载未匹配交易CSV",
                data=csv,
                file_name=f"unmatched_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ 所有交易均已匹配！")


def show_duplicate_detection_page(df, analyzer):
    """显示重复检测页面"""
    
    st.markdown("## 🔍 重复交易检测")
    
    # 分析重复情况
    with st.spinner("正在检测重复交易..."):
        dup_results = analyzer.detect_duplicates(df)
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总交易数", dup_results['total'])
    with col2:
        st.metric("标记重复", dup_results['marked_duplicates'],
                 delta=f"{dup_results['duplicate_rate']:.1f}%")
    with col3:
        st.metric("AI检测", dup_results['ai_detected'])
    with col4:
        status = "优秀" if dup_results['duplicate_rate'] < 2 else "良好" if dup_results['duplicate_rate'] < 5 else "需改进"
        st.metric("重复控制", status)
    
    st.markdown("---")
    
    # 详细分析
    tab1, tab2 = st.tabs(["📋 重复交易列表", "🤖 AI检测结果"])
    
    with tab1:
        st.markdown("#### 已标记的重复交易")
        dup_trades = dup_results['duplicate_trades']
        
        if len(dup_trades) > 0:
            st.warning(f"发现 {len(dup_trades)} 条重复交易")
            
            display_cols = ['Account', 'Date']
            optional_cols = ['Ticket Number', 'Security', 'Trade Date', 'As of Date', 'Amount (Pennies)']
            for col in optional_cols:
                if col in dup_trades.columns:
                    display_cols.append(col)
            display_df = dup_trades[display_cols].head(20)
            st.dataframe(display_df, use_container_width=True)
            
            # 下载按钮
            csv = dup_trades.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载重复交易CSV",
                data=csv,
                file_name=f"duplicate_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ 未发现重复交易！")
    
    with tab2:
        st.markdown("#### AI聚类检测结果")
        dup_groups = dup_results['duplicate_groups']
        
        if dup_groups:
            st.info(f"AI检测到 {len(dup_groups)} 个可疑重复组")
            
            for i, group in enumerate(dup_groups[:10], 1):
                with st.expander(f"重复组 {i}: {group['account']} ({group['count']} 条交易)"):
                    group_trades = df.loc[group['indices']]
                    st.dataframe(group_trades[display_cols], use_container_width=True)
        else:
            st.success("✅ AI未检测到可疑重复模式！")


def show_delay_prediction_page(df, analyzer):
    """显示延迟预警页面"""
    
    st.markdown("## ⏱️ 交收延迟预警")
    
    # 分析延迟情况
    with st.spinner("正在分析交收时长..."):
        delay_results = analyzer.predict_settlement_delay(df)
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总交易数", delay_results['total'])
    with col2:
        st.metric("延迟交易", delay_results['delayed_count'],
                 delta=f"{delay_results['delay_rate']:.1f}%")
    with col3:
        st.metric("平均交收天数", f"{delay_results['avg_settlement_days']:.1f}天")
    with col4:
        st.metric("最长交收天数", f"{delay_results['max_settlement_days']:.0f}天")
    
    st.markdown("---")
    
    # 详细分析
    tab1, tab2 = st.tabs(["📊 延迟统计", "🔍 延迟详情"])
    
    with tab1:
        st.markdown("#### 各交易类型交收时长")
        type_stats = delay_results['type_delay_stats']
        
        if not type_stats.empty:
            st.dataframe(type_stats, use_container_width=True)
    
    with tab2:
        st.markdown("#### 延迟交易详情（>3天）")
        delayed = delay_results['delayed_trades']
        
        if len(delayed) > 0:
            st.warning(f"发现 {len(delayed)} 条延迟交易")
            
            display_cols = ['Account', 'Date']
            optional_cols = ['Ticket Number', 'Security', 'Trade Date', 'Settlement Date', 'Settlement_Days']
            for col in optional_cols:
                if col in delayed.columns:
                    display_cols.append(col)
            display_df = delayed[display_cols].head(20)
            st.dataframe(display_df, use_container_width=True)
            
            # 下载按钮
            csv = delayed.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载延迟交易CSV",
                data=csv,
                file_name=f"delayed_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ 所有交易均按时交收！")


def show_recommendations_page(df, analyzer):
    """显示智能建议页面"""
    
    st.markdown("## 💡 智能决策建议")
    
    # 综合分析
    with st.spinner("正在进行综合分析..."):
        analysis_results = analyzer.comprehensive_analysis(df)
    
    recommendations = analysis_results['recommendations']
    
    if recommendations:
        st.info(f"基于AI分析，生成 {len(recommendations)} 条优化建议")
        
        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                'High': 'danger',
                'Medium': 'warning',
                'Low': 'success'
            }
            
            color_class = priority_color.get(rec['priority'], 'warning')
            
            st.markdown(f"### 建议 {i}: {rec['category']}")
            st.markdown(f'<div class="{color_class}-box">', unsafe_allow_html=True)
            st.markdown(f"**优先级**: {rec['priority']}")
            st.markdown(f"**问题**: {rec['issue']}")
            st.markdown(f"**建议**: {rec['recommendation']}")
            st.markdown(f"**预期改进**: {rec['expected_improvement']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("✅ 系统运行良好，暂无优化建议！")
    
    # 显示详细统计
    st.markdown("---")
    st.markdown("## 📊 详细统计数据")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 匹配统计")
        match_stats = analysis_results['match_status']
        st.metric("匹配率", f"{match_stats['match_rate']:.1f}%")
        st.metric("已匹配", match_stats['matched'])
        st.metric("未匹配", match_stats['unmatched'])
    
    with col2:
        st.markdown("### 质量统计")
        dup_stats = analysis_results['duplicate_detection']
        delay_stats = analysis_results['delay_prediction']
        st.metric("重复率", f"{dup_stats['duplicate_rate']:.1f}%")
        st.metric("延迟率", f"{delay_stats['delay_rate']:.1f}%")
        st.metric("平均交收天数", f"{delay_stats['avg_settlement_days']:.1f}天")


if __name__ == '__main__':
    main()