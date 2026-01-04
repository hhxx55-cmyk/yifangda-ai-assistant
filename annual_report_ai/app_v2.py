# -*- coding: utf-8 -*-
"""
年报核对AI助手 - 重构版本
简化功能，专注于数据勾稽和文字检查
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os
import tempfile

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from annual_report_ai.financial_reconciliation import FinancialReconciliation
from annual_report_ai.enhanced_text_checker import EnhancedTextChecker


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
    .error-highlight {
        background-color: #ffcccc;
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """初始化系统（缓存）"""
    reconciliation = FinancialReconciliation(tolerance=0.01)
    text_checker = EnhancedTextChecker()
    return reconciliation, text_checker


def main():
    """主函数"""
    
    # 标题
    st.markdown('<div class="main-header">📄 年报核对AI助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    reconciliation, text_checker = initialize_system()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("# 📄 年报助手")
        st.markdown("**年报核对智能系统**")
        st.markdown("---")
        st.markdown("### 📊 系统功能")
        
        page = st.radio(
            "选择功能模块",
            ["🏠 首页概览", "📊 数据勾稽验证", "📝 文字内容检查"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ 关于")
        st.info("**版本**: v2.0\n\n**更新**: 2024-12-29\n\n**功能**: 数据勾稽 + 文字检查")
    
    # 主内容区
    if page == "🏠 首页概览":
        show_home_page()
    elif page == "📊 数据勾稽验证":
        show_reconciliation_page(reconciliation)
    elif page == "📝 文字内容检查":
        show_text_check_page(text_checker)


def show_home_page():
    """显示首页"""
    
    st.markdown("## 📊 系统概览")
    
    st.markdown("""
    ### 🎯 核心功能
    
    **1. 数据勾稽验证**
    - 上传Excel格式的财务报表
    - 同年度不同报表间勾稽关系验证
    - 跨年度数据一致性验证
    - 详细的公式、项目和数值展示
    
    **2. 文字内容检查**
    - 上传PDF格式的年报文档
    - 语法错误检测
    - 术语一致性检查
    - 表述规范性验证
    - 完整上下文展示和错误高亮
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 数据勾稽验证</h4>
            <ul>
                <li>资产负债表内部勾稽</li>
                <li>利润表与资产负债表勾稽</li>
                <li>净资产变动表勾稽</li>
                <li>跨年度数据一致性验证</li>
            </ul>
            <p><strong>支持格式</strong>: Excel (.xlsx, .xls)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📝 文字内容检查</h4>
            <ul>
                <li>语法错误检测</li>
                <li>术语一致性检查</li>
                <li>表述规范性验证</li>
                <li>完整上下文展示</li>
            </ul>
            <p><strong>支持格式</strong>: PDF (.pdf)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🚀 快速开始")
    st.markdown("""
    1. 点击左侧菜单选择功能模块
    2. 上传相应格式的文件
    3. 查看验证结果和详细报告
    4. 根据建议进行修正
    """)


def show_reconciliation_page(reconciliation: FinancialReconciliation):
    """显示数据勾稽验证页面"""
    
    st.markdown("## 📊 数据勾稽验证")
    
    st.info("上传Excel格式的财务报表，系统将自动验证各报表间的勾稽关系")
    
    # 文件上传区域
    st.markdown("### 📤 上传财务报表")
    
    uploaded_files = st.file_uploader(
        "选择Excel文件（可上传多个年度的报表）",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="支持上传多个Excel文件，每个文件应包含资产负债表、利润表、净资产变动表等工作表"
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
        
        # 保存上传的文件到session state
        if 'financial_reports' not in st.session_state:
            st.session_state.financial_reports = {}
        
        # 处理上传的文件
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            try:
                # 加载Excel数据
                with st.spinner(f"正在加载 {file_name}..."):
                    sheets = reconciliation.load_excel_data(tmp_path)
                    financial_data = reconciliation.extract_financial_data(sheets)
                    
                    st.session_state.financial_reports[file_name] = {
                        'sheets': sheets,
                        'financial_data': financial_data,
                        'file_path': tmp_path
                    }
                
                # 显示文件信息
                with st.expander(f"📄 {file_name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("工作表数量", len(sheets))
                    with col2:
                        st.metric("提取数据项", len(financial_data))
                    with col3:
                        year = extract_year_from_filename(file_name)
                        st.metric("年份", year if year else "未识别")
                    
                    st.markdown("**包含的工作表**:")
                    for sheet_name in sheets.keys():
                        st.text(f"  • {sheet_name}")
            
            except Exception as e:
                st.error(f"加载 {file_name} 失败: {str(e)}")
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        st.markdown("---")
        
        # 验证选项
        st.markdown("### 🔍 选择验证类型")
        
        validation_type = st.selectbox(
            "验证类型",
            ["同年度报表勾稽验证", "跨年度数据一致性验证"]
        )
        
        if validation_type == "同年度报表勾稽验证":
            show_same_year_validation(reconciliation)
        else:
            show_cross_year_validation(reconciliation)


def show_same_year_validation(reconciliation: FinancialReconciliation):
    """显示同年度报表勾稽验证"""
    
    st.markdown("#### 同年度报表勾稽验证")
    st.info("验证同一年度内，资产负债表、利润表、净资产变动表之间的勾稽关系")
    
    if 'financial_reports' not in st.session_state or not st.session_state.financial_reports:
        st.warning("请先上传财务报表")
        return
    
    # 选择要验证的报表
    report_names = list(st.session_state.financial_reports.keys())
    selected_report = st.selectbox("选择要验证的报表", report_names)
    
    if st.button("开始验证", type="primary"):
        with st.spinner("正在进行勾稽验证..."):
            report_data = st.session_state.financial_reports[selected_report]
            financial_data = report_data['financial_data']
            
            # 执行勾稽验证
            results = reconciliation.validate_reconciliation(financial_data)
            
            # 显示验证结果
            if results:
                # 统计信息
                passed = [r for r in results if r['is_pass']]
                failed = [r for r in results if not r['is_pass']]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("验证项目总数", len(results))
                with col2:
                    st.metric("✓ 通过", len(passed), delta=f"{len(passed)/len(results)*100:.1f}%")
                with col3:
                    st.metric("❌ 不通过", len(failed), 
                             delta=f"{len(failed)/len(results)*100:.1f}%", 
                             delta_color="inverse")
                
                st.markdown("---")
                
                # 显示详细结果
                st.markdown("### 📋 详细验证结果")
                
                # 创建结果表格
                result_data = []
                for result in results:
                    result_data.append({
                        '勾稽类别': result['category'],
                        '验证项目': result['name'],
                        '勾稽公式': result['formula'],
                        '差异金额': f"{result['difference']:,.2f}",
                        '验证状态': result['status']
                    })
                
                result_df = pd.DataFrame(result_data)
                
                # 使用颜色标记状态
                def highlight_status(row):
                    if '✓' in row['验证状态']:
                        return ['background-color: #d4edda'] * len(row)
                    else:
                        return ['background-color: #f8d7da'] * len(row)
                
                st.dataframe(
                    result_df.style.apply(highlight_status, axis=1),
                    use_container_width=True,
                    height=400
                )
                
                # 下载按钮
                csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载验证结果（CSV）",
                    data=csv,
                    file_name=f"勾稽验证结果_{selected_report}.csv",
                    mime="text/csv"
                )
                
                st.markdown("---")
                
                # 显示不通过的详细信息
                if failed:
                    st.markdown("### ❌ 不通过项目详情")
                    st.warning(f"发现 {len(failed)} 个勾稽差异，需要重点关注")
                    
                    for result in failed:
                        with st.expander(f"❌ {result['name']} - 差异 {result['difference']:,.2f}元"):
                            st.markdown(f"**勾稽类别**: {result['category']}")
                            st.markdown(f"**勾稽公式**: `{result['formula']}`")
                            
                            st.markdown("**涉及项目及数值**:")
                            values_df = pd.DataFrame([
                                {'项目': k, '金额（元）': f"{v:,.2f}"} 
                                for k, v in result['values'].items()
                            ])
                            st.table(values_df)
                            
                            st.markdown(f"**差异金额**: {result['difference']:,.2f} 元")
                            
                            # 建议
                            st.markdown("**处理建议**:")
                            st.markdown("- 核对原始数据来源")
                            st.markdown("- 检查计算公式是否正确")
                            st.markdown("- 确认是否存在四舍五入误差")
                else:
                    st.success("✓ 所有勾稽关系验证通过！")
            
            else:
                st.warning("未能执行验证，请检查报表数据是否完整")


def show_cross_year_validation(reconciliation: FinancialReconciliation):
    """显示跨年度数据一致性验证"""
    
    st.markdown("#### 跨年度数据一致性验证")
    st.info("验证当年报表中的期初数据是否与上年报表的期末数据一致")
    
    if 'financial_reports' not in st.session_state or not st.session_state.financial_reports:
        st.warning("请先上传财务报表")
        return
    
    reports = st.session_state.financial_reports
    
    if len(reports) < 2:
        st.warning("需要至少上传2个年度的报表才能进行跨年度验证")
        return
    
    # 选择两个年度的报表
    report_names = list(reports.keys())
    col1, col2 = st.columns(2)
    
    with col1:
        current_report = st.selectbox("当前年度报表", report_names)
    with col2:
        previous_report = st.selectbox(
            "上一年度报表", 
            [r for r in report_names if r != current_report]
        )
    
    if st.button("开始验证", type="primary"):
        with st.spinner("正在进行跨年度验证..."):
            current_data = reports[current_report]['financial_data']
            previous_data = reports[previous_report]['financial_data']
            
            # 执行跨年度验证
            results = reconciliation.validate_cross_year_consistency(
                current_data, previous_data
            )
            
            # 显示验证结果
            if results:
                # 统计信息
                passed = [r for r in results if r['is_pass']]
                failed = [r for r in results if not r['is_pass']]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("验证项目总数", len(results))
                with col2:
                    st.metric("✓ 一致", len(passed), delta=f"{len(passed)/len(results)*100:.1f}%")
                with col3:
                    st.metric("❌ 不一致", len(failed),
                             delta=f"{len(failed)/len(results)*100:.1f}%",
                             delta_color="inverse")
                
                st.markdown("---")
                
                # 显示完整对比表格
                st.markdown("### 📊 完整对比数据")
                
                result_data = []
                for result in results:
                    # 统一格式：项目 - 当年的上年度可比区间数值 - 上一年度的本期数值 - 差异 - 状态
                    result_data.append({
                        '项目': result['item'],
                        '当年的上年度可比区间数值': f"{result['current_year_comparable']:,.2f}",
                        '上一年度的本期数值': f"{result['previous_year_current']:,.2f}",
                        '差异': f"{result['difference']:,.2f}",
                        '状态': result['status']
                    })
                
                result_df = pd.DataFrame(result_data)
                
                # 使用颜色标记状态
                def highlight_status(row):
                    if '✓' in row['状态']:
                        return ['background-color: #d4edda'] * len(row)
                    else:
                        return ['background-color: #f8d7da'] * len(row)
                
                st.dataframe(
                    result_df.style.apply(highlight_status, axis=1),
                    use_container_width=True,
                    height=400
                )
                
                # 下载按钮
                csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载对比结果（CSV）",
                    data=csv,
                    file_name=f"跨年度对比_{current_report}_vs_{previous_report}.csv",
                    mime="text/csv"
                )
                
                st.markdown("---")
                
                # 显示不一致的详细信息
                if failed:
                    st.markdown("### ❌ 不一致项目详情")
                    st.warning(f"发现 {len(failed)} 处数据不一致，需要重点关注")
                    
                    for result in failed:
                        with st.expander(f"❌ {result['item']} - 差异 {result['difference']:,.2f}元"):
                            st.markdown(f"**验证公式**: `{result['formula']}`")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("当年的上年度可比区间数值", f"{result['current_year_comparable']:,.2f}")
                            with col2:
                                st.metric("上一年度的本期数值", f"{result['previous_year_current']:,.2f}")
                            with col3:
                                st.metric("差异", f"{result['difference']:,.2f}")
                            
                            st.markdown("**处理建议**:")
                            st.markdown("- 核对两个年度报表的数据来源")
                            st.markdown("- 检查是否存在会计政策变更")
                            st.markdown("- 确认是否有追溯调整")
                else:
                    st.success("✓ 所有跨年度数据完全一致！")
            
            else:
                st.warning("未能执行验证，请检查报表数据是否完整")


def show_text_check_page(text_checker: EnhancedTextChecker):
    """显示文字内容检查页面"""
    
    st.markdown("## 📝 文字内容检查")
    
    st.info("上传PDF格式的年报文档，系统将检查语法、术语和表述规范性")
    
    # 文件上传区域
    st.markdown("### 📤 上传年报PDF")
    
    uploaded_file = st.file_uploader(
        "选择PDF文件",
        type=['pdf'],
        help="上传年报PDF文件进行文字内容检查"
    )
    
    if uploaded_file:
        st.success(f"已上传: {uploaded_file.name}")
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        if st.button("开始检查", type="primary"):
            try:
                with st.spinner("正在提取PDF文本..."):
                    # 提取PDF文本
                    text_data = text_checker.extract_text_from_pdf(tmp_path)
                    
                    st.success(f"成功提取文本: {text_data['total_pages']} 页, {text_data['total_chars']} 字符")
                
                with st.spinner("正在检查文字内容..."):
                    # 执行文字检查
                    issues = text_checker.check_text_with_context(text_data)
                    
                    # 显示统计信息
                    grammar_issues = [i for i in issues if i['type'] == '语法问题']
                    expression_issues = [i for i in issues if i['type'] == '表述问题']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("总问题数", len(issues))
                    with col2:
                        st.metric("语法问题", len(grammar_issues))
                    with col3:
                        st.metric("语病检查", len(expression_issues))
                    
                    st.markdown("---")
                    
                    # 显示详细问题
                    if issues:
                        st.markdown("### 📋 检查结果详情")
                        
                        # 按类型分组显示
                        tab1, tab2 = st.tabs(["语法问题", "语病检查"])
                        
                        with tab1:
                            show_issues_by_type(grammar_issues, text_checker, "语法问题")
                        
                        with tab2:
                            show_issues_by_type(expression_issues, text_checker, "语病检查")
                    
                    else:
                        st.success("✓ 未发现任何问题，文字内容规范！")
            
            except Exception as e:
                st.error(f"检查失败: {str(e)}")
            
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


def show_issues_by_type(issues: List[Dict], text_checker: EnhancedTextChecker, 
                       issue_type: str):
    """按类型显示问题"""
    
    if not issues:
        st.success(f"✓ 未发现{issue_type}")
        return
    
    st.warning(f"发现 {len(issues)} 个{issue_type}")
    
    for idx, issue in enumerate(issues, 1):
        with st.expander(f"问题 {idx}: {issue['issue_name']} (第{issue['page_num']}页)"):
            st.markdown(f"**问题类型**: {issue['issue_name']}")
            st.markdown(f"**问题描述**: {issue['description']}")
            st.markdown(f"**页码**: 第 {issue['page_num']} 页")
            
            # 显示错误文本
            st.markdown(f"**错误文本**: `{issue['matched_text']}`")
            
            # 显示带高亮的上下文
            st.markdown("**上下文**:")
            error_start, error_end = issue['error_position']
            highlighted_context = text_checker.highlight_error_in_text(
                issue['context'], error_start, error_end
            )
            st.markdown(highlighted_context, unsafe_allow_html=True)
            
            # 显示完整段落
            st.markdown("**完整段落**:")
            with st.container():
                st.text(issue['full_paragraph'])
            
            # 显示建议（如果有）
            if 'suggestion' in issue:
                st.markdown(f"**修改建议**: {issue['suggestion']}")


def extract_year_from_filename(filename: str) -> Optional[str]:
    """从文件名中提取年份"""
    import re
    match = re.search(r'20\d{2}', filename)
    return match.group() if match else None


if __name__ == '__main__':
    main()