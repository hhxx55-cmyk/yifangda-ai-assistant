# -*- coding: utf-8 -*-
"""
估值核对AI助手 - AI分析引擎
实现智能差异识别、根因分析和解决方案推荐
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')


class ValuationAIAnalyzer:
    """估值AI分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.anomaly_detector = None
        self.root_cause_classifier = None
        self.label_encoder = None
        self.tfidf_vectorizer = None
        self.historical_cases = None
        self.rules = None
        
        # 差异类型权重（用于综合判断）
        self.diff_type_weights = {
            '价格差异': 0.35,
            '汇率差异': 0.25,
            '应计利息差异': 0.20,
            '持仓数量差异': 0.15,
            '费用差异': 0.05
        }
    
    def load_historical_data(self, cases_df, rules_df):
        """加载历史数据
        
        Args:
            cases_df: 历史案例DataFrame
            rules_df: 估值规则DataFrame
        """
        self.historical_cases = cases_df
        self.rules = rules_df
        
        # 训练异常检测模型
        self._train_anomaly_detector(cases_df)
        
        # 训练根因分类模型
        self._train_root_cause_classifier(cases_df)
        
        # 训练文本相似度模型
        self._train_text_similarity(cases_df)
        
        # 数据加载完成（移除print避免Streamlit环境错误）
        pass
    
    def _train_anomaly_detector(self, cases_df):
        """训练异常检测模型
        
        Args:
            cases_df: 历史案例DataFrame
        """
        # 提取特征
        features = cases_df[['difference_amount', 'difference_pct', 'resolution_time']].copy()
        features = features.fillna(0)
        
        # 训练Isolation Forest
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.anomaly_detector.fit(features)
        
        # 模型训练完成
        pass
    
    def _train_root_cause_classifier(self, cases_df):
        """训练根因分类模型
        
        Args:
            cases_df: 历史案例DataFrame
        """
        # 准备训练数据
        features = []
        labels = []
        
        for _, row in cases_df.iterrows():
            feature = [
                row['difference_amount'],
                row['difference_pct'],
                1 if row['asset_class'] == 'Bond' else 0,
                1 if row['asset_class'] == 'Equity' else 0,
                1 if row['asset_class'] == 'Cash' else 0
            ]
            features.append(feature)
            labels.append(row['difference_type'])
        
        X = np.array(features)
        y = np.array(labels)
        
        # 编码标签
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # 训练随机森林分类器
        self.root_cause_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.root_cause_classifier.fit(X, y_encoded)
        
        # 分类器训练完成
        pass
    
    def _train_text_similarity(self, cases_df):
        """训练文本相似度模型
        
        Args:
            cases_df: 历史案例DataFrame
        """
        # 合并文本特征
        texts = (cases_df['difference_type'] + ' ' + 
                cases_df['root_cause'] + ' ' + 
                cases_df['asset_class'])
        
        # 训练TF-IDF向量化器
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100)
        self.tfidf_vectorizer.fit(texts)
        
        # 相似度模型训练完成
        pass
    
    def analyze_difference(self, diff_record):
        """分析单条差异记录
        
        Args:
            diff_record: 差异记录（Series或dict）
            
        Returns:
            dict: 分析结果
        """
        if isinstance(diff_record, pd.Series):
            diff_record = diff_record.to_dict()
        
        result = {
            'record_id': diff_record['id'],
            'fund_code': diff_record['fund_code'],
            'security_code': diff_record['security_code'],
            'difference_amount': diff_record['difference'],
            'difference_pct': diff_record['difference_pct'],
            'is_anomaly': False,
            'anomaly_score': 0,
            'predicted_type': '',
            'confidence': 0,
            'root_causes': [],
            'recommended_solutions': [],
            'similar_cases': [],
            'urgency_level': 'Low',
            'estimated_resolution_time': 0,
            'field_decomposition': {}
        }
        
        # 0. 差异分解
        decomposition = self._decompose_difference(diff_record)
        result['field_decomposition'] = decomposition
        
        # 1. 异常检测
        anomaly_result = self._detect_anomaly(diff_record)
        result.update(anomaly_result)
        
        # 2. 根因预测
        root_cause_result = self._predict_root_cause(diff_record)
        result.update(root_cause_result)
        
        # 3. 查找相似案例（优化：结合资产类别和预测类型）
        similar_cases = self._find_similar_cases(diff_record, result['predicted_type'])
        result['similar_cases'] = similar_cases
        
        # 4. 推荐解决方案（优化：结合资产类别和预测类型）
        solutions = self._recommend_solutions(diff_record, similar_cases, result['predicted_type'])
        result['recommended_solutions'] = solutions
        
        # 5. 评估紧急程度
        urgency = self._assess_urgency(diff_record)
        result['urgency_level'] = urgency
        
        # 6. 预估解决时长
        est_time = self._estimate_resolution_time(similar_cases)
        result['estimated_resolution_time'] = est_time
        
        return result
    
    def _decompose_difference(self, diff_record):
        """差异分解 - 计算各字段对总差异的贡献
        
        Args:
            diff_record: 差异记录
            
        Returns:
            dict: 差异分解结果
        """
        total_diff = diff_record['difference']
        quantity = diff_record.get('quantity', 0)
        
        # 价格差异贡献
        price_diff = diff_record['price_custodian'] - diff_record['price_internal']
        price_contribution = price_diff * quantity * diff_record['fx_rate_custodian']
        
        # 汇率差异贡献
        fx_diff = diff_record['fx_rate_custodian'] - diff_record['fx_rate_internal']
        fx_contribution = diff_record['price_internal'] * quantity * fx_diff
        
        # 应计利息差异
        accrued_diff = diff_record['accrued_interest_custodian'] - diff_record['accrued_interest_internal']
        accrued_contribution = accrued_diff
        
        # 计算各贡献的绝对值总和
        total_abs_contribution = abs(price_contribution) + abs(fx_contribution) + abs(accrued_contribution)
        
        # 计算贡献度百分比（归一化到100%）
        if total_abs_contribution > 0.01:
            price_pct = abs(price_contribution) / total_abs_contribution * 100
            fx_pct = abs(fx_contribution) / total_abs_contribution * 100
            accrued_pct = abs(accrued_contribution) / total_abs_contribution * 100
        else:
            price_pct = fx_pct = accrued_pct = 0
        
        return {
            'price_diff': float(price_diff),
            'price_contribution': float(price_contribution),
            'price_contribution_pct': float(price_pct),
            'fx_diff': float(fx_diff),
            'fx_contribution': float(fx_contribution),
            'fx_contribution_pct': float(fx_pct),
            'accrued_diff': float(accrued_diff),
            'accrued_contribution': float(accrued_contribution),
            'accrued_contribution_pct': float(accrued_pct),
            'has_price_diff': abs(price_diff) > 0.0001,
            'has_fx_diff': abs(fx_diff) > 0.0001,
            'has_accrued_diff': abs(accrued_diff) > 0.01
        }
    
    def _detect_anomaly(self, diff_record):
        """检测是否为异常差异
        
        Args:
            diff_record: 差异记录
            
        Returns:
            dict: 异常检测结果
        """
        # 提取特征
        features = np.array([[
            abs(diff_record['difference']),
            abs(diff_record['difference_pct']),
            30  # 假设平均解决时长
        ]])
        
        # 预测
        anomaly_score = self.anomaly_detector.score_samples(features)[0]
        is_anomaly = self.anomaly_detector.predict(features)[0] == -1
        
        # 归一化分数到0-10 (修复：调整归一化公式)
        # Isolation Forest的score_samples返回负值，越负越异常
        # 通常范围在-0.5到0之间
        normalized_score = min(10, max(0, (-anomaly_score) * 10))
        
        return {
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': float(normalized_score)
        }
    
    def _predict_root_cause(self, diff_record):
        """预测根本原因
        
        Args:
            diff_record: 差异记录
            
        Returns:
            dict: 根因预测结果
        """
        # 提取特征
        features = np.array([[
            abs(diff_record['difference']),
            abs(diff_record['difference_pct']),
            1 if diff_record['asset_class'] == 'Bond' else 0,
            1 if diff_record['asset_class'] == 'Equity' else 0,
            1 if diff_record['asset_class'] == 'Cash' else 0
        ]])
        
        # 预测
        pred_encoded = self.root_cause_classifier.predict(features)[0]
        pred_proba = self.root_cause_classifier.predict_proba(features)[0]
        
        predicted_type = self.label_encoder.inverse_transform([pred_encoded])[0]
        confidence = float(pred_proba.max())
        
        # 获取可能的根本原因
        root_causes = self._get_root_causes_for_type(predicted_type, diff_record)
        
        return {
            'predicted_type': predicted_type,
            'confidence': confidence,
            'root_causes': root_causes
        }
    
    def _get_root_causes_for_type(self, diff_type, diff_record):
        """获取特定差异类型的可能根本原因
        
        Args:
            diff_type: 差异类型
            diff_record: 差异记录
            
        Returns:
            list: 可能的根本原因列表
        """
        # 从历史案例中获取该类型的常见原因
        type_cases = self.historical_cases[
            self.historical_cases['difference_type'] == diff_type
        ]
        
        if len(type_cases) > 0:
            # 统计最常见的原因
            cause_counts = type_cases['root_cause'].value_counts()
            top_causes = cause_counts.head(3).index.tolist()
            
            # 添加置信度
            total = cause_counts.sum()
            causes_with_conf = [
                {
                    'cause': cause,
                    'frequency': int(cause_counts[cause]),
                    'confidence': float(cause_counts[cause] / total)
                }
                for cause in top_causes
            ]
            
            return causes_with_conf
        
        return []
    
    def _find_similar_cases(self, diff_record, predicted_type, top_n=5):
        """查找相似历史案例（优化：结合资产类别和预测类型）
        
        Args:
            diff_record: 差异记录
            predicted_type: 预测的差异类型
            top_n: 返回前N个最相似案例
            
        Returns:
            list: 相似案例列表
        """
        if self.historical_cases is None or len(self.historical_cases) == 0:
            return []
        
        # 优先筛选：相同资产类别和差异类型的案例
        asset_class = diff_record.get('asset_class', '')
        filtered_cases = self.historical_cases[
            (self.historical_cases['asset_class'] == asset_class) &
            (self.historical_cases['difference_type'] == predicted_type)
        ]
        
        # 如果筛选后案例太少，扩大到相同资产类别
        if len(filtered_cases) < 3:
            filtered_cases = self.historical_cases[
                self.historical_cases['asset_class'] == asset_class
            ]
        
        # 如果还是太少，使用全部案例
        if len(filtered_cases) < 3:
            filtered_cases = self.historical_cases
        
        # 构建查询文本（包含资产类别、差异类型和差异比例）
        query_text = f"{asset_class} {predicted_type} {abs(diff_record['difference_pct'])}"
        
        # 计算文本相似度
        query_vec = self.tfidf_vectorizer.transform([query_text])
        
        cases_texts = (filtered_cases['difference_type'] + ' ' +
                      filtered_cases['root_cause'] + ' ' +
                      filtered_cases['asset_class'])
        cases_vecs = self.tfidf_vectorizer.transform(cases_texts)
        
        similarities = cosine_similarity(query_vec, cases_vecs)[0]
        
        # 获取最相似的案例
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        similar_cases = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # 降低相似度阈值
                case = filtered_cases.iloc[idx]
                similar_cases.append({
                    'case_id': case['case_id'],
                    'date': str(case['date']),
                    'difference_type': case['difference_type'],
                    'root_cause': case['root_cause'],
                    'resolution': case['resolution'],
                    'resolution_time': int(case['resolution_time']),
                    'similarity': float(similarities[idx]),
                    'asset_class': case['asset_class']
                })
        
        return similar_cases
    
    def _recommend_solutions(self, diff_record, similar_cases, predicted_type):
        """推荐解决方案（优化：结合资产类别和预测类型）
        
        Args:
            diff_record: 差异记录
            similar_cases: 相似案例列表
            predicted_type: 预测的差异类型
            
        Returns:
            list: 推荐的解决方案
        """
        solutions = []
        
        # 从相似案例中提取解决方案
        if similar_cases:
            for case in similar_cases[:3]:  # 取前3个最相似的
                solutions.append({
                    'solution': case['resolution'],
                    'source': f"历史案例 {case['case_id']}",
                    'success_rate': case['similarity'],
                    'avg_time': case['resolution_time']
                })
        
        # 添加基于规则的建议（传入预测类型）
        rule_solutions = self._get_rule_based_solutions(diff_record, predicted_type)
        solutions.extend(rule_solutions)
        
        # 去重并排序（按成功率排序）
        unique_solutions = []
        seen = set()
        for sol in solutions:
            if sol['solution'] not in seen:
                seen.add(sol['solution'])
                unique_solutions.append(sol)
        
        # 按成功率排序
        unique_solutions.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return unique_solutions[:5]  # 返回前5个
    
    def _get_rule_based_solutions(self, diff_record, predicted_type):
        """基于规则获取解决方案（优化：结合预测类型）
        
        Args:
            diff_record: 差异记录
            predicted_type: 预测的差异类型
            
        Returns:
            list: 基于规则的解决方案
        """
        solutions = []
        
        # 根据资产类别、差异类型和差异大小提供建议
        asset_class = diff_record['asset_class']
        diff_pct = abs(diff_record['difference_pct'])
        
        # 根据预测类型提供针对性建议
        if predicted_type == '价格差异':
            if asset_class == 'Bond':
                solutions.append({
                    'solution': '检查债券价格源是否一致',
                    'source': '规则引擎',
                    'success_rate': 0.85,
                    'avg_time': 30
                })
            elif asset_class == 'Equity':
                solutions.append({
                    'solution': '确认股票价格时点是否一致',
                    'source': '规则引擎',
                    'success_rate': 0.90,
                    'avg_time': 20
                })
        
        elif predicted_type == '应计利息差异':
            if asset_class == 'Bond':
                solutions.append({
                    'solution': '核对应计利息计算方法',
                    'source': '规则引擎',
                    'success_rate': 0.88,
                    'avg_time': 45
                })
        
        elif predicted_type == '汇率差异':
            solutions.append({
                'solution': '统一汇率数据源和时点',
                'source': '规则引擎',
                'success_rate': 0.95,
                'avg_time': 15
            })
        
        # 检查具体字段差异
        if abs(diff_record['fx_rate_custodian'] - diff_record['fx_rate_internal']) > 0.0001:
            solutions.append({
                'solution': '统一汇率数据源和时点',
                'source': '规则引擎',
                'success_rate': 0.95,
                'avg_time': 15
            })
        
        if abs(diff_record['price_custodian'] - diff_record['price_internal']) > 0.01:
            if asset_class == 'Bond':
                solutions.append({
                    'solution': '检查债券价格源是否一致',
                    'source': '规则引擎',
                    'success_rate': 0.85,
                    'avg_time': 30
                })
        
        return solutions
    
    def _assess_urgency(self, diff_record):
        """评估紧急程度
        
        Args:
            diff_record: 差异记录
            
        Returns:
            str: 紧急程度 (High/Medium/Low)
        """
        diff_amount = abs(diff_record['difference'])
        diff_pct = abs(diff_record['difference_pct'])
        
        # 根据金额和比例判断
        if diff_amount > 100000 or diff_pct > 1.0:
            return 'High'
        elif diff_amount > 10000 or diff_pct > 0.1:
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_resolution_time(self, similar_cases):
        """预估解决时长
        
        Args:
            similar_cases: 相似案例列表
            
        Returns:
            int: 预估时长（分钟）
        """
        if not similar_cases:
            return 60  # 默认60分钟
        
        # 计算加权平均时长
        total_weight = sum(case['similarity'] for case in similar_cases)
        if total_weight == 0:
            return 60
        
        weighted_time = sum(
            case['resolution_time'] * case['similarity'] 
            for case in similar_cases
        )
        
        return int(weighted_time / total_weight)
    
    def batch_analyze(self, differences_df):
        """批量分析差异
        
        Args:
            differences_df: 差异数据DataFrame
            
        Returns:
            list: 分析结果列表
        """
        results = []
        
        # 批量分析（移除print避免Streamlit环境错误）
        for idx, row in differences_df.iterrows():
            if row['status'] != 'Matched':  # 只分析有差异的记录
                result = self.analyze_difference(row)
                results.append(result)
        
        return results
    
    def generate_analysis_report(self, results):
        """生成分析报告
        
        Args:
            results: 分析结果列表
            
        Returns:
            dict: 统计报告
        """
        if not results:
            return {}
        
        report = {
            '总差异数': len(results),
            '异常差异数': sum(1 for r in results if r['is_anomaly']),
            '差异类型分布': {},
            '紧急程度分布': {},
            '平均置信度': np.mean([r['confidence'] for r in results]),
            '平均预估解决时长': np.mean([r['estimated_resolution_time'] for r in results]),
            '高置信度预测数': sum(1 for r in results if r['confidence'] > 0.7)
        }
        
        # 统计差异类型
        for r in results:
            diff_type = r['predicted_type']
            report['差异类型分布'][diff_type] = report['差异类型分布'].get(diff_type, 0) + 1
        
        # 统计紧急程度
        for r in results:
            urgency = r['urgency_level']
            report['紧急程度分布'][urgency] = report['紧急程度分布'].get(urgency, 0) + 1
        
        return report


if __name__ == '__main__':
    # 测试代码
    pass