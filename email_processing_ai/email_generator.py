"""
邮件生成器 - 生成随机真实的邮件数据
"""

import random
from datetime import datetime, timedelta
import re

def generate_realistic_emails():
    """生成30封随机真实的邮件"""
    
    emails = []
    
    # 邮件模板库 - 更加随机和真实
    email_templates = [
        # 1. 简短通知类（bullet points）
        {
            'subject': '今日估值数据已更新',
            'sender': '估值系统 <valuation@efunds.com>',
            'category': '估值',
            'body': '''各位同事：

今日估值数据已完成更新，请注意：

• 更新时间：{date1}
• 涉及基金：HKGBF、HKGCLF、HKHKDCF
• 数据状态：正常
• 下一次更新：{date2}

如有疑问请联系估值团队。''',
            'has_dates': True,
            'has_amounts': False,
            'has_keywords': True
        },
        
        # 2. 详细说明类（大段文字）
        {
            'subject': '关于HKCACIB基金估值差异的说明',
            'sender': '张明 <zhang.ming@efunds.com>',
            'category': '估值',
            'body': '''各位领导、同事：

关于{date1}HKCACIB基金出现的估值差异问题，经过详细核查，现将情况说明如下。该基金在当日收盘后进行估值核算时，发现净值与托管行数据存在{amount1}的差异。经过逐笔核对交易记录和持仓数据，我们发现差异主要来源于一笔债券交易的估值方法不一致。托管行采用了收盘价估值，而我们系统使用的是第三方估值机构提供的公允价值。经与托管行沟通确认，双方同意采用第三方估值价格作为最终估值依据。目前该问题已经解决，净值数据已重新计算并更新。后续我们会加强与托管行的沟通，避免类似情况再次发生。请各位知悉。''',
            'has_dates': True,
            'has_amounts': True,
            'has_keywords': True
        },
        
        # 3. 紧急通知类（信息不全）
        {
            'subject': '紧急：交易确认单缺失',
            'sender': '李华 <li.hua@efunds.com>',
            'category': '交易',
            'body': '''紧急通知！

HKCAHXB基金今日有一笔交易尚未收到确认单，请相关同事尽快跟进处理。交易对手方为招商证券，涉及债券品种。

请在今日下班前完成确认，谢谢！''',
            'has_dates': False,
            'has_amounts': False,
            'has_keywords': True
        },
        
        # 4. 数据核对类（bullet + 金额）
        {
            'subject': '基金清算数据核对',
            'sender': '清算部 <settlement@efunds.com>',
            'category': '清算',
            'body': '''各位同事：

请核对以下基金的清算数据：

基金代码：HKGRBF
清算日期：{date1}
应收金额：{amount1}
实收金额：{amount2}
差异金额：{amount3}

请在{date2}前完成核对并反馈结果。''',
            'has_dates': True,
            'has_amounts': True,
            'has_keywords': True
        },
        
        # 5. 会议通知类（无金额）
        {
            'subject': '运营部周会通知',
            'sender': '王芳 <wang.fang@efunds.com>',
            'category': '其他',
            'body': '''各位同事：

本周运营部例会安排如下：

会议时间：{date1} 14:00-16:00
会议地点：会议室A
参会人员：全体运营部成员

主要议题包括本周工作总结、下周工作计划、系统优化讨论等。请大家准时参加。''',
            'has_dates': True,
            'has_amounts': False,
            'has_keywords': False
        },
        
        # 6. 问题反馈类（大段文字，无日期）
        {
            'subject': '系统操作问题反馈',
            'sender': '陈静 <chen.jing@efunds.com>',
            'category': '其他',
            'body': '''技术支持团队：

在使用估值系统时遇到一些问题，希望能得到帮助。具体情况是这样的，当我尝试导入交易数据时，系统总是提示格式错误，但我已经按照模板要求整理了数据。我检查了多次，包括日期格式、金额格式、基金代码等，都没有发现明显错误。不知道是不是系统最近有更新导致的兼容性问题。另外，在查询历史估值数据时，系统响应速度也比较慢，有时候需要等待很长时间才能显示结果。这些问题影响了日常工作效率，希望能尽快解决。如果需要提供更详细的信息或者截图，请告诉我。谢谢！''',
            'has_dates': False,
            'has_amounts': False,
            'has_keywords': True
        },
        
        # 7. 交易确认类（完整信息）
        {
            'subject': 'HKCACLR2基金交易确认',
            'sender': '交易部 <trading@efunds.com>',
            'category': '交易',
            'body': '''交易确认通知：

基金名称：HKCACLR2
交易日期：{date1}
交易类型：买入
证券代码：000001.SZ
证券名称：平安银行
交易数量：100,000股
成交价格：15.50元
交易金额：{amount1}
结算日期：{date2}
交易对手：中信证券

请相关人员确认并更新系统数据。''',
            'has_dates': True,
            'has_amounts': True,
            'has_keywords': True
        },
        
        # 8. 简短提醒（信息极少）
        {
            'subject': '提醒：报表提交截止',
            'sender': '系统提醒 <noreply@efunds.com>',
            'category': '其他',
            'body': '''温馨提醒：

月度运营报表提交截止日期为{date1}，请尚未提交的同事抓紧时间完成。

此邮件为系统自动发送，请勿回复。''',
            'has_dates': True,
            'has_amounts': False,
            'has_keywords': False
        },
        
        # 9. 详细分析类（大段文字+数据）
        {
            'subject': '本月基金运营数据分析报告',
            'sender': '数据分析组 <analytics@efunds.com>',
            'category': '报告',
            'body': '''各位领导、同事：

现将本月基金运营数据分析报告呈报如下。本月共处理交易笔数较上月增长15%，主要集中在股票型基金。从估值准确率来看，本月估值差异率控制在0.01%以内，达到了预期目标。具体来看，HKGBF基金本月交易金额达到{amount1}，为所有基金中最高。HKHKDCF基金虽然交易笔数不多，但单笔金额较大，平均每笔达到{amount2}。在清算效率方面，本月平均清算时间为T+1.2天，较上月的T+1.5天有所改善。但仍有个别基金存在清算延迟情况，主要原因是交易对手方确认不及时。建议下月加强与交易对手的沟通协调，进一步提升清算效率。另外，系统稳定性方面表现良好，本月未发生重大系统故障，仅有两次短暂的网络波动，已及时处理。''',
            'has_dates': False,
            'has_amounts': True,
            'has_keywords': True
        },
        
        # 10. 问询类（bullet points，无金额）
        {
            'subject': '关于HKCASAI3基金持仓的问询',
            'sender': '审计部 <audit@efunds.com>',
            'category': '审计',
            'body': '''运营部同事：

关于HKCASAI3基金，需要了解以下信息：

• 截至{date1}的完整持仓明细
• 近一个月的交易记录
• 估值方法说明文档
• 托管协议复印件

请在{date2}前提供相关资料，谢谢配合！''',
            'has_dates': True,
            'has_amounts': False,
            'has_keywords': True
        },
        
        # 11. 系统通知类（技术性，无日期金额）
        {
            'subject': '系统维护通知',
            'sender': 'IT部门 <it@efunds.com>',
            'category': '系统',
            'body': '''各位用户：

估值系统将进行例行维护升级，届时系统将暂停服务。维护期间请勿进行数据操作，以免造成数据丢失。本次维护主要内容包括数据库优化、性能提升、bug修复等。维护完成后系统功能和界面不会有明显变化，但整体运行速度会有所提升。如在维护后使用过程中遇到任何问题，请及时联系技术支持团队。感谢大家的理解与配合。''',
            'has_dates': False,
            'has_amounts': False,
            'has_keywords': True
        },
        
        # 12. 对账通知（完整信息）
        {
            'subject': '托管行对账差异处理',
            'sender': '对账组 <reconciliation@efunds.com>',
            'category': '清算',
            'body': '''紧急通知：

基金代码：HKHYBF
对账日期：{date1}
差异类型：现金余额不符
我方记录：{amount1}
托管行记录：{amount2}
差异金额：{amount3}

经初步核查，差异可能来源于一笔分红款项的入账时间差异。请相关同事立即核实并在{date2}前完成调整。''',
            'has_dates': True,
            'has_amounts': True,
            'has_keywords': True
        },
        
        # 13. 培训通知（无金额）
        {
            'subject': '新系统操作培训安排',
            'sender': '培训中心 <training@efunds.com>',
            'category': '培训',
            'body': '''各位同事：

为帮助大家更好地使用新上线的运营管理系统，特安排以下培训：

培训时间：{date1} 上午9:00-12:00
培训地点：培训室B
培训讲师：技术部李工
培训内容：系统基本操作、数据导入导出、报表生成、常见问题处理

请相关人员务必参加，如有特殊情况无法参加，请提前告知。''',
            'has_dates': True,
            'has_amounts': False,
            'has_keywords': False
        },
        
        # 14. 简短确认（极简）
        {
            'subject': 'Re: 数据已确认',
            'sender': '赵磊 <zhao.lei@efunds.com>',
            'category': '其他',
            'body': '''收到，数据已核对无误。

谢谢！''',
            'has_dates': False,
            'has_amounts': False,
            'has_keywords': False
        },
        
        # 15. 风险提示（大段文字）
        {
            'subject': '市场波动风险提示',
            'sender': '风控部 <risk@efunds.com>',
            'category': '风控',
            'body': '''各位基金经理、运营同事：

近期市场波动加剧，需要特别关注以下风险点。首先是流动性风险，部分债券品种交易量明显下降，可能影响估值准确性和赎回处理。建议加强对相关基金的流动性监控，必要时采取限制大额赎回等措施。其次是信用风险，个别发行主体出现负面新闻，虽然暂未影响债券价格，但需要密切关注后续发展。第三是操作风险，由于市场波动，交易确认和清算可能出现延迟，请运营团队做好应对准备。建议各基金经理审慎决策，运营团队加强风险监控，确保基金平稳运作。如有异常情况请及时上报。''',
            'has_dates': False,
            'has_amounts': False,
            'has_keywords': True
        },
    ]
    
    # 生成30封随机邮件
    base_date = datetime.now()
    
    for i in range(30):
        # 随机选择模板
        template = random.choice(email_templates)
        
        # 生成随机日期
        days_ago = random.randint(0, 7)
        email_time = base_date - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # 生成随机日期字符串
        date1 = (base_date - timedelta(days=random.randint(0, 5))).strftime('%Y年%m月%d日')
        date2 = (base_date + timedelta(days=random.randint(1, 7))).strftime('%Y年%m月%d日')
        
        # 生成随机金额
        amount1 = f"{random.randint(100, 9999)}万元"
        amount2 = f"{random.randint(100, 9999)}万元"
        amount3 = f"{random.randint(1, 100)}万元"
        
        # 填充模板
        body = template['body']
        if template['has_dates']:
            body = body.format(date1=date1, date2=date2, amount1=amount1, amount2=amount2, amount3=amount3)
        elif template['has_amounts']:
            body = body.format(amount1=amount1, amount2=amount2, amount3=amount3, date1=date1, date2=date2)
        else:
            body = body.replace('{date1}', date1).replace('{date2}', date2)
            body = body.replace('{amount1}', amount1).replace('{amount2}', amount2).replace('{amount3}', amount3)
        
        # 提取信息
        extracted_info = extract_information(body)
        
        # 生成AI总结
        ai_summary = generate_ai_summary(body, template['subject'], template['category'])
        
        # 生成关键词标签
        keyword_tags = generate_keyword_tags(body, template['subject'], template['category'])
        
        # 推荐处理人
        recommended_handler = recommend_handler(template['category'], body, template['subject'])
        
        # 计算AI评分
        ai_score = calculate_ai_score(template['category'], extracted_info, template['subject'])
        
        # 确定优先级
        if ai_score >= 8:
            priority = '高'
        elif ai_score >= 5:
            priority = '中'
        else:
            priority = '低'
        
        # 创建邮件对象
        email = {
            'id': f'EMAIL{i+1:03d}',
            'subject': template['subject'],
            'sender': template['sender'],
            'category': template['category'],
            'priority': priority,
            'ai_score': ai_score,
            'body': body,
            'received_time': email_time,
            'is_read': random.choice([True, False]),
            'has_attachments': random.choice([True, False, False]),  # 30%概率有附件
            'is_urgent': ai_score >= 8,
            'extracted_info': extracted_info,
            'ai_summary': ai_summary,
            'keyword_tags': keyword_tags,
            'recommended_handler': recommended_handler
        }
        
        emails.append(email)
    
    # 按时间倒序排序
    emails.sort(key=lambda x: x['received_time'], reverse=True)
    
    return emails

def extract_information(text):
    """从文本中提取关键信息"""
    info = {
        'dates': [],
        'amounts': [],
        'keywords': []
    }
    
    # 提取日期
    date_patterns = [
        r'\d{4}年\d{1,2}月\d{1,2}日',
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}/\d{2}/\d{4}'
    ]
    for pattern in date_patterns:
        dates = re.findall(pattern, text)
        info['dates'].extend(dates)
    
    # 去重
    info['dates'] = list(set(info['dates']))[:5]
    
    # 提取金额
    amount_patterns = [
        r'\d+(?:,\d{3})*(?:\.\d{2})?元',
        r'\d+(?:,\d{3})*万元',
        r'\d+(?:,\d{3})*亿元',
        r'[¥$]\s*\d+(?:,\d{3})*(?:\.\d{2})?'
    ]
    for pattern in amount_patterns:
        amounts = re.findall(pattern, text)
        info['amounts'].extend(amounts)
    
    # 去重
    info['amounts'] = list(set(info['amounts']))[:5]
    
    # 提取关键词
    keywords = ['紧急', '重要', '确认', '核对', '差异', '风险', '截止', '完成', '处理', '通知']
    for keyword in keywords:
        if keyword in text:
            info['keywords'].append(keyword)
    
    # 去重
    info['keywords'] = list(set(info['keywords']))[:5]
    
    return info

def calculate_ai_score(category, extracted_info, subject):
    """计算AI评分"""
    score = 5  # 基础分
    
    # 根据类别调整
    if category in ['估值', '交易', '清算']:
        score += 2
    
    # 根据提取信息调整
    if extracted_info['dates']:
        score += 1
    if extracted_info['amounts']:
        score += 1
    if extracted_info['keywords']:
        score += len(extracted_info['keywords']) * 0.3
    
    # 根据主题关键词调整
    urgent_keywords = ['紧急', '重要', '立即', '尽快', '截止']
    for keyword in urgent_keywords:
        if keyword in subject:
            score += 1
    
    # 限制在0-10之间
    score = max(0, min(10, score))
    
    return round(score, 1)

def generate_ai_summary(body, subject, category):
    """生成AI总结（模拟AI分析）"""
    summary_points = []
    
    # 提取日期
    dates = re.findall(r'\d{4}年\d{1,2}月\d{1,2}日', body)
    if dates:
        summary_points.append(f"📅 关键时间：{dates[0]}")
    
    # 提取金额
    amounts = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?(?:万元|亿元|元)', body)
    if amounts:
        if len(amounts) == 1:
            summary_points.append(f"💰 涉及金额：{amounts[0]}")
        else:
            summary_points.append(f"💰 涉及金额：{amounts[0]}等{len(amounts)}笔")
    
    # 根据类别生成事项总结
    if category == '估值':
        if '差异' in body:
            summary_points.append("📊 事项：估值差异需要核对处理")
        elif '更新' in body or '完成' in body:
            summary_points.append("📊 事项：估值数据已更新完成")
        else:
            summary_points.append("📊 事项：估值相关工作事项")
    
    elif category == '交易':
        if '确认' in body:
            summary_points.append("💼 事项：交易确认单需要处理")
        elif '缺失' in body or '遗漏' in body:
            summary_points.append("💼 事项：交易文件缺失需跟进")
        else:
            summary_points.append("💼 事项：交易相关业务处理")
    
    elif category == '清算':
        if '核对' in body or '对账' in body:
            summary_points.append("🔄 事项：清算数据需要核对")
        elif '差异' in body:
            summary_points.append("🔄 事项：清算差异需要处理")
        else:
            summary_points.append("🔄 事项：清算业务处理")
    
    elif category == '审计':
        summary_points.append("🔍 事项：审计资料需要准备提供")
    
    elif category == '风控':
        summary_points.append("⚠️ 事项：风险提示需要关注")
    
    elif category == '系统':
        if '维护' in body:
            summary_points.append("🔧 事项：系统维护通知")
        else:
            summary_points.append("🔧 事项：系统相关事项")
    
    elif category == '培训':
        summary_points.append("📚 事项：培训安排通知")
    
    elif category == '报告':
        summary_points.append("📈 事项：报告分析内容")
    
    else:
        summary_points.append("📋 事项：一般性工作通知")
    
    # 提取基金代码
    fund_codes = re.findall(r'HK[A-Z]{2,10}', body)
    if fund_codes:
        unique_funds = list(set(fund_codes))[:3]
        if len(unique_funds) == 1:
            summary_points.append(f"🏦 涉及基金：{unique_funds[0]}")
        else:
            summary_points.append(f"🏦 涉及基金：{', '.join(unique_funds)}等{len(unique_funds)}只")
    
    # 判断紧急程度
    urgent_keywords = ['紧急', '立即', '尽快', '截止']
    if any(keyword in subject or keyword in body for keyword in urgent_keywords):
        summary_points.append("⏰ 紧急程度：高，需要优先处理")
    
    # 提取对接人/部门
    if '托管行' in body:
        summary_points.append("👥 对接方：托管行")
    elif '交易对手' in body or '券商' in body or '证券' in body:
        summary_points.append("👥 对接方：交易对手方")
    elif '审计' in body:
        summary_points.append("👥 对接方：审计部门")
    elif 'IT' in body or '技术' in body:
        summary_points.append("👥 对接方：技术部门")
    
    # 如果没有生成任何要点，添加默认要点
    if not summary_points:
        summary_points.append("📋 邮件内容需要查看详情")
    
    return summary_points

def generate_keyword_tags(body, subject, category):
    """生成关键词标签"""
    tags = []
    
    # 1. 业务类型标签
    business_tags = {
        '估值': '估值核算',
        '交易': '交易处理',
        '清算': '清算结算',
        '审计': '审计合规',
        '风控': '风险管理',
        '系统': '系统运维',
        '培训': '培训学习',
        '报告': '数据分析',
        '其他': '一般事务'
    }
    tags.append(business_tags.get(category, '一般事务'))
    
    # 2. 紧急程度标签
    urgent_keywords = ['紧急', '立即', '尽快', '马上']
    important_keywords = ['重要', '关键', '必须', '务必']
    deadline_keywords = ['截止', '期限', '最晚']
    
    if any(keyword in subject or keyword in body for keyword in urgent_keywords):
        tags.append('紧急处理')
    elif any(keyword in subject or keyword in body for keyword in important_keywords):
        tags.append('重要事项')
    elif any(keyword in subject or keyword in body for keyword in deadline_keywords):
        tags.append('有截止期限')
    else:
        tags.append('常规事项')
    
    # 3. 对接人员/部门标签
    if '托管行' in body or '托管' in body:
        tags.append('托管行对接')
    if '交易对手' in body or '券商' in body or '证券' in body:
        tags.append('交易对手对接')
    if '审计' in body:
        tags.append('审计部门')
    if 'IT' in body or '技术' in body or '系统' in body:
        tags.append('技术支持')
    if '风控' in body or '风险' in body:
        tags.append('风控部门')
    
    # 4. 操作类型标签
    if '确认' in body or '核对' in body:
        tags.append('需要确认')
    if '提交' in body or '上报' in body:
        tags.append('需要提交')
    if '查询' in body or '问询' in body:
        tags.append('信息查询')
    if '通知' in subject or '提醒' in subject:
        tags.append('通知类')
    if '会议' in body or '培训' in body:
        tags.append('会议培训')
    
    # 5. 数据相关标签
    if '差异' in body:
        tags.append('存在差异')
    if '金额' in body or re.search(r'\d+(?:万|亿)?元', body):
        tags.append('涉及金额')
    if re.search(r'HK[A-Z]{2,10}', body):
        tags.append('涉及基金')
    
    # 6. 状态标签 - 删除"已完成"相关标签
    if '待' in body or '需要' in body:
        tags.append('待处理')
    
    # 去重并限制数量
    tags = list(dict.fromkeys(tags))  # 保持顺序去重
    return tags[:8]  # 最多返回8个标签

def recommend_handler(category, body, subject):
    """根据邮件内容推荐处理人"""
    
    # 根据类别推荐
    if category == '估值':
        return '估值员'
    elif category == '交易':
        return '交易员'
    elif category == '清算':
        return '清算员'
    elif category == '审计':
        return '合规员'
    elif category == '风控':
        return '风控员'
    elif category == '系统':
        return '技术员'
    elif category == '培训':
        return '全部'
    elif category == '报告':
        return '披露员'
    else:
        # 根据内容关键词推荐
        if '估值' in body or '净值' in body:
            return '估值员'
        elif '交易' in body or '买入' in body or '卖出' in body:
            return '交易员'
        elif '清算' in body or '结算' in body:
            return '清算员'
        elif '披露' in body or '报告' in body:
            return '披露员'
        elif '合规' in body or '审计' in body:
            return '合规员'
        elif '风险' in body or '风控' in body:
            return '风控员'
        else:
            return '全部'

if __name__ == '__main__':
    emails = generate_realistic_emails()
    print(f"生成了 {len(emails)} 封邮件")
    for email in emails[:3]:
        print(f"\n标题: {email['subject']}")
        print(f"发件人: {email['sender']}")
        print(f"正文长度: {len(email['body'])} 字符")
        print(f"提取信息: {email['extracted_info']}")