# -*- coding: utf-8 -*-
"""
标的交收AI助手 - AI分析引擎
实现智能匹配分析、重复检测、延迟预警等功能
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class SettlementAIAnalyzer:
    """交收AI分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.duplicate_detector = None
        self.delay_predictor = None
        self.type_classifier = None
        
    def analyze_match_status(self, trades_df: pd.DataFrame) -> Dict:
        """
        分析匹配状态
        
        Args:
            trades_df: 交易数据DataFrame
        
        Returns:
            分析结果字典
        """
        if trades_df.empty:
            return {}
        
        total = len(trades_df)
        matched = (trades_df['Matched?'] == 'Y').sum()
        unmatched = total - matched
        match_rate = (matched / total * 100) if total > 0 else 0
        
        # 按账户统计 - 使用size()代替count()避免列名问题
        account_stats = trades_df.groupby('Account').agg({
            'Matched?': lambda x: (x == 'Y').sum()
        }).reset_index()
        account_stats['Total'] = trades_df.groupby('Account').size().values
        account_stats.columns = ['Account', 'Matched', 'Total']
        account_stats['Match_Rate'] = (account_stats['Matched'] / account_stats['Total'] * 100).round(2)
        
        # 按日期统计 - 使用size()代替count()避免列名问题
        date_stats = trades_df.groupby('Date').agg({
            'Matched?': lambda x: (x == 'Y').sum()
        }).reset_index()
        date_stats['Total'] = trades_df.groupby('Date').size().values
        date_stats.columns = ['Date', 'Matched', 'Total']
        date_stats['Match_Rate'] = (date_stats['Matched'] / date_stats['Total'] * 100).round(2)
        
        # 未匹配交易详情
        unmatched_trades = trades_df[trades_df['Matched?'] != 'Y'].copy()
        
        return {
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': match_rate,
            'account_stats': account_stats,
            'date_stats': date_stats,
            'unmatched_trades': unmatched_trades
        }
    
    def detect_duplicates(self, trades_df: pd.DataFrame) -> Dict:
        """
        检测重复交易
        
        Args:
            trades_df: 交易数据DataFrame
        
        Returns:
            检测结果字典
        """
        if trades_df.empty:
            return {}
        
        total = len(trades_df)
        
        # 基于Duplicated?标记的统计
        marked_duplicates = (trades_df['Duplicated?'] == 'Y').sum()
        
        # AI检测：基于多维特征的聚类
        # 特征：Ticket Number, Amount, Settlement Date, Security
        duplicate_groups = []
        
        # 按账户分组检测
        for account in trades_df['Account'].unique():
            account_trades = trades_df[trades_df['Account'] == account].copy()
            
            if len(account_trades) < 2:
                continue
            
            # 准备特征
            features = []
            indices = []
            
            for idx, row in account_trades.iterrows():
                # 特征向量：金额、日期差、证券哈希
                amount = row.get('Amount (Pennies)', 0)
                if pd.isna(amount):
                    amount = 0
                
                settlement_date = row.get('Settlement Date')
                if pd.notna(settlement_date):
                    date_num = settlement_date.toordinal()
                else:
                    date_num = 0
                
                security = str(row.get('Security', ''))
                security_hash = hash(security) % 10000
                
                features.append([amount, date_num, security_hash])
                indices.append(idx)
            
            if len(features) < 2:
                continue
            
            # DBSCAN聚类
            features_array = np.array(features)
            # 标准化
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_array)
            
            clustering = DBSCAN(eps=0.5, min_samples=2).fit(features_scaled)
            labels = clustering.labels_
            
            # 提取重复组
            for label in set(labels):
                if label == -1:  # 噪声点
                    continue
                
                cluster_indices = [indices[i] for i, l in enumerate(labels) if l == label]
                if len(cluster_indices) >= 2:
                    duplicate_groups.append({
                        'account': account,
                        'indices': cluster_indices,
                        'count': len(cluster_indices)
                    })
        
        ai_detected = sum(group['count'] for group in duplicate_groups)
        
        # 重复交易详情
        duplicate_trades = trades_df[trades_df['Duplicated?'] == 'Y'].copy()
        
        return {
            'total': total,
            'marked_duplicates': marked_duplicates,
            'ai_detected': ai_detected,
            'duplicate_rate': (marked_duplicates / total * 100) if total > 0 else 0,
            'duplicate_groups': duplicate_groups,
            'duplicate_trades': duplicate_trades
        }
    
    def predict_settlement_delay(self, trades_df: pd.DataFrame) -> Dict:
        """
        预测交收延迟
        
        Args:
            trades_df: 交易数据DataFrame
        
        Returns:
            预测结果字典
        """
        if trades_df.empty:
            return {}
        
        # 计算交收时长
        trades_df = trades_df.copy()
        trades_df['Settlement_Days'] = 0
        
        for idx, row in trades_df.iterrows():
            trade_date = row.get('Trade Date')
            settlement_date = row.get('Settlement Date')
            
            if pd.notna(trade_date) and pd.notna(settlement_date):
                days = (settlement_date - trade_date).days
                trades_df.at[idx, 'Settlement_Days'] = days
        
        # 统计
        avg_days = trades_df['Settlement_Days'].mean()
        max_days = trades_df['Settlement_Days'].max()
        
        # 识别延迟交易（超过3天）
        delayed_trades = trades_df[trades_df['Settlement_Days'] > 3].copy()
        delay_count = len(delayed_trades)
        delay_rate = (delay_count / len(trades_df) * 100) if len(trades_df) > 0 else 0
        
        # 按交易类型统计延迟
        if 'Blotter Transaction Type' in trades_df.columns:
            type_delay_stats = trades_df.groupby('Blotter Transaction Type').agg({
                'Settlement_Days': ['mean', 'max', 'count']
            }).round(2)
        else:
            type_delay_stats = pd.DataFrame()
        
        return {
            'total': len(trades_df),
            'delayed_count': delay_count,
            'delay_rate': delay_rate,
            'avg_settlement_days': avg_days,
            'max_settlement_days': max_days,
            'delayed_trades': delayed_trades,
            'type_delay_stats': type_delay_stats
        }
    
    def analyze_transaction_types(self, trades_df: pd.DataFrame) -> Dict:
        """
        分析交易类型
        
        Args:
            trades_df: 交易数据DataFrame
        
        Returns:
            分析结果字典
        """
        if trades_df.empty:
            return {}
        
        # 交易类型分布
        if 'Blotter Transaction Type' in trades_df.columns:
            type_dist = trades_df['Blotter Transaction Type'].value_counts()
        else:
            type_dist = pd.Series()
        
        # 特殊标记统计
        flag_columns = ['Bond?', 'Fund?', 'Future?', 'Forward?', 'FX?']
        flag_stats = {}
        
        for col in flag_columns:
            if col in trades_df.columns:
                count = (trades_df[col] == 'Y').sum()
                rate = (count / len(trades_df) * 100) if len(trades_df) > 0 else 0
                flag_stats[col] = {
                    'count': count,
                    'rate': rate
                }
        
        # 货币分布
        if 'Currency' in trades_df.columns:
            currency_dist = trades_df['Currency'].value_counts()
        else:
            currency_dist = pd.Series()
        
        # 买卖方向分布
        if 'Buy/Sell' in trades_df.columns:
            bs_dist = trades_df['Buy/Sell'].value_counts()
        else:
            bs_dist = pd.Series()
        
        return {
            'type_distribution': type_dist,
            'flag_statistics': flag_stats,
            'currency_distribution': currency_dist,
            'buy_sell_distribution': bs_dist
        }
    
    def generate_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """
        生成智能建议
        
        Args:
            analysis_results: 分析结果
        
        Returns:
            建议列表
        """
        recommendations = []
        
        # 基于匹配率的建议
        if 'match_status' in analysis_results:
            match_rate = analysis_results['match_status'].get('match_rate', 0)
            
            if match_rate < 90:
                recommendations.append({
                    'priority': 'High',
                    'category': '匹配问题',
                    'issue': f'匹配率仅为 {match_rate:.1f}%，低于90%目标',
                    'recommendation': '建议检查未匹配交易的Ticket Number是否正确，确认Combined Match数据是否完整',
                    'expected_improvement': '提升匹配率至95%以上'
                })
            elif match_rate < 95:
                recommendations.append({
                    'priority': 'Medium',
                    'category': '匹配优化',
                    'issue': f'匹配率为 {match_rate:.1f}%，接近但未达到95%目标',
                    'recommendation': '建议优化匹配规则，考虑模糊匹配算法',
                    'expected_improvement': '提升匹配率至98%以上'
                })
        
        # 基于重复率的建议
        if 'duplicate_detection' in analysis_results:
            dup_rate = analysis_results['duplicate_detection'].get('duplicate_rate', 0)
            
            if dup_rate > 5:
                recommendations.append({
                    'priority': 'High',
                    'category': '重复交易',
                    'issue': f'重复交易率为 {dup_rate:.1f}%，超过5%警戒线',
                    'recommendation': '建议加强交易录入前的重复检查，实施自动去重机制',
                    'expected_improvement': '降低重复率至2%以下'
                })
            elif dup_rate > 2:
                recommendations.append({
                    'priority': 'Medium',
                    'category': '重复控制',
                    'issue': f'重复交易率为 {dup_rate:.1f}%，需要关注',
                    'recommendation': '建议定期审查重复交易模式，优化录入流程',
                    'expected_improvement': '降低重复率至1%以下'
                })
        
        # 基于延迟率的建议
        if 'delay_prediction' in analysis_results:
            delay_rate = analysis_results['delay_prediction'].get('delay_rate', 0)
            
            if delay_rate > 10:
                recommendations.append({
                    'priority': 'High',
                    'category': '交收延迟',
                    'issue': f'交收延迟率为 {delay_rate:.1f}%，超过10%警戒线',
                    'recommendation': '建议分析延迟原因，优化交收流程，加强与对手方沟通',
                    'expected_improvement': '降低延迟率至5%以下'
                })
            elif delay_rate > 5:
                recommendations.append({
                    'priority': 'Medium',
                    'category': '交收优化',
                    'issue': f'交收延迟率为 {delay_rate:.1f}%，有改进空间',
                    'recommendation': '建议建立延迟预警机制，提前介入处理',
                    'expected_improvement': '降低延迟率至3%以下'
                })
        
        # 按优先级排序
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    def comprehensive_analysis(self, trades_df: pd.DataFrame) -> Dict:
        """
        综合分析
        
        Args:
            trades_df: 交易数据DataFrame
        
        Returns:
            完整分析结果
        """
        results = {}
        
        # 1. 匹配状态分析
        results['match_status'] = self.analyze_match_status(trades_df)
        
        # 2. 重复检测
        results['duplicate_detection'] = self.detect_duplicates(trades_df)
        
        # 3. 延迟预测
        results['delay_prediction'] = self.predict_settlement_delay(trades_df)
        
        # 4. 交易类型分析
        results['transaction_analysis'] = self.analyze_transaction_types(trades_df)
        
        # 5. 生成建议
        results['recommendations'] = self.generate_recommendations(results)
        
        return results


if __name__ == '__main__':
    # 测试代码
    print("AI分析引擎模块已就绪")