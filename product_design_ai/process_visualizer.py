"""
流程可视化引擎
生成流程图和时间规划图
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import networkx as nx

class ProcessVisualizer:
    """流程可视化引擎类"""
    
    def __init__(self):
        """初始化可视化引擎"""
        pass
    
    def create_process_flowchart(self, process_steps):
        """创建流程图"""
        # 使用Plotly创建流程图
        fig = go.Figure()
        
        # 计算节点位置
        num_steps = len(process_steps)
        positions = self._calculate_positions(process_steps)
        
        # 添加连接线
        for i, step in enumerate(process_steps):
            predecessor = step.get('predecessor_steps', '')
            if predecessor and predecessor != '':
                # 找到前置步骤的索引
                pred_idx = next((j for j, s in enumerate(process_steps) 
                               if s.get('step_name') == predecessor), None)
                if pred_idx is not None:
                    # 添加箭头
                    fig.add_trace(go.Scatter(
                        x=[positions[pred_idx][0], positions[i][0]],
                        y=[positions[pred_idx][1], positions[i][1]],
                        mode='lines',
                        line=dict(color='gray', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
        
        # 添加节点
        for i, step in enumerate(process_steps):
            x, y = positions[i]
            
            # 根据风险等级设置颜色
            risk_level = step.get('risk_level', '低')
            if risk_level == '高':
                color = 'red'
            elif risk_level == '中':
                color = 'orange'
            else:
                color = 'lightblue'
            
            # 添加节点
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=30, color=color, line=dict(color='black', width=2)),
                text=f"{i+1}",
                textposition='middle center',
                name=step['step_name'],
                hovertemplate=f"<b>{step['step_name']}</b><br>" +
                             f"负责部门: {step['responsible_dept']}<br>" +
                             f"计划时长: {step['planned_duration']}小时<br>" +
                             f"风险等级: {risk_level}<extra></extra>"
            ))
        
        # 更新布局
        fig.update_layout(
            title='工作流程图',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
            plot_bgcolor='white'
        )
        
        return fig
    
    def _calculate_positions(self, process_steps):
        """计算节点位置"""
        positions = []
        num_steps = len(process_steps)
        
        # 简单的从左到右布局
        for i in range(num_steps):
            x = i * 2
            y = 0
            positions.append((x, y))
        
        return positions
    
    def create_gantt_chart(self, process_steps, start_date=None):
        """创建甘特图"""
        if start_date is None:
            start_date = datetime.now()
        
        # 准备数据
        gantt_data = []
        current_time = start_date
        
        for i, step in enumerate(process_steps):
            duration_hours = step['planned_duration']
            end_time = current_time + timedelta(hours=duration_hours)
            
            gantt_data.append({
                'Task': f"{i+1}. {step['step_name']}",
                'Start': current_time,
                'Finish': end_time,
                'Department': step['responsible_dept'],
                'Duration': duration_hours
            })
            
            current_time = end_time
        
        df = pd.DataFrame(gantt_data)
        
        # 创建甘特图
        fig = px.timeline(
            df,
            x_start='Start',
            x_end='Finish',
            y='Task',
            color='Department',
            title='流程时间规划（甘特图）',
            labels={'Task': '步骤', 'Department': '负责部门'},
            hover_data=['Duration']
        )
        
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(height=max(400, len(process_steps) * 40))
        
        return fig
    
    def create_duration_chart(self, process_steps):
        """创建时长分布图"""
        # 准备数据
        step_names = [f"{i+1}. {s['step_name']}" for i, s in enumerate(process_steps)]
        durations = [s['planned_duration'] for s in process_steps]
        departments = [s['responsible_dept'] for s in process_steps]
        
        # 创建柱状图
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=step_names,
            y=durations,
            text=durations,
            textposition='auto',
            marker_color='lightblue',
            hovertemplate='<b>%{x}</b><br>时长: %{y}小时<extra></extra>'
        ))
        
        fig.update_layout(
            title='各步骤时长分布',
            xaxis_title='步骤',
            yaxis_title='时长（小时）',
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_department_workload_chart(self, process_steps):
        """创建部门工作量分布图"""
        # 统计各部门工作量
        dept_workload = {}
        for step in process_steps:
            dept = step['responsible_dept']
            duration = step['planned_duration']
            dept_workload[dept] = dept_workload.get(dept, 0) + duration
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(dept_workload.keys()),
            values=list(dept_workload.values()),
            hole=0.3,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>工作量: %{value}小时<br>占比: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='部门工作量分布',
            height=400
        )
        
        return fig
    
    def create_risk_distribution_chart(self, process_steps):
        """创建风险分布图"""
        # 统计风险等级
        risk_counts = {'高': 0, '中': 0, '低': 0}
        for step in process_steps:
            risk_level = step.get('risk_level', '低')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # 创建柱状图
        fig = go.Figure(data=[go.Bar(
            x=list(risk_counts.keys()),
            y=list(risk_counts.values()),
            text=list(risk_counts.values()),
            textposition='auto',
            marker_color=['red', 'orange', 'green']
        )])
        
        fig.update_layout(
            title='流程风险分布',
            xaxis_title='风险等级',
            yaxis_title='步骤数量',
            height=400
        )
        
        return fig
    
    def create_collaboration_matrix(self, process_steps):
        """创建协作矩阵"""
        # 提取所有部门
        departments = list(set(s['responsible_dept'] for s in process_steps))
        departments.sort()
        
        # 创建协作矩阵
        n = len(departments)
        matrix = [[0] * n for _ in range(n)]
        
        # 统计协作关系
        for i, step in enumerate(process_steps):
            if i > 0:
                prev_dept = process_steps[i-1]['responsible_dept']
                curr_dept = step['responsible_dept']
                
                if prev_dept != curr_dept:
                    prev_idx = departments.index(prev_dept)
                    curr_idx = departments.index(curr_dept)
                    matrix[prev_idx][curr_idx] += 1
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=departments,
            y=departments,
            colorscale='Blues',
            text=matrix,
            texttemplate='%{text}',
            textfont={"size": 12},
            hovertemplate='从 %{y} 到 %{x}<br>协作次数: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='部门协作矩阵',
            xaxis_title='后续部门',
            yaxis_title='前序部门',
            height=500
        )
        
        return fig
    
    def create_process_summary(self, process_steps, risk_warnings):
        """创建流程摘要"""
        total_steps = len(process_steps)
        total_duration = sum(s['planned_duration'] for s in process_steps)
        
        # 统计部门
        departments = set(s['responsible_dept'] for s in process_steps)
        
        # 统计风险
        high_risk_count = sum(1 for s in process_steps if s.get('risk_level') == '高')
        medium_risk_count = sum(1 for s in process_steps if s.get('risk_level') == '中')
        
        summary = {
            'total_steps': total_steps,
            'total_duration': total_duration,
            'involved_departments': len(departments),
            'department_list': list(departments),
            'high_risk_steps': high_risk_count,
            'medium_risk_steps': medium_risk_count,
            'low_risk_steps': total_steps - high_risk_count - medium_risk_count,
            'risk_warnings': len(risk_warnings)
        }
        
        return summary

def main():
    """测试函数"""
    visualizer = ProcessVisualizer()
    
    # 测试数据
    test_steps = [
        {
            'step_name': '交易执行',
            'step_type': '交易',
            'responsible_dept': '交易部',
            'predecessor_steps': '',
            'planned_duration': 2.0,
            'risk_level': '中'
        },
        {
            'step_name': '清算处理',
            'step_type': '清算',
            'responsible_dept': '清算部',
            'predecessor_steps': '交易执行',
            'planned_duration': 3.0,
            'risk_level': '高'
        },
        {
            'step_name': '估值计算',
            'step_type': '估值',
            'responsible_dept': '估值部',
            'predecessor_steps': '清算处理',
            'planned_duration': 2.5,
            'risk_level': '低'
        },
        {
            'step_name': '信息披露',
            'step_type': '披露',
            'responsible_dept': '披露部',
            'predecessor_steps': '估值计算',
            'planned_duration': 1.5,
            'risk_level': '低'
        }
    ]
    
    # 创建流程摘要
    summary = visualizer.create_process_summary(test_steps, [])
    print("=== 流程摘要 ===")
    print(f"总步骤数: {summary['total_steps']}")
    print(f"总时长: {summary['total_duration']}小时")
    print(f"涉及部门: {summary['involved_departments']}个")
    print(f"高风险步骤: {summary['high_risk_steps']}个")
    
    print("\n可视化图表已准备就绪")

if __name__ == '__main__':
    main()