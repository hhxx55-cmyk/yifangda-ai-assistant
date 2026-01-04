# -*- coding: utf-8 -*-
"""
境外资管运营AI优化方案 - 主入口
包含5个AI助手模块的导航界面
"""

import streamlit as st
import sys
import os

# 页面配置
st.set_page_config(
    page_title="境外资管运营AI优化方案",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"  # 默认展开侧边栏
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    /* 模块卡片样式 */
    .module-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        color: white;
        text-align: center;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .module-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .module-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .module-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .module-desc {
        font-size: 1rem;
        opacity: 0.9;
        line-height: 1.6;
    }
    
    .module-status {
        margin-top: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .status-ready {
        background-color: rgba(76, 175, 80, 0.3);
        border: 1px solid rgba(76, 175, 80, 0.5);
    }
    
    .status-coming {
        background-color: rgba(255, 193, 7, 0.3);
        border: 1px solid rgba(255, 193, 7, 0.5);
    }
    
    /* 渐变背景色 */
    .gradient-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .gradient-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .gradient-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .gradient-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .gradient-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    
    /* 信息卡片 */
    .info-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 2rem 0;
    }
    
    .feature-list {
        list-style: none;
        padding-left: 0;
    }
    
    .feature-list li {
        padding: 0.5rem 0;
        padding-left: 2rem;
        position: relative;
    }
    
    .feature-list li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    
    # 检查是否选择了模块
    if 'selected_module' not in st.session_state:
        st.session_state.selected_module = None
    
    # 如果已选择模块，跳转到对应页面
    if st.session_state.selected_module:
        show_module_page(st.session_state.selected_module)
        return
    
    # 显示主页
    show_home_page()


def show_home_page():
    """显示主页"""
    
    # 标题
    st.markdown('<div class="main-title">🤖 境外资管运营AI优化方案</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Overseas Asset Management Operations AI Optimization Solution</div>', unsafe_allow_html=True)
    
    # 简介
    st.markdown("""
    <div class="info-card">
        <h3>📋 方案概述</h3>
        <p>本方案针对境外基金运营部的多个工作场景，基于主流人工智能模型，提供智能化的运营优化解决方案。</p>
        <p>通过AI技术提升运营效率、降低人工错误率、优化工作流程，实现运营工作的智能化转型。</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## 🎯 选择AI助手模块")
    st.markdown("")
    
    # 创建5个模块卡片
    col1, col2 = st.columns(2)
    
    with col1:
        # 模块1：估值核对AI助手
        st.markdown("""
        <div class="module-card gradient-1">
            <div class="module-icon">📊</div>
            <div class="module-title">估值核对AI助手</div>
            <div class="module-desc">
                智能识别估值差异、自动分析根本原因<br>
                推荐解决方案、预测处理时长<br>
                提升估值核对效率85%以上
            </div>
            <div class="module-status status-ready">✓ 已上线</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("进入估值核对AI助手", key="btn_valuation", use_container_width=True):
            st.session_state.selected_module = "valuation"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 模块3：年报核对AI助手
        st.markdown("""
        <div class="module-card gradient-3">
            <div class="module-icon">📄</div>
            <div class="module-title">年报核对AI助手</div>
            <div class="module-desc">
                自动核对年报数据前后勾稽关系<br>
                智能检查文字内容语法和表述<br>
                生成优化建议和修改方案
            </div>
            <div class="module-status status-ready">✓ 已上线</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("进入年报核对AI助手", key="btn_report", use_container_width=True):
            st.session_state.selected_module = "report"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 模块5：邮件处理AI助手
        st.markdown("""
        <div class="module-card gradient-5">
            <div class="module-icon">📧</div>
            <div class="module-title">邮件处理AI助手</div>
            <div class="module-desc">
                智能分类和优先级排序邮件<br>
                自动识别关键信息和待办事项<br>
                提醒重要邮件，避免遗漏
            </div>
            <div class="module-status status-ready">✓ 已上线</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("进入邮件处理AI助手", key="btn_email", use_container_width=True):
            st.session_state.selected_module = "email"
            st.rerun()
    
    with col2:
        # 模块2：标的交收AI助手
        st.markdown("""
        <div class="module-card gradient-2">
            <div class="module-icon">🔄</div>
            <div class="module-title">标的交收AI助手</div>
            <div class="module-desc">
                智能监控交收流程各环节<br>
                预警潜在延迟和遗漏风险<br>
                自动生成交收确认报告
            </div>
            <div class="module-status status-ready">✓ 已上线</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("进入标的交收AI助手", key="btn_settlement", use_container_width=True):
            st.session_state.selected_module = "settlement"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 模块4：产品设计AI助手
        st.markdown("""
        <div class="module-card gradient-4">
            <div class="module-icon">🎨</div>
            <div class="module-title">产品设计AI助手</div>
            <div class="module-desc">
                智能设计多边运营工作流程<br>
                识别流程设计中的潜在问题<br>
                提供最佳实践和优化建议
            </div>
            <div class="module-status status-ready">✓ 已上线</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("进入产品设计AI助手", key="btn_product", use_container_width=True):
            st.session_state.selected_module = "product"
            st.rerun()
    
    # 底部信息
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>🎯 核心优势</h4>
            <ul class="feature-list">
                <li>AI驱动的智能分析</li>
                <li>实时监控和预警</li>
                <li>自动化流程优化</li>
                <li>历史数据学习</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>📈 预期效果</h4>
            <ul class="feature-list">
                <li>效率提升 80%+</li>
                <li>错误率降低 90%+</li>
                <li>处理时长减少 70%+</li>
                <li>人工成本节省 60%+</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>🔧 技术栈</h4>
            <ul class="feature-list">
                <li>机器学习算法</li>
                <li>自然语言处理</li>
                <li>异常检测模型</li>
                <li>智能推荐系统</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def show_module_page(module):
    """显示模块页面"""
    
    # 返回按钮
    if st.button("← 返回主页", key="back_home"):
        st.session_state.selected_module = None
        st.rerun()
    
    st.markdown("---")
    
    if module == "valuation":
        # 运行估值核对AI助手
        show_valuation_assistant()
    
    elif module == "settlement":
        # 运行标的交收AI助手
        show_settlement_assistant()
    
    elif module == "report":
        # 运行年报核对AI助手
        show_annual_report_assistant()
    
    elif module == "product":
        # 运行产品设计AI助手
        show_product_design_assistant()
    
    elif module == "email":
        # 运行邮件处理AI助手
        show_email_processing_assistant()


def show_coming_soon_page(title, module_key, features):
    """显示即将上线页面"""
    
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Coming Soon...</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 📋 功能规划")
        st.markdown("")
        
        for i, feature in enumerate(features, 1):
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #1f77b4;">
                <strong>{i}. {feature}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.info("💡 该模块正在开发中，敬请期待！")
    
    with col2:
        st.markdown("## 📊 开发进度")
        st.markdown("")
        
        progress_data = {
            "需求分析": 100,
            "方案设计": 100,
            "数据准备": 60,
            "模型训练": 30,
            "界面开发": 20,
            "测试优化": 0
        }
        
        for stage, progress in progress_data.items():
            st.markdown(f"**{stage}**")
            st.progress(progress / 100)
            st.markdown(f"<small>{progress}%</small>", unsafe_allow_html=True)
            st.markdown("")
        
        st.markdown("---")
        st.markdown("### 📅 预计上线时间")
        st.markdown("**2025年 Q1**")


def show_valuation_assistant():
    """显示估值核对AI助手"""
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime
    import sys
    import os
    
    # 添加valuation_ai目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'valuation_ai'))
    
    from valuation_ai.data_generator import ValuationDataGenerator
    from valuation_ai.ai_analyzer import ValuationAIAnalyzer
    
    # 自定义CSS（估值核对专用）
    st.markdown("""
    <style>
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
    
    # 初始化系统
    @st.cache_resource
    def initialize_valuation_system():
        generator = ValuationDataGenerator(seed=42)
        analyzer = ValuationAIAnalyzer()
        return generator, analyzer
    
    @st.cache_data
    def load_valuation_data():
        generator, _ = initialize_valuation_system()
        df_diff = generator.generate_valuation_differences(n_records=100)
        df_cases = generator.generate_historical_cases(n_cases=50)
        df_rules = generator.generate_valuation_rules()
        return df_diff, df_cases, df_rules
    
    # 标题
    st.markdown('<div class="main-title">🤖 估值核对AI助手</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 初始化
    generator, analyzer = initialize_valuation_system()
    df_diff, df_cases, df_rules = load_valuation_data()
    
    # 侧边栏
    with st.sidebar:
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
        st.metric("总差异记录", len(df_diff))
        st.metric("待处理差异", len(df_diff[df_diff['status'] == 'Pending']))
        st.metric("历史案例", len(df_cases))
        
        st.markdown("---")
        st.markdown("### ℹ️ 关于")
        st.info("**版本**: v1.0\n\n**作者**: Kilo Code\n\n**更新**: 2024-12-22")
    
    # 导入估值核对的页面函数
    from valuation_ai.app import (
        show_home_page,
        show_data_analysis_page,
        show_ai_diagnosis_page,
        show_historical_cases_page,
        show_settings_page
    )
    
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


def show_settlement_assistant():
    """显示标的交收AI助手"""
    import sys
    import os
    
    # 添加settlement_ai目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'settlement_ai'))
    
    # 导入并运行标的交收应用
    from settlement_ai.app import main as settlement_main
    settlement_main()


def show_annual_report_assistant():
    """显示年报核对AI助手"""
    import sys
    import os
    
    # 添加annual_report_ai目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'annual_report_ai'))
    
    # 导入并运行年报核对应用（使用重构版本）
    from annual_report_ai.app_v2 import main as annual_report_main
    annual_report_main()


def show_product_design_assistant():
    """显示产品设计AI助手"""
    import sys
    import os
    
    # 添加product_design_ai目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'product_design_ai'))
    
    # 导入并运行产品设计应用
    from product_design_ai.app import main as product_design_main
    product_design_main()


def show_email_processing_assistant():
    """显示邮件处理AI助手"""
    import sys
    import os
    
    # 添加email_processing_ai目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'email_processing_ai'))
    
    # 导入并运行邮件处理应用
    from email_processing_ai.app import main as email_processing_main
    email_processing_main()


if __name__ == '__main__':
    main()