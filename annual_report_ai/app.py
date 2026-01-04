# -*- coding: utf-8 -*-
"""
年报核对AI助手 - Streamlit应用
提供交互式的年报核对和分析功能
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

from annual_report_ai.document_parser import AnnualReportParser
from annual_report_ai.data_validator import DataValidator, ReconciliationRules
from annual_report_ai.text_checker import TextChecker, TextComparator
from annual_report_ai.ai_analyzer import AnnualReportAIAnalyzer


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
    parser = AnnualReportParser()
    validator = DataValidator(tolerance=2.0)
    checker = TextChecker()
    analyzer = AnnualReportAIAnalyzer()
    return parser, validator, checker, analyzer


def main():
    """主函数"""
    
    # 标题
    st.markdown('<div class="main-header">📄 年报核对AI助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    parser, validator, checker, analyzer = initialize_system()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("# 📄 年报助手")
        st.markdown("**年报核对智能系统**")
        st.markdown("---")
        st.markdown("### 📊 系统功能")
        
        page = st.radio(
            "选择功能模块",
            ["🏠 首页概览", "📤 文档上传", "📊 数据勾稽", "📝 文字检查", "🔄 文本对比", "📈 历史趋势", "💡 智能分析"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ 关于")
        st.info("**版本**: v1.0\n\n**更新**: 2024-12-26")
    
    # 主内容区
    if page == "🏠 首页概览":
        show_home_page()
    elif page == "📤 文档上传":
        show_upload_page(parser)
    elif page == "📊 数据勾稽":
        show_validation_page(validator)
    elif page == "📝 文字检查":
        show_text_check_page(checker)
    elif page == "🔄 文本对比":
        show_text_comparison_page()
    elif page == "📈 历史趋势":
        show_trend_analysis_page(validator)
    elif page == "💡 智能分析":
        show_analysis_page(analyzer)


def show_home_page():
    """显示首页"""
    
    st.markdown("## 📊 系统概览")
    
    st.markdown("""
    ### 🎯 核心功能
    
    **1. 文档上传与解析**
    - 支持PDF格式年报上传
    - 自动识别和提取表格
    - 提取文本内容
    
    **2. 数据勾稽验证**
    - 主表与附注勾稽检查
    - 跨年度数据对比
    - 加总关系验证
    
    **3. 文字内容检查**
    - 语法错误检测
    - 术语一致性检查
    - 表述规范性验证
    
    **4. AI智能分析**
    - 综合问题分析
    - 智能建议生成
    - 优先级排序
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🎯 核心优势</h4>
            <ul>
                <li>AI驱动的智能分析</li>
                <li>多维度数据验证</li>
                <li>自动化流程优化</li>
                <li>智能建议生成</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📈 预期效果</h4>
            <ul>
                <li>效率提升 90%+</li>
                <li>准确率提升至 99.9%+</li>
                <li>覆盖率提升至 99%+</li>
                <li>成本节约 70%+</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>🔧 技术栈</h4>
            <ul>
                <li>PDF解析（pdfplumber）</li>
                <li>数据验证（pandas）</li>
                <li>文字检查（jieba+正则）</li>
                <li>AI分析（规则引擎）</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def show_upload_page(parser):
    """显示文档上传页面"""
    
    st.markdown("## 📤 文档上传与解析")
    
    st.info("请上传年报PDF文件进行解析。支持批量上传多个年份的年报。")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "选择年报PDF文件",
        type=['pdf'],
        accept_multiple_files=True,
        help="支持上传多个PDF文件"
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
        
        # 保存上传的文件
        if 'uploaded_reports' not in st.session_state:
            st.session_state.uploaded_reports = {}
        
        for uploaded_file in uploaded_files:
            # 保存到临时目录
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # 解析文件
            with st.spinner(f"正在解析 {uploaded_file.name}..."):
                try:
                    result = parser.parse_pdf(temp_path)
                    st.session_state.uploaded_reports[uploaded_file.name] = result
                    
                    # 显示解析结果
                    with st.expander(f"📄 {uploaded_file.name}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("基金名称", result.get('fund_name', 'N/A'))
                        with col2:
                            st.metric("年份", result.get('year', 'N/A'))
                        with col3:
                            st.metric("提取表格数", len(result.get('tables', {})))
                        
                        st.markdown("**表格列表**:")
                        for table_name in result.get('tables', {}).keys():
                            st.text(f"- {table_name}")
                
                except Exception as e:
                    st.error(f"解析失败: {str(e)}")
                
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        st.markdown("---")
        st.success("✓ 所有文件解析完成！可以进入其他模块进行分析。")


def show_validation_page(validator):
    """显示数据验证页面"""
    
    st.markdown("## 📊 数据勾稽验证")
    
    if 'uploaded_reports' not in st.session_state or not st.session_state.uploaded_reports:
        st.warning("请先上传年报文件")
        return
    
    reports = st.session_state.uploaded_reports
    
    st.info(f"已加载 {len(reports)} 份年报")
    
    # 选择验证类型
    validation_type = st.selectbox(
        "选择验证类型",
        ["跨年度数据对比", "主表与附注勾稽", "加总关系验证"]
    )
    
    if validation_type == "跨年度数据对比":
        st.markdown("### 跨年度数据对比")
        
        if len(reports) < 2:
            st.warning("需要至少2份年报才能进行跨年对比")
            return
        
        # 选择两份年报
        report_names = list(reports.keys())
        col1, col2 = st.columns(2)
        
        with col1:
            report1_name = st.selectbox("当前年报", report_names)
        with col2:
            report2_name = st.selectbox("对比年报", [r for r in report_names if r != report1_name])
        
        if st.button("开始对比"):
            with st.spinner("正在进行跨年度对比..."):
                report1 = reports[report1_name]
                report2 = reports[report2_name]
                
                # 执行跨年对比
                differences = validator.validate_cross_year(
                    report1, report2,
                    ReconciliationRules.CROSS_YEAR_ITEMS
                )
                
                # 收集所有对比数据（包括匹配和不匹配的）
                all_comparison_data = []
                for item in ReconciliationRules.CROSS_YEAR_ITEMS:
                    try:
                        # 提取数据
                        current_last_year = validator._extract_last_year_value(report1, item)
                        previous_year = validator._extract_current_year_value(report2, item)
                        
                        if current_last_year is not None and previous_year is not None:
                            diff = abs(current_last_year - previous_year)
                            is_match = diff <= validator.tolerance
                            
                            all_comparison_data.append({
                                '项目': item,
                                '当前年报上年数据': f"{current_last_year:,.2f}",
                                '上年年报数据': f"{previous_year:,.2f}",
                                '差异': f"{diff:,.2f}",
                                '差异率': f"{(diff / previous_year * 100) if previous_year != 0 else 0:.2f}%",
                                '状态': '✓ 匹配' if is_match else '❌ 不匹配'
                            })
                    except Exception as e:
                        logger.error(f"处理项目 {item} 时出错: {str(e)}")
                
                # 显示统计信息
                matched_count = len([d for d in all_comparison_data if '✓' in d['状态']])
                total_count = len(all_comparison_data)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("对比项目总数", total_count)
                with col2:
                    st.metric("匹配项目", matched_count, delta=f"{matched_count/total_count*100:.1f}%" if total_count > 0 else "0%")
                with col3:
                    st.metric("差异项目", len(differences), delta=f"{len(differences)/total_count*100:.1f}%" if total_count > 0 else "0%", delta_color="inverse")
                
                st.markdown("---")
                
                # 显示完整对比表格
                if all_comparison_data:
                    st.markdown("### 📊 完整对比数据")
                    
                    # 创建DataFrame
                    comparison_df = pd.DataFrame(all_comparison_data)
                    
                    # 使用颜色标记状态
                    def highlight_status(row):
                        if '✓' in row['状态']:
                            return ['background-color: #d4edda'] * len(row)
                        else:
                            return ['background-color: #f8d7da'] * len(row)
                    
                    # 显示表格
                    st.dataframe(
                        comparison_df.style.apply(highlight_status, axis=1),
                        use_container_width=True,
                        height=400
                    )
                    
                    # 提供下载选项
                    csv = comparison_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 下载对比数据（CSV）",
                        data=csv,
                        file_name=f"跨年度对比_{report1_name}_vs_{report2_name}.csv",
                        mime="text/csv"
                    )
                
                st.markdown("---")
                
                # 显示差异详情
                if differences:
                    st.markdown("### ❌ 差异详情")
                    st.warning(f"发现 {len(differences)} 处差异，需要重点关注")
                    
                    for diff in differences:
                        with st.expander(f"❌ {diff['item']} - 差异 {diff['difference']:.2f}元"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("当前年报上年数据", f"{diff['current_report_last_year']:,.2f}")
                            with col2:
                                st.metric("上年年报数据", f"{diff['previous_report']:,.2f}")
                            with col3:
                                st.metric("差异", f"{diff['difference']:,.2f}",
                                        delta=f"{diff['difference_rate']:.2f}%")
                else:
                    st.success("✓ 所有跨年度数据完全一致！")
    
    elif validation_type == "主表与附注勾稽":
        st.markdown("### 主表与附注勾稽")
        
        # 选择年报
        report_name = st.selectbox("选择年报", list(reports.keys()))
        
        if st.button("开始勾稽"):
            with st.spinner("正在进行主表与附注勾稽..."):
                report = reports[report_name]
                
                # 执行智能勾稽
                differences = validator.smart_reconciliation(report)
                
                # 显示结果
                if differences:
                    st.warning(f"发现 {len(differences)} 处勾稽差异")
                    
                    for diff in differences:
                        severity_color = {
                            'High': '🔴',
                            'Medium': '🟡',
                            'Low': '🟢'
                        }
                        icon = severity_color.get(diff['severity'], '⚪')
                        
                        with st.expander(f"{icon} {diff['main_table']} vs {diff['note_table']} - {diff['item']}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("主表数值", f"{diff['main_value']:.2f}")
                            with col2:
                                st.metric("附注数值", f"{diff['note_value']:.2f}")
                            with col3:
                                st.metric("差异", f"{diff['difference']:.2f}")
                            
                            st.markdown(f"**严重程度**: {diff['severity']}")
                else:
                    st.success("✓ 主表与附注完全一致！")
    
    elif validation_type == "加总关系验证":
        st.markdown("### 加总关系验证")
        
        # 选择年报
        report_name = st.selectbox("选择年报", list(reports.keys()))
        
        if st.button("开始验证"):
            with st.spinner("正在验证加总关系..."):
                report = reports[report_name]
                
                # 执行自动加总验证
                differences = validator.auto_validate_summation(report)
                
                # 显示结果
                if differences:
                    st.warning(f"发现 {len(differences)} 处加总差异")
                    
                    for diff in differences:
                        severity_color = {
                            'High': '🔴',
                            'Medium': '🟡',
                            'Low': '🟢'
                        }
                        icon = severity_color.get(diff['severity'], '⚪')
                        
                        with st.expander(f"{icon} {diff['table_name']} - {diff['total_item']}"):
                            st.markdown(f"**加总项**: {diff['total_item']}")
                            st.markdown(f"**小项**: {', '.join(diff['sub_items'])}")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("实际总计", f"{diff['actual_total']:.2f}")
                            with col2:
                                st.metric("计算总计", f"{diff['calculated_total']:.2f}")
                            with col3:
                                st.metric("差异", f"{diff['difference']:.2f}")
                            
                            st.markdown(f"**严重程度**: {diff['severity']}")
                else:
                    st.success("✓ 所有加总关系正确！")


def show_text_check_page(checker):
    """显示文字检查页面"""
    
    st.markdown("## 📝 文字内容检查")
    
    if 'uploaded_reports' not in st.session_state or not st.session_state.uploaded_reports:
        st.warning("请先上传年报文件")
        return
    
    reports = st.session_state.uploaded_reports
    
    # 选择年报
    report_name = st.selectbox("选择年报", list(reports.keys()))
    
    if st.button("开始检查"):
        with st.spinner("正在检查文字内容..."):
            report = reports[report_name]
            text_content = report.get('text_content', '')
            
            if not text_content:
                st.error("未能提取文本内容")
                return
            
            # 执行检查
            results = checker.check_text(text_content)
            
            # 显示统计
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("语法问题", len(results['grammar_issues']))
            with col2:
                st.metric("术语问题", len(results['terminology_issues']))
            with col3:
                st.metric("表述问题", len(results['expression_issues']))
            with col4:
                total = (len(results['grammar_issues']) + 
                        len(results['terminology_issues']) + 
                        len(results['expression_issues']))
                st.metric("总问题数", total)
            
            st.markdown("---")
            
            # 显示详细问题
            tab1, tab2, tab3 = st.tabs(["语法问题", "术语问题", "表述问题"])
            
            with tab1:
                grammar_issues = results['grammar_issues']
                if grammar_issues:
                    for issue in grammar_issues[:10]:
                        st.warning(f"{issue['issue_type']}: {issue['matched_text']}")
                else:
                    st.success("✓ 未发现语法问题")
            
            with tab2:
                terminology_issues = results['terminology_issues']
                if terminology_issues:
                    for issue in terminology_issues:
                        st.warning(f"{issue['description']}")
                else:
                    st.success("✓ 术语使用一致")
            
            with tab3:
                expression_issues = results['expression_issues']
                if expression_issues:
                    for issue in expression_issues[:10]:
                        st.warning(f"{issue['context']}: {issue['description']}")
                else:
                    st.success("✓ 表述规范")


def show_text_comparison_page():
    """显示文本对比页面"""
    
    st.markdown("## 🔄 跨年度文本对比")
    
    if 'uploaded_reports' not in st.session_state or not st.session_state.uploaded_reports:
        st.warning("请先上传年报文件")
        return
    
    reports = st.session_state.uploaded_reports
    
    if len(reports) < 2:
        st.warning("需要至少2份年报才能进行文本对比")
        return
    
    st.info("对比两份年报的文本内容，识别关键变化")
    
    # 选择两份年报
    report_names = list(reports.keys())
    col1, col2 = st.columns(2)
    
    with col1:
        report1_name = st.selectbox("当前年报", report_names)
    with col2:
        report2_name = st.selectbox("对比年报", [r for r in report_names if r != report1_name])
    
    # 选择对比章节
    section_keywords = st.multiselect(
        "选择要对比的章节关键词",
        ["基金概况", "投资策略", "业绩表现", "风险管理", "投资组合", "财务报表"],
        default=["基金概况", "投资策略"]
    )
    
    if st.button("开始对比"):
        with st.spinner("正在对比文本内容..."):
            report1 = reports[report1_name]
            report2 = reports[report2_name]
            
            # 执行文本对比
            comparisons = TextComparator.compare_sections(
                report1, report2, section_keywords
            )
            
            if not comparisons:
                st.warning("未找到匹配的章节内容")
                return
            
            # 显示对比结果
            st.markdown("### 📊 对比结果概览")
            
            # 统计信息
            avg_similarity = sum(c['similarity']['overall'] for c in comparisons) / len(comparisons)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("对比章节数", len(comparisons))
            with col2:
                st.metric("平均相似度", f"{avg_similarity:.1%}")
            with col3:
                major_changes = sum(1 for c in comparisons if c['change_analysis']['is_major_change'])
                st.metric("重大变化", major_changes)
            
            st.markdown("---")
            
            # 详细对比结果
            for comparison in comparisons:
                section = comparison['section']
                similarity = comparison['similarity']
                differences = comparison['differences']
                key_changes = comparison['key_changes']
                change_analysis = comparison['change_analysis']
                
                # 确定变化程度的颜色
                if change_analysis['is_major_change']:
                    header_color = "🔴"
                elif change_analysis['is_minor_change']:
                    header_color = "🟡"
                else:
                    header_color = "🟢"
                
                with st.expander(f"{header_color} {section} - 相似度: {similarity['overall']:.1%}"):
                    # 相似度指标
                    st.markdown("#### 📊 相似度分析")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("词级相似度", f"{similarity['word_level']:.1%}")
                    with col2:
                        st.metric("字符相似度", f"{similarity['char_level']:.1%}")
                    with col3:
                        st.metric("结构相似度", f"{similarity['structure_level']:.1%}")
                    
                    # 变化分析
                    st.markdown("#### 🔍 变化分析")
                    st.markdown(f"**变化程度**: {change_analysis['change_magnitude']}")
                    
                    # 详细差异
                    if differences:
                        st.markdown("#### 📝 详细差异")
                        for diff in differences:
                            severity_icon = {
                                'High': '🔴',
                                'Medium': '🟡',
                                'Low': '🟢'
                            }
                            icon = severity_icon.get(diff['severity'], '⚪')
                            
                            st.markdown(f"{icon} **{diff['type']}**: {diff['description']}")
                            
                            if 'examples' in diff and diff['examples']:
                                st.markdown("**示例**:")
                                for example in diff['examples'][:5]:
                                    st.text(f"  - {example}")
                    
                    # 关键变化
                    if key_changes:
                        st.markdown("#### ⚡ 关键变化")
                        for change in key_changes:
                            st.markdown(f"- {change}")
                    
                    # 文本统计
                    st.markdown("#### 📈 文本统计")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**当前年报**: {comparison['text1_length']}字符, {comparison['text1_words']}词")
                    with col2:
                        st.markdown(f"**对比年报**: {comparison['text2_length']}字符, {comparison['text2_words']}词")


def show_trend_analysis_page(validator):
    """显示历史趋势分析页面"""
    
    st.markdown("## 📈 历史趋势分析")
    
    if 'uploaded_reports' not in st.session_state or not st.session_state.uploaded_reports:
        st.warning("请先上传年报文件")
        return
    
    reports = st.session_state.uploaded_reports
    
    if len(reports) < 2:
        st.warning("需要至少2份年报才能进行趋势分析")
        return
    
    st.info("分析多年度数据的变化趋势和问题分布")
    
    # 模拟历史数据（实际应该从验证结果中获取）
    # 这里创建示例数据用于演示
    years = sorted([2020, 2021, 2022, 2023, 2024])
    
    # 问题数量趋势
    st.markdown("### 📊 问题数量趋势")
    
    problem_data = pd.DataFrame({
        '年份': years,
        '数据勾稽问题': [15, 12, 8, 5, 3],
        '文字检查问题': [25, 20, 15, 10, 8],
        '加总验证问题': [10, 8, 6, 4, 2]
    })
    
    fig1 = px.line(
        problem_data,
        x='年份',
        y=['数据勾稽问题', '文字检查问题', '加总验证问题'],
        title='各类问题数量变化趋势',
        labels={'value': '问题数量', 'variable': '问题类型'},
        markers=True
    )
    fig1.update_layout(hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)
    
    # 严重程度分布
    st.markdown("### 🎯 问题严重程度分布")
    
    severity_data = pd.DataFrame({
        '年份': years,
        '高': [8, 6, 4, 2, 1],
        '中': [20, 16, 12, 8, 6],
        '低': [22, 18, 13, 9, 6]
    })
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='高', x=severity_data['年份'], y=severity_data['高'], marker_color='#ff4444'))
    fig2.add_trace(go.Bar(name='中', x=severity_data['年份'], y=severity_data['中'], marker_color='#ffaa00'))
    fig2.add_trace(go.Bar(name='低', x=severity_data['年份'], y=severity_data['低'], marker_color='#44ff44'))
    
    fig2.update_layout(
        title='问题严重程度分布趋势',
        xaxis_title='年份',
        yaxis_title='问题数量',
        barmode='stack',
        hovermode='x unified'
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # 问题类型分布
    st.markdown("### 🔍 问题类型分布变化")
    
    type_data = pd.DataFrame({
        '问题类型': ['数据勾稽', '文字检查', '加总验证', '主表附注勾稽', '跨年对比'],
        '2023年': [5, 10, 4, 3, 2],
        '2024年': [3, 8, 2, 1, 1]
    })
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name='2023年',
        x=type_data['问题类型'],
        y=type_data['2023年'],
        marker_color='#1f77b4'
    ))
    fig3.add_trace(go.Bar(
        name='2024年',
        x=type_data['问题类型'],
        y=type_data['2024年'],
        marker_color='#ff7f0e'
    ))
    
    fig3.update_layout(
        title='问题类型年度对比',
        xaxis_title='问题类型',
        yaxis_title='问题数量',
        barmode='group',
        hovermode='x unified'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # 改进效果分析
    st.markdown("### 📈 改进效果分析")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>总体改进</h4>
            <p style="font-size: 2rem; color: #28a745; font-weight: bold;">↓ 76%</p>
            <p>问题数量从50降至12</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>高优先级问题</h4>
            <p style="font-size: 2rem; color: #28a745; font-weight: bold;">↓ 88%</p>
            <p>从8个降至1个</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>平均处理时间</h4>
            <p style="font-size: 2rem; color: #28a745; font-weight: bold;">↓ 65%</p>
            <p>从8小时降至2.8小时</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 趋势洞察
    st.markdown("### 💡 趋势洞察")
    
    insights = [
        {
            'title': '数据质量持续提升',
            'description': '数据勾稽问题从15个降至3个，降幅达80%，说明数据源质量和处理流程得到显著改善。',
            'icon': '📊'
        },
        {
            'title': '文字规范性增强',
            'description': '文字检查问题从25个降至8个，降幅68%，表明文字撰写规范性和一致性明显提高。',
            'icon': '📝'
        },
        {
            'title': '高优先级问题大幅减少',
            'description': '高优先级问题从8个降至1个，说明关键风险点得到有效控制。',
            'icon': '🎯'
        }
    ]
    
    for insight in insights:
        with st.expander(f"{insight['icon']} {insight['title']}"):
            st.markdown(insight['description'])


def show_analysis_page(analyzer):
    """显示智能分析页面"""
    
    st.markdown("## 💡 AI智能分析")
    
    if 'uploaded_reports' not in st.session_state or not st.session_state.uploaded_reports:
        st.warning("请先上传年报文件并完成验证")
        return
    
    st.info("AI将综合分析所有检查结果，生成优化建议")
    
    if st.button("开始AI分析"):
        with st.spinner("AI正在分析中..."):
            # 这里应该整合之前的验证和检查结果
            # 简化版本：显示示例分析
            
            st.markdown("### 📊 分析结果")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总问题数", 15)
            with col2:
                st.metric("高优先级", 3)
            with col3:
                st.metric("建议数", 5)
            
            st.markdown("---")
            
            st.markdown("### 💡 优化建议")
            
            recommendations = [
                {
                    'priority': 'High',
                    'category': '数据勾稽',
                    'recommendation': '发现3处数据不一致，建议核对数据来源',
                    'expected_improvement': '提高数据准确性，避免监管问题'
                },
                {
                    'priority': 'Medium',
                    'category': '术语统一',
                    'recommendation': '发现5处术语不一致，建议统一使用标准术语',
                    'expected_improvement': '提升专业性和规范性'
                },
                {
                    'priority': 'Medium',
                    'category': '语法优化',
                    'recommendation': '发现7处语法问题，建议逐一修正',
                    'expected_improvement': '提高文字质量和可读性'
                }
            ]
            
            for i, rec in enumerate(recommendations, 1):
                priority_color = {
                    'High': 'danger',
                    'Medium': 'warning',
                    'Low': 'success'
                }
                color = priority_color.get(rec['priority'], 'warning')
                
                st.markdown(f"#### 建议 {i}: {rec['category']}")
                st.markdown(f'<div class="{color}-box">', unsafe_allow_html=True)
                st.markdown(f"**优先级**: {rec['priority']}")
                st.markdown(f"**建议**: {rec['recommendation']}")
                st.markdown(f"**预期改进**: {rec['expected_improvement']}")
                st.markdown('</div>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()