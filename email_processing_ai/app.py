"""
邮件处理AI助手 - Streamlit演示应用
展示核心功能和技术方案
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import re

def init_session_state():
    """初始化session state"""
    if 'demo_emails' not in st.session_state:
        st.session_state.demo_emails = generate_demo_emails()
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'role': '全部',  # 默认显示全部
            'interested_categories': ['估值', '清算'],
            'notification_level': '高优先级'
        }
    if 'selected_keyword' not in st.session_state:
        st.session_state.selected_keyword = None
    if 'email_processed_status' not in st.session_state:
        st.session_state.email_processed_status = {}  # 存储邮件处理状态
    if 'sorting_rules' not in st.session_state:
        # 默认排序规则
        st.session_state.sorting_rules = {
            'sender_weight': 3,
            'keyword_weight': 3,
            'timeliness_weight': 2,
            'behavior_weight': 2
        }
    if 'email_handlers' not in st.session_state:
        st.session_state.email_handlers = {}  # 存储邮件处理人分配
    if 'operation_logs' not in st.session_state:
        st.session_state.operation_logs = []  # 存储操作日志

def generate_demo_emails():
    """生成100封演示邮件数据"""
    # 导入邮件生成器
    try:
        from email_generator import generate_realistic_emails
        return generate_realistic_emails()
    except:
        # 如果导入失败，使用简化版本
        return generate_simple_emails()

def generate_simple_emails():
    """生成简化版邮件数据"""
    categories = ['交易', '清算', '估值', '披露', '合规', '风控', '其他']
    priorities = ['紧急', '重要', '普通']
    senders = [
        '托管行-工商银行', '托管行-建设银行', '交易对手-中信证券',
        '监管机构-证监会', '内部-交易部', '内部-清算部', '内部-风控部'
    ]
    
    emails = []
    base_time = datetime.now() - timedelta(days=1)
    
    # 生成100封演示邮件
    for i in range(100):
        category = random.choice(categories)
        priority = random.choice(priorities)
        sender = random.choice(senders)
        
        # 根据类别生成相应的主题和内容
        if category == '估值':
            subjects = [
                f'【{priority}】{datetime.now().strftime("%Y%m%d")}估值数据核对',
                f'估值差异说明 - 产品{random.randint(1,10)}号',
                f'托管行估值核对结果 - {datetime.now().strftime("%m月%d日")}',
                f'估值调整通知 - 紧急处理'
            ]
            body_templates = [
                f'请核对今日估值数据，发现{random.randint(1,5)}笔差异需要确认。',
                f'产品估值与托管行存在差异，金额{random.randint(1000,50000)}元。',
                f'估值核对完成，无差异。',
                f'发现估值异常，请立即处理。'
            ]
        elif category == '交易':
            subjects = [
                f'交易确认 - {random.randint(100,999)}号',
                f'交易失败通知',
                f'交易指令执行完成',
                f'【紧急】交易异常处理'
            ]
            body_templates = [
                f'交易已执行，成交金额{random.randint(100,1000)}万元。',
                f'交易失败，原因：资金不足。',
                f'交易指令已全部执行完成。',
                f'发现交易异常，请立即确认。'
            ]
        elif category == '清算':
            subjects = [
                f'清算数据确认 - {datetime.now().strftime("%Y%m%d")}',
                f'资金清算通知',
                f'清算差异说明',
                f'清算完成确认'
            ]
            body_templates = [
                f'今日清算数据已生成，请确认。',
                f'资金清算金额{random.randint(1000,10000)}万元。',
                f'发现清算差异，需要核对。',
                f'清算已完成，无差异。'
            ]
        else:
            subjects = [f'{category}相关事项 - {i+1}']
            body_templates = [f'这是一封{category}类别的邮件。']
        
        subject = random.choice(subjects)
        body = random.choice(body_templates)
        
        # 计算AI评分
        ai_score = random.randint(1, 10)
        if priority == '紧急':
            ai_score = max(ai_score, 8)
        elif priority == '重要':
            ai_score = max(ai_score, 6)
        
        # 生成时间
        email_time = base_time + timedelta(hours=random.randint(0, 24), 
                                          minutes=random.randint(0, 59))
        
        emails.append({
            'id': f'EMAIL{i+1:03d}',
            'subject': subject,
            'sender': sender,
            'category': category,
            'priority': priority,
            'ai_score': ai_score,
            'body': body,
            'received_time': email_time,
            'is_read': random.choice([True, False]),
            'has_attachments': random.choice([True, False]),
            'is_urgent': priority == '紧急',
            'extracted_info': {
                'dates': [datetime.now().strftime('%Y-%m-%d')] if random.random() > 0.5 else [],
                'amounts': [f'{random.randint(1000,50000)}元'] if random.random() > 0.5 else [],
                'keywords': random.sample(['估值', '核对', '差异', '确认', '紧急'], k=random.randint(1,3))
            }
        })
    
    # 按AI评分排序
    emails.sort(key=lambda x: x['ai_score'], reverse=True)
    
    return emails

def show_home_page():
    """显示首页"""
    st.title("📧 邮件处理AI助手")
    st.markdown("---")
    
    # 系统介绍
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 系统简介
        
        邮件处理AI助手是一个基于**NLP、机器学习、个性化推荐**的智能邮件管理系统，
        帮助您高效处理海量邮件，避免遗漏关键信息。
        
        ### ✨ 核心功能
        
        1. **🎯 智能分类** - 自动识别邮件类别和重要性
        2. **⚡ 优先级排序** - 基于AI的智能排序
        3. **📝 信息提取** - 自动提取关键信息和生成摘要
        4. **🔔 智能提醒** - 个性化提醒策略
        5. **🧠 持续学习** - 根据用户行为不断优化
        
        ### 🎯 解决的痛点
        
        - ❌ 每天数千封邮件，处理耗时长
        - ❌ 关键邮件容易被淹没
        - ❌ 突发事件难以及时发现
        - ❌ 传统规则无法覆盖所有场景
        - ❌ 不同人关注点不同，难以统一
        
        ### 📈 预期效果
        
        - ✅ **效率提升 75%+** - 处理时间从2-3小时降至30-45分钟
        - ✅ **遗漏率 <1%** - 关键邮件不再遗漏
        - ✅ **准确率 90%+** - 智能分类和优先级判断
        """)
    
    with col2:
        emails_count = len(st.session_state.demo_emails) if 'demo_emails' in st.session_state else 30
        unread_count = sum(1 for e in st.session_state.demo_emails if not e['is_read']) if 'demo_emails' in st.session_state else 15
        urgent_count = sum(1 for e in st.session_state.demo_emails if e['is_urgent']) if 'demo_emails' in st.session_state else 8
        high_priority = sum(1 for e in st.session_state.demo_emails if e['priority'] == '高') if 'demo_emails' in st.session_state else 10
        
        st.info(f"""
        ### 📊 演示数据
        
        - **邮件总数**: {emails_count}封
        - **今日新邮件**: {emails_count}封
        - **未读邮件**: {unread_count}封
        - **紧急邮件**: {urgent_count}封
        - **高优先级**: {high_priority}封
        """)
        
        st.success("""
        ### 🚀 快速开始
        
        1. 查看智能分类结果
        2. 按优先级处理邮件
        3. 查看信息提取结果
        4. 设置个性化偏好
        5. 查看统计分析
        """)
        
        st.warning("""
        ### 💡 注意
        
        这是演示版本，展示
        核心功能和技术方案。
        实际部署需要集成
        邮件系统API。
        """)

def show_email_list_page():
    """显示邮件列表页面"""
    st.title("📬 智能邮件列表")
    st.markdown("---")
    
    emails = st.session_state.demo_emails
    
    # 根据当前角色筛选邮件
    current_role = st.session_state.user_preferences.get('role', '全部')
    if current_role != '全部':
        emails = [e for e in emails if st.session_state.email_handlers.get(e['id'], e.get('recommended_handler', '全部')) == current_role]
    
    # 筛选选项 - 5列布局
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        category_filter = st.selectbox(
            "类别筛选",
            ['全部'] + list(set([e['category'] for e in emails]))
        )
    
    with col2:
        # 动态获取所有优先级选项
        all_priorities = list(set([e.get('priority', '普通') for e in emails]))
        priority_filter = st.selectbox(
            "优先级筛选",
            ['全部'] + sorted(all_priorities)
        )
    
    with col3:
        read_filter = st.selectbox(
            "阅读状态",
            ['全部', '未读', '已读']
        )
    
    with col4:
        # 新增：处理状态筛选器，默认显示待处理
        process_filter = st.selectbox(
            "完成状态",
            ['待处理', '已处理', '全部'],
            index=0  # 默认选择"待处理"
        )
    
    with col5:
        sort_by = st.selectbox(
            "排序方式",
            ['AI智能排序', '时间倒序', '优先级']
        )
    
    # 应用筛选
    filtered_emails = emails.copy()
    
    if category_filter != '全部':
        filtered_emails = [e for e in filtered_emails if e['category'] == category_filter]
    
    if priority_filter != '全部':
        filtered_emails = [e for e in filtered_emails if e['priority'] == priority_filter]
    
    if read_filter == '未读':
        filtered_emails = [e for e in filtered_emails if not e['is_read']]
    elif read_filter == '已读':
        filtered_emails = [e for e in filtered_emails if e['is_read']]
    
    # 应用处理状态筛选
    if process_filter == '待处理':
        filtered_emails = [e for e in filtered_emails if not st.session_state.email_processed_status.get(e['id'], False)]
    elif process_filter == '已处理':
        filtered_emails = [e for e in filtered_emails if st.session_state.email_processed_status.get(e['id'], False)]
    
    # 排序
    if sort_by == '时间倒序':
        filtered_emails.sort(key=lambda x: x['received_time'], reverse=True)
    elif sort_by == '优先级':
        priority_order = {'高': 0, '紧急': 0, '中': 1, '重要': 1, '低': 2, '普通': 2}
        filtered_emails.sort(key=lambda x: priority_order.get(x.get('priority', '普通'), 2))
    
    st.markdown(f"### 📊 共 {len(filtered_emails)} 封邮件")
    
    # 显示邮件列表
    for email in filtered_emails:  # 显示所有邮件
        # 获取当前邮件的处理状态
        is_processed = st.session_state.email_processed_status.get(email['id'], False)
        
        with st.expander(
            f"{'🔴' if email['is_urgent'] else '🟢'} "
            f"[{email['category']}] {email['subject']} "
            f"(AI评分: {email['ai_score']}/10)",
            expanded=False
        ):
            # 添加处理状态按钮
            col_status, col_main, col_info = st.columns([0.5, 2.5, 1])
            
            with col_status:
                # 处理状态按钮
                if is_processed:
                    if st.button("✅", key=f"status_{email['id']}", help="点击标记为未处理"):
                        st.session_state.email_processed_status[email['id']] = False
                        add_operation_log('标记未处理', f'将邮件标记为未处理 (邮件ID: {email["id"]}, 主题: {email["subject"]})',
                                        st.session_state.user_preferences.get('role', '未知'))
                        st.rerun()
                else:
                    if st.button("⬜", key=f"status_{email['id']}", help="点击标记为已处理"):
                        st.session_state.email_processed_status[email['id']] = True
                        add_operation_log('标记已处理', f'将邮件标记为已处理 (邮件ID: {email["id"]}, 主题: {email["subject"]})',
                                        st.session_state.user_preferences.get('role', '未知'))
                        st.rerun()
            
            with col_main:
            
                st.markdown(f"**发件人**: {email['sender']}")
                st.markdown(f"**时间**: {email['received_time'].strftime('%Y-%m-%d %H:%M')}")
                
                # 显示正文（取消高亮）
                st.markdown("**正文**:")
                body_text = email['body']
                
                # 直接显示正文，不进行高亮处理
                st.markdown(
                    f'<div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">{body_text}</div>',
                    unsafe_allow_html=True
                )
                
                # 显示AI总结
                st.markdown("---")
                st.markdown("**🤖 AI智能总结**:")
                if email.get('ai_summary'):
                    for point in email['ai_summary']:
                        st.markdown(f"• {point}")
                else:
                    st.caption("暂无AI总结")
                
                # 显示关键词标签
                st.markdown("---")
                st.markdown("**🏷️ 关键词标签**:")
                if email.get('keyword_tags'):
                    tags_html = ""
                    for tag in email['keyword_tags']:
                        # 根据标签类型设置不同颜色
                        if tag in ['紧急处理', '重要事项']:
                            color = '#f44336'  # 红色
                        elif tag in ['估值核算', '交易处理', '清算结算']:
                            color = '#2196F3'  # 蓝色
                        elif tag in ['托管行对接', '交易对手对接', '审计部门']:
                            color = '#FF9800'  # 橙色
                        elif tag in ['需要确认', '需要提交', '待处理']:
                            color = '#9C27B0'  # 紫色
                        elif tag in ['涉及金额', '涉及基金', '存在差异']:
                            color = '#4CAF50'  # 绿色
                        else:
                            color = '#607D8B'  # 灰色
                        
                        tags_html += f'<span style="background-color: {color}; color: white; padding: 4px 10px; border-radius: 15px; margin: 3px; display: inline-block; font-size: 12px;">{tag}</span>'
                    
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.caption("暂无关键词标签")
                
                # 显示推荐处理人
                st.markdown("---")
                st.markdown("**👤 推荐处理人**:")
                current_handler = st.session_state.email_handlers.get(email['id'], email.get('recommended_handler', '全部'))
                
                col_handler1, col_handler2 = st.columns([2, 1])
                with col_handler1:
                    st.info(f"当前处理人：**{current_handler}**")
                
                with col_handler2:
                    if st.button("🔄 更改", key=f"change_handler_{email['id']}"):
                        st.session_state[f'show_handler_select_{email["id"]}'] = True
                        st.rerun()
                
                # 显示处理人选择器
                if st.session_state.get(f'show_handler_select_{email["id"]}', False):
                    new_handler = st.selectbox(
                        "选择新的处理人",
                        ['估值员', '交易员', '清算员', '披露员', '合规员', '风控员', '技术员', '全部'],
                        key=f"handler_select_{email['id']}"
                    )
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("✅ 确认", key=f"confirm_handler_{email['id']}"):
                            old_handler = current_handler
                            st.session_state.email_handlers[email['id']] = new_handler
                            st.session_state[f'show_handler_select_{email["id"]}'] = False
                            add_operation_log('更改处理人', f'更改邮件处理人 (邮件ID: {email["id"]}, 从 {old_handler} 改为 {new_handler})',
                                            st.session_state.user_preferences.get('role', '未知'))
                            st.success(f"已更改处理人为：{new_handler}")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("❌ 取消", key=f"cancel_handler_{email['id']}"):
                            st.session_state[f'show_handler_select_{email["id"]}'] = False
                            st.rerun()
            
            with col_info:
                st.metric("AI评分", f"{email['ai_score']}/10")
                st.metric("优先级", email.get('priority', '中'))
                st.markdown(f"**类别**: {email['category']}")
                st.markdown(f"**状态**: {'已读' if email['is_read'] else '未读'}")
                st.markdown(f"**附件**: {'有' if email['has_attachments'] else '无'}")

def add_operation_log(operation_type, operation_detail, operator):
    """添加操作日志"""
    log_entry = {
        'id': len(st.session_state.operation_logs) + 1,
        'timestamp': datetime.now(),
        'operation_type': operation_type,
        'operation_detail': operation_detail,
        'operator': operator,
        'is_reverted': False
    }
    st.session_state.operation_logs.append(log_entry)

def show_operation_logs_page():
    """显示操作日志页面"""
    st.title("📋 操作日志")
    st.markdown("---")
    
    logs = st.session_state.operation_logs
    
    if not logs:
        st.info("暂无操作日志")
        return
    
    # 筛选器
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 操作时间筛选
        time_filter = st.selectbox(
            "操作时间",
            ['全部', '今天', '最近7天', '最近30天']
        )
    
    with col2:
        # 操作类别筛选
        all_types = list(set([log['operation_type'] for log in logs]))
        type_filter = st.selectbox(
            "操作类别",
            ['全部'] + all_types
        )
    
    with col3:
        # 操作人筛选
        all_operators = list(set([log['operator'] for log in logs]))
        operator_filter = st.selectbox(
            "操作人",
            ['全部'] + all_operators
        )
    
    # 应用筛选
    filtered_logs = logs.copy()
    
    # 时间筛选
    if time_filter != '全部':
        now = datetime.now()
        if time_filter == '今天':
            filtered_logs = [log for log in filtered_logs if log['timestamp'].date() == now.date()]
        elif time_filter == '最近7天':
            filtered_logs = [log for log in filtered_logs if (now - log['timestamp']).days <= 7]
        elif time_filter == '最近30天':
            filtered_logs = [log for log in filtered_logs if (now - log['timestamp']).days <= 30]
    
    # 类别筛选
    if type_filter != '全部':
        filtered_logs = [log for log in filtered_logs if log['operation_type'] == type_filter]
    
    # 操作人筛选
    if operator_filter != '全部':
        filtered_logs = [log for log in filtered_logs if log['operator'] == operator_filter]
    
    # 按时间倒序排序
    filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    st.markdown(f"### 📊 共 {len(filtered_logs)} 条日志")
    
    # 显示日志表格
    for log in filtered_logs:
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 3, 1.5, 1, 1])
            
            with col1:
                st.markdown(f"**{log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**")
            
            with col2:
                st.markdown(f"**{log['operation_type']}**")
            
            with col3:
                st.markdown(log['operation_detail'])
            
            with col4:
                st.markdown(f"*{log['operator']}*")
            
            with col5:
                if log['is_reverted']:
                    st.markdown("🔄 已撤销")
                else:
                    st.markdown("✅ 正常")
            
            with col6:
                # 所有操作类型都可以撤销
                if not log['is_reverted']:
                    if st.button("撤销", key=f"revert_{log['id']}"):
                        # 执行撤销操作
                        if log['operation_type'] == '标记已处理':
                            # 找到对应邮件ID并撤销
                            email_id = log['operation_detail'].split('邮件ID: ')[1].split(',')[0] if '邮件ID: ' in log['operation_detail'] else None
                            if email_id and email_id in st.session_state.email_processed_status:
                                st.session_state.email_processed_status[email_id] = False
                                add_operation_log('撤销操作', f'撤销操作：{log["operation_detail"]}', log['operator'])
                                log['is_reverted'] = True
                                st.success("已撤销操作")
                                st.rerun()
                        
                        elif log['operation_type'] == '标记未处理':
                            email_id = log['operation_detail'].split('邮件ID: ')[1].split(',')[0] if '邮件ID: ' in log['operation_detail'] else None
                            if email_id:
                                st.session_state.email_processed_status[email_id] = True
                                add_operation_log('撤销操作', f'撤销操作：{log["operation_detail"]}', log['operator'])
                                log['is_reverted'] = True
                                st.success("已撤销操作")
                                st.rerun()
                        
                        elif log['operation_type'] == '更改处理人':
                            email_id = log['operation_detail'].split('邮件ID: ')[1].split(',')[0] if '邮件ID: ' in log['operation_detail'] else None
                            if email_id and email_id in st.session_state.email_handlers:
                                # 恢复到原处理人
                                original_handler = log['operation_detail'].split('从 ')[1].split(' 改为')[0] if '从 ' in log['operation_detail'] else '全部'
                                st.session_state.email_handlers[email_id] = original_handler
                                add_operation_log('撤销操作', f'撤销操作：{log["operation_detail"]}', log['operator'])
                                log['is_reverted'] = True
                                st.success("已撤销操作")
                                st.rerun()
            
            st.markdown("---")

def show_priority_page():
    """显示优先级排序页面"""
    st.title("⚡ 智能优先级排序")
    st.markdown("---")
    
    emails = st.session_state.demo_emails
    
    # 排序规则按钮
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🧠 AI排序算法")
    
    with col2:
        if st.button("📋 查看当前排序规则", use_container_width=True):
            st.session_state.show_rules = not st.session_state.get('show_rules', False)
    
    with col3:
        if st.button("⚙️ 修改排序规则", use_container_width=True):
            st.session_state.edit_rules = not st.session_state.get('edit_rules', False)
    
    # 显示当前排序规则
    if st.session_state.get('show_rules', False):
        st.info(f"""
        ### 📊 当前排序规则
        
        - **发件人重要性权重**: {st.session_state.sorting_rules['sender_weight']}分 (满分3分)
        - **关键词匹配权重**: {st.session_state.sorting_rules['keyword_weight']}分 (满分3分)
        - **时效性权重**: {st.session_state.sorting_rules['timeliness_weight']}分 (满分2分)
        - **用户行为预测权重**: {st.session_state.sorting_rules['behavior_weight']}分 (满分2分)
        
        **总分范围**: 0-10分
        """)
    
    # 修改排序规则
    if st.session_state.get('edit_rules', False):
        st.markdown("### ⚙️ 修改排序规则")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sender_weight = st.slider(
                "发件人重要性权重 (0-3分)",
                0, 3,
                st.session_state.sorting_rules['sender_weight']
            )
            
            keyword_weight = st.slider(
                "关键词匹配权重 (0-3分)",
                0, 3,
                st.session_state.sorting_rules['keyword_weight']
            )
        
        with col2:
            timeliness_weight = st.slider(
                "时效性权重 (0-2分)",
                0, 2,
                st.session_state.sorting_rules['timeliness_weight']
            )
            
            behavior_weight = st.slider(
                "用户行为预测权重 (0-2分)",
                0, 2,
                st.session_state.sorting_rules['behavior_weight']
            )
        
        if st.button("💾 保存规则", type="primary"):
            st.session_state.sorting_rules = {
                'sender_weight': sender_weight,
                'keyword_weight': keyword_weight,
                'timeliness_weight': timeliness_weight,
                'behavior_weight': behavior_weight
            }
            st.success("✅ 排序规则已更新！")
            st.session_state.edit_rules = False
            st.rerun()
    
    st.markdown("---")
    
    # 优先级分布
    priority_counts = {}
    for email in emails:
        priority = email.get('priority', '普通')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # 创建柱状图
    fig_bar = go.Figure(data=[go.Bar(
        x=list(priority_counts.keys()),
        y=list(priority_counts.values()),
        text=list(priority_counts.values()),
        textposition='auto',
        marker_color=['red', 'orange', 'green']
    )])
    
    fig_bar.update_layout(
        title='优先级分布',
        xaxis_title='优先级',
        yaxis_title='邮件数量',
        height=400
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Top 10 高优先级邮件 - 支持下拉查看详情
    st.markdown("### 🔝 Top 10 高优先级邮件")
    
    top_emails = sorted(emails, key=lambda x: x['ai_score'], reverse=True)[:10]
    
    for i, email in enumerate(top_emails, 1):
        with st.expander(
            f"#{i} [{email['category']}] {email['subject']} (AI评分: {email['ai_score']}/10)",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**发件人**: {email['sender']}")
                st.markdown(f"**时间**: {email['received_time'].strftime('%Y-%m-%d %H:%M')}")
                
                # 显示正文
                st.markdown("**正文**:")
                st.markdown(
                    f'<div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">{email["body"]}</div>',
                    unsafe_allow_html=True
                )
                
                # 显示AI总结
                st.markdown("---")
                st.markdown("**🤖 AI智能总结**:")
                if email.get('ai_summary'):
                    for point in email['ai_summary']:
                        st.markdown(f"• {point}")
                else:
                    st.caption("暂无AI总结")
                
                # 显示关键词标签
                st.markdown("---")
                st.markdown("**🏷️ 关键词标签**:")
                if email.get('keyword_tags'):
                    tags_html = ""
                    for tag in email['keyword_tags']:
                        if tag in ['紧急处理', '重要事项']:
                            color = '#f44336'
                        elif tag in ['估值核算', '交易处理', '清算结算']:
                            color = '#2196F3'
                        elif tag in ['托管行对接', '交易对手对接', '审计部门']:
                            color = '#FF9800'
                        elif tag in ['需要确认', '需要提交', '待处理']:
                            color = '#9C27B0'
                        elif tag in ['涉及金额', '涉及基金', '存在差异']:
                            color = '#4CAF50'
                        else:
                            color = '#607D8B'
                        
                        tags_html += f'<span style="background-color: {color}; color: white; padding: 4px 10px; border-radius: 15px; margin: 3px; display: inline-block; font-size: 12px;">{tag}</span>'
                    
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.caption("暂无关键词标签")
            
            with col2:
                st.metric("AI评分", f"{email['ai_score']}/10")
                st.metric("优先级", email.get('priority', '中'))
                st.markdown(f"**类别**: {email['category']}")
                st.markdown(f"**状态**: {'已读' if email['is_read'] else '未读'}")
                st.markdown(f"**附件**: {'有' if email['has_attachments'] else '无'}")

def show_extraction_page():
    """显示信息提取页面"""
    st.title("📝 智能信息提取")
    st.markdown("---")
    
    st.markdown("""
    ### 🔍 提取能力
    
    系统可以自动提取以下信息：
    - **日期时间** - 截止日期、会议时间等
    - **金额数字** - 交易金额、差异金额等
    - **产品名称** - 基金产品、证券代码等
    - **关键词** - 重要术语和概念
    - **待办事项** - 需要处理的任务
    """)
    
    # 选择一封邮件进行演示
    emails = st.session_state.demo_emails
    
    st.markdown("### 📧 示例邮件")
    
    demo_email = emails[0]
    
    st.markdown(f"**主题**: {demo_email['subject']}")
    st.markdown(f"**发件人**: {demo_email['sender']}")
    st.markdown(f"**正文**: {demo_email['body']}")
    
    st.markdown("---")
    st.markdown("### 🎯 提取结果")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 时间信息")
        if demo_email['extracted_info']['dates']:
            for date in demo_email['extracted_info']['dates']:
                st.success(f"✓ {date}")
        else:
            st.info("未提取到日期信息")
        
        st.markdown("#### 💰 金额信息")
        if demo_email['extracted_info']['amounts']:
            for amount in demo_email['extracted_info']['amounts']:
                st.success(f"✓ {amount}")
        else:
            st.info("未提取到金额信息")
    
    with col2:
        st.markdown("#### 🔑 关键词")
        if demo_email['extracted_info']['keywords']:
            for keyword in demo_email['extracted_info']['keywords']:
                st.success(f"✓ {keyword}")
        else:
            st.info("未提取到关键词")
        
        st.markdown("#### 📋 邮件摘要")
        st.info(f"{demo_email['body'][:50]}...")

def show_statistics_page():
    """显示统计分析页面"""
    st.title("📊 统计分析")
    st.markdown("---")
    
    emails = st.session_state.demo_emails
    
    # 总体统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("邮件总数", len(emails))
    with col2:
        unread_count = sum(1 for e in emails if not e['is_read'])
        st.metric("未读邮件", unread_count)
    with col3:
        urgent_count = sum(1 for e in emails if e['is_urgent'])
        st.metric("紧急邮件", urgent_count)
    with col4:
        avg_score = sum(e['ai_score'] for e in emails) / len(emails)
        st.metric("平均AI评分", f"{avg_score:.1f}")
    
    st.markdown("---")
    
    # 从智能分类移过来的图表
    # 1. 邮件类别分布饼图
    st.markdown("### 📊 邮件类别分布")
    
    category_counts = {}
    for email in emails:
        category = email['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(category_counts.keys()),
        values=list(category_counts.values()),
        hole=0.3,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
    )])
    
    fig_pie.update_layout(
        title='邮件类别分布',
        height=400
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # 2. 各类别详情表格
    st.markdown("### 📋 各类别详情")
    
    category_data = []
    for category, count in category_counts.items():
        category_emails = [e for e in emails if e['category'] == category]
        avg_score = sum(e['ai_score'] for e in category_emails) / len(category_emails)
        urgent_count = sum(1 for e in category_emails if e['is_urgent'])
        urgent_ratio = (urgent_count / count * 100) if count > 0 else 0
        total_ratio = (count / len(emails) * 100) if len(emails) > 0 else 0
        
        category_data.append({
            '类别': category,
            '平均AI评分': f"{avg_score:.1f}",
            '数量': count,
            '占总量占比': f"{total_ratio:.1f}%",
            '紧急邮件': urgent_count,
            '紧急邮件占比': f"{urgent_ratio:.1f}%"
        })
    
    st.dataframe(pd.DataFrame(category_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 时间分布
    st.markdown("### ⏰ 邮件时间分布")
    
    # 筛选器
    col1, col2 = st.columns(2)
    with col1:
        time_process_filter = st.selectbox(
            "邮件处理状态",
            ['全部', '待处理', '已处理'],
            key='time_process_filter'
        )
    with col2:
        time_category_filter = st.selectbox(
            "邮件类别",
            ['全部'] + list(set([e['category'] for e in emails])),
            key='time_category_filter'
        )
    
    # 应用筛选
    filtered_time_emails = emails.copy()
    if time_process_filter == '待处理':
        filtered_time_emails = [e for e in filtered_time_emails if not st.session_state.email_processed_status.get(e['id'], False)]
    elif time_process_filter == '已处理':
        filtered_time_emails = [e for e in filtered_time_emails if st.session_state.email_processed_status.get(e['id'], False)]
    
    if time_category_filter != '全部':
        filtered_time_emails = [e for e in filtered_time_emails if e['category'] == time_category_filter]
    
    # 按日期统计
    date_counts = {}
    for email in filtered_time_emails:
        date_str = email['received_time'].strftime('%Y/%m/%d')
        date_counts[date_str] = date_counts.get(date_str, 0) + 1
    
    # 排序日期
    sorted_dates = sorted(date_counts.keys())
    sorted_counts = [date_counts[d] for d in sorted_dates]
    
    fig_time = go.Figure(data=[go.Bar(
        x=sorted_dates,
        y=sorted_counts,
        text=sorted_counts,
        textposition='auto',
        marker_color='#1f77b4'
    )])
    
    fig_time.update_layout(
        title='邮件日期分布',
        xaxis_title='日期',
        yaxis_title='邮件数量',
        height=400,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_time, use_container_width=True)
    
    # 发件人统计
    st.markdown("### 👥 发件人统计")
    
    # 分级时间筛选器
    sender_time_selection = create_hierarchical_time_filter('sender')
    
    # 根据选择的时间筛选数据
    sender_counts = {}
    for email in emails:
        sender = email['sender']
        email_time = email['received_time']
        
        # 根据选择的时间级别进行匹配
        if sender_time_selection:
            if len(sender_time_selection) == 1:  # 只选了年
                if email_time.year != sender_time_selection[0]:
                    continue
                time_key = f"{sender_time_selection[0]}"
            elif len(sender_time_selection) == 2:  # 选了年月
                if email_time.year != sender_time_selection[0] or email_time.month != sender_time_selection[1]:
                    continue
                time_key = f"{sender_time_selection[0]}/{sender_time_selection[1]:02d}"
            elif len(sender_time_selection) == 3:  # 选了年月日
                if email_time.date() != datetime(sender_time_selection[0], sender_time_selection[1], sender_time_selection[2]).date():
                    continue
                time_key = f"{sender_time_selection[0]}/{sender_time_selection[1]:02d}/{sender_time_selection[2]:02d}"
        else:
            time_key = "全部"
        
        key = f"{sender} ({time_key})"
        sender_counts[key] = sender_counts.get(key, 0) + 1
    
    sender_data = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    fig_sender = go.Figure(data=[go.Bar(
        x=[s[1] for s in sender_data],
        y=[s[0] for s in sender_data],
        orientation='h',
        text=[s[1] for s in sender_data],
        textposition='auto',
        marker_color='#2ca02c'
    )])
    
    fig_sender.update_layout(
        title='Top 10 发件人',
        xaxis_title='邮件数量',
        yaxis_title='发件人',
        height=400
    )
    
    st.plotly_chart(fig_sender, use_container_width=True)
    
    # 处理人统计
    st.markdown("### 👤 处理人统计")
    
    # 分级时间筛选器
    handler_time_selection = create_hierarchical_time_filter('handler')
    
    # 根据选择的时间筛选数据
    handler_counts = {}
    for email in emails:
        handler = st.session_state.email_handlers.get(email['id'], email.get('recommended_handler', '全部'))
        email_time = email['received_time']
        
        # 根据选择的时间级别进行匹配
        if handler_time_selection:
            if len(handler_time_selection) == 1:  # 只选了年
                if email_time.year != handler_time_selection[0]:
                    continue
                time_key = f"{handler_time_selection[0]}"
            elif len(handler_time_selection) == 2:  # 选了年月
                if email_time.year != handler_time_selection[0] or email_time.month != handler_time_selection[1]:
                    continue
                time_key = f"{handler_time_selection[0]}/{handler_time_selection[1]:02d}"
            elif len(handler_time_selection) == 3:  # 选了年月日
                if email_time.date() != datetime(handler_time_selection[0], handler_time_selection[1], handler_time_selection[2]).date():
                    continue
                time_key = f"{handler_time_selection[0]}/{handler_time_selection[1]:02d}/{handler_time_selection[2]:02d}"
        else:
            time_key = "全部"
        
        key = f"{handler} ({time_key})"
        handler_counts[key] = handler_counts.get(key, 0) + 1
    
    handler_data = sorted(handler_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    fig_handler = go.Figure(data=[go.Bar(
        x=[h[1] for h in handler_data],
        y=[h[0] for h in handler_data],
        orientation='h',
        text=[h[1] for h in handler_data],
        textposition='auto',
        marker_color='#ff7f0e'
    )])
    
    fig_handler.update_layout(
        title='Top 10 处理人',
        xaxis_title='邮件数量',
        yaxis_title='处理人',
        height=400
    )
    
    st.plotly_chart(fig_handler, use_container_width=True)

def create_hierarchical_time_filter(key_prefix):
    """创建分级时间筛选器"""
    emails = st.session_state.demo_emails
    
    # 获取所有年份
    years = sorted(list(set([e['received_time'].year for e in emails])), reverse=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_year = st.selectbox(
            "选择年份",
            ['全部'] + years,
            key=f'{key_prefix}_year'
        )
    
    if selected_year == '全部':
        return None
    
    # 获取该年的所有月份
    months = sorted(list(set([e['received_time'].month for e in emails if e['received_time'].year == selected_year])))
    
    with col2:
        selected_month = st.selectbox(
            "选择月份（可选）",
            ['全部'] + months,
            key=f'{key_prefix}_month'
        )
    
    if selected_month == '全部':
        return [selected_year]
    
    # 获取该年月的所有日期
    days = sorted(list(set([e['received_time'].day for e in emails
                            if e['received_time'].year == selected_year
                            and e['received_time'].month == selected_month])))
    
    with col3:
        selected_day = st.selectbox(
            "选择日期（可选）",
            ['全部'] + days,
            key=f'{key_prefix}_day'
        )
    
    if selected_day == '全部':
        return [selected_year, selected_month]
    
    return [selected_year, selected_month, selected_day]

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
                "📬 智能邮件列表",
                "⚡ 优先级排序",
                "📊 统计分析",
                "📋 操作日志"
            ]
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ 个性化设置")
        
        role = st.selectbox(
            "我的角色",
            ['全部', '估值员', '交易员', '清算员', '披露员', '合规员', '风控员', '技术员']
        )
        
        st.session_state.user_preferences['role'] = role
        
        st.markdown("---")
        st.markdown("""
        ### 💡 使用提示
        
        1. 查看智能分类的邮件
        2. 按AI评分处理高优先级邮件
        3. 查看自动提取的关键信息
        4. 设置个性化偏好
        5. 查看统计分析报告
        
        ### 📖 技术方案
        
        详见完整的技术方案文档，
        包含算法设计、数据需求、
        实施计划等内容。
        """)
    
    # 主内容区
    if page == "🏠 首页概览":
        show_home_page()
    elif page == "📬 智能邮件列表":
        show_email_list_page()
    elif page == "⚡ 优先级排序":
        show_priority_page()
    elif page == "📊 统计分析":
        show_statistics_page()
    elif page == "📋 操作日志":
        show_operation_logs_page()

if __name__ == '__main__':
    main()