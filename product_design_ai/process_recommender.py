"""
流程推荐引擎
基于产品特征和历史数据推荐最优工作流程
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import os

class ProcessRecommender:
    """流程推荐引擎类"""
    
    def __init__(self, data_dir='product_design_ai/data'):
        """初始化推荐引擎"""
        self.data_dir = data_dir
        self.products_df = None
        self.processes_df = None
        self.steps_df = None
        self.issues_df = None
        self.label_encoders = {}
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        try:
            self.products_df = pd.read_csv(os.path.join(self.data_dir, 'product_features.csv'))
            self.processes_df = pd.read_csv(os.path.join(self.data_dir, 'historical_processes.csv'))
            self.steps_df = pd.read_csv(os.path.join(self.data_dir, 'process_steps.csv'))
            self.issues_df = pd.read_csv(os.path.join(self.data_dir, 'process_issues.csv'))
            print(f"数据加载成功：{len(self.products_df)}个产品，{len(self.processes_df)}个流程")
        except Exception as e:
            print(f"数据加载失败：{e}")
            raise
    
    def encode_features(self, product_features):
        """编码产品特征"""
        encoded_features = {}
        
        categorical_features = [
            'product_type', 'asset_class', 'investment_scope', 
            'trading_market', 'custodian', 'investment_strategy',
            'risk_level', 'trading_frequency', 'settlement_cycle',
            'valuation_method', 'disclosure_frequency'
        ]
        
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                # 使用所有产品的数据来fit encoder
                self.label_encoders[feature].fit(self.products_df[feature].astype(str))
            
            # 编码当前产品特征
            value = product_features.get(feature, '')
            try:
                encoded_features[feature] = self.label_encoders[feature].transform([str(value)])[0]
            except:
                # 如果是未见过的值，使用默认值
                encoded_features[feature] = 0
        
        return encoded_features
    
    def calculate_similarity(self, target_features, candidate_features):
        """计算产品相似度"""
        # 提取特征向量
        feature_names = [
            'product_type', 'asset_class', 'investment_scope',
            'trading_market', 'custodian', 'investment_strategy',
            'risk_level', 'trading_frequency', 'settlement_cycle',
            'valuation_method', 'disclosure_frequency'
        ]
        
        target_vector = [target_features.get(f, 0) for f in feature_names]
        candidate_vector = [candidate_features.get(f, 0) for f in feature_names]
        
        # 计算余弦相似度
        similarity = cosine_similarity([target_vector], [candidate_vector])[0][0]
        
        # 产品类型完全匹配加权
        if target_features.get('product_type') == candidate_features.get('product_type'):
            similarity *= 1.2
        
        return similarity
    
    def recommend_process(self, product_features, top_n=3):
        """推荐流程"""
        print(f"\n正在为产品推荐流程...")
        print(f"产品特征：{product_features}")
        
        # 编码目标产品特征
        target_encoded = self.encode_features(product_features)
        
        # 计算与所有历史产品的相似度
        similarities = []
        
        for idx, product in self.products_df.iterrows():
            # 编码候选产品特征
            candidate_features = product.to_dict()
            candidate_encoded = self.encode_features(candidate_features)
            
            # 计算相似度
            similarity = self.calculate_similarity(target_encoded, candidate_encoded)
            
            # 获取该产品的流程
            product_processes = self.processes_df[
                self.processes_df['product_id'] == product['product_id']
            ]
            
            for _, process in product_processes.iterrows():
                # 获取流程步骤
                process_steps = self.steps_df[
                    self.steps_df['process_id'] == process['process_id']
                ]
                
                # 获取流程问题
                process_issues = self.issues_df[
                    self.issues_df['process_id'] == process['process_id']
                ]
                
                # 计算流程质量分数
                total_steps = len(process_steps)
                problem_steps = len(process_issues)
                quality_score = 1.0 - (problem_steps / max(total_steps, 1)) * 0.5
                
                # 综合评分
                final_score = similarity * quality_score
                
                similarities.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'product_type': product['product_type'],
                    'process_id': process['process_id'],
                    'process_version': process['process_version'],
                    'similarity': similarity,
                    'quality_score': quality_score,
                    'final_score': final_score,
                    'total_steps': total_steps,
                    'problem_steps': problem_steps,
                    'steps': process_steps,
                    'issues': process_issues
                })
        
        # 按综合评分排序
        similarities.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 返回Top-N推荐
        recommendations = similarities[:top_n]
        
        print(f"\n找到 {len(recommendations)} 个推荐流程")
        
        return recommendations
    
    def generate_recommended_process(self, product_features, base_process):
        """基于推荐流程生成新流程"""
        print(f"\n生成推荐流程...")
        
        steps = base_process['steps']
        issues = base_process['issues']
        
        # 生成流程步骤列表
        recommended_steps = []
        risk_warnings = []
        
        for idx, step in steps.iterrows():
            step_info = {
                'step_order': idx + 1,
                'step_name': step['step_name'],
                'step_type': step['step_type'],
                'responsible_dept': step['responsible_dept'],
                'predecessor_steps': step['predecessor_steps'],
                'planned_duration': step['planned_duration'],
                'description': f"{step['step_name']}由{step['responsible_dept']}负责执行"
            }
            
            # 检查该步骤是否有历史问题
            step_issues = issues[issues['step_id'] == step['step_id']]
            if len(step_issues) > 0:
                issue = step_issues.iloc[0]
                risk_warnings.append({
                    'step_name': step['step_name'],
                    'risk_type': issue['issue_type'],
                    'risk_desc': issue['issue_desc'],
                    'root_cause': issue['root_cause'],
                    'suggestion': issue['solution'],
                    'impact_level': issue['impact_level']
                })
                step_info['has_risk'] = True
                step_info['risk_level'] = issue['impact_level']
            else:
                step_info['has_risk'] = False
                step_info['risk_level'] = '低'
            
            recommended_steps.append(step_info)
        
        # 计算总时长
        total_duration = sum([s['planned_duration'] for s in recommended_steps])
        
        result = {
            'product_features': product_features,
            'base_process': {
                'product_name': base_process['product_name'],
                'product_type': base_process['product_type'],
                'similarity': base_process['similarity'],
                'quality_score': base_process['quality_score']
            },
            'recommended_steps': recommended_steps,
            'total_steps': len(recommended_steps),
            'total_duration': total_duration,
            'risk_warnings': risk_warnings,
            'risk_count': len(risk_warnings)
        }
        
        return result
    
    def get_process_statistics(self, product_type=None):
        """获取流程统计信息"""
        if product_type:
            filtered_processes = self.processes_df[
                self.processes_df['product_type'] == product_type
            ]
        else:
            filtered_processes = self.processes_df
        
        stats = {
            'total_processes': len(filtered_processes),
            'product_types': filtered_processes['product_type'].value_counts().to_dict(),
            'avg_steps': 0,
            'avg_duration': 0,
            'issue_rate': 0
        }
        
        if len(filtered_processes) > 0:
            # 计算平均步骤数
            process_ids = filtered_processes['process_id'].tolist()
            steps_count = []
            durations = []
            
            for process_id in process_ids:
                process_steps = self.steps_df[self.steps_df['process_id'] == process_id]
                steps_count.append(len(process_steps))
                durations.append(process_steps['actual_duration'].sum())
            
            stats['avg_steps'] = np.mean(steps_count) if steps_count else 0
            stats['avg_duration'] = np.mean(durations) if durations else 0
            
            # 计算问题率
            total_steps = len(self.steps_df[self.steps_df['process_id'].isin(process_ids)])
            total_issues = len(self.issues_df[self.issues_df['process_id'].isin(process_ids)])
            stats['issue_rate'] = (total_issues / total_steps * 100) if total_steps > 0 else 0
        
        return stats

def main():
    """测试函数"""
    recommender = ProcessRecommender()
    
    # 测试推荐
    test_product = {
        'product_type': '股票型',
        'asset_class': '股票',
        'investment_scope': '境内股票',
        'trading_market': '沪深交易所',
        'custodian': '工商银行',
        'investment_strategy': '主动管理',
        'risk_level': '高',
        'trading_frequency': '高频',
        'settlement_cycle': 'T+1',
        'valuation_method': '市价法',
        'disclosure_frequency': '季度'
    }
    
    recommendations = recommender.recommend_process(test_product, top_n=3)
    
    print("\n=== 推荐结果 ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n推荐 {i}:")
        print(f"  产品: {rec['product_name']}")
        print(f"  相似度: {rec['similarity']:.2%}")
        print(f"  质量分数: {rec['quality_score']:.2%}")
        print(f"  综合评分: {rec['final_score']:.2%}")
        print(f"  步骤数: {rec['total_steps']}")
        print(f"  问题数: {rec['problem_steps']}")
    
    # 生成推荐流程
    if recommendations:
        result = recommender.generate_recommended_process(test_product, recommendations[0])
        print(f"\n=== 生成的推荐流程 ===")
        print(f"总步骤数: {result['total_steps']}")
        print(f"预计时长: {result['total_duration']:.1f}小时")
        print(f"风险点数: {result['risk_count']}")

if __name__ == '__main__':
    main()