# -*- coding: utf-8 -*-
"""
AI分析引擎
综合分析年报数据，生成智能建议
"""

from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnnualReportAIAnalyzer:
    """年报AI分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    
    def comprehensive_analysis(self, 
                              validation_results: Dict,
                              text_check_results: Dict) -> Dict:
        """
        综合分析
        
        参数:
            validation_results: 数据验证结果
            text_check_results: 文字检查结果
        
        返回:
            综合分析结果
        """
        logger.info("开始综合分析...")
        
        # 收集所有问题
        all_issues = []
        
        # 数据验证问题
        if validation_results:
            differences = validation_results.get('differences', [])
            for diff in differences:
                all_issues.append({
                    'category': '数据验证',
                    'type': diff.get('type', ''),
                    'severity': diff.get('severity', 'Medium'),
                    'description': self._format_data_issue(diff),
                    'details': diff
                })
        
        # 文字检查问题
        if text_check_results:
            for issue_type in ['grammar_issues', 'terminology_issues', 'expression_issues']:
                issues = text_check_results.get(issue_type, [])
                for issue in issues:
                    all_issues.append({
                        'category': '文字检查',
                        'type': issue.get('type', ''),
                        'severity': issue.get('severity', 'Medium'),
                        'description': self._format_text_issue(issue),
                        'details': issue
                    })
        
        # 生成建议
        recommendations = self.generate_recommendations(all_issues)
        
        # 统计分析
        statistics = self._calculate_statistics(all_issues)
        
        result = {
            'total_issues': len(all_issues),
            'issues': all_issues,
            'recommendations': recommendations,
            'statistics': statistics,
            'summary': self._generate_summary(all_issues, recommendations)
        }
        
        logger.info(f"分析完成: 发现{len(all_issues)}个问题，生成{len(recommendations)}条建议")
        
        return result
    
    def generate_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """
        生成智能建议
        
        参数:
            issues: 问题列表
        
        返回:
            建议列表
        """
        recommendations = []
        
        # 按严重程度分组
        high_priority = [i for i in issues if i.get('severity') == 'High']
        medium_priority = [i for i in issues if i.get('severity') == 'Medium']
        low_priority = [i for i in issues if i.get('severity') == 'Low']
        
        # 高优先级建议
        if high_priority:
            recommendations.append({
                'priority': 'High',
                'category': '紧急处理',
                'issue_count': len(high_priority),
                'recommendation': f'发现{len(high_priority)}个高优先级问题，需要立即处理',
                'expected_improvement': '避免重大错误，确保年报质量',
                'action_items': self._generate_action_items(high_priority[:5])
            })
        
        # 数据勾稽问题
        data_issues = [i for i in issues if i.get('category') == '数据验证']
        if data_issues:
            recommendations.append({
                'priority': 'High',
                'category': '数据勾稽',
                'issue_count': len(data_issues),
                'recommendation': f'发现{len(data_issues)}处数据不一致，建议核对数据来源',
                'expected_improvement': '提高数据准确性，避免监管问题',
                'action_items': self._generate_action_items(data_issues[:3])
            })
        
        # 术语一致性问题
        terminology_issues = [i for i in issues if '术语' in i.get('type', '')]
        if terminology_issues:
            recommendations.append({
                'priority': 'Medium',
                'category': '术语统一',
                'issue_count': len(terminology_issues),
                'recommendation': f'发现{len(terminology_issues)}处术语不一致，建议统一使用标准术语',
                'expected_improvement': '提升专业性和规范性',
                'action_items': self._generate_action_items(terminology_issues[:3])
            })
        
        # 语法问题
        grammar_issues = [i for i in issues if '语法' in i.get('type', '')]
        if grammar_issues:
            recommendations.append({
                'priority': 'Medium',
                'category': '语法优化',
                'issue_count': len(grammar_issues),
                'recommendation': f'发现{len(grammar_issues)}处语法问题，建议逐一修正',
                'expected_improvement': '提高文字质量和可读性',
                'action_items': self._generate_action_items(grammar_issues[:3])
            })
        
        # 表述规范问题
        expression_issues = [i for i in issues if '表述' in i.get('type', '')]
        if expression_issues:
            recommendations.append({
                'priority': 'Low',
                'category': '表述规范',
                'issue_count': len(expression_issues),
                'recommendation': f'发现{len(expression_issues)}处表述不规范，建议按标准格式修改',
                'expected_improvement': '符合行业规范，提升专业形象',
                'action_items': self._generate_action_items(expression_issues[:3])
            })
        
        # 按优先级排序
        recommendations.sort(key=lambda x: self.priority_order.get(x['priority'], 999))
        
        return recommendations
    
    def _format_data_issue(self, diff: Dict) -> str:
        """格式化数据问题描述"""
        diff_type = diff.get('type', '')
        
        if diff_type == '勾稽差异':
            main_item = diff.get('main_item', '')
            note_item = diff.get('note_item', '')
            difference = diff.get('difference', 0)
            return f"{main_item}与{note_item}不一致，差异{difference:.2f}元"
        
        elif diff_type == '跨年不一致':
            item = diff.get('item', '')
            difference = diff.get('difference', 0)
            return f"{item}跨年数据不一致，差异{difference:.2f}元"
        
        elif diff_type == '加总错误':
            total_item = diff.get('total_item', '')
            difference = diff.get('difference', 0)
            return f"{total_item}加总错误，差异{difference:.2f}元"
        
        return str(diff)
    
    def _format_text_issue(self, issue: Dict) -> str:
        """格式化文字问题描述"""
        issue_type = issue.get('type', '')
        
        if issue_type == '语法问题':
            return f"{issue.get('issue_type', '')}: {issue.get('matched_text', '')}"
        
        elif issue_type == '术语不一致':
            term = issue.get('term', '')
            standard = issue.get('standard', '')
            return f"应使用'{standard}'而非'{term}'"
        
        elif issue_type == '表述不规范':
            context = issue.get('context', '')
            return f"{context}: {issue.get('description', '')}"
        
        return str(issue)
    
    def _generate_action_items(self, issues: List[Dict]) -> List[str]:
        """生成行动项"""
        action_items = []
        
        for issue in issues:
            description = issue.get('description', '')
            if description:
                action_items.append(description)
        
        return action_items
    
    def _calculate_statistics(self, issues: List[Dict]) -> Dict:
        """计算统计信息"""
        stats = {
            'by_severity': {
                'High': len([i for i in issues if i.get('severity') == 'High']),
                'Medium': len([i for i in issues if i.get('severity') == 'Medium']),
                'Low': len([i for i in issues if i.get('severity') == 'Low'])
            },
            'by_category': {},
            'by_type': {}
        }
        
        # 按类别统计
        for issue in issues:
            category = issue.get('category', 'Unknown')
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1
            
            # 按类型统计
            issue_type = issue.get('type', 'Unknown')
            if issue_type not in stats['by_type']:
                stats['by_type'][issue_type] = 0
            stats['by_type'][issue_type] += 1
        
        return stats
    
    def _generate_summary(self, issues: List[Dict], 
                         recommendations: List[Dict]) -> str:
        """生成摘要"""
        total = len(issues)
        high = len([i for i in issues if i.get('severity') == 'High'])
        medium = len([i for i in issues if i.get('severity') == 'Medium'])
        low = len([i for i in issues if i.get('severity') == 'Low'])
        
        summary = f"年报核对发现{total}个问题，其中高优先级{high}个、中优先级{medium}个、低优先级{low}个。"
        
        if high > 0:
            summary += f"建议优先处理{high}个高优先级问题，避免重大错误。"
        
        if recommendations:
            summary += f"系统生成了{len(recommendations)}条优化建议，请按优先级逐一处理。"
        
        return summary
    
    def analyze_trends(self, historical_results: List[Dict]) -> Dict:
        """
        分析历史趋势
        
        参数:
            historical_results: 历史分析结果列表
        
        返回:
            趋势分析结果
        """
        if not historical_results:
            return {}
        
        trends = {
            'issue_count_trend': [],
            'severity_trend': [],
            'category_trend': {}
        }
        
        for result in historical_results:
            year = result.get('year', '')
            total_issues = result.get('total_issues', 0)
            
            trends['issue_count_trend'].append({
                'year': year,
                'count': total_issues
            })
            
            # 严重程度趋势
            stats = result.get('statistics', {})
            by_severity = stats.get('by_severity', {})
            trends['severity_trend'].append({
                'year': year,
                'high': by_severity.get('High', 0),
                'medium': by_severity.get('Medium', 0),
                'low': by_severity.get('Low', 0)
            })
        
        return trends
    
    def compare_reports(self, report1: Dict, report2: Dict) -> Dict:
        """
        对比两份年报
        
        参数:
            report1: 年报1
            report2: 年报2
        
        返回:
            对比结果
        """
        comparison = {
            'report1_year': report1.get('year'),
            'report2_year': report2.get('year'),
            'differences': [],
            'improvements': [],
            'regressions': []
        }
        
        # 对比问题数量
        issues1 = report1.get('total_issues', 0)
        issues2 = report2.get('total_issues', 0)
        
        if issues2 < issues1:
            comparison['improvements'].append(
                f"问题数量从{issues1}减少到{issues2}，改进{issues1-issues2}个"
            )
        elif issues2 > issues1:
            comparison['regressions'].append(
                f"问题数量从{issues1}增加到{issues2}，增加{issues2-issues1}个"
            )
        
        return comparison


def main():
    """测试函数"""
    analyzer = AnnualReportAIAnalyzer()
    
    # 模拟验证结果
    validation_results = {
        'differences': [
            {
                'type': '勾稽差异',
                'main_item': '资产总计',
                'note_item': '附注资产合计',
                'difference': 100.50,
                'severity': 'Medium'
            },
            {
                'type': '跨年不一致',
                'item': '净资产',
                'difference': 500.00,
                'severity': 'High'
            }
        ]
    }
    
    # 模拟文字检查结果
    text_check_results = {
        'grammar_issues': [
            {
                'type': '语法问题',
                'issue_type': '重复标点',
                'matched_text': '。。',
                'severity': 'Medium'
            }
        ],
        'terminology_issues': [
            {
                'type': '术语不一致',
                'term': '该基金',
                'standard': '本基金',
                'severity': 'Medium'
            }
        ],
        'expression_issues': []
    }
    
    # 综合分析
    result = analyzer.comprehensive_analysis(validation_results, text_check_results)
    
    print(f"\n分析结果:")
    print(f"总问题数: {result['total_issues']}")
    print(f"建议数: {len(result['recommendations'])}")
    print(f"\n摘要: {result['summary']}")
    
    print(f"\n建议列表:")
    for rec in result['recommendations']:
        print(f"- [{rec['priority']}] {rec['category']}: {rec['recommendation']}")


if __name__ == '__main__':
    main()