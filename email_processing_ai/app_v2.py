"""
邮件处理AI助手 - 优化版
包含100封真实邮件和交互式高亮功能
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
        st.session_state.demo_emails = generate_realistic_emails()
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'role': '估值员',
            'interested_categories': ['估值', '清算'],
            'notification_level': '高优先级'
        }
    if 'selected_keyword' not in st.session_state:
        st.session_state.selected_keyword = None

def generate_realistic_emails():
    """生成100封真实详细的邮件"""
    emails = []
    base_time = datetime.now() - timedelta(days=7)
    
    # 邮件模板库
    email_templates = [
        # 估值类邮件
        {
            'category': '估值',
            'subjects': [
                '【紧急】{date}估值数据核对差异说明',
                '{product}产品估值核对结果通知',
                '托管行估值差异确认 - {date}',
                '估值调整通知 - 需立即处理'
            ],
            'bodies': [
                '''尊敬的运营团队：

您好！根据{date}的估值核对结果，我行发现以下产品存在估值差异，需要贵司尽快确认并处理：

一、差异明细：
1. 产品名称：{product}
2. 估值日期：{date}
3. 我行估值：{amount1}元
4. 贵司估值：{amount2}元
5. 差异金额：{diff}元
6. 差异率：{rate}%

二、初步分析：
经我行初步核查，差异可能由以下原因造成：
1. 债券估值方法差异（摊余成本法 vs 市价法）
2. 应收利息计算时点不同
3. 交易确认时间差异

三、处理要求：
1. 请于{deadline}前完成差异核对
2. 如确认为我行错误，我行将及时调整
3. 如为贵司错误，请提供调整说明
4. 重大差异需提交书面说明

请及时回复确认，如有疑问请随时联系。

此致
敬礼

工商银行托管部
联系人：张经理
电话：010-12345678
日期：{send_date}''',
                
                '''各位同事：

今日估值核对工作已完成，现将核对结果通报如下：

【核对概况】
- 核对产品数：{count}只
- 核对通过：{pass_count}只
- 存在差异：{diff_count}只
- 差异总金额：{total_diff}元

【差异产品明细】
1. {product1} - 差异{amount1}元（原因：交易确认时点）
2. {product2} - 差异{amount2}元（原因：应收利息）
3. {product3} - 差异{amount3}元（原因：估值方法）

【处理进度】
- 已确认差异：{confirmed}只
- 待确认差异：{pending}只
- 已调整完成：{adjusted}只

【注意事项】
1. 所有差异需在{deadline}前处理完毕
2. 重大差异（>10万元）需上报领导
3. 连续3日出现差异的产品需重点关注

请相关同事及时跟进处理。

估值核对小组
{send_date}'''
            ]
        },
        
        # 交易类邮件
        {
            'category': '交易',
            'subjects': [
                '交易确认通知 - {trade_no}',
                '【紧急】交易失败处理 - {product}',
                '{date}交易执行情况汇总',
                '交易异常预警 - 需立即确认'
            ],
            'bodies': [
                '''交易确认通知

交易编号：{trade_no}
交易日期：{date}
产品名称：{product}

【交易详情】
证券代码：{code}
证券名称：{security}
交易方向：买入
交易数量：{quantity}股
成交价格：{price}元
成交金额：{amount}元
手续费：{fee}元
实际支付：{total}元

【交割信息】
交割日期：{settlement_date}
交割方式：DVP
托管账户：{account}
资金账户：{fund_account}

【风险提示】
1. 请确认交易信息准确无误
2. 确保资金账户余额充足
3. 关注交割日资金到账情况
4. 如有异议请在{deadline}前反馈

如有疑问，请联系交易部。

交易部
{send_date}''',
                
                '''紧急通知

【交易失败情况】
产品：{product}
交易编号：{trade_no}
失败时间：{fail_time}
失败原因：资金不足

【详细说明】
1. 计划交易金额：{plan_amount}元
2. 账户可用余额：{balance}元
3. 资金缺口：{shortage}元
4. 影响范围：当日交易计划

【处理措施】
1. 立即补充资金{shortage}元
2. 重新提交交易指令
3. 调整当日交易计划
4. 上报风控部门

【时间要求】
- 资金补充：{deadline1}前
- 交易执行：{deadline2}前
- 情况说明：{deadline3}前

请立即处理！

交易部
{send_date}'''
            ]
        },
        
        # 清算类邮件
        {
            'category': '清算',
            'subjects': [
                '{date}清算数据确认通知',
                '资金清算结果 - {product}',
                '清算差异说明 - 需核对',
                '【重要】清算完成确认'
            ],
            'bodies': [
                '''清算数据确认通知

清算日期：{date}
产品数量：{count}只

【清算汇总】
1. 交易清算
   - 股票交易：{stock_count}笔，金额{stock_amount}元
   - 债券交易：{bond_count}笔，金额{bond_amount}元
   - 基金交易：{fund_count}笔，金额{fund_amount}元

2. 资金清算
   - 应收款项：{receivable}元
   - 应付款项：{payable}元
   - 净额：{net}元

3. 费用清算
   - 管理费：{management_fee}元
   - 托管费：{custody_fee}元
   - 其他费用：{other_fee}元
   - 费用合计：{total_fee}元

【注意事项】
1. 请核对清算数据是否准确
2. 确认资金账户余额充足
3. 关注大额资金变动
4. 如有差异请及时反馈

请于{deadline}前完成确认。

清算部
{send_date}''',
                
                '''清算差异说明

【差异概况】
产品名称：{product}
清算日期：{date}
差异类型：资金清算差异
差异金额：{diff}元

【差异分析】
1. 我方清算金额：{amount1}元
   - 交易金额：{trade_amount}元
   - 费用金额：{fee_amount}元
   - 其他调整：{adjust_amount}元

2. 托管行清算金额：{amount2}元
   - 差异金额：{diff}元
   - 差异率：{rate}%

3. 差异原因：
   - 主要原因：{reason1}
   - 次要原因：{reason2}
   - 其他因素：{reason3}

【处理方案】
1. 核对交易明细
2. 确认费用计算
3. 调整清算数据
4. 重新生成报表

【时间安排】
- 核对完成：{deadline1}
- 调整完成：{deadline2}
- 报表生成：{deadline3}

清算部
{send_date}'''
            ]
        },
        
        # 披露类邮件
        {
            'category': '披露',
            'subjects': [
                '{product}季度报告披露提醒',
                '【截止】{date}信息披露截止日',
                '披露文件审核意见 - {product}',
                '临时公告发布通知'
            ],
            'bodies': [
                '''信息披露提醒

【披露要求】
产品名称：{product}
报告类型：季度报告
报告期间：{period}
披露截止：{deadline}

【披露内容】
1. 基金概况
2. 主要财务指标
3. 投资组合报告
4. 基金份额变动
5. 重大事项说明

【时间安排】
- 数据准备：{date1}前
- 初稿完成：{date2}前
- 内部审核：{date3}前
- 外部审核：{date4}前
- 正式披露：{deadline}前

【注意事项】
1. 确保数据准确完整
2. 格式符合监管要求
3. 及时完成审核流程
4. 按时完成披露工作

请各相关部门配合完成。

披露部
{send_date}''',
                
                '''披露文件审核意见

产品：{product}
文件：{doc_name}
审核人：{reviewer}
审核日期：{review_date}

【审核意见】
一、格式问题（{format_count}处）
1. 第{page1}页表格格式不规范
2. 第{page2}页字体大小不一致
3. 第{page3}页页码错误

二、内容问题（{content_count}处）
1. 财务数据前后不一致
2. 投资组合数据需更新
3. 重大事项披露不完整

三、合规问题（{compliance_count}处）
1. 缺少必要的风险提示
2. 关联交易披露不充分
3. 部分表述不符合监管要求

【修改要求】
1. 请于{deadline1}前完成修改
2. 修改后重新提交审核
3. 确保所有问题全部解决

【联系方式】
审核人：{reviewer}
电话：{phone}
邮箱：{email}

披露部
{send_date}'''
            ]
        },
        
        # 合规类邮件
        {
            'category': '合规',
            'subjects': [
                '合规检查通知 - {product}',
                '【重要】监管要求落实情况',
                '合规风险提示 - {risk_type}',
                '内部审计发现问题整改'
            ],
            'bodies': [
                '''合规检查通知

【检查安排】
检查对象：{product}
检查时间：{check_date}
检查人员：{checker}
检查类型：定期合规检查

【检查内容】
1. 投资范围合规性
   - 投资比例是否符合合同约定
   - 是否存在超范围投资
   - 关联交易是否合规

2. 交易行为合规性
   - 交易流程是否规范
   - 是否存在异常交易
   - 交易对手是否合规

3. 信息披露合规性
   - 披露是否及时完整
   - 披露内容是否准确
   - 是否存在遗漏披露

4. 内部控制有效性
   - 制度是否健全
   - 执行是否到位
   - 是否存在漏洞

【配合要求】
1. 准备相关资料
2. 安排人员配合
3. 及时反馈问题
4. 落实整改措施

请做好准备工作。

合规部
{send_date}''',
                
                '''监管要求落实情况

【监管要求】
文件名称：{regulation}
发布机构：{regulator}
发布日期：{reg_date}
落实截止：{deadline}

【主要内容】
1. 加强投资管理
   - 完善投资决策流程
   - 强化风险控制措施
   - 规范交易行为

2. 规范信息披露
   - 提高披露及时性
   - 增强披露完整性
   - 确保披露准确性

3. 强化内部控制
   - 健全制度体系
   - 加强执行监督
   - 完善问责机制

【落实情况】
1. 已完成事项：{completed}项
2. 进行中事项：{ongoing}项
3. 未开始事项：{pending}项

【下一步工作】
1. 加快推进进度
2. 确保按时完成
3. 做好自查工作
4. 及时报告进展

合规部
{send_date}'''
            ]
        },
        
        # 风控类邮件
        {
            'category': '风控',
            'subjects': [
                '风险预警 - {product}',
                '【紧急】风险事件处置',
                '{date}风险监控日报',
                '风险指标超限提示'
            ],
            'bodies': [
                '''风险预警通知

【预警信息】
产品名称：{product}
预警类型：{risk_type}
预警等级：{level}
预警时间：{alert_time}

【风险情况】
1. 市场风险
   - 净值波动：{volatility}%
   - 最大回撤：{drawdown}%
   - 风险等级：{risk_level}

2. 流动性风险
   - 流动性比率：{liquidity}%
   - 预警阈值：{threshold}%
   - 超限幅度：{excess}%

3. 信用风险
   - 信用评级：{rating}
   - 违约概率：{default_prob}%
   - 风险敞口：{exposure}元

【应对措施】
1. 立即评估风险影响
2. 制定应对预案
3. 加强监控频率
4. 及时上报情况

【处置要求】
- 评估完成：{deadline1}
- 预案制定：{deadline2}
- 措施落实：{deadline3}

请高度重视，及时处置！

风控部
{send_date}''',
                
                '''风险监控日报

监控日期：{date}
报告编号：{report_no}

【市场风险】
1. 股票市场
   - 上证指数：{index1}点（{change1}%）
   - 深证成指：{index2}点（{change2}%）
   - 创业板指：{index3}点（{change3}%）

2. 债券市场
   - 10年国债：{bond_yield}%
   - 信用利差：{credit_spread}bp
   - 市场情绪：{sentiment}

3. 产品表现
   - 平均收益：{avg_return}%
   - 最大回撤：{max_drawdown}%
   - 波动率：{volatility}%

【流动性风险】
1. 整体情况
   - 流动性充足率：{liquidity}%
   - 预警产品：{alert_count}只
   - 风险等级：{risk_level}

2. 重点产品
   - {product1}：流动性{liq1}%
   - {product2}：流动性{liq2}%
   - {product3}：流动性{liq3}%

【信用风险】
1. 信用事件：{credit_events}起
2. 评级调整：{rating_changes}次
3. 违约风险：{default_risk}

【风险提示】
1. 关注市场波动
2. 加强流动性管理
3. 防范信用风险
4. 做好应急准备

风控部
{send_date}'''
            ]
        }
    ]
    
    # 生成100封邮件
    for i in range(100):
        template = random.choice(email_templates)
        category = template['category']
        subject_template = random.choice(template['subjects'])
        body_template = random.choice(template['bodies'])
        
        # 生成时间
        email_time = base_time + timedelta(
            days=random.randint(0, 7),
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59)
        )
        
        # 生成数据
        date_str = email_time.strftime('%Y-%m-%d')
        product_names = ['易方达香港恒生指数基金', '易方达中证500ETF', '易方达稳健收益债券', 
                        '易方达货币市场基金', '易方达蓝筹精选混合']
        product = random.choice(product_names)
        
        # 替换模板变量
        replacements = {
            '{date}': date_str,
            '{product}': product,
            '{product1}': random.choice(product_names),
            '{product2}': random.choice(product_names),
            '{product3}': random.choice(product_names),
            '{amount}': f'{random.randint(100, 9999)}万',
            '{amount1}': f'{random.randint(10000, 99999)}',
            '{amount2}': f'{random.randint(10000, 99999)}',
            '{diff}': f'{random.randint(100, 5000)}',
            '{rate}': f'{random.uniform(0.01, 0.5):.2f}',
            '{deadline}': (email_time + timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d %H:00'),
            '{send_date}': email_time.strftime('%Y年%m月%d日'),
            '{count}': str(random.randint(10, 50)),
            '{pass_count}': str(random.randint(8, 45)),
            '{diff_count}': str(random.randint(1, 5)),
            '{total_diff}': f'{random.randint(1000, 50000)}',
            '{confirmed}': str(random.randint(1, 3)),
            '{pending}': str(random.randint(1, 2)),
            '{adjusted}': str(random.randint(0, 2)),
            '{trade_no}': f'T{random.randint(100000, 999999)}',
            '{code}': f'{random.randint(600000, 603999)}',
            '{security}': random.choice(['中国平安', '贵州茅台', '招商银行', '工商银行']),
            '{quantity}': f'{random.randint(100, 10000)}',
            '{price}': f'{random.uniform(10, 200):.2f}',
            '{fee}': f'{random.randint(100, 1000)}',
            '{total}': f'{random.randint(10000, 100000)}',
            '{settlement_date}': (email_time + timedelta(days=1)).strftime('%Y-%m-%d'),
            '{account}': f'ACC{random.randint(100000, 999999)}',
            '{fund_account}': f'FA{random.randint(100000, 999999)}',
            '{fail_time}': email_time.strftime('%Y-%m-%d %H:%M'),
            '{plan_amount}': f'{random.randint(1000, 5000)}万',
            '{balance}': f'{random.randint(500, 4000)}万',
            '{shortage}': f'{random.randint(100, 1000)}万',
            '{deadline1}': (email_time + timedelta(hours=2)).strftime('%H:00'),
            '{deadline2}': (email_time + timedelta(hours=4)).strftime('%H:00'),
            '{deadline3}': (email_time + timedelta(days=1)).strftime('%Y-%m-%d'),
            '{stock_count}': str(random.randint(10, 50)),
            '{bond_count}': str(random.randint(5, 30)),
            '{fund_count}': str(random.randint(3, 20)),
            '{stock_amount}': f'{random.randint(1000, 5000)}万',
            '{bond_amount}': f'{random.randint(500, 3000)}万',
            '{fund_amount}': f'{random.randint(200, 1000)}万',
            '{receivable}': f'{random.randint(1000, 5000)}万',
            '{payable}': f'{random.randint(800, 4500)}万',
            '{net}': f'{random.randint(100, 1000)}万',
            '{management_fee}': f'{random.randint(10, 100)}万',
            '{custody_fee}': f'{random.randint(5, 50)}万',
            '{other_fee}': f'{random.randint(1, 20)}万',
            '{total_fee}': f'{random.randint(20, 150)}万',
            '{trade_amount}': f'{random.randint(1000, 5000)}万',
            '{fee_amount}': f'{random.randint(10, 100)}万',
            '{adjust_amount}': f'{random.randint(0, 50)}万',
            '{reason1}': random.choice(['交易确认时点差异', '费用计算方法不同', '汇率折算差异']),
            '{reason2}': random.choice(['应收利息计算差异', '估值方法差异', '数据传输延迟']),
            '{reason3}': random.choice(['系统处理差异', '人工调整', '其他因素']),
            '{period}': f'{email_time.year}年第{(email_time.month-1)//3+1}季度',
            '{date1}': (email_time + timedelta(days=5)).strftime('%m月%d日'),
            '{date2}': (email_time + timedelta(days=10)).strftime('%m月%d日'),
            '{date3}': (email_time + timedelta(days=15)).strftime('%m月%d日'),
            '{date4}': (email_time + timedelta(days=20)).strftime('%m月%d日'),
            '{doc_name}': f'{product}2024年第{random.randint(1,4)}季度报告',
            '{reviewer}': random.choice(['李经理', '王主管', '张总监']),
            '{review_date}': email_time.strftime('%Y-%m-%d'),
            '{format_count}': str(random.randint(1, 5)),
            '{content_count}': str(random.randint(1, 3)),
            '{compliance_count}': str(random.randint(0, 2)),
            '{page1}': str(random.randint(1, 10)),
            '{page2}': str(random.randint(11, 20)),
            '{page3}': str(random.randint(21, 30)),
            '{phone}': '010-12345678',
            '{email}': 'reviewer@efunds.com',
            '{check_date}': (email_time + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
            '{checker}': random.choice(['合规部检查组', '内审部', '风控部']),
            '{regulation}': random.choice(['关于加强基金投资管理的通知', '资管新规实施细则', '基金信息披露管理办法']),
            '{regulator}': random.choice(['证监会', '基金业协会', '银保监会']),
            '{reg_date}': (email_time - timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
            '{completed}': str(random.randint(5, 10)),
            '{ongoing}': str(random.randint(2, 5)),
            '{pending}': str(random.randint(0, 3)),
            '{risk_type}': random.choice(['流动性风险', '市场风险', '信用风险']),
            '{level}': random.choice(['高', '中', '低']),
            '{alert_time}': email_time.strftime('%Y-%m-%d %H:%M'),
            '{volatility}': f'{random.uniform(1, 5):.2f}',
            '{drawdown}': f'{random.uniform(2, 10):.2f}',
            '{risk_level}': random.choice(['高', '中', '低']),
            '{liquidity}': f'{random.uniform(80, 95):.1f}',
            '{threshold}': '85.0',
            '{excess}': f'{random.uniform(0, 5):.1f}',
            '{rating}': random.choice(['AAA', 'AA+', 'AA']),
            '{default_prob}': f'{random.uniform(0.1, 2):.2f}',
            '{exposure}': f'{random.randint(1000, 10000)}万',
            '{report_no}': f'R{email_time.strftime("%Y%m%d")}{random.randint(1, 99):02d}',
            '{index1}': f'{random.randint(3000, 3500)}',
            '{change1}': f'{random.uniform(-2, 2):+.2f}',
            '{index2}': f'{random.randint(10000, 12000)}',
            '{change2}': f'{random.uniform(-2, 2):+.2f}',
            '{index3}': f'{random.randint(2000, 2500)}',
            '{change3}': f'{random.uniform(-2, 2):+.2f}',
            '{bond_yield}': f'{random.uniform(2.5, 3.5):.2f}',
            '{credit_spread}': f'{random.randint(50, 150)}',
            '{sentiment}': random.choice(['乐观', '中性', '谨慎']),
            '{avg_return}': f'{random.uniform(-1, 1):+.2f}',
            '{max_drawdown}': f'{random.uniform(1, 5):.2f}',
            '{liq1}': f'{random.uniform(80, 95):.1f}',
            '{liq2}': f'{random.uniform(80, 95):.1f}',
            '{liq3}': f'{random.uniform(80, 95):.1f}',
            '{credit_events}': str(random.randint(0, 3)),
            '{rating_changes}': str(random.randint(0, 5)),
            '{default_risk}': random.choice(['低', '中', '高'])
        }
        
        subject = subject_template
        body = body_template
        for key, value in replacements.items():
            subject = subject.replace(key, value)
            body = body.replace(key, value)
        
        # 提取信息
        dates = re.findall(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}日?', body)
        amounts = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?[万元]', body)
        
        # 提取关键词
        keywords = []
        keyword_patterns = ['紧急', '重要', '确认', '核对', '差异', '调整', '截止', '预警', '风险', '合规']
        for kw in keyword_patterns:
            if kw in subject or kw in body:
                keywords.append(kw)
        
        # 确定优先级
        if '紧急' in subject or '【紧急】' in subject:
            priority = '紧急'
            ai_score = random.randint(8, 10)
        elif '重要' in subject or '【重要】' in subject:
            priority = '重要'
            ai_score = random.randint(6, 8)
        else:
            priority = '普通'
            ai_score = random.randint(3, 7)
        
        # 确定发件人
        if category == '估值':
            sender = random.choice(['托管行-工商银行', '托管行-建设银行', '内部-估值部'])
        elif category == '交易':
            sender = random.choice(['交易对手-中信证券', '交易对手-华泰证券', '内部-交易部'])
        elif category == '清算':
            sender = random.choice(['托管行-