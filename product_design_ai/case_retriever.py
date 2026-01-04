"""
案例检索引擎
基于产品特征和问题描述检索相似案例
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import os

class CaseRetriever:
    """案例检索引擎类"""
    
    def __init__(self, data_dir='product_design_ai/data'):
        """初始化检索引擎"""
        self.data_dir = data_dir
        self.cases_df = None
        self.vectorizer = None
        self.case_vectors = None
        self.load_data()
        self.build_index()
    
    def load_data(self):
        """加载案例数据"""
        try:
            self.cases_df = pd.read_csv(os.path.join(self.data_dir, 'case_library.csv'))
            print(f"案例数据加载成功：{len(self.cases_df)}个案例")
        except Exception as e:
            print(f"案例数据加载失败：{e}")
            raise
    
    def build_index(self):
        """构建案例索引"""
        print("构建案例索引...")
        
        # 合并案例的文本字段
        self.cases_df['combined_text'] = (
            self.cases_df['product_type'] + ' ' +
            self.cases_df['scenario'] + ' ' +
            self.cases_df['problem_desc'] + ' ' +
            self.cases_df['tags']
        )
        
        # 使用jieba分词
        self.cases_df['segmented_text'] = self.cases_df['combined_text'].apply(
            lambda x: ' '.join(jieba.cut(str(x)))
        )
        
        # 构建TF-IDF向量
        self.vectorizer = TfidfVectorizer(max_features=500)
        self.case_vectors = self.vectorizer.fit_transform(
            self.cases_df['segmented_text']
        )
        
        print(f"索引构建完成：{self.case_vectors.shape}")
    
    def search_cases(self, query, product_type=None, case_type=None, top_n=5):
        """检索案例"""
        print(f"\n检索案例：{query}")
        
        # 分词
        query_segmented = ' '.join(jieba.cut(query))
        
        # 向量化查询
        query_vector = self.vectorizer.transform([query_segmented])
        
        # 计算相似度
        similarities = cosine_similarity(query_vector, self.case_vectors)[0]
        
        # 添加相似度到DataFrame
        results = self.cases_df.copy()
        results['similarity'] = similarities
        
        # 过滤条件
        if product_type:
            results = results[results['product_type'] == product_type]
        
        if case_type:
            results = results[results['case_type'] == case_type]
        
        # 排序并返回Top-N
        results = results.sort_values('similarity', ascending=False).head(top_n)
        
        print(f"找到 {len(results)} 个相关案例")
        
        return results
    
    def get_case_details(self, case_id):
        """获取案例详情"""
        case = self.cases_df[self.cases_df['case_id'] == case_id]
        
        if len(case) == 0:
            return None
        
        case = case.iloc[0]
        
        return {
            'case_id': case['case_id'],
            'product_type': case['product_type'],
            'case_type': case['case_type'],
            'scenario': case['scenario'],
            'problem_desc': case['problem_desc'],
            'root_cause': case['root_cause'],
            'solution': case['solution'],
            'lessons_learned': case['lessons_learned'],
            'best_practices': case['best_practices'],
            'tags': case['tags']
        }
    
    def get_recommendations_from_cases(self, cases):
        """从案例中提取建议"""
        recommendations = []
        
        for idx, case in cases.iterrows():
            recommendations.append({
                'case_id': case['case_id'],
                'product_type': case['product_type'],
                'case_type': case['case_type'],
                'similarity': case['similarity'],
                'scenario': case['scenario'],
                'key_lesson': case['lessons_learned'],
                'best_practice': case['best_practices'],
                'applicable': case['similarity'] > 0.3
            })
        
        return recommendations
    
    def analyze_case_patterns(self, product_type=None):
        """分析案例模式"""
        if product_type:
            filtered_cases = self.cases_df[self.cases_df['product_type'] == product_type]
        else:
            filtered_cases = self.cases_df
        
        patterns = {
            'total_cases': len(filtered_cases),
            'success_rate': len(filtered_cases[filtered_cases['case_type'] == '成功案例']) / len(filtered_cases) * 100 if len(filtered_cases) > 0 else 0,
            'case_types': filtered_cases['case_type'].value_counts().to_dict(),
            'common_scenarios': filtered_cases['scenario'].value_counts().head(5).to_dict(),
            'key_lessons': []
        }
        
        # 提取关键经验
        for idx, case in filtered_cases.iterrows():
            if case['case_type'] == '成功案例':
                patterns['key_lessons'].append({
                    'scenario': case['scenario'],
                    'lesson': case['lessons_learned'],
                    'practice': case['best_practices']
                })
        
        return patterns

def main():
    """测试函数"""
    retriever = CaseRetriever()
    
    # 测试检索
    query = "股票型产品估值核对延迟"
    results = retriever.search_cases(query, top_n=3)
    
    print("\n=== 检索结果 ===")
    for idx, case in results.iterrows():
        print(f"\n案例 {idx + 1}:")
        print(f"  相似度: {case['similarity']:.2%}")
        print(f"  产品类型: {case['product_type']}")
        print(f"  案例类型: {case['case_type']}")
        print(f"  场景: {case['scenario']}")
        print(f"  经验教训: {case['lessons_learned']}")
    
    # 获取建议
    recommendations = retriever.get_recommendations_from_cases(results)
    print(f"\n=== 从案例中提取的建议 ===")
    for rec in recommendations:
        if rec['applicable']:
            print(f"\n- {rec['scenario']}")
            print(f"  关键经验: {rec['key_lesson']}")
            print(f"  最佳实践: {rec['best_practice']}")

if __name__ == '__main__':
    main()