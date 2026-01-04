"""
流程优化引擎
分析历史流程数据，识别瓶颈并提供优化建议
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class ProcessOptimizer:
    """流程优化引擎类"""
    
    def __init__(self, data_dir='product_design_ai/data'):
        """初始化优化引擎"""
        self.data_dir = data_dir
        self.steps_df = None
        self.issues_df = None
        self.load_data()
        
        # 定义标准流程步骤清单（关键步骤）
        self.standard_steps = {
            '产品设计': ['产品方案设计', '产品结构设计', '投资策略设计'],
            '合规审核': ['合规审核', '法律审核', '风控审核'],
            '系统配置': ['系统参数配置', '账户开立', '权限设置'],
            '托管协调': ['托管协议签署', '托管账户开立', '托管系统对接'],
            '交易准备': ['交易权限申请', '交易系统测试', '交易流程确认'],
            '估值准备': ['估值方法确认', '估值系统配置', '估值流程测试'],
            '信息披露': ['信息披露方案', '披露渠道确认', '披露模板准备'],
            '上线准备': ['上线检查清单', '应急预案准备', '上线评审会议']
        }
    
    def load_data(self):
        """加载数据"""
        try:
            self.steps_df = pd.read_csv(os.path.join(self.data_dir, 'process_steps.csv'))
            self.issues_df = pd.read_csv(os.path.join(self.data_dir, 'process_issues.csv'))
            print(f"数据加载成功：{len(self.steps_df)}个步骤，{len(self.issues_df)}个问题")
        except Exception as e:
            print(f"数据加载失败：{e}")
            raise
    
    def analyze_bottlenecks(self, process_steps):
        """分析流程瓶颈"""
        bottlenecks = []
        
        for idx, step in process_steps.iterrows():
            # 计算时间偏差
            planned = step['planned_duration']
            actual = step['actual_duration']
            deviation = (actual - planned) / planned * 100 if planned > 0 else 0
            
            # 识别瓶颈（实际时间超出计划30%以上）
            if deviation > 30:
                bottlenecks.append({
                    'step_name': step['step_name'],
                    'step_type': step['step_type'],
                    'responsible_dept': step['responsible_dept'],
                    'planned_duration': planned,
                    'actual_duration': actual,
                    'deviation': deviation,
                    'severity': 'high' if deviation > 50 else 'medium'
                })
        
        return bottlenecks
    
    def identify_redundant_steps(self, process_steps):
        """识别冗余步骤"""
        redundant = []
        
        # 检查是否有可以合并的步骤
        step_groups = process_steps.groupby(['step_type', 'responsible_dept'])
        
        for (step_type, dept), group in step_groups:
            if len(group) > 1:
                # 同一类型、同一部门的多个步骤可能可以合并
                steps_list = group['step_name'].tolist()
                total_duration = group['actual_duration'].sum()
                
                # 生成具体的步骤名称列表
                steps_detail = '、'.join(steps_list[:3])  # 最多显示3个
                if len(steps_list) > 3:
                    steps_detail += f'等{len(steps_list)}个步骤'
                
                redundant.append({
                    'step_type': step_type,
                    'responsible_dept': dept,
                    'steps': steps_list,
                    'count': len(steps_list),
                    'total_duration': total_duration,
                    'suggestion': f'考虑将以下{len(steps_list)}个{step_type}步骤合并：{steps_detail}，可能节省{total_duration * 0.2:.1f}小时'
                })
        
        return redundant
    
    def find_parallel_opportunities(self, process_steps):
        """寻找可并行执行的步骤"""
        parallel_ops = []
        
        # 1. 找到没有依赖关系的独立步骤
        independent_steps = process_steps[
            (process_steps['predecessor_steps'].isna()) |
            (process_steps['predecessor_steps'] == '')
        ]
        
        if len(independent_steps) > 1:
            steps_list = independent_steps['step_name'].tolist()
            steps_detail = '、'.join(steps_list[:4])  # 最多显示4个
            if len(steps_list) > 4:
                steps_detail += f'等{len(steps_list)}个步骤'
            
            parallel_ops.append({
                'steps': steps_list,
                'count': len(steps_list),
                'potential_saving': independent_steps['actual_duration'].sum() * 0.3,
                'suggestion': f'以下{len(steps_list)}个步骤没有依赖关系，可以并行执行：{steps_detail}'
            })
        
        # 2. 分析不同部门的步骤（可能可以并行）
        dept_groups = process_steps.groupby('responsible_dept')
        if len(dept_groups) > 1:
            parallel_by_dept = []
            for dept, group in dept_groups:
                if len(group) >= 2:
                    # 同一部门内的连续步骤
                    steps_list = group['step_name'].tolist()[:3]  # 取前3个
                    parallel_by_dept.append({
                        'dept': dept,
                        'steps': steps_list
                    })
            
            if len(parallel_by_dept) >= 2:
                # 不同部门的步骤可以并行
                dept_info = []
                all_steps = []
                for item in parallel_by_dept[:2]:  # 最多显示2个部门
                    dept_steps = '、'.join(item['steps'][:2])
                    dept_info.append(f"{item['dept']}的{dept_steps}")
                    all_steps.extend(item['steps'])
                
                parallel_ops.append({
                    'steps': all_steps,
                    'count': len(all_steps),
                    'potential_saving': len(all_steps) * 2,  # 估算节省时间
                    'suggestion': f'不同部门的步骤可以并行执行：{" 与 ".join(dept_info)}'
                })
        
        return parallel_ops
    
    def analyze_issue_patterns(self, process_issues):
        """分析问题模式"""
        if len(process_issues) == 0:
            return []
        
        patterns = []
        
        # 按问题类型分组
        issue_groups = process_issues.groupby('issue_type')
        
        for issue_type, group in issue_groups:
            count = len(group)
            impact_dist = group['impact_level'].value_counts().to_dict()
            
            # 找出最常见的根本原因
            root_causes = group['root_cause'].value_counts()
            top_cause = root_causes.index[0] if len(root_causes) > 0 else '未知'
            
            # 找出最常见的解决方案
            solutions = group['solution'].value_counts()
            top_solution = solutions.index[0] if len(solutions) > 0 else '未知'
            
            patterns.append({
                'issue_type': issue_type,
                'count': count,
                'frequency': count / len(process_issues) * 100,
                'impact_distribution': impact_dist,
                'top_root_cause': top_cause,
                'top_solution': top_solution,
                'recommendation': f'针对{issue_type}问题，建议：{top_solution}'
            })
        
        # 按频率排序
        patterns.sort(key=lambda x: x['frequency'], reverse=True)
        
        return patterns
    
    def check_missing_steps(self, process_steps):
        """检查遗漏的关键步骤"""
        missing_steps = []
        
        # 获取当前流程中的所有步骤名称
        current_step_names = set(process_steps['step_name'].tolist())
        
        # 检查每个类别的标准步骤
        for category, standard_list in self.standard_steps.items():
            missing_in_category = []
            for standard_step in standard_list:
                # 检查是否存在包含该关键词的步骤
                found = any(standard_step in step_name for step_name in current_step_names)
                if not found:
                    missing_in_category.append(standard_step)
            
            if missing_in_category:
                missing_steps.append({
                    'category': category,
                    'missing': missing_in_category,
                    'count': len(missing_in_category)
                })
        
        return missing_steps
    
    def generate_optimization_suggestions(self, process_steps, process_issues):
        """生成优化建议"""
        suggestions = []
        
        # 0. 遗漏步骤检测（新增）
        missing = self.check_missing_steps(process_steps)
        if missing:
            for item in missing:
                missing_detail = '、'.join(item['missing'][:3])  # 最多显示3个
                if len(item['missing']) > 3:
                    missing_detail += f'等{len(item["missing"])}个步骤'
                
                suggestions.append({
                    'category': '遗漏步骤',
                    'priority': 'high',
                    'target': f"{item['category']}环节",
                    'problem': f"缺少{len(item['missing'])}个关键步骤",
                    'suggestion': f"建议补充{item['category']}环节的关键步骤：{missing_detail}",
                    'expected_benefit': f"完善流程，避免遗漏风险"
                })
        
        # 1. 瓶颈分析
        bottlenecks = self.analyze_bottlenecks(process_steps)
        if bottlenecks:
            for bottleneck in bottlenecks:
                suggestions.append({
                    'category': '瓶颈优化',
                    'priority': 'high' if bottleneck['severity'] == 'high' else 'medium',
                    'target': bottleneck['step_name'],
                    'problem': f"步骤「{bottleneck['step_name']}」实际耗时超出计划{bottleneck['deviation']:.1f}%",
                    'suggestion': f"建议优化「{bottleneck['step_name']}」流程，目标缩短{(bottleneck['actual_duration'] - bottleneck['planned_duration']) * 0.5:.1f}小时",
                    'expected_benefit': f"预计节省{(bottleneck['actual_duration'] - bottleneck['planned_duration']) * 0.5:.1f}小时"
                })
        
        # 2. 冗余步骤
        redundant = self.identify_redundant_steps(process_steps)
        if redundant:
            for item in redundant:
                suggestions.append({
                    'category': '流程简化',
                    'priority': 'medium',
                    'target': f"{item['step_type']}步骤",
                    'problem': f"存在{item['count']}个相似的{item['step_type']}步骤",
                    'suggestion': item['suggestion'],
                    'expected_benefit': f"预计节省{item['total_duration'] * 0.2:.1f}小时"
                })
        
        # 3. 并行机会
        parallel = self.find_parallel_opportunities(process_steps)
        if parallel:
            for item in parallel:
                suggestions.append({
                    'category': '并行优化',
                    'priority': 'high',
                    'target': f"{item['count']}个独立步骤",
                    'problem': f"发现{item['count']}个可并行执行的步骤",
                    'suggestion': item['suggestion'],
                    'expected_benefit': f"预计节省{item['potential_saving']:.1f}小时"
                })
        
        # 4. 问题模式
        patterns = self.analyze_issue_patterns(process_issues)
        for pattern in patterns[:3]:  # 只取前3个最常见的问题
            suggestions.append({
                'category': '问题预防',
                'priority': 'high' if pattern['frequency'] > 20 else 'medium',
                'target': f"{pattern['issue_type']}问题",
                'problem': f"「{pattern['issue_type']}」问题出现频率{pattern['frequency']:.1f}%，根本原因：{pattern['top_root_cause']}",
                'suggestion': pattern['recommendation'],
                'expected_benefit': f"预计减少{pattern['count']}个{pattern['issue_type']}问题"
            })
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 2))
        
        return suggestions
    
    def calculate_optimization_impact(self, suggestions):
        """计算优化影响"""
        impact = {
            'time_saving': 0,
            'issue_reduction': 0,
            'efficiency_improvement': 0
        }
        
        for suggestion in suggestions:
            benefit = suggestion['expected_benefit']
            
            # 提取时间节省
            if '小时' in benefit:
                try:
                    hours = float(benefit.split('节省')[1].split('小时')[0])
                    impact['time_saving'] += hours
                except:
                    pass
            
            # 提取问题减少
            if '问题' in benefit:
                try:
                    count = int(benefit.split('减少')[1].split('个')[0])
                    impact['issue_reduction'] += count
                except:
                    pass
        
        # 计算效率提升百分比（假设原始总时长）
        if impact['time_saving'] > 0:
            impact['efficiency_improvement'] = impact['time_saving'] / 20 * 100  # 假设原始20小时
        
        return impact
    
    def optimize_process(self, process_steps, process_issues):
        """优化流程"""
        print(f"\n正在分析流程...")
        print(f"步骤数: {len(process_steps)}")
        print(f"问题数: {len(process_issues)}")
        
        # 生成优化建议
        suggestions = self.generate_optimization_suggestions(process_steps, process_issues)
        
        # 计算优化影响
        impact = self.calculate_optimization_impact(suggestions)
        
        result = {
            'original_steps': len(process_steps),
            'original_issues': len(process_issues),
            'suggestions': suggestions,
            'suggestion_count': len(suggestions),
            'impact': impact
        }
        
        print(f"\n生成 {len(suggestions)} 条优化建议")
        print(f"预计节省时间: {impact['time_saving']:.1f}小时")
        print(f"预计减少问题: {impact['issue_reduction']}个")
        print(f"预计效率提升: {impact['efficiency_improvement']:.1f}%")
        
        return result

def main():
    """测试函数"""
    optimizer = ProcessOptimizer()
    
    # 测试优化
    # 获取一个示例流程
    process_id = optimizer.steps_df['process_id'].iloc[0]
    process_steps = optimizer.steps_df[optimizer.steps_df['process_id'] == process_id]
    process_issues = optimizer.issues_df[optimizer.issues_df['process_id'] == process_id]
    
    result = optimizer.optimize_process(process_steps, process_issues)
    
    print("\n=== 优化建议 ===")
    for i, suggestion in enumerate(result['suggestions'], 1):
        print(f"\n建议 {i} [{suggestion['priority'].upper()}]:")
        print(f"  类别: {suggestion['category']}")
        print(f"  目标: {suggestion['target']}")
        print(f"  问题: {suggestion['problem']}")
        print(f"  建议: {suggestion['suggestion']}")
        print(f"  预期收益: {suggestion['expected_benefit']}")

if __name__ == '__main__':
    main()