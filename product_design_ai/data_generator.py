"""
数据生成器
生成模拟的历史流程数据、产品特征、监管规则和案例库
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

class DataGenerator:
    """数据生成器类"""
    
    def __init__(self, output_dir='data'):
        """初始化数据生成器"""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 产品类型
        self.product_types = ['股票型', '债券型', '混合型', '货币型', 'QDII', 'FOF']
        
        # 投资范围
        self.investment_scopes = ['境内股票', '境内债券', '境外股票', '境外债券', '混合资产']
        
        # 交易市场
        self.trading_markets = ['沪深交易所', '银行间市场', '香港交易所', '美国市场', '多市场']
        
        # 托管行
        self.custodians = ['工商银行', '建设银行', '招商银行', '中信银行', '浦发银行']
        
        # 部门
        self.departments = ['交易部', '清算部', '估值部', '披露部', '合规部', '风控部']
        
        # 步骤类型
        self.step_types = ['交易', '清算', '估值', '披露', '合规检查', '风险监控', '托管核对']
        
        # 问题类型
        self.issue_types = ['延迟', '错误', '遗漏', '协作问题', '系统问题', '数据问题']
        
        # 影响程度
        self.impact_levels = ['高', '中', '低']
        
    def generate_all_data(self, num_products=50):
        """生成所有数据"""
        print("开始生成数据...")
        
        # 1. 生成产品特征数据
        print("生成产品特征数据...")
        products_df = self.generate_product_features(num_products)
        products_df.to_csv(os.path.join(self.output_dir, 'product_features.csv'), 
                          index=False, encoding='utf-8-sig')
        
        # 2. 生成历史流程数据
        print("生成历史流程数据...")
        processes_df, steps_df, issues_df = self.generate_historical_processes(products_df)
        processes_df.to_csv(os.path.join(self.output_dir, 'historical_processes.csv'), 
                           index=False, encoding='utf-8-sig')
        steps_df.to_csv(os.path.join(self.output_dir, 'process_steps.csv'), 
                       index=False, encoding='utf-8-sig')
        issues_df.to_csv(os.path.join(self.output_dir, 'process_issues.csv'), 
                        index=False, encoding='utf-8-sig')
        
        # 3. 生成监管规则数据
        print("生成监管规则数据...")
        rules_df = self.generate_regulatory_rules()
        rules_df.to_csv(os.path.join(self.output_dir, 'regulatory_rules.csv'), 
                       index=False, encoding='utf-8-sig')
        
        # 4. 生成案例库数据
        print("生成案例库数据...")
        cases_df = self.generate_case_library(products_df, issues_df)
        cases_df.to_csv(os.path.join(self.output_dir, 'case_library.csv'), 
                       index=False, encoding='utf-8-sig')
        
        print(f"数据生成完成！共生成：")
        print(f"  - 产品特征: {len(products_df)} 条")
        print(f"  - 历史流程: {len(processes_df)} 条")
        print(f"  - 流程步骤: {len(steps_df)} 条")
        print(f"  - 流程问题: {len(issues_df)} 条")
        print(f"  - 监管规则: {len(rules_df)} 条")
        print(f"  - 案例库: {len(cases_df)} 条")
        
        return {
            'products': products_df,
            'processes': processes_df,
            'steps': steps_df,
            'issues': issues_df,
            'rules': rules_df,
            'cases': cases_df
        }
    
    def generate_product_features(self, num_products=50):
        """生成产品特征数据"""
        data = []
        
        for i in range(num_products):
            product_type = random.choice(self.product_types)
            
            # 根据产品类型设置特征
            if product_type == '股票型':
                asset_class = '股票'
                investment_strategy = random.choice(['主动管理', '指数跟踪', '量化投资'])
                risk_level = random.choice(['高', '中高'])
                trading_frequency = random.choice(['高频', '中频'])
                settlement_cycle = 'T+1'
                valuation_method = '市价法'
                disclosure_frequency = '季度'
            elif product_type == '债券型':
                asset_class = '债券'
                investment_strategy = random.choice(['信用债', '利率债', '可转债'])
                risk_level = random.choice(['低', '中低'])
                trading_frequency = random.choice(['低频', '中频'])
                settlement_cycle = 'T+1'
                valuation_method = random.choice(['市价法', '摊余成本法'])
                disclosure_frequency = '季度'
            elif product_type == '货币型':
                asset_class = '货币市场工具'
                investment_strategy = '流动性管理'
                risk_level = '低'
                trading_frequency = '高频'
                settlement_cycle = 'T+0'
                valuation_method = '摊余成本法'
                disclosure_frequency = '每日'
            else:
                asset_class = random.choice(['股票', '债券', '混合资产'])
                investment_strategy = random.choice(['主动管理', '被动管理', '混合策略'])
                risk_level = random.choice(['高', '中高', '中', '中低', '低'])
                trading_frequency = random.choice(['高频', '中频', '低频'])
                settlement_cycle = random.choice(['T+0', 'T+1', 'T+2'])
                valuation_method = random.choice(['市价法', '摊余成本法', '混合法'])
                disclosure_frequency = random.choice(['每日', '每周', '季度'])
            
            data.append({
                'product_id': f'PROD{i+1:04d}',
                'product_name': f'易方达{product_type}基金{i+1}号',
                'product_type': product_type,
                'asset_class': asset_class,
                'investment_scope': random.choice(self.investment_scopes),
                'trading_market': random.choice(self.trading_markets),
                'custodian': random.choice(self.custodians),
                'investment_strategy': investment_strategy,
                'risk_level': risk_level,
                'trading_frequency': trading_frequency,
                'settlement_cycle': settlement_cycle,
                'valuation_method': valuation_method,
                'disclosure_frequency': disclosure_frequency,
                'special_requirements': random.choice(['无', '跨境投资', '衍生品投资', '杠杆投资', ''])
            })
        
        return pd.DataFrame(data)
    
    def generate_historical_processes(self, products_df):
        """生成历史流程数据"""
        processes = []
        all_steps = []
        all_issues = []
        
        for idx, product in products_df.iterrows():
            product_id = product['product_id']
            product_type = product['product_type']
            
            # 每个产品生成1-2个流程版本
            num_versions = random.randint(1, 2)
            
            for version in range(1, num_versions + 1):
                process_id = f"{product_id}_V{version}"
                setup_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
                
                # 流程状态
                if version == num_versions:
                    status = random.choice(['执行中', '已完成'])
                else:
                    status = '已完成'
                
                processes.append({
                    'process_id': process_id,
                    'product_id': product_id,
                    'product_name': product['product_name'],
                    'product_type': product_type,
                    'investment_scope': product['investment_scope'],
                    'trading_market': product['trading_market'],
                    'custodian': product['custodian'],
                    'setup_date': setup_date.strftime('%Y-%m-%d'),
                    'process_version': version,
                    'status': status
                })
                
                # 生成流程步骤
                steps, issues = self.generate_process_steps(process_id, product_id, product_type, setup_date)
                all_steps.extend(steps)
                all_issues.extend(issues)
        
        return pd.DataFrame(processes), pd.DataFrame(all_steps), pd.DataFrame(all_issues)
    
    def generate_process_steps(self, process_id, product_id, product_type, setup_date):
        """生成流程步骤"""
        steps = []
        issues = []
        
        # 根据产品类型定义标准流程
        if product_type in ['股票型', 'QDII']:
            step_templates = [
                ('交易指令接收', '交易部', '交易', None, 1, 0.5),
                ('交易执行', '交易部', '交易', 'STEP001', 2, 1),
                ('交易确认', '交易部', '交易', 'STEP002', 1, 0.5),
                ('清算数据接收', '清算部', '清算', 'STEP003', 2, 1),
                ('清算处理', '清算部', '清算', 'STEP004', 3, 2),
                ('托管行清算核对', '清算部', '清算', 'STEP005', 2, 1),
                ('估值数据准备', '估值部', '估值', 'STEP006', 2, 1),
                ('估值计算', '估值部', '估值', 'STEP007', 3, 2),
                ('托管行估值核对', '估值部', '估值', 'STEP008', 2, 1.5),
                ('估值结果确认', '估值部', '估值', 'STEP009', 1, 0.5),
                ('信息披露准备', '披露部', '披露', 'STEP010', 2, 1),
                ('信息披露审核', '披露部', '披露', 'STEP011', 2, 1),
                ('信息披露发布', '披露部', '披露', 'STEP012', 1, 0.5)
            ]
        elif product_type == '债券型':
            step_templates = [
                ('交易指令接收', '交易部', '交易', None, 1, 0.5),
                ('交易执行', '交易部', '交易', 'STEP001', 2, 1),
                ('交易确认', '交易部', '交易', 'STEP002', 1, 0.5),
                ('清算数据接收', '清算部', '清算', 'STEP003', 2, 1),
                ('清算处理', '清算部', '清算', 'STEP004', 2, 1.5),
                ('托管行清算核对', '清算部', '清算', 'STEP005', 2, 1),
                ('估值数据准备', '估值部', '估值', 'STEP006', 1, 0.5),
                ('估值计算', '估值部', '估值', 'STEP007', 2, 1.5),
                ('托管行估值核对', '估值部', '估值', 'STEP008', 2, 1),
                ('估值结果确认', '估值部', '估值', 'STEP009', 1, 0.5),
                ('信息披露准备', '披露部', '披露', 'STEP010', 1, 0.5),
                ('信息披露发布', '披露部', '披露', 'STEP011', 1, 0.5)
            ]
        elif product_type == '货币型':
            step_templates = [
                ('交易指令接收', '交易部', '交易', None, 0.5, 0.3),
                ('交易执行', '交易部', '交易', 'STEP001', 1, 0.5),
                ('清算处理', '清算部', '清算', 'STEP002', 1, 0.5),
                ('估值计算', '估值部', '估值', 'STEP003', 1, 0.5),
                ('托管行核对', '估值部', '估值', 'STEP004', 1, 0.5),
                ('信息披露', '披露部', '披露', 'STEP005', 0.5, 0.3)
            ]
        else:
            step_templates = [
                ('交易指令接收', '交易部', '交易', None, 1, 0.5),
                ('交易执行', '交易部', '交易', 'STEP001', 2, 1),
                ('清算处理', '清算部', '清算', 'STEP002', 2, 1.5),
                ('托管行清算核对', '清算部', '清算', 'STEP003', 2, 1),
                ('估值计算', '估值部', '估值', 'STEP004', 2, 1.5),
                ('托管行估值核对', '估值部', '估值', 'STEP005', 2, 1),
                ('信息披露', '披露部', '披露', 'STEP006', 1, 0.5)
            ]
        
        current_time = setup_date + timedelta(hours=9)  # 从早上9点开始
        
        for i, (step_name, dept, step_type, predecessor, planned_hours, actual_hours_base) in enumerate(step_templates):
            step_id = f"{process_id}_STEP{i+1:03d}"
            
            # 实际时长有波动
            actual_hours = actual_hours_base * random.uniform(0.8, 1.5)
            
            # 步骤状态
            status = random.choice(['已完成', '已完成', '已完成', '有问题'])
            
            start_time = current_time
            end_time = current_time + timedelta(hours=actual_hours)
            
            steps.append({
                'step_id': step_id,
                'process_id': process_id,
                'product_id': product_id,
                'step_name': step_name,
                'step_type': step_type,
                'responsible_dept': dept,
                'responsible_person': f'{dept}_{random.randint(1, 5)}号员工',
                'predecessor_steps': predecessor if predecessor else '',
                'planned_duration': planned_hours,
                'actual_duration': round(actual_hours, 2),
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': status
            })
            
            # 如果有问题，生成问题记录
            if status == '有问题' and random.random() < 0.7:
                issue_type = random.choice(self.issue_types)
                impact_level = random.choice(self.impact_levels)
                
                # 根据问题类型生成描述
                if issue_type == '延迟':
                    issue_desc = f'{step_name}环节执行延迟，超出计划时间{round((actual_hours - planned_hours) * 60)}分钟'
                    root_cause = random.choice(['数据准备不及时', '系统响应慢', '人员协调问题', '前置步骤延迟'])
                    solution = random.choice(['优化数据准备流程', '升级系统性能', '加强协作机制', '调整时间安排'])
                elif issue_type == '错误':
                    issue_desc = f'{step_name}环节出现数据错误，需要重新处理'
                    root_cause = random.choice(['数据源错误', '计算公式错误', '人工操作失误', '系统bug'])
                    solution = random.choice(['修正数据源', '修正计算逻辑', '加强培训', '修复系统'])
                elif issue_type == '遗漏':
                    issue_desc = f'{step_name}环节遗漏关键步骤或数据'
                    root_cause = random.choice(['流程设计不完整', '检查清单缺失', '人员疏忽', '系统提示不足'])
                    solution = random.choice(['完善流程设计', '建立检查清单', '加强培训', '优化系统提示'])
                else:
                    issue_desc = f'{step_name}环节{issue_type}'
                    root_cause = random.choice(['流程设计问题', '系统问题', '人员问题', '协作问题'])
                    solution = random.choice(['优化流程', '修复系统', '加强培训', '改进协作'])
                
                issue_time = start_time + timedelta(hours=actual_hours * 0.5)
                resolution_time = end_time
                
                issues.append({
                    'issue_id': f"{step_id}_ISSUE",
                    'process_id': process_id,
                    'product_id': product_id,
                    'step_id': step_id,
                    'issue_type': issue_type,
                    'issue_desc': issue_desc,
                    'root_cause': root_cause,
                    'solution': solution,
                    'impact_level': impact_level,
                    'occurrence_time': issue_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'resolution_time': resolution_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            current_time = end_time
        
        return steps, issues
    
    def generate_regulatory_rules(self):
        """生成监管规则数据"""
        rules = [
            {
                'rule_id': 'RULE001',
                'rule_name': '基金交易结算规定',
                'rule_category': '交易',
                'applicable_products': '所有产品',
                'rule_content': '基金交易应当遵循T+1结算原则，特殊情况需报备',
                'effective_date': '2020-01-01',
                'source': '证监会'
            },
            {
                'rule_id': 'RULE002',
                'rule_name': '基金估值业务指引',
                'rule_category': '估值',
                'applicable_products': '所有产品',
                'rule_content': '基金估值应当采用公允价值计量，确保估值的准确性和及时性',
                'effective_date': '2020-01-01',
                'source': '基金业协会'
            },
            {
                'rule_id': 'RULE003',
                'rule_name': '货币市场基金估值规定',
                'rule_category': '估值',
                'applicable_products': '货币型',
                'rule_content': '货币市场基金可采用摊余成本法进行估值',
                'effective_date': '2020-01-01',
                'source': '证监会'
            },
            {
                'rule_id': 'RULE004',
                'rule_name': '基金信息披露管理办法',
                'rule_category': '披露',
                'applicable_products': '所有产品',
                'rule_content': '基金应当按照规定及时、准确、完整地披露信息',
                'effective_date': '2020-01-01',
                'source': '证监会'
            },
            {
                'rule_id': 'RULE005',
                'rule_name': 'QDII基金投资管理规定',
                'rule_category': '交易',
                'applicable_products': 'QDII',
                'rule_content': 'QDII基金投资境外市场应当遵守外汇管理规定',
                'effective_date': '2020-01-01',
                'source': '证监会'
            },
            {
                'rule_id': 'RULE006',
                'rule_name': '基金托管业务管理办法',
                'rule_category': '合规',
                'applicable_products': '所有产品',
                'rule_content': '基金托管人应当履行安全保管、资金清算、会计复核等职责',
                'effective_date': '2020-01-01',
                'source': '证监会'
            },
            {
                'rule_id': 'RULE007',
                'rule_name': '基金风险管理指引',
                'rule_category': '风控',
                'applicable_products': '所有产品',
                'rule_content': '基金管理人应当建立健全风险管理体系',
                'effective_date': '2020-01-01',
                'source': '基金业协会'
            },
            {
                'rule_id': 'RULE008',
                'rule_name': '基金清算业务规范',
                'rule_category': '清算',
                'applicable_products': '所有产品',
                'rule_content': '基金清算应当确保数据准确、流程规范、时效性强',
                'effective_date': '2020-01-01',
                'source': '基金业协会'
            }
        ]
        
        return pd.DataFrame(rules)
    
    def generate_case_library(self, products_df, issues_df):
        """生成案例库数据"""
        cases = []
        
        # 从问题中提取案例
        for idx, issue in issues_df.iterrows():
            if random.random() < 0.3:  # 30%的问题转化为案例
                product_id = issue['product_id']
                product = products_df[products_df['product_id'] == product_id].iloc[0]
                
                case_type = '失败案例' if issue['impact_level'] == '高' else '成功案例'
                
                cases.append({
                    'case_id': f"CASE{len(cases)+1:04d}",
                    'product_id': product_id,
                    'product_type': product['product_type'],
                    'case_type': case_type,
                    'scenario': f"{product['product_type']}产品{issue['issue_type']}问题",
                    'problem_desc': issue['issue_desc'],
                    'root_cause': issue['root_cause'],
                    'solution': issue['solution'],
                    'lessons_learned': f"在{product['product_type']}产品流程设计中，需要特别注意{issue['issue_type']}风险",
                    'best_practices': f"建议：{issue['solution']}",
                    'tags': f"{product['product_type']},{issue['issue_type']},{issue['impact_level']}影响"
                })
        
        # 添加一些成功案例
        success_cases = [
            {
                'case_id': f"CASE{len(cases)+1:04d}",
                'product_id': 'PROD0001',
                'product_type': '股票型',
                'case_type': '成功案例',
                'scenario': '股票型产品流程优化',
                'problem_desc': '初始流程设计中估值核对环节耗时过长',
                'root_cause': '托管行核对流程不够自动化',
                'solution': '与托管行协商建立自动化核对接口',
                'lessons_learned': '提前与托管行沟通技术对接方案可以大幅提升效率',
                'best_practices': '在产品设计阶段就与托管行确定技术对接方案',
                'tags': '股票型,流程优化,自动化'
            },
            {
                'case_id': f"CASE{len(cases)+2:04d}",
                'product_id': 'PROD0002',
                'product_type': '债券型',
                'case_type': '成功案例',
                'scenario': '债券型产品清算流程简化',
                'problem_desc': '清算流程步骤过多，容易出错',
                'root_cause': '流程设计过于复杂',
                'solution': '合并部分可以并行的步骤，简化流程',
                'lessons_learned': '流程设计应当追求简洁高效，避免不必要的复杂性',
                'best_practices': '定期review流程，持续优化',
                'tags': '债券型,流程简化,效率提升'
            }
        ]
        
        cases.extend(success_cases)
        
        return pd.DataFrame(cases)

def main():
    """主函数"""
    generator = DataGenerator(output_dir='product_design_ai/data')
    data = generator.generate_all_data(num_products=50)
    print("\n数据生成完成！")
    print(f"数据保存在: product_design_ai/data/")

if __name__ == '__main__':
    main()