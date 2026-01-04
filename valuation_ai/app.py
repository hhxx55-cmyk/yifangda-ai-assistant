"""
估值核对AI助手 - Streamlit演示界面
提供交互式的估值差异分析和可视化
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

from data_generator import ValuationDataGenerator
from ai_analyzer import ValuationAIAnalyzer

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
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
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
    generator = ValuationDataGenerator(seed=42)
    analyzer = ValuationAIAnalyzer()
    return generator, analyzer


@st.cache_data
def load_data():
    """加载数据（缓存）"""
    generator, _ = initialize_system()
    
    # 生成数据
    df_diff = generator.generate_valuation_differences(n_records=100)
    df_cases = generator.generate_historical_cases(n_cases=50)
    df_rules = generator.generate_valuation_rules()
    
    return df_diff, df_cases, df_rules


def main():
    """主函数"""
    
    # 标题
    st.markdown('<div class="main-header">🤖 估值核对AI助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    generator, analyzer = initialize_system()
    
    # 侧边栏
    with st.sidebar:
        # 使用文本标题代替图片
        st.markdown("# 🤖 AI助手")
        st.markdown("**估值核对智能系统**")
        st.markdown("---")
        st.markdown("### 📊 系统功能")
        
        page = st.radio(
            "选择功能模块",
            ["🏠 首页概览", "📈 数据分析", "🔍 智能诊断", "📋 历史案例", "⚙️ 系统设置"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📌 快速统计")
        
        # 加载数据
        df_diff, df_cases, df_rules = load_data()
        
        st.metric("总差异记录", len(df_diff))
        st.metric("待处理差异", len(df_diff[df_diff['status'] == 'Pending']))
        st.metric("历史案例", len(df_cases))
        
        st.markdown("---")
        st.markdown("### ℹ️ 关于")
        st.info("**版本**: v1.0\n\n**作者**: Kilo Code\n\n**更新**: 2024-12-22")
    
    # 主内容区
    if page == "🏠 首页概览":
        show_home_page(df_diff, df_cases, df_rules)
    
    elif page == "📈 数据分析":
        show_data_analysis_page(df_diff, df_cases)
    
    elif page == "🔍 智能诊断":
        show_ai_diagnosis_page(df_diff, df_cases, df_rules, analyzer)
    
    elif page == "📋 历史案例":
        show_historical_cases_page(df_cases)
    
    elif page == "⚙️ 系统设置":
        show_settings_page(df_rules)


def show_home_page(df_diff, df_cases, df_rules):
    """显示首页"""
    
    st.markdown("## 📊 系统概览")
    
    # 关键指标 - 删除匹配率，改为3列均匀排布
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="总差异数",
            value=len(df_diff),
            delta=f"{len(df_diff[df_diff['status'] == 'Pending'])} 待处理"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        avg_diff = df_diff['difference'].abs().mean()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="平均差异金额",
            value=f"${avg_diff:,.2f}",
            delta=f"{df_diff['difference_pct'].abs().mean():.3f}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="历史案例",
            value=len(df_cases),
            delta=f"平均 {df_cases['resolution_time'].mean():.0f} 分钟"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 图表展示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 差异金额分布")
        fig = px.histogram(
            df_diff,
            x='difference',
            nbins=30,
            title="差异金额分布图",
            labels={'difference': '差异金额', 'count': '数量'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 资产类别分布")
        asset_dist = df_diff['asset_class'].value_counts()
        fig = px.pie(
            values=asset_dist.values,
            names=asset_dist.index,
            title="资产类别占比"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 基金分布
    st.markdown("### 📈 基金差异统计")
    fund_stats = df_diff.groupby('fund_code').agg({
        'difference': ['count', 'mean', 'sum']
    }).round(2)
    fund_stats.columns = ['差异数量', '平均差异', '总差异']
    fund_stats = fund_stats.sort_values('差异数量', ascending=False)
    
    fig = go.Figure(data=[
        go.Bar(name='差异数量', x=fund_stats.index, y=fund_stats['差异数量']),
    ])
    fig.update_layout(title="各基金差异数量", xaxis_title="基金代码", yaxis_title="数量")
    st.plotly_chart(fig, use_container_width=True)
    
    # 最新差异
    st.markdown("### 🔔 最新待处理差异")
    pending_diff = df_diff[df_diff['status'] == 'Pending'].head(10)
    
    if len(pending_diff) > 0:
        display_df = pending_diff[[
            'id', 'fund_code', 'security_name', 'difference', 
            'difference_pct', 'asset_class'
        ]].copy()
        display_df.columns = ['ID', '基金', '证券', '差异金额', '差异比例(%)', '资产类别']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.success("✅ 暂无待处理差异")


def show_data_analysis_page(df_diff, df_cases):
    """显示数据分析页面"""
    
    st.markdown("## 📈 数据分析")
    
    # 筛选器
    st.markdown("### 🔍 数据筛选")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_funds = st.multiselect(
            "选择基金",
            options=df_diff['fund_code'].unique(),
            default=df_diff['fund_code'].unique()[:3]
        )
    
    with col2:
        selected_assets = st.multiselect(
            "选择资产类别",
            options=df_diff['asset_class'].unique(),
            default=df_diff['asset_class'].unique()
        )
    
    with col3:
        selected_status = st.multiselect(
            "选择状态",
            options=df_diff['status'].unique(),
            default=df_diff['status'].unique()
        )
    
    # 筛选数据
    filtered_df = df_diff[
        (df_diff['fund_code'].isin(selected_funds)) &
        (df_diff['asset_class'].isin(selected_assets)) &
        (df_diff['status'].isin(selected_status))
    ]
    
    st.info(f"📊 筛选后共 {len(filtered_df)} 条记录")
    
    # 详细分析
    tab1, tab2, tab3 = st.tabs(["📊 统计分析", "📈 趋势分析", "🔍 详细数据"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 差异金额统计")
            st.write(filtered_df['difference'].describe())
            
            # 箱线图
            fig = px.box(
                filtered_df,
                y='difference',
                x='asset_class',
                title="各资产类别差异分布",
                labels={'difference': '差异金额', 'asset_class': '资产类别'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 差异比例统计")
            st.write(filtered_df['difference_pct'].describe())
            
            # 散点图
            # 使用绝对值作为size，避免负值错误
            filtered_df_plot = filtered_df.copy()
            filtered_df_plot['abs_diff_pct'] = filtered_df_plot['difference_pct'].abs()
            
            fig = px.scatter(
                filtered_df_plot,
                x='custodian_value',
                y='difference',
                color='asset_class',
                size='abs_diff_pct',
                title="估值金额 vs 差异金额",
                labels={
                    'custodian_value': '托管行估值',
                    'difference': '差异金额',
                    'asset_class': '资产类别'
                },
                hover_data=['difference_pct']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("#### 历史案例解决时长趋势")
        
        # 按日期统计
        cases_by_date = df_cases.groupby('date').agg({
            'resolution_time': 'mean',
            'case_id': 'count'
        }).reset_index()
        cases_by_date.columns = ['date', 'avg_time', 'count']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cases_by_date['date'],
            y=cases_by_date['avg_time'],
            mode='lines+markers',
            name='平均解决时长',
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            x=cases_by_date['date'],
            y=cases_by_date['count'],
            name='案例数量',
            yaxis='y2',
            opacity=0.3
        ))
        
        fig.update_layout(
            title="历史案例趋势分析",
            xaxis_title="日期",
            yaxis_title="平均解决时长(分钟)",
            yaxis2=dict(title="案例数量", overlaying='y', side='right'),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("#### 详细数据表")
        st.dataframe(filtered_df, use_container_width=True)
        
        # 下载按钮
        csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载CSV",
            data=csv,
            file_name=f"valuation_diff_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def show_ai_diagnosis_page(df_diff, df_cases, df_rules, analyzer):
    """显示AI诊断页面"""
    
    st.markdown("## 🔍 智能诊断")
    
    # 加载历史数据到分析器
    if 'analyzer_loaded' not in st.session_state:
        with st.spinner("正在加载AI模型..."):
            analyzer.load_historical_data(df_cases, df_rules)
            st.session_state.analyzer_loaded = True
        st.success("✅ AI模型加载完成")
    
    # 选择分析模式
    mode = st.radio(
        "选择分析模式",
        ["单条记录分析", "批量分析"],
        horizontal=True
    )
    
    if mode == "单条记录分析":
        show_single_analysis(df_diff, analyzer)
    else:
        show_batch_analysis(df_diff, analyzer)


def show_single_analysis(df_diff, analyzer):
    """单条记录分析"""
    
    st.markdown("### 📝 选择要分析的差异记录")
    
    # 只显示有差异的记录
    diff_records = df_diff[df_diff['status'] != 'Matched']
    
    if len(diff_records) == 0:
        st.info("暂无待分析的差异记录")
        return
    
    # 选择记录
    selected_id = st.selectbox(
        "选择记录ID",
        options=diff_records['id'].tolist(),
        format_func=lambda x: f"{x} - {diff_records[diff_records['id']==x]['fund_code'].values[0]} - {diff_records[diff_records['id']==x]['security_name'].values[0]}"
    )
    
    if st.button("🚀 开始分析", type="primary"):
        record = diff_records[diff_records['id'] == selected_id].iloc[0]
        
        with st.spinner("AI正在分析中..."):
            result = analyzer.analyze_difference(record)
        
        # 显示分析结果
        st.markdown("---")
        st.markdown("### 📊 分析结果")
        
        # 基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("差异金额", f"${result['difference_amount']:,.2f}")
        with col2:
            st.metric("差异比例", f"{result['difference_pct']:.3f}%")
        with col3:
            urgency_color = {
                'High': '🔴',
                'Medium': '🟡',
                'Low': '🟢'
            }
            st.metric("紧急程度", f"{urgency_color[result['urgency_level']]} {result['urgency_level']}")
        
        # 异常检测
        st.markdown("#### 🎯 异常检测")
        if result['is_anomaly']:
            st.markdown('<div class="danger-box">⚠️ <b>检测到异常差异</b><br>异常评分: {:.2f}/10</div>'.format(
                result['anomaly_score']), unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ <b>正常差异范围</b><br>异常评分: {:.2f}/10</div>'.format(
                result['anomaly_score']), unsafe_allow_html=True)
        
        # 根因分析
        st.markdown("#### 🔬 根因分析")
        
        # 显示差异分解
        if 'field_decomposition' in result and result['field_decomposition']:
            st.markdown("**📊 差异分解详情**:")
            decomp = result['field_decomposition']
            
            # 创建三列显示差异分解
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**价格差异**")
                if decomp['has_price_diff']:
                    st.write(f"• 托管行价格: ${record['price_custodian']:.4f}")
                    st.write(f"• 内部价格: ${record['price_internal']:.4f}")
                    st.write(f"• 差异: ${decomp['price_diff']:.4f}")
                    st.write(f"• 贡献金额: ${decomp['price_contribution']:,.2f}")
                    st.write(f"• 贡献占比: **{decomp['price_contribution_pct']:.1f}%**")
                else:
                    st.write("✓ 无价格差异")
            
            with col2:
                st.markdown("**汇率差异**")
                if decomp['has_fx_diff']:
                    st.write(f"• 托管行汇率: {record['fx_rate_custodian']:.4f}")
                    st.write(f"• 内部汇率: {record['fx_rate_internal']:.4f}")
                    st.write(f"• 差异: {decomp['fx_diff']:.4f}")
                    st.write(f"• 贡献金额: ${decomp['fx_contribution']:,.2f}")
                    st.write(f"• 贡献占比: **{decomp['fx_contribution_pct']:.1f}%**")
                else:
                    st.write("✓ 无汇率差异")
            
            with col3:
                st.markdown("**应计利息差异**")
                if decomp['has_accrued_diff']:
                    st.write(f"• 托管行利息: ${record['accrued_interest_custodian']:,.2f}")
                    st.write(f"• 内部利息: ${record['accrued_interest_internal']:,.2f}")
                    st.write(f"• 差异: ${decomp['accrued_diff']:,.2f}")
                    st.write(f"• 贡献金额: ${decomp['accrued_contribution']:,.2f}")
                    st.write(f"• 贡献占比: **{decomp['accrued_contribution_pct']:.1f}%**")
                else:
                    st.write("✓ 无利息差异")
            
            st.markdown("---")
        
        st.info(f"**AI预测类型**: {result['predicted_type']} (置信度: {result['confidence']:.1%})")
        
        if result['root_causes']:
            st.markdown("**可能的根本原因**:")
            for i, cause in enumerate(result['root_causes'], 1):
                st.write(f"{i}. {cause['cause']} (出现频率: {cause['frequency']}次, 置信度: {cause['confidence']:.1%})")
        
        # 相似案例
        st.markdown("#### 📚 相似历史案例")
        if result['similar_cases']:
            for i, case in enumerate(result['similar_cases'][:3], 1):
                with st.expander(f"案例 {i}: {case['case_id']} (相似度: {case['similarity']:.1%})"):
                    st.write(f"**日期**: {case['date']}")
                    st.write(f"**差异类型**: {case['difference_type']}")
                    st.write(f"**根本原因**: {case['root_cause']}")
                    st.write(f"**解决方案**: {case['resolution']}")
                    st.write(f"**解决时长**: {case['resolution_time']} 分钟")
        else:
            st.write("暂无相似案例")
        
        # 推荐解决方案
        st.markdown("#### 💡 推荐解决方案")
        if result['recommended_solutions']:
            for i, sol in enumerate(result['recommended_solutions'], 1):
                st.markdown(f"""
                **方案 {i}**: {sol['solution']}
                - 来源: {sol['source']}
                - 成功率: {sol['success_rate']:.1%}
                - 预计时长: {sol['avg_time']} 分钟
                """)
        
        # 预估时长
        st.markdown("#### ⏱️ 预估解决时长")
        st.metric("预计需要", f"{result['estimated_resolution_time']} 分钟")


def show_batch_analysis(df_diff, analyzer):
    """批量分析"""
    
    st.markdown("### 📊 批量分析")
    
    # 只分析有差异的记录
    diff_records = df_diff[df_diff['status'] != 'Matched']
    
    # 添加全选功能
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("#### 选择要分析的差异记录")
    with col2:
        select_all = st.checkbox("一键全选", value=False)
    
    # 创建可选择的记录列表
    if 'selected_records' not in st.session_state:
        st.session_state.selected_records = []
    
    # 如果点击全选，更新选中状态
    if select_all:
        st.session_state.selected_records = diff_records['id'].tolist()
    
    # 显示可选择的记录
    selected_ids = st.multiselect(
        "选择记录（可多选）",
        options=diff_records['id'].tolist(),
        default=st.session_state.selected_records if select_all else [],
        format_func=lambda x: f"{x} - {diff_records[diff_records['id']==x]['fund_code'].values[0]} - {diff_records[diff_records['id']==x]['security_name'].values[0]} (差异: ${diff_records[diff_records['id']==x]['difference'].values[0]:,.2f})"
    )
    
    st.session_state.selected_records = selected_ids
    
    st.info(f"已选择 {len(selected_ids)} 条记录进行分析")
    
    if len(selected_ids) == 0:
        st.warning("⚠️ 请至少选择一条记录进行分析")
        return
    
    if st.button("🚀 开始批量分析", type="primary"):
        # 只分析选中的记录
        selected_diff_records = diff_records[diff_records['id'].isin(selected_ids)]
        
        with st.spinner("AI正在批量分析中..."):
            results = analyzer.batch_analyze(selected_diff_records)
            report = analyzer.generate_analysis_report(results)
        
        st.success("✅ 批量分析完成")
        
        # 显示统计报告
        st.markdown("### 📈 分析报告")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总差异数", report['总差异数'])
        with col2:
            st.metric("异常差异数", report['异常差异数'])
        with col3:
            st.metric("平均置信度", f"{report['平均置信度']:.1%}")
        with col4:
            st.metric("平均解决时长", f"{report['平均预估解决时长']:.0f}分钟")
        
        # 差异类型分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 差异类型分布")
            fig = px.pie(
                values=list(report['差异类型分布'].values()),
                names=list(report['差异类型分布'].keys()),
                title="差异类型占比"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 紧急程度分布")
            fig = px.bar(
                x=list(report['紧急程度分布'].keys()),
                y=list(report['紧急程度分布'].values()),
                title="紧急程度统计",
                labels={'x': '紧急程度', 'y': '数量'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 详细结果
        st.markdown("### 📋 详细分析结果")
        
        # 处理结果数据，将复杂对象转换为字符串
        display_results = []
        for r in results:
            display_r = {
                'record_id': r['record_id'],
                'fund_code': r['fund_code'],
                'security_code': r['security_code'],
                'difference_amount': f"${r['difference_amount']:,.2f}",
                'difference_pct': f"{r['difference_pct']:.3f}%",
                'is_anomaly': '是' if r['is_anomaly'] else '否',
                'anomaly_score': f"{r['anomaly_score']:.2f}",
                'predicted_type': r['predicted_type'],
                'confidence': f"{r['confidence']:.1%}",
                'urgency_level': r['urgency_level'],
                'estimated_resolution_time': f"{r['estimated_resolution_time']}分钟",
                'root_causes_count': len(r['root_causes']),
                'similar_cases_count': len(r['similar_cases']),
                'solutions_count': len(r['recommended_solutions'])
            }
            display_results.append(display_r)
        
        results_df = pd.DataFrame(display_results)
        results_df.columns = [
            '记录ID', '基金代码', '证券代码', '差异金额', '差异比例',
            '是否异常', '异常评分', '预测类型', '置信度', '紧急程度',
            '预估时长', '根本原因数', '相似案例数', '解决方案数'
        ]
        st.dataframe(results_df, use_container_width=True)
        
        # 添加详细信息展开
        st.markdown("#### 🔍 查看详细信息")
        selected_record = st.selectbox(
            "选择记录查看详细分析",
            options=range(len(results)),
            format_func=lambda x: f"{results[x]['record_id']} - {results[x]['fund_code']}"
        )
        
        if selected_record is not None:
            detail = results[selected_record]
            
            with st.expander("📊 详细分析结果", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**根本原因**:")
                    if detail['root_causes']:
                        for i, cause in enumerate(detail['root_causes'], 1):
                            st.write(f"{i}. {cause['cause']} (频率: {cause['frequency']}, 置信度: {cause['confidence']:.1%})")
                    else:
                        st.write("暂无")
                    
                    st.markdown("**相似案例**:")
                    if detail['similar_cases']:
                        for i, case in enumerate(detail['similar_cases'][:3], 1):
                            st.write(f"{i}. {case['case_id']} - {case['difference_type']} (相似度: {case['similarity']:.1%})")
                    else:
                        st.write("暂无")
                
                with col2:
                    st.markdown("**推荐解决方案**:")
                    if detail['recommended_solutions']:
                        for i, sol in enumerate(detail['recommended_solutions'], 1):
                            st.write(f"{i}. {sol['solution']}")
                            st.write(f"   来源: {sol['source']}, 成功率: {sol['success_rate']:.1%}, 时长: {sol['avg_time']}分钟")
                    else:
                        st.write("暂无")


def show_historical_cases_page(df_cases):
    """显示历史案例页面"""
    
    st.markdown("## 📋 历史案例库")
    
    # 统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总案例数", len(df_cases))
    with col2:
        st.metric("平均解决时长", f"{df_cases['resolution_time'].mean():.0f} 分钟")
    with col3:
        st.metric("差异类型数", df_cases['difference_type'].nunique())
    
    st.markdown("---")
    
    # 筛选
    col1, col2 = st.columns(2)
    with col1:
        selected_type = st.multiselect(
            "差异类型",
            options=df_cases['difference_type'].unique(),
            default=df_cases['difference_type'].unique()
        )
    with col2:
        selected_asset = st.multiselect(
            "资产类别",
            options=df_cases['asset_class'].unique(),
            default=df_cases['asset_class'].unique()
        )
    
    filtered_cases = df_cases[
        (df_cases['difference_type'].isin(selected_type)) &
        (df_cases['asset_class'].isin(selected_asset))
    ]
    
    # 显示案例
    st.markdown(f"### 📚 案例列表 ({len(filtered_cases)} 条)")
    
    for _, case in filtered_cases.head(20).iterrows():
        with st.expander(f"{case['case_id']} - {case['difference_type']} - {case['date']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**基金代码**: {case['fund_code']}")
                st.write(f"**资产类别**: {case['asset_class']}")
                st.write(f"**差异金额**: ${case['difference_amount']:,.2f}")
                st.write(f"**差异比例**: {case['difference_pct']:.3f}%")
            with col2:
                st.write(f"**根本原因**: {case['root_cause']}")
                st.write(f"**解决方案**: {case['resolution']}")
                st.write(f"**解决时长**: {case['resolution_time']} 分钟")
                st.write(f"**解决人**: {case['resolved_by']}")


def show_settings_page(df_rules):
    """显示设置页面"""
    
    st.markdown("## ⚙️ 系统设置")
    
    tab1, tab2, tab3 = st.tabs(["📏 估值规则", "🔔 告警设置", "📊 数据管理"])
    
    with tab1:
        st.markdown("### 📏 估值规则配置")
        st.dataframe(df_rules, use_container_width=True)
        
        st.markdown("#### 添加新规则")
        with st.form("add_rule"):
            col1, col2 = st.columns(2)
            with col1:
                rule_id = st.text_input("规则ID")
                asset_class = st.selectbox("资产类别", ["Bond", "Equity", "Cash", "Fund", "All"])
                rule_type = st.text_input("规则类型")
            with col2:
                threshold_amount = st.number_input("金额阈值", min_value=0.0)
                threshold_pct = st.number_input("比例阈值(%)", min_value=0.0)
                priority = st.number_input("优先级", min_value=1, max_value=10, value=1)
            
            rule_description = st.text_area("规则描述")
            
            if st.form_submit_button("添加规则"):
                st.success("✅ 规则添加成功（演示模式）")
    
    with tab2:
        st.markdown("### 🔔 告警设置")
        
        st.number_input("差异金额告警阈值($)", min_value=0, value=10000)
        st.number_input("差异比例告警阈值(%)", min_value=0.0, value=0.1)
        st.multiselect("告警接收人", ["张三", "李四", "王五"], default=["张三"])
        st.selectbox("告警方式", ["邮件", "短信", "系统通知", "全部"])
        
        if st.button("保存设置"):
            st.success("✅ 设置保存成功（演示模式）")
    
    with tab3:
        st.markdown("### 📊 数据管理")
        
        st.markdown("#### 数据导入")
        uploaded_file = st.file_uploader("上传估值差异数据", type=['csv', 'xlsx'])
        if uploaded_file:
            st.info("文件已上传（演示模式）")
        
        st.markdown("#### 数据导出")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("导出估值差异数据"):
                st.success("✅ 数据导出成功（演示模式）")
        with col2:
            if st.button("导出历史案例"):
                st.success("✅ 数据导出成功（演示模式）")


if __name__ == '__main__':
    # 页面配置（仅在直接运行时设置）
    st.set_page_config(
        page_title="估值核对AI助手",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()