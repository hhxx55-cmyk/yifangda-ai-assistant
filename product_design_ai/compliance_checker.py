"""
合规检查引擎
检查流程设计是否符合监管规则
"""

import pandas as pd
import numpy as np
import jieba
import os

class ComplianceChecker:
    """合规检查引擎类"""
    
    def __init__(self, data_dir='product_design_ai/data'):
        """初始化合规检查引擎"""
        self.data_dir = data_dir
        self.rules_df = None
        self.load_data()
    
    def load_data(self):
        """加载监管规则数据"""
        try:
            self.rules_df = pd.read_csv(os.path.join(self.data_dir, 'regulatory_rules.csv'))
            print(f"监管规则加载成功：{len(self.rules_df)}条规则")
        except Exception as e:
            print(f"监管规则加载失败：{e}")
            raise
    
    def get_applicable_rules(self, product_type):
        """获取适用的监管规则"""
        # 筛选适用规则
        applicable = self.rules_df[
            (self.rules_df['applicable_products'] == '所有产品') |
            (self.rules_df['applicable_products'] == product_type)
        ]
        
        return applicable
    
    def check_process_compliance(self, product_features, process_steps):
        """检查流程合规性"""
        print(f"\n检查流程合规性...")
        
        product_type = product_features.get('product_type', '')
        
        # 获取适用规则
        applicable_rules = self.get_applicable_rules(product_type)
        
        print(f"适用规则数: {len(applicable_rules)}")
        
        compliance_results = []
        
        # 检查每条规则
        for idx, rule in applicable_rules.iterrows():
            check_result = self._check_rule(rule, product_features, process_steps)
            compliance_results.append(check_result)
        
        # 计算合规分数
        total_rules = len(compliance_results)
        compliant_rules = sum(1 for r in compliance_results if r['compliant'])
        compliance_score = (compliant_rules / total_rules * 100) if total_rules > 0 else 100
        
        result = {
            'product_type': product_type,
            'total_rules': total_rules,
            'compliant_rules': compliant_rules,
            'non_compliant_rules': total_rules - compliant_rules,
            'compliance_score': compliance_score,
            'check_results': compliance_results
        }
        
        print(f"合规检查完成：{compliance_score:.1f}%")
        
        return result
    
    def _check_rule(self, rule, product_features, process_steps):
        """检查单条规则"""
        rule_category = rule['rule_category']
        rule_content = rule['rule_content']
        
        # 根据规则类别进行检查
        if rule_category == '交易':
            compliant, reason = self._check_trading_rule(rule, product_features, process_steps)
        elif rule_category == '清算':
            compliant, reason = self._check_settlement_rule(rule, product_features, process_steps)
        elif rule_category == '估值':
            compliant, reason = self._check_valuation_rule(rule, product_features, process_steps)
        elif rule_category == '披露':
            compliant, reason = self._check_disclosure_rule(rule, product_features, process_steps)
        elif rule_category == '合规':
            compliant, reason = self._check_compliance_rule(rule, product_features, process_steps)
        elif rule_category == '风控':
            compliant, reason = self._check_risk_rule(rule, product_features, process_steps)
        else:
            compliant, reason = True, '规则类别未知，默认合规'
        
        return {
            'rule_id': rule['rule_id'],
            'rule_name': rule['rule_name'],
            'rule_category': rule_category,
            'rule_content': rule_content,
            'compliant': compliant,
            'reason': reason,
            'severity': 'high' if not compliant else 'none',
            'suggestion': self._generate_suggestion(rule, compliant, reason) if not compliant else ''
        }
    
    def _check_trading_rule(self, rule, product_features, process_steps):
        """检查交易规则"""
        # 检查是否有交易相关步骤
        trading_steps = [s for s in process_steps if s.get('step_type') == '交易']
        
        if len(trading_steps) == 0:
            return False, '流程中缺少交易步骤'
        
        # 检查结算周期
        settlement_cycle = product_features.get('settlement_cycle', '')
        if 'T+1' in rule['rule_content'] and settlement_cycle != 'T+1':
            if product_features.get('product_type') not in ['货币型']:
                return False, f'结算周期为{settlement_cycle}，不符合T+1要求'
        
        return True, '交易流程符合规定'
    
    def _check_settlement_rule(self, rule, product_features, process_steps):
        """检查清算规则"""
        # 检查是否有清算相关步骤
        settlement_steps = [s for s in process_steps if s.get('step_type') == '清算']
        
        if len(settlement_steps) == 0:
            return False, '流程中缺少清算步骤'
        
        return True, '清算流程符合规定'
    
    def _check_valuation_rule(self, rule, product_features, process_steps):
        """检查估值规则"""
        # 检查是否有估值相关步骤
        valuation_steps = [s for s in process_steps if s.get('step_type') == '估值']
        
        if len(valuation_steps) == 0:
            return False, '流程中缺少估值步骤'
        
        # 检查估值方法
        valuation_method = product_features.get('valuation_method', '')
        product_type = product_features.get('product_type', '')
        
        if '摊余成本法' in rule['rule_content']:
            if product_type == '货币型' and valuation_method != '摊余成本法':
                return False, f'货币型基金应采用摊余成本法，当前为{valuation_method}'
        
        # 检查是否有托管行核对
        has_custodian_check = any('托管' in s.get('step_name', '') for s in process_steps)
        if not has_custodian_check:
            return False, '缺少托管行估值核对步骤'
        
        return True, '估值流程符合规定'
    
    def _check_disclosure_rule(self, rule, product_features, process_steps):
        """检查披露规则"""
        # 检查是否有披露相关步骤
        disclosure_steps = [s for s in process_steps if s.get('step_type') == '披露']
        
        if len(disclosure_steps) == 0:
            return False, '流程中缺少信息披露步骤'
        
        return True, '信息披露流程符合规定'
    
    def _check_compliance_rule(self, rule, product_features, process_steps):
        """检查合规规则"""
        # 检查是否有托管相关步骤
        has_custodian = any('托管' in s.get('step_name', '') for s in process_steps)
        
        if not has_custodian:
            return False, '流程中缺少托管相关步骤'
        
        return True, '合规流程符合规定'
    
    def _check_risk_rule(self, rule, product_features, process_steps):
        """检查风控规则"""
        # 检查是否有风险监控步骤
        has_risk_control = any(
            s.get('step_type') in ['风险监控', '合规检查'] 
            for s in process_steps
        )
        
        if not has_risk_control:
            return False, '流程中缺少风险管理步骤'
        
        return True, '风险管理流程符合规定'
    
    def _generate_suggestion(self, rule, compliant, reason):
        """生成整改建议"""
        if '缺少' in reason:
            missing_item = reason.split('缺少')[1]
            return f'建议在流程中增加{missing_item}'
        elif '不符合' in reason:
            return f'建议调整流程以符合{rule["rule_name"]}要求'
        else:
            return f'建议参考{rule["rule_name"]}进行整改'
    
    def generate_compliance_report(self, compliance_result):
        """生成合规报告"""
        report = {
            'summary': {
                'compliance_score': compliance_result['compliance_score'],
                'total_rules': compliance_result['total_rules'],
                'compliant_rules': compliance_result['compliant_rules'],
                'non_compliant_rules': compliance_result['non_compliant_rules'],
                'status': '合规' if compliance_result['compliance_score'] >= 90 else '需整改'
            },
            'non_compliant_items': [],
            'recommendations': []
        }
        
        # 提取不合规项
        for result in compliance_result['check_results']:
            if not result['compliant']:
                report['non_compliant_items'].append({
                    'rule_name': result['rule_name'],
                    'rule_category': result['rule_category'],
                    'reason': result['reason'],
                    'severity': result['severity']
                })
                
                report['recommendations'].append({
                    'rule_name': result['rule_name'],
                    'suggestion': result['suggestion']
                })
        
        return report

def main():
    """测试函数"""
    checker = ComplianceChecker()
    
    # 测试合规检查
    test_product = {
        'product_type': '股票型',
        'settlement_cycle': 'T+1',
        'valuation_method': '市价法'
    }
    
    test_steps = [
        {'step_name': '交易执行', 'step_type': '交易'},
        {'step_name': '清算处理', 'step_type': '清算'},
        {'step_name': '估值计算', 'step_type': '估值'},
        {'step_name': '托管行核对', 'step_type': '估值'},
        {'step_name': '信息披露', 'step_type': '披露'}
    ]
    
    result = checker.check_process_compliance(test_product, test_steps)
    
    print("\n=== 合规检查结果 ===")
    print(f"合规分数: {result['compliance_score']:.1f}%")
    print(f"合规规则: {result['compliant_rules']}/{result['total_rules']}")
    
    # 生成报告
    report = checker.generate_compliance_report(result)
    
    if report['non_compliant_items']:
        print("\n不合规项:")
        for item in report['non_compliant_items']:
            print(f"  - {item['rule_name']}: {item['reason']}")
        
        print("\n整改建议:")
        for rec in report['recommendations']:
            print(f"  - {rec['suggestion']}")

if __name__ == '__main__':
    main()