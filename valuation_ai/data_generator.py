"""
估值核对AI助手 - 数据生成模块
生成模拟的估值差异数据和历史案例数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

class ValuationDataGenerator:
    """估值数据生成器"""
    
    def __init__(self, seed=42):
        """初始化生成器
        
        Args:
            seed: 随机种子，保证可重复性
        """
        random.seed(seed)
        np.random.seed(seed)
        
        # 基金代码和名称
        self.funds = {
            'HKGBF': '香港全球债券基金',
            'HKGRBF': '香港环球股票基金',
            'HKHYBF': '香港高收益债券基金',
            'HKGCLF': '香港中国股票基金',
            'HKMMF': '香港货币市场基金',
            'HKCACLR1': '香港中国A股基金',
            'HKCACLR2': '香港亚洲债券基金'
        }
        
        # 资产类别
        self.asset_classes = ['Bond', 'Equity', 'Cash', 'Fund']
        
        # 差异类型及其特征
        self.difference_types = {
            '价格差异': {
                'causes': [
                    '托管行使用前日收盘价',
                    '价格源不一致',
                    '交易所价格延迟更新',
                    '使用不同的定价服务商'
                ],
                'typical_pct': (0.01, 0.5),  # 典型差异比例范围
                'resolution': [
                    '联系托管行更新价格源',
                    '确认价格时点一致性',
                    '统一使用Bloomberg价格',
                    '等待交易所价格更新'
                ]
            },
            '汇率差异': {
                'causes': [
                    '汇率更新时间差异',
                    '使用不同汇率源',
                    '汇率取值时点不同',
                    '中间价与买卖价差异'
                ],
                'typical_pct': (0.005, 0.2),
                'resolution': [
                    '确认汇率时点一致性',
                    '统一汇率数据源',
                    '使用中间价统一标准',
                    '联系托管行确认汇率'
                ]
            },
            '应计利息差异': {
                'causes': [
                    '计息天数计算方法不同',
                    '计息基准不一致',
                    '付息日期理解差异',
                    '计息规则理解不同'
                ],
                'typical_pct': (0.01, 0.3),
                'resolution': [
                    '统一计息规则',
                    '确认计息天数标准',
                    '核对付息日期',
                    '联系托管行确认计息方法'
                ]
            },
            '持仓数量差异': {
                'causes': [
                    '交易未及时入账',
                    '公司行动处理差异',
                    '持仓拆分合并差异',
                    '托管行数据延迟'
                ],
                'typical_pct': (0.1, 2.0),
                'resolution': [
                    '核对交易记录',
                    '确认公司行动处理',
                    '联系托管行核对持仓',
                    '等待托管行数据更新'
                ]
            },
            '费用差异': {
                'causes': [
                    '管理费计提方法不同',
                    '托管费计算差异',
                    '其他费用未计提',
                    '费用分摊方法不同'
                ],
                'typical_pct': (0.005, 0.1),
                'resolution': [
                    '统一费用计提标准',
                    '核对费用计算公式',
                    '确认费用分摊方法',
                    '联系托管行确认费用'
                ]
            }
        }
        
        # 状态
        self.statuses = ['Pending', 'Resolved', 'Matched']
        
    def generate_valuation_differences(self, n_records=100, date=None):
        """生成估值差异数据
        
        Args:
            n_records: 生成记录数
            date: 估值日期，默认为今天
            
        Returns:
            DataFrame: 估值差异数据
        """
        if date is None:
            date = datetime.now().date()
        
        data = []
        
        for i in range(n_records):
            # 随机选择基金
            fund_code = random.choice(list(self.funds.keys()))
            fund_name = self.funds[fund_code]
            
            # 随机选择资产类别
            asset_class = random.choice(self.asset_classes)
            
            # 生成证券代码和名称
            if asset_class == 'Bond':
                security_code = f'US{random.randint(100000, 999999)}{random.choice(["AA", "AB", "AC"])}{random.randint(1, 9)}'
                security_name = f'US Treasury {random.uniform(1.0, 5.0):.2f}% {random.randint(2024, 2034)}'
            elif asset_class == 'Equity':
                security_code = f'US{random.randint(100000000, 999999999)}'
                companies = ['Apple Inc', 'Microsoft Corp', 'Amazon.com Inc', 'Google Inc', 'Tesla Inc']
                security_name = random.choice(companies)
            else:
                security_code = f'CASH{random.randint(1000, 9999)}'
                security_name = f'Cash {random.choice(["USD", "HKD", "CNY"])}'
            
            # 生成基础估值
            custodian_value = round(random.uniform(1000000, 10000000), 2)
            
            # 决定是否有差异（80%有差异，20%完全匹配）
            has_difference = random.random() < 0.8
            
            if has_difference:
                # 随机选择差异类型
                diff_type = random.choice(list(self.difference_types.keys()))
                diff_info = self.difference_types[diff_type]
                
                # 根据差异类型生成差异比例
                min_pct, max_pct = diff_info['typical_pct']
                diff_pct = random.uniform(min_pct, max_pct) * random.choice([-1, 1])
                
                internal_value = custodian_value * (1 + diff_pct / 100)
                status = random.choice(['Pending', 'Resolved'])
            else:
                diff_pct = 0
                internal_value = custodian_value
                status = 'Matched'
            
            difference = custodian_value - internal_value
            
            # 生成价格和数量
            if asset_class in ['Bond', 'Equity']:
                quantity = round(random.uniform(10000, 100000), 2)
                price_custodian = round(custodian_value / quantity, 6)
                price_internal = round(internal_value / quantity, 6)
            else:
                quantity = custodian_value
                price_custodian = 1.0
                price_internal = 1.0
            
            # 生成汇率
            currency = random.choice(['USD', 'HKD', 'CNY', 'EUR'])
            if currency == 'USD':
                fx_rate_custodian = round(random.uniform(7.20, 7.30), 6)
                fx_rate_internal = round(fx_rate_custodian + random.uniform(-0.01, 0.01), 6)
            elif currency == 'HKD':
                fx_rate_custodian = round(random.uniform(0.90, 0.95), 6)
                fx_rate_internal = round(fx_rate_custodian + random.uniform(-0.005, 0.005), 6)
            else:
                fx_rate_custodian = 1.0
                fx_rate_internal = 1.0
            
            # 生成应计利息（仅债券）
            if asset_class == 'Bond':
                accrued_interest_custodian = round(random.uniform(0, 5000), 2)
                accrued_interest_internal = round(accrued_interest_custodian + random.uniform(-100, 100), 2)
            else:
                accrued_interest_custodian = 0
                accrued_interest_internal = 0
            
            record = {
                'id': f'VD{date.strftime("%Y%m%d")}{str(i+1).zfill(3)}',
                'date': date,
                'fund_code': fund_code,
                'fund_name': fund_name,
                'security_code': security_code,
                'security_name': security_name,
                'asset_class': asset_class,
                'custodian_value': round(custodian_value, 2),
                'internal_value': round(internal_value, 2),
                'difference': round(difference, 2),
                'difference_pct': round(diff_pct, 6),
                'price_custodian': round(price_custodian, 6),
                'price_internal': round(price_internal, 6),
                'quantity': round(quantity, 2),
                'currency': currency,
                'fx_rate_custodian': round(fx_rate_custodian, 6),
                'fx_rate_internal': round(fx_rate_internal, 6),
                'accrued_interest_custodian': round(accrued_interest_custodian, 2),
                'accrued_interest_internal': round(accrued_interest_internal, 2),
                'status': status,
                'created_at': datetime.combine(date, datetime.min.time()) + timedelta(hours=9)
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        return df
    
    def generate_historical_cases(self, n_cases=50):
        """生成历史差异案例
        
        Args:
            n_cases: 生成案例数
            
        Returns:
            DataFrame: 历史案例数据
        """
        data = []
        
        for i in range(n_cases):
            # 随机日期（过去90天内）
            days_ago = random.randint(1, 90)
            case_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            # 随机选择基金和资产类别
            fund_code = random.choice(list(self.funds.keys()))
            asset_class = random.choice(self.asset_classes)
            
            # 随机选择差异类型
            diff_type = random.choice(list(self.difference_types.keys()))
            diff_info = self.difference_types[diff_type]
            
            # 生成差异金额和比例
            difference_amount = round(random.uniform(100, 50000), 2)
            difference_pct = round(random.uniform(diff_info['typical_pct'][0], 
                                                 diff_info['typical_pct'][1]), 6)
            
            # 随机选择根本原因和解决方案
            root_cause = random.choice(diff_info['causes'])
            resolution = random.choice(diff_info['resolution'])
            
            # 生成解决时长（5-120分钟）
            resolution_time = random.randint(5, 120)
            
            # 随机选择解决人
            resolvers = ['张三', '李四', '王五', '赵六', '钱七']
            resolved_by = random.choice(resolvers)
            
            # 生成证券代码
            if asset_class == 'Bond':
                security_code = f'US{random.randint(100000, 999999)}{random.choice(["AA", "AB"])}{random.randint(1, 9)}'
            else:
                security_code = f'US{random.randint(100000000, 999999999)}'
            
            # 生成相似案例（可能为空）
            if random.random() < 0.3:  # 30%的案例有相似案例
                n_similar = random.randint(1, 3)
                similar_cases = ','.join([f'CASE{random.randint(20240101, 20241231)}{str(random.randint(1, 999)).zfill(3)}' 
                                         for _ in range(n_similar)])
            else:
                similar_cases = ''
            
            record = {
                'case_id': f'CASE{case_date.strftime("%Y%m%d")}{str(i+1).zfill(3)}',
                'date': case_date,
                'fund_code': fund_code,
                'security_code': security_code,
                'asset_class': asset_class,
                'difference_type': diff_type,
                'root_cause': root_cause,
                'difference_amount': difference_amount,
                'difference_pct': difference_pct,
                'resolution': resolution,
                'resolution_time': resolution_time,
                'resolved_by': resolved_by,
                'similar_cases': similar_cases,
                'created_at': datetime.combine(case_date, datetime.min.time()) + timedelta(hours=10, minutes=random.randint(0, 480))
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        return df
    
    def generate_valuation_rules(self):
        """生成估值规则配置
        
        Returns:
            DataFrame: 估值规则数据
        """
        rules = [
            {
                'rule_id': 'RULE001',
                'asset_class': 'Bond',
                'rule_type': '价格来源',
                'rule_description': '债券使用收盘价估值',
                'threshold_amount': 1000.00,
                'threshold_pct': 0.010000,
                'priority': 1,
                'is_active': True,
                'created_at': datetime(2024, 1, 1)
            },
            {
                'rule_id': 'RULE002',
                'asset_class': 'Equity',
                'rule_type': '价格来源',
                'rule_description': '股票使用实时价格估值',
                'threshold_amount': 500.00,
                'threshold_pct': 0.005000,
                'priority': 1,
                'is_active': True,
                'created_at': datetime(2024, 1, 1)
            },
            {
                'rule_id': 'RULE003',
                'asset_class': 'Cash',
                'rule_type': '汇率规则',
                'rule_description': '现金使用当日中间价',
                'threshold_amount': 100.00,
                'threshold_pct': 0.001000,
                'priority': 2,
                'is_active': True,
                'created_at': datetime(2024, 1, 1)
            },
            {
                'rule_id': 'RULE004',
                'asset_class': 'Bond',
                'rule_type': '应计利息',
                'rule_description': '债券应计利息使用ACT/360计算',
                'threshold_amount': 200.00,
                'threshold_pct': 0.020000,
                'priority': 2,
                'is_active': True,
                'created_at': datetime(2024, 1, 1)
            },
            {
                'rule_id': 'RULE005',
                'asset_class': 'All',
                'rule_type': '汇率规则',
                'rule_description': '所有资产使用统一汇率时点',
                'threshold_amount': 50.00,
                'threshold_pct': 0.005000,
                'priority': 3,
                'is_active': True,
                'created_at': datetime(2024, 1, 1)
            }
        ]
        
        df = pd.DataFrame(rules)
        return df
    
    def save_all_data(self, output_dir='valuation_ai/data'):
        """生成并保存所有数据
        
        Args:
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成估值差异数据
        print("生成估值差异数据...")
        df_diff = self.generate_valuation_differences(n_records=100)
        df_diff.to_csv(f'{output_dir}/valuation_differences.csv', index=False, encoding='utf-8-sig')
        df_diff.to_excel(f'{output_dir}/valuation_differences.xlsx', index=False)
        print(f"[OK] 已生成 {len(df_diff)} 条估值差异数据")
        
        # 生成历史案例
        print("\n生成历史案例数据...")
        df_cases = self.generate_historical_cases(n_cases=50)
        df_cases.to_csv(f'{output_dir}/historical_cases.csv', index=False, encoding='utf-8-sig')
        df_cases.to_excel(f'{output_dir}/historical_cases.xlsx', index=False)
        print(f"[OK] 已生成 {len(df_cases)} 条历史案例")
        
        # 生成估值规则
        print("\n生成估值规则配置...")
        df_rules = self.generate_valuation_rules()
        df_rules.to_csv(f'{output_dir}/valuation_rules.csv', index=False, encoding='utf-8-sig')
        df_rules.to_excel(f'{output_dir}/valuation_rules.xlsx', index=False)
        print(f"[OK] 已生成 {len(df_rules)} 条估值规则")
        
        # 生成数据统计报告
        print("\n生成数据统计报告...")
        report = {
            '估值差异数据': {
                '总记录数': len(df_diff),
                '有差异记录': len(df_diff[df_diff['status'] != 'Matched']),
                '已匹配记录': len(df_diff[df_diff['status'] == 'Matched']),
                '平均差异金额': float(df_diff['difference'].abs().mean()),
                '最大差异金额': float(df_diff['difference'].abs().max()),
                '资产类别分布': df_diff['asset_class'].value_counts().to_dict(),
                '基金分布': df_diff['fund_code'].value_counts().to_dict()
            },
            '历史案例数据': {
                '总案例数': len(df_cases),
                '差异类型分布': df_cases['difference_type'].value_counts().to_dict(),
                '平均解决时长': float(df_cases['resolution_time'].mean()),
                '资产类别分布': df_cases['asset_class'].value_counts().to_dict()
            },
            '估值规则': {
                '总规则数': len(df_rules),
                '启用规则数': len(df_rules[df_rules['is_active'] == True])
            }
        }
        
        with open(f'{output_dir}/data_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] 所有数据已保存到 {output_dir}/")
        print(f"\n数据统计：")
        print(f"  - 估值差异数据: {len(df_diff)} 条")
        print(f"  - 历史案例: {len(df_cases)} 条")
        print(f"  - 估值规则: {len(df_rules)} 条")
        
        return df_diff, df_cases, df_rules


if __name__ == '__main__':
    # 创建生成器并生成数据
    generator = ValuationDataGenerator(seed=42)
    generator.save_all_data()