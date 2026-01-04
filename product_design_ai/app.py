"""
产品设计AI助手 - Streamlit应用
"""

import streamlit as st
import pandas as pd
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from process_recommender import ProcessRecommender
from process_optimizer import ProcessOptimizer
from case_retriever import CaseRetriever
from compliance_checker import ComplianceChecker
from process_visualizer import ProcessVisualizer

def init_session_state():
    """初始化session state"""
    if 'current_product' not in st.session_state:
        st.session_state.current_product = None
    if 'recommended_process' not in st.session_state:
        st.session_state.recommended_process = None
    if 'optimized_process' not in st.session_state:
        st.session_state.optimized_process = None
    if 'selected_steps' not in st.session_state:
        st.session_state.selected_steps = []  # 存储勾选的步骤
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = []  # 当前流程方案
    if 'saved_plans' not in st.session_state:
        st.session_state.saved_plans = []  # 保存的方案列表
    if 'product_name' not in st.session_state:
        st.session_state.product_name = ''  # 产品名称
    if 'product_manager' not in st.session_state:
        st.session_state.product_manager = ''  # 产品负责人

def show_home_page():
    """显示首页"""
    st.title("🎯 产品设计AI助手")
    st.markdown("---")
    
    # 系统介绍
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 系统简介
        
        产品设计AI助手是一个基于**流程挖掘、知识图谱、机器学习**的智能流程设计系统，
        帮助您快速设计新产品成立时的运营工作流程。
        
        ### ✨ 核心功能
        
        1. **🎯 智能流程推荐** - 基于产品特征推荐最优流程
        2. **⚡ 流程智能优化** - 识别瓶颈并提供优化建议
        3. **📚 相似案例检索** - 快速找到相似案例和经验
        4. **✅ 合规性检查** - 自动进行合规性检查
        5. **📊 流程可视化** - 直观展示流程和协作关系
        
        ### 🎯 解决的痛点
        
        - ❌ 流程设计不完善，与实际执行存在差异
        - ❌ 需要反复修订，耗费大量时间和人力
        - ❌ 跨部门协作复杂，协调困难
        - ❌ 经验难以复用，知识难以传承
        - ❌ 风险识别不足，潜在问题难以预见
        
        ### 📈 预期效果
        
        - ✅ **效率提升 85%+** - 流程设计时间从3-5天缩短到4-6小时
        - ✅ **修订减少 60%+** - 修订次数从3-5次减少到1-2次
        - ✅ **质量提升** - 流程完整性、合规性、可执行性显著提升
        """)
    
    with col2:
        st.info("""
        ### 📊 系统统计
        
        - **历史产品**: 50个
        - **历史流程**: 76个
        - **流程步骤**: 757个
        - **问题记录**: 146个
        - **监管规则**: 8条
        - **案例库**: 55个
        """)
        
        st.success("""
        ### 🚀 快速开始
        
        1. 点击左侧菜单选择功能
        2. 输入产品特征
        3. 获取AI推荐
        4. 查看分析结果
        5. 导出流程方案
        """)

def show_historical_products_page():
    """显示历史产品库页面"""
    st.title("📚 历史产品库")
    st.markdown("---")
    
    st.markdown("""
    ### 🔍 历史产品查询
    查看历史产品的详细信息和流程设计。
    """)
    
    # 加载历史产品数据
    try:
        import os
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'product_features.csv')
        products_df = pd.read_csv(data_path, encoding='utf-8-sig')
        
        # 筛选器
        col1, col2, col3 = st.columns(3)
        
        with col1:
            product_type_filter = st.selectbox(
                "产品类型",
                ['全部'] + list(products_df['product_type'].unique())
            )
        
        with col2:
            trading_market_filter = st.selectbox(
                "交易市场",
                ['全部'] + list(products_df['trading_market'].unique())
            )
        
        with col3:
            custodian_filter = st.selectbox(
                "托管行",
                ['全部'] + list(products_df['custodian'].unique())
            )
        
        # 应用筛选
        filtered_df = products_df.copy()
        if product_type_filter != '全部':
            filtered_df = filtered_df[filtered_df['product_type'] == product_type_filter]
        if trading_market_filter != '全部':
            filtered_df = filtered_df[filtered_df['trading_market'] == trading_market_filter]
        if custodian_filter != '全部':
            filtered_df = filtered_df[filtered_df['custodian'] == custodian_filter]
        
        st.markdown(f"### 📊 共 {len(filtered_df)} 个产品")
        
        # 显示产品列表
        for idx, product in filtered_df.iterrows():
            with st.expander(f"📦 {product['product_name']} ({product['product_type']})"):
                # 产品基本信息 - 每行4个信息
                st.markdown("#### 📋 产品基本信息")
                
                # 第一行
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**产品ID**: {product['product_id']}")
                with col2:
                    st.markdown(f"**产品类型**: {product['product_type']}")
                with col3:
                    st.markdown(f"**资产类别**: {product['asset_class']}")
                with col4:
                    st.markdown(f"**投资范围**: {product['investment_scope']}")
                
                # 第二行
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**交易市场**: {product['trading_market']}")
                with col2:
                    st.markdown(f"**托管行**: {product['custodian']}")
                with col3:
                    st.markdown(f"**投资策略**: {product['investment_strategy']}")
                with col4:
                    st.markdown(f"**风险等级**: {product['risk_level']}")
                
                # 第三行
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**交易频率**: {product['trading_frequency']}")
                with col2:
                    st.markdown(f"**结算周期**: {product['settlement_cycle']}")
                with col3:
                    st.markdown(f"**估值方法**: {product['valuation_method']}")
                with col4:
                    st.markdown(f"**披露频率**: {product['disclosure_frequency']}")
                
                if product.get('special_requirements') and product['special_requirements']:
                    st.info(f"**特殊要求**: {product['special_requirements']}")
                
                # 显示流程步骤
                st.markdown("---")
                st.markdown("#### 📝 流程步骤")
                
                try:
                    # 加载流程步骤数据
                    steps_path = os.path.join(os.path.dirname(__file__), 'data', 'process_steps.csv')
                    steps_df = pd.read_csv(steps_path, encoding='utf-8-sig')
                    
                    # 筛选该产品的步骤
                    product_steps = steps_df[steps_df['product_id'] == product['product_id']]
                    
                    if len(product_steps) > 0:
                        # 显示步骤表格
                        steps_display = []
                        for _, step in product_steps.iterrows():
                            steps_display.append({
                                '步骤名称': step['step_name'],
                                '步骤类型': step['step_type'],
                                '负责部门': step['responsible_dept'],
                                '计划时长(小时)': step['planned_duration'],
                                '状态': step['status']
                            })
                        
                        st.dataframe(pd.DataFrame(steps_display), use_container_width=True, hide_index=True)
                    else:
                        st.info("该产品暂无流程步骤记录")
                
                except Exception as e:
                    st.warning(f"无法加载流程步骤数据: {str(e)}")
    
    except Exception as e:
        st.error(f"加载历史产品数据失败: {str(e)}")
        st.info("请确保数据文件存在于 product_design_ai/data/ 目录下")

def show_process_recommendation_page():
    """显示流程推荐页面"""
    st.title("🎯 智能流程推荐")
    st.markdown("---")
    
    st.markdown("""
    ### 📝 产品信息
    请填写新产品的基本信息，系统将为您推荐最优的工作流程。
    """)
    
    # 产品特征输入
    col1, col2 = st.columns(2)
    
    with col1:
        # 新增：产品名称和产品负责人
        product_name = st.text_input("产品名称", value=st.session_state.product_name, placeholder="例如：易方达股票型基金1号")
        product_manager = st.text_input("产品负责人", value=st.session_state.product_manager, placeholder="例如：张三")
        
        # 保存到session_state
        st.session_state.product_name = product_name
        st.session_state.product_manager = product_manager
        
        product_type = st.selectbox(
            "产品类型",
            ['股票型', '债券型', '混合型', '货币型', 'QDII', 'FOF']
        )
        
        investment_scope = st.selectbox(
            "投资范围",
            ['境内股票', '境内债券', '境外股票', '境外债券', '混合资产']
        )
        
        trading_market = st.selectbox(
            "交易市场",
            ['沪深交易所', '银行间市场', '香港交易所', '美国市场', '多市场']
        )
        
        custodian = st.selectbox(
            "托管行",
            ['工商银行', '建设银行', '招商银行', '中信银行', '浦发银行']
        )
        
        investment_strategy = st.selectbox(
            "投资策略",
            ['主动管理', '被动管理', '指数跟踪', '量化投资', '混合策略']
        )
    
    with col2:
        risk_level = st.selectbox(
            "风险等级",
            ['高', '中高', '中', '中低', '低']
        )
        
        trading_frequency = st.selectbox(
            "交易频率",
            ['高频', '中频', '低频']
        )
        
        settlement_cycle = st.selectbox(
            "结算周期",
            ['T+0', 'T+1', 'T+2']
        )
        
        valuation_method = st.selectbox(
            "估值方法",
            ['市价法', '摊余成本法', '混合法']
        )
        
        disclosure_frequency = st.selectbox(
            "披露频率",
            ['每日', '每周', '季度']
        )
    
    # 推荐按钮
    if st.button("🎯 获取流程推荐", type="primary", use_container_width=True):
        with st.spinner("正在分析产品特征并推荐流程..."):
            # 构建产品特征
            product_features = {
                'product_name': product_name,
                'product_manager': product_manager,
                'product_type': product_type,
                'asset_class': product_type.replace('型', ''),
                'investment_scope': investment_scope,
                'trading_market': trading_market,
                'custodian': custodian,
                'investment_strategy': investment_strategy,
                'risk_level': risk_level,
                'trading_frequency': trading_frequency,
                'settlement_cycle': settlement_cycle,
                'valuation_method': valuation_method,
                'disclosure_frequency': disclosure_frequency
            }
            
            # 保存到session state
            st.session_state.current_product = product_features
            
            # 获取推荐
            recommender = ProcessRecommender()
            recommendations = recommender.recommend_process(product_features, top_n=3)
            
            if recommendations:
                # 生成推荐流程
                recommended_process = recommender.generate_recommended_process(
                    product_features, 
                    recommendations[0]
                )
                st.session_state.recommended_process = recommended_process
                
                st.success("✅ 流程推荐完成！")
    
    # 显示推荐结果
    if st.session_state.recommended_process:
        st.markdown("---")
        st.markdown("### 📊 推荐结果")
        
        result = st.session_state.recommended_process
        
        # 基础信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总步骤数", f"{result['total_steps']}个")
        with col2:
            st.metric("预计时长", f"{result['total_duration']:.1f}小时")
        with col3:
            st.metric("风险点数", f"{result['risk_count']}个")
        with col4:
            similarity = result['base_process']['similarity']
            st.metric("相似度", f"{similarity:.1%}")
        
        # 参考产品信息
        st.info(f"""
        **参考产品**: {result['base_process']['product_name']}  
        **产品类型**: {result['base_process']['product_type']}  
        **质量分数**: {result['base_process']['quality_score']:.1%}
        """)
        
        # 流程步骤 - 添加勾选功能
        st.markdown("#### 📋 推荐流程步骤")
        
        # 显示表头
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 0.8, 2, 1.2, 1.2, 1, 1, 0.8])
        with col1:
            st.markdown("**勾选**")
        with col2:
            st.markdown("**序号**")
        with col3:
            st.markdown("**步骤名称**")
        with col4:
            st.markdown("**步骤类型**")
        with col5:
            st.markdown("**负责部门**")
        with col6:
            st.markdown("**时长(h)**")
        with col7:
            st.markdown("**风险**")
        with col8:
            st.markdown("**状态**")
        
        # 显示步骤表格，每行添加勾选框，序号从1开始
        for i, step in enumerate(result['recommended_steps'], 1):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 0.8, 2, 1.2, 1.2, 1, 1, 0.8])
            
            with col1:
                # 勾选框 - 使用唯一的key（结合索引和step_order）
                unique_key = f"select_step_{i}_{step['step_order']}"
                is_selected = st.checkbox(
                    "",
                    value=step['step_order'] in [s['step_order'] for s in st.session_state.current_plan],
                    key=unique_key
                )
                
                # 如果勾选状态改变，更新当前方案
                if is_selected:
                    # 添加到当前方案（如果不存在）
                    if step['step_order'] not in [s['step_order'] for s in st.session_state.current_plan]:
                        st.session_state.current_plan.append(step)
                        # 按step_order排序
                        st.session_state.current_plan.sort(key=lambda x: x['step_order'])
                else:
                    # 从当前方案中移除
                    st.session_state.current_plan = [
                        s for s in st.session_state.current_plan
                        if s['step_order'] != step['step_order']
                    ]
            
            with col2:
                st.markdown(f"**{i}**")
            with col3:
                st.markdown(step['step_name'])
            with col4:
                st.markdown(step['step_type'])
            with col5:
                st.markdown(step['responsible_dept'])
            with col6:
                st.markdown(f"{step['planned_duration']}")
            with col7:
                st.markdown(step['risk_level'])
            with col8:
                st.markdown('⚠️' if step['has_risk'] else '✅')
        
        # 显示表头（在第一行之前）
        st.markdown("---")
        
        # 风险警告
        if result['risk_warnings']:
            st.markdown("#### ⚠️ 风险警告")
            
            for warning in result['risk_warnings']:
                with st.expander(f"⚠️ {warning['step_name']} - {warning['risk_type']}"):
                    st.warning(f"**风险描述**: {warning['risk_desc']}")
                    st.info(f"**根本原因**: {warning['root_cause']}")
                    st.success(f"**建议措施**: {warning['suggestion']}")
                    st.caption(f"影响程度: {warning['impact_level']}")
        
        # 当前流程方案模块
        st.markdown("---")
        st.markdown("### 📝 当前流程方案")
        
        if st.session_state.current_plan:
            st.info(f"已选择 {len(st.session_state.current_plan)} 个步骤")
            
            # 显示当前方案 - 序号从1开始重新排列，每行添加移除按钮
            for idx, step in enumerate(st.session_state.current_plan, 1):
                col1, col2, col3, col4, col5, col6, col7 = st.columns([0.6, 1.5, 1.2, 1.2, 1, 1, 0.8])
                
                with col1:
                    st.markdown(f"**{idx}**")
                with col2:
                    st.markdown(step['step_name'])
                with col3:
                    st.markdown(step['step_type'])
                with col4:
                    st.markdown(step['responsible_dept'])
                with col5:
                    st.markdown(f"{step['planned_duration']}")
                with col6:
                    st.markdown(step['risk_level'])
                with col7:
                    if st.button("🗑️", key=f"remove_step_{idx}_{step['step_order']}", help="移除此步骤"):
                        st.session_state.current_plan.pop(idx - 1)
                        st.rerun()
            
            # 添加步骤和保存方案按钮
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ 添加步骤", use_container_width=True):
                    st.session_state.show_add_step_form = True
            
            with col2:
                if st.button("💾 保存方案", type="primary", use_container_width=True):
                    # 保存当前方案
                    from datetime import datetime
                    # 使用产品名称作为方案名称的一部分
                    product_name_part = st.session_state.product_name if st.session_state.product_name else "未命名产品"
                    plan_name = f"{product_name_part}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    saved_plan = {
                        'plan_name': plan_name,
                        'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'steps': st.session_state.current_plan.copy(),
                        'product_info': st.session_state.current_product
                    }
                    st.session_state.saved_plans.append(saved_plan)
                    st.success(f"✅ 方案已保存：{plan_name}")
            
            # 添加步骤表单
            if st.session_state.get('show_add_step_form', False):
                st.markdown("#### ➕ 添加自定义步骤")
                
                with st.form("add_step_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_step_name = st.text_input("步骤名称", placeholder="例如：风险评估")
                        new_step_type = st.selectbox("步骤类型", ['交易', '清算', '估值', '披露', '合规检查', '风险监控', '托管核对'])
                        new_dept = st.selectbox("负责部门", ['交易部', '清算部', '估值部', '披露部', '合规部', '风控部'])
                    
                    with col2:
                        new_duration = st.number_input("计划时长(小时)", min_value=0.5, max_value=24.0, value=1.0, step=0.5)
                        new_risk_level = st.selectbox("风险等级", ['高', '中', '低'])
                        # 新增：插入位置
                        insert_position = st.number_input(
                            "插入位置（序号）",
                            min_value=1,
                            max_value=len(st.session_state.current_plan) + 1 if st.session_state.current_plan else 1,
                            value=len(st.session_state.current_plan) + 1 if st.session_state.current_plan else 1,
                            step=1,
                            help="新步骤将插入到此序号位置，原步骤顺延"
                        )
                    
                    col_submit, col_cancel = st.columns(2)
                    
                    with col_submit:
                        submitted = st.form_submit_button("✅ 添加", use_container_width=True)
                        if submitted and new_step_name:
                            # 创建新步骤
                            new_step = {
                                'step_order': 0,  # 临时值，后面会重新分配
                                'step_name': new_step_name,
                                'step_type': new_step_type,
                                'responsible_dept': new_dept,
                                'planned_duration': new_duration,
                                'risk_level': new_risk_level,
                                'has_risk': new_risk_level == '高'
                            }
                            
                            # 插入到指定位置（insert_position是从1开始的）
                            insert_index = int(insert_position) - 1
                            st.session_state.current_plan.insert(insert_index, new_step)
                            
                            # 重新分配step_order（保持原有顺序）
                            for idx, step in enumerate(st.session_state.current_plan):
                                step['step_order'] = idx + 1
                            
                            st.session_state.show_add_step_form = False
                            st.success(f"✅ 步骤已插入到第{insert_position}位")
                            st.rerun()
                    
                    with col_cancel:
                        cancelled = st.form_submit_button("❌ 取消", use_container_width=True)
                        if cancelled:
                            st.session_state.show_add_step_form = False
                            st.rerun()
            
            # 显示已保存的方案
            if st.session_state.saved_plans:
                st.markdown("---")
                st.markdown("### 💾 已保存的方案")
                
                for i, plan in enumerate(st.session_state.saved_plans):
                    with st.expander(f"📋 {plan['plan_name']} (创建时间: {plan['create_time']})"):
                        st.markdown(f"**步骤数**: {len(plan['steps'])}个")
                        
                        plan_steps_data = []
                        for idx, step in enumerate(plan['steps'], 1):
                            plan_steps_data.append({
                                '序号': idx,
                                '步骤名称': step['step_name'],
                                '步骤类型': step['step_type'],
                                '负责部门': step['responsible_dept'],
                                '计划时长(小时)': step['planned_duration']
                            })
                        
                        st.dataframe(pd.DataFrame(plan_steps_data), use_container_width=True, hide_index=True)
                        
                        # 添加一键复用和删除按钮
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("🔄 一键复用", key=f"reuse_plan_{i}", use_container_width=True):
                                # 复用方案到当前流程方案
                                st.session_state.current_plan = plan['steps'].copy()
                                st.success(f"✅ 已复用方案：{plan['plan_name']}")
                                st.rerun()
                        
                        with col_btn2:
                            if st.button("🗑️ 删除", key=f"delete_plan_{i}", use_container_width=True):
                                # 删除方案
                                st.session_state.saved_plans.pop(i)
                                st.success(f"✅ 已删除方案：{plan['plan_name']}")
                                st.rerun()
        else:
            st.info("请从推荐流程中勾选步骤，或点击\"添加步骤\"按钮添加自定义步骤")

def show_process_optimization_page():
    """显示流程优化页面"""
    st.title("⚡ 流程智能优化")
    st.markdown("---")
    
    # 方案选择
    st.markdown("### 📋 选择分析方案")
    
    # 构建方案选项
    plan_options = []
    if st.session_state.current_plan:
        plan_options.append("当前流程方案")
    if st.session_state.recommended_process:
        plan_options.append("推荐流程")
    if st.session_state.saved_plans:
        for i, plan in enumerate(st.session_state.saved_plans):
            plan_options.append(f"已保存方案: {plan['plan_name']}")
    
    if not plan_options:
        st.warning("⚠️ 请先在【智能流程推荐】页面获取推荐流程或创建当前方案")
        return
    
    selected_plan = st.selectbox(
        "选择要分析的方案",
        plan_options,
        help="选择一个方案进行优化分析"
    )
    
    # 根据选择获取步骤数据
    if selected_plan == "当前流程方案":
        steps_to_analyze = st.session_state.current_plan
        st.info("📝 将对当前流程方案进行优化分析")
    elif selected_plan == "推荐流程":
        steps_to_analyze = st.session_state.recommended_process['recommended_steps']
        st.info("📋 将对推荐流程进行优化分析")
    else:
        # 从已保存方案中获取
        for plan in st.session_state.saved_plans:
            if f"已保存方案: {plan['plan_name']}" == selected_plan:
                steps_to_analyze = plan['steps']
                st.info(f"💾 将对已保存方案「{plan['plan_name']}」进行优化分析")
                break
    
    st.markdown("""
    ### 🔍 流程分析
    系统将分析流程，识别瓶颈并提供优化建议。
    """)
    
    if st.button("⚡ 开始优化分析", type="primary", use_container_width=True):
        with st.spinner("正在分析流程并生成优化建议..."):
            # 转换为DataFrame格式，添加actual_duration字段
            steps_data = []
            for step in steps_to_analyze:
                step_data = step.copy()
                # 添加actual_duration字段（模拟实际执行时间，为计划时长的0.8-1.5倍）
                import random
                step_data['actual_duration'] = step['planned_duration'] * random.uniform(0.8, 1.5)
                steps_data.append(step_data)
            
            steps_df = pd.DataFrame(steps_data)
            
            # 模拟问题数据
            issues_data = []
            if st.session_state.recommended_process and 'risk_warnings' in st.session_state.recommended_process:
                for warning in st.session_state.recommended_process['risk_warnings']:
                    issues_data.append({
                        'issue_type': warning['risk_type'],
                        'issue_desc': warning['risk_desc'],
                        'root_cause': warning['root_cause'],
                        'solution': warning['suggestion'],
                        'impact_level': warning['impact_level']
                    })
            issues_df = pd.DataFrame(issues_data) if issues_data else pd.DataFrame()
            
            # 执行优化
            optimizer = ProcessOptimizer()
            optimization_result = optimizer.optimize_process(steps_df, issues_df)
            
            st.session_state.optimized_process = optimization_result
            st.success("✅ 优化分析完成！")
    
    # 显示优化结果
    if st.session_state.optimized_process:
        st.markdown("---")
        st.markdown("### 📊 优化分析结果")
        
        result = st.session_state.optimized_process
        
        # 优化影响
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("预计节省时间", f"{result['impact']['time_saving']:.1f}小时")
        with col2:
            st.metric("预计减少问题", f"{result['impact']['issue_reduction']}个")
        with col3:
            st.metric("效率提升", f"{result['impact']['efficiency_improvement']:.1f}%")
        
        # 优化建议
        st.markdown("#### 💡 优化建议")
        
        suggestions = result['suggestions']
        
        # 按优先级分组
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        medium_priority = [s for s in suggestions if s['priority'] == 'medium']
        
        if high_priority:
            st.markdown("##### 🔴 高优先级建议")
            for i, suggestion in enumerate(high_priority, 1):
                with st.expander(f"{i}. [{suggestion['category']}] {suggestion['target']}"):
                    st.error(f"**问题**: {suggestion['problem']}")
                    st.info(f"**建议**: {suggestion['suggestion']}")
                    st.success(f"**预期收益**: {suggestion['expected_benefit']}")
        
        if medium_priority:
            st.markdown("##### 🟡 中优先级建议")
            for i, suggestion in enumerate(medium_priority, 1):
                with st.expander(f"{i}. [{suggestion['category']}] {suggestion['target']}"):
                    st.warning(f"**问题**: {suggestion['problem']}")
                    st.info(f"**建议**: {suggestion['suggestion']}")
                    st.success(f"**预期收益**: {suggestion['expected_benefit']}")

def show_case_retrieval_page():
    """显示案例检索页面"""
    st.title("📚 相似案例检索")
    st.markdown("---")
    
    st.markdown("""
    ### 🔍 案例检索
    输入您遇到的问题或场景，系统将为您检索相似的历史案例。
    """)
    
    # 检索条件
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "问题描述",
            placeholder="例如：股票型产品估值核对延迟问题"
        )
    
    with col2:
        product_type_filter = st.selectbox(
            "产品类型",
            ['全部', '股票型', '债券型', '混合型', '货币型', 'QDII', 'FOF']
        )
    
    if st.button("🔍 检索案例", type="primary", use_container_width=True):
        if query:
            with st.spinner("正在检索相似案例..."):
                retriever = CaseRetriever()
                
                product_type = None if product_type_filter == '全部' else product_type_filter
                results = retriever.search_cases(query, product_type=product_type, top_n=5)
                
                st.markdown("---")
                st.markdown(f"### 📊 检索结果（共{len(results)}个）")
                
                for idx, case in results.iterrows():
                    similarity = case['similarity']
                    
                    # 根据相似度设置颜色
                    if similarity > 0.5:
                        badge = "🟢 高度相关"
                    elif similarity > 0.3:
                        badge = "🟡 中度相关"
                    else:
                        badge = "🔴 低度相关"
                    
                    with st.expander(f"{badge} - {case['scenario']} (相似度: {similarity:.1%})"):
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            st.markdown(f"""
                            **产品类型**: {case['product_type']}  
                            **案例类型**: {case['case_type']}  
                            **相似度**: {similarity:.1%}
                            """)
                        
                        with col2:
                            st.markdown(f"**问题描述**: {case['problem_desc']}")
                            st.markdown(f"**根本原因**: {case['root_cause']}")
                            st.markdown(f"**解决方案**: {case['solution']}")
                            st.info(f"💡 **经验教训**: {case['lessons_learned']}")
                            st.success(f"✅ **最佳实践**: {case['best_practices']}")
        else:
            st.warning("请输入问题描述")

def show_compliance_check_page():
    """显示合规检查页面"""
    st.title("✅ 合规性检查")
    st.markdown("---")
    
    # 方案选择
    st.markdown("### 📋 选择检查方案")
    
    # 构建方案选项
    plan_options = []
    if st.session_state.current_plan:
        plan_options.append("当前流程方案")
    if st.session_state.recommended_process:
        plan_options.append("推荐流程")
    if st.session_state.saved_plans:
        for i, plan in enumerate(st.session_state.saved_plans):
            plan_options.append(f"已保存方案: {plan['plan_name']}")
    
    if not plan_options:
        st.warning("⚠️ 请先在【智能流程推荐】页面获取推荐流程或创建当前方案")
        return
    
    selected_plan = st.selectbox(
        "选择要检查的方案",
        plan_options,
        help="选择一个方案进行合规性检查"
    )
    
    # 根据选择获取步骤数据
    if selected_plan == "当前流程方案":
        steps_to_check = st.session_state.current_plan
        st.info("📝 将对当前流程方案进行合规性检查")
    elif selected_plan == "推荐流程":
        steps_to_check = st.session_state.recommended_process['recommended_steps']
        st.info("📋 将对推荐流程进行合规性检查")
    else:
        # 从已保存方案中获取
        for i, plan in enumerate(st.session_state.saved_plans):
            if f"已保存方案: {plan['plan_name']}" == selected_plan:
                steps_to_check = plan['steps']
                st.info(f"💾 将对已保存方案「{plan['plan_name']}」进行合规性检查")
                break
    
    if not st.session_state.current_product:
        st.warning("⚠️ 请先在【智能流程推荐】页面输入产品信息")
        return
    
    st.markdown("""
    ### 🔍 合规性检查
    系统将检查流程是否符合监管规则要求。
    """)
    
    if st.button("✅ 开始合规检查", type="primary", use_container_width=True):
        with st.spinner("正在进行合规性检查..."):
            product_features = st.session_state.current_product
            
            # 执行合规检查
            checker = ComplianceChecker()
            compliance_result = checker.check_process_compliance(
                product_features,
                steps_to_check
            )
            
            # 生成报告
            report = checker.generate_compliance_report(compliance_result)
            
            st.markdown("---")
            st.markdown("### 📊 合规检查结果")
            
            # 合规分数
            score = compliance_result['compliance_score']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("合规分数", f"{score:.1f}%")
            with col2:
                st.metric("合规规则", f"{compliance_result['compliant_rules']}/{compliance_result['total_rules']}")
            with col3:
                st.metric("不合规项", f"{compliance_result['non_compliant_rules']}个")
            with col4:
                status = report['summary']['status']
                st.metric("状态", status)
            
            # 合规状态
            if score >= 90:
                st.success(f"✅ 流程设计符合监管要求（合规分数: {score:.1f}%）")
            else:
                st.warning(f"⚠️ 流程设计需要整改（合规分数: {score:.1f}%）")
            
            # 不合规项
            if report['non_compliant_items']:
                st.markdown("#### ⚠️ 不合规项")
                
                for item in report['non_compliant_items']:
                    with st.expander(f"⚠️ {item['rule_name']} - {item['rule_category']}"):
                        st.error(f"**问题**: {item['reason']}")
                        
                        # 找到对应的建议
                        suggestion = next(
                            (r['suggestion'] for r in report['recommendations'] 
                             if r['rule_name'] == item['rule_name']),
                            '请参考监管规则进行整改'
                        )
                        st.info(f"**整改建议**: {suggestion}")
            else:
                st.success("✅ 所有监管规则检查通过！")
            
            # 适用规则列表
            with st.expander("📋 查看所有适用规则"):
                rules_data = []
                for check in compliance_result['check_results']:
                    rules_data.append({
                        '规则名称': check['rule_name'],
                        '规则类别': check['rule_category'],
                        '合规状态': '✅ 合规' if check['compliant'] else '❌ 不合规',
                        '检查结果': check['reason']
                    })
                
                st.dataframe(pd.DataFrame(rules_data), use_container_width=True, hide_index=True)

def show_visualization_page():
    """显示流程可视化页面"""
    st.title("📊 流程可视化")
    st.markdown("---")
    
    # 方案选择
    st.markdown("### 📋 选择可视化方案")
    
    # 构建方案选项
    plan_options = []
    if st.session_state.current_plan:
        plan_options.append("当前流程方案")
    if st.session_state.recommended_process:
        plan_options.append("推荐流程")
    if st.session_state.saved_plans:
        for i, plan in enumerate(st.session_state.saved_plans):
            plan_options.append(f"已保存方案: {plan['plan_name']}")
    
    if not plan_options:
        st.warning("⚠️ 请先在【智能流程推荐】页面获取推荐流程或创建当前方案")
        return
    
    selected_plan = st.selectbox(
        "选择要可视化的方案",
        plan_options,
        help="选择一个方案进行可视化展示"
    )
    
    # 根据选择获取步骤数据
    risk_warnings = []
    if selected_plan == "当前流程方案":
        steps_to_visualize = st.session_state.current_plan
        st.info("📝 正在可视化当前流程方案")
    elif selected_plan == "推荐流程":
        steps_to_visualize = st.session_state.recommended_process['recommended_steps']
        risk_warnings = st.session_state.recommended_process.get('risk_warnings', [])
        st.info("📋 正在可视化推荐流程")
    else:
        # 从已保存方案中获取
        for i, plan in enumerate(st.session_state.saved_plans):
            if f"已保存方案: {plan['plan_name']}" == selected_plan:
                steps_to_visualize = plan['steps']
                st.info(f"💾 正在可视化已保存方案「{plan['plan_name']}」")
                break
    
    visualizer = ProcessVisualizer()
    
    # 流程摘要
    summary = visualizer.create_process_summary(
        steps_to_visualize,
        risk_warnings
    )
    
    st.markdown("### 📋 流程摘要")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总步骤数", f"{summary['total_steps']}个")
    with col2:
        st.metric("总时长", f"{summary['total_duration']:.1f}小时")
    with col3:
        st.metric("涉及部门", f"{summary['involved_departments']}个")
    with col4:
        st.metric("风险警告", f"{summary['risk_warnings']}个")
    
    # 可视化图表
    st.markdown("---")
    
    # 时长分布
    st.markdown("### ⏱️ 步骤时长分布")
    fig_duration = visualizer.create_duration_chart(steps_to_visualize)
    st.plotly_chart(fig_duration, use_container_width=True)
    
    # 甘特图
    st.markdown("### 📅 流程时间规划")
    fig_gantt = visualizer.create_gantt_chart(steps_to_visualize)
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    # 部门工作量和风险分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 部门工作量分布")
        fig_workload = visualizer.create_department_workload_chart(steps_to_visualize)
        st.plotly_chart(fig_workload, use_container_width=True)
    
    with col2:
        st.markdown("### ⚠️ 风险分布")
        fig_risk = visualizer.create_risk_distribution_chart(steps_to_visualize)
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # 协作矩阵
    st.markdown("### 🤝 部门协作矩阵")
    fig_collab = visualizer.create_collaboration_matrix(steps_to_visualize)
    st.plotly_chart(fig_collab, use_container_width=True)

def main():
    """主函数"""
    init_session_state()
    
    # 侧边栏
    with st.sidebar:
        st.title("📋 功能菜单")
        
        page = st.radio(
            "选择功能",
            [
                "🏠 首页概览",
                "🎯 智能流程推荐",
                "⚡ 流程智能优化",
                "✅ 合规性检查",
                "📊 流程可视化",
                "🔍 相似案例检索",
                "📚 历史产品库"
            ]
        )
        
        st.markdown("---")
        st.markdown("""
        ### 💡 使用提示
        
        1. 先在【智能流程推荐】输入产品信息
        2. 获取推荐流程后可使用其他功能
        3. 查看优化建议和合规检查
        4. 参考相似案例经验
        5. 通过可视化图表分析流程
        """)
    
    # 主内容区
    if page == "🏠 首页概览":
        show_home_page()
    elif page == "🎯 智能流程推荐":
        show_process_recommendation_page()
    elif page == "⚡ 流程智能优化":
        show_process_optimization_page()
    elif page == "✅ 合规性检查":
        show_compliance_check_page()
    elif page == "📊 流程可视化":
        show_visualization_page()
    elif page == "🔍 相似案例检索":
        show_case_retrieval_page()
    elif page == "📚 历史产品库":
        show_historical_products_page()

if __name__ == '__main__':
    main()