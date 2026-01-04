# -*- coding: utf-8 -*-
"""
数据验证模块
实现年报数据的勾稽验证、跨年对比、加总验证
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""
    
    def __init__(self, tolerance=2.0):
        """
        初始化验证器
        
        参数:
            tolerance: 允许的差异容忍度（元）
        """
        self.tolerance = tolerance
        self.validation_results = []
    
    def validate_reconciliation(self, main_table: pd.DataFrame, 
                               note_table: pd.DataFrame,
                               mapping: Dict[str, str]) -> List[Dict]:
        """
        验证主表与附注的勾稽关系
        
        参数:
            main_table: 主表DataFrame
            note_table: 附注表DataFrame
            mapping: 映射关系 {主表项目: 附注项目}
        
        返回:
            差异列表
        """
        differences = []
        
        for main_item, note_item in mapping.items():
            try:
                # 从主表提取值
                main_value = self._extract_value(main_table, main_item)
                
                # 从附注提取值
                note_value = self._extract_value(note_table, note_item)
                
                if main_value is not None and note_value is not None:
                    # 计算差异
                    diff = abs(main_value - note_value)
                    
                    if diff > self.tolerance:
                        differences.append({
                            'type': '勾稽差异',
                            'main_item': main_item,
                            'note_item': note_item,
                            'main_value': main_value,
                            'note_value': note_value,
                            'difference': diff,
                            'difference_rate': (diff / main_value * 100) if main_value != 0 else 0,
                            'severity': self._assess_severity(diff, main_value)
                        })
                        
                        logger.warning(f"勾稽差异: {main_item} vs {note_item}, 差异={diff:.2f}")
            
            except Exception as e:
                logger.error(f"验证 {main_item} 失败: {str(e)}")
        
        return differences
    
    def validate_cross_year(self, current_report: Dict, 
                           previous_report: Dict,
                           items: List[str]) -> List[Dict]:
        """
        验证跨年度数据一致性
        
        参数:
            current_report: 当前年报数据
            previous_report: 上一年年报数据
            items: 需要对比的项目列表
        
        返回:
            差异列表
        """
        differences = []
        
        current_year = current_report.get('year')
        previous_year = previous_report.get('year')
        
        logger.info(f"跨年度对比: {current_year}年报中的{previous_year}数据 vs {previous_year}年报数据")
        
        for item in items:
            try:
                # 从当前年报中提取上一年的数据
                current_last_year_value = self._extract_last_year_value(
                    current_report, item
                )
                
                # 从上一年年报中提取数据
                previous_year_value = self._extract_current_year_value(
                    previous_report, item
                )
                
                if current_last_year_value is not None and previous_year_value is not None:
                    # 跨年数据必须完全一致
                    if current_last_year_value != previous_year_value:
                        diff = abs(current_last_year_value - previous_year_value)
                        
                        differences.append({
                            'type': '跨年不一致',
                            'item': item,
                            'current_report_last_year': current_last_year_value,
                            'previous_report': previous_year_value,
                            'difference': diff,
                            'difference_rate': (diff / previous_year_value * 100) if previous_year_value != 0 else 0,
                            'severity': 'High'  # 跨年不一致都是高优先级
                        })
                        
                        logger.warning(f"跨年不一致: {item}, 差异={diff:.2f}")
            
            except Exception as e:
                logger.error(f"跨年对比 {item} 失败: {str(e)}")
        
        return differences
    
    def validate_summation(self, table: pd.DataFrame, 
                          summation_rules: Dict[str, List[str]]) -> List[Dict]:
        """
        验证加总关系
        
        参数:
            table: 数据表
            summation_rules: 加总规则 {总计项: [小项列表]}
        
        返回:
            差异列表
        """
        differences = []
        
        for total_item, sub_items in summation_rules.items():
            try:
                # 提取总计值
                total_value = self._extract_value(table, total_item)
                
                # 提取并累加小项
                sub_values = []
                for sub_item in sub_items:
                    value = self._extract_value(table, sub_item)
                    if value is not None:
                        sub_values.append(value)
                
                if total_value is not None and sub_values:
                    calculated_total = sum(sub_values)
                    diff = abs(total_value - calculated_total)
                    
                    if diff > self.tolerance:
                        differences.append({
                            'type': '加总错误',
                            'total_item': total_item,
                            'sub_items': sub_items,
                            'reported_total': total_value,
                            'calculated_total': calculated_total,
                            'difference': diff,
                            'difference_rate': (diff / total_value * 100) if total_value != 0 else 0,
                            'severity': self._assess_severity(diff, total_value)
                        })
                        
                        logger.warning(f"加总错误: {total_item}, 差异={diff:.2f}")
            
            except Exception as e:
                logger.error(f"加总验证 {total_item} 失败: {str(e)}")
        
        return differences
    
    def _extract_value(self, table: pd.DataFrame, item_name: str) -> Optional[float]:
        """
        从表格中提取数值
        
        参数:
            table: 数据表
            item_name: 项目名称
        
        返回:
            数值或None
        """
        if table is None or table.empty:
            return None
        
        # 在第一列查找项目名称
        for idx, row in table.iterrows():
            first_col = str(row.iloc[0]) if len(row) > 0 else ''
            
            if item_name in first_col:
                # 尝试从第二列或第三列提取数值
                for col_idx in range(1, min(len(row), 4)):
                    value_str = str(row.iloc[col_idx])
                    value = self._parse_number(value_str)
                    if value is not None:
                        return value
        
        return None
    
    def _extract_last_year_value(self, report: Dict, item_name: str) -> Optional[float]:
        """从当前年报中提取上一年的数据"""
        # 通常在表格的"上年同期"或"上年末"列
        tables = report.get('tables', {})
        
        for table_name, table in tables.items():
            if '资产负债表' in table_name or '利润表' in table_name:
                value = self._extract_value_from_column(table, item_name, ['上年', '上期'])
                if value is not None:
                    return value
        
        return None
    
    def _extract_current_year_value(self, report: Dict, item_name: str) -> Optional[float]:
        """从年报中提取当年数据"""
        tables = report.get('tables', {})
        
        for table_name, table in tables.items():
            if '资产负债表' in table_name or '利润表' in table_name:
                value = self._extract_value_from_column(table, item_name, ['本期', '期末', '本年'])
                if value is not None:
                    return value
        
        return None
    
    def _extract_value_from_column(self, table: pd.DataFrame, 
                                   item_name: str, 
                                   column_keywords: List[str]) -> Optional[float]:
        """从特定列提取数值"""
        if table is None or table.empty:
            return None
        
        # 查找包含关键词的列
        target_col = None
        for col in table.columns:
            col_str = str(col)
            if any(keyword in col_str for keyword in column_keywords):
                target_col = col
                break
        
        if target_col is None:
            return None
        
        # 在第一列查找项目名称
        for idx, row in table.iterrows():
            first_col = str(row.iloc[0]) if len(row) > 0 else ''
            
            if item_name in first_col:
                value_str = str(row[target_col])
                return self._parse_number(value_str)
        
        return None
    
    def _parse_number(self, value_str: str) -> Optional[float]:
        """
        解析数字字符串
        
        参数:
            value_str: 数字字符串
        
        返回:
            浮点数或None
        """
        if not value_str or value_str in ['', 'None', 'nan', '-']:
            return None
        
        try:
            # 移除逗号和空格
            value_str = value_str.replace(',', '').replace(' ', '').strip()
            
            # 处理负数
            is_negative = False
            if value_str.startswith('-') or value_str.startswith('('):
                is_negative = True
                value_str = value_str.replace('-', '').replace('(', '').replace(')', '')
            
            # 提取数字
            match = re.search(r'[\d.]+', value_str)
            if match:
                value = float(match.group())
                return -value if is_negative else value
        
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def _assess_severity(self, diff: float, base_value: float) -> str:
        """
        评估差异严重程度
        
        参数:
            diff: 差异值
            base_value: 基准值
        
        返回:
            严重程度 (High/Medium/Low)
        """
        if base_value == 0:
            return 'High' if diff > 100 else 'Medium'
        
        rate = abs(diff / base_value)
        
        if rate > 0.01 or diff > 1000:  # 差异率>1% 或 差异>1000元
            return 'High'
        elif rate > 0.001 or diff > 100:  # 差异率>0.1% 或 差异>100元
            return 'Medium'
        else:
            return 'Low'
    
    def smart_reconciliation(self, report: Dict) -> List[Dict]:
        """
        智能主表与附注勾稽（新增）
        
        参数:
            report: 年报数据
        
        返回:
            差异列表
        """
        differences = []
        tables = report.get('tables', {})
        
        # 分离主表和附注表
        main_tables = {}
        note_tables = {}
        
        for table_name, table_df in tables.items():
            if '主表' in table_name:
                main_tables[table_name] = table_df
            elif '附注' in table_name or '明细' in table_name:
                note_tables[table_name] = table_df
        
        logger.info(f"找到 {len(main_tables)} 个主表, {len(note_tables)} 个附注表")
        
        # 对每个主表，尝试找到对应的附注表进行勾稽
        for main_table_name, main_table in main_tables.items():
            # 确定主表类型
            if '资产负债表' in main_table_name:
                # 查找资产负债表相关的附注
                for note_table_name, note_table in note_tables.items():
                    if '资产' in note_table_name or '负债' in note_table_name:
                        # 执行勾稽验证
                        diffs = self._reconcile_tables(
                            main_table, note_table,
                            main_table_name, note_table_name
                        )
                        differences.extend(diffs)
            
            elif '利润表' in main_table_name:
                # 查找利润表相关的附注
                for note_table_name, note_table in note_tables.items():
                    if '收入' in note_table_name or '费用' in note_table_name or '损益' in note_table_name:
                        diffs = self._reconcile_tables(
                            main_table, note_table,
                            main_table_name, note_table_name
                        )
                        differences.extend(diffs)
        
        return differences
    
    def _reconcile_tables(self, main_table: pd.DataFrame, note_table: pd.DataFrame,
                         main_name: str, note_name: str) -> List[Dict]:
        """
        勾稽两个表格
        
        参数:
            main_table: 主表
            note_table: 附注表
            main_name: 主表名称
            note_name: 附注表名称
        
        返回:
            差异列表
        """
        differences = []
        
        # 获取主表的所有项目
        if main_table is None or main_table.empty:
            return differences
        
        main_items = main_table.iloc[:, 0].astype(str).tolist()
        note_items = note_table.iloc[:, 0].astype(str).tolist() if note_table is not None and not note_table.empty else []
        
        # 对每个主表项目，尝试在附注中找到匹配项
        for main_item in main_items:
            if not main_item or main_item.strip() == '':
                continue
            
            # 查找匹配的附注项目
            matching_note_items = ReconciliationRules.find_matching_items(main_item, note_items)
            
            if matching_note_items:
                # 提取并对比数值
                main_value = self._extract_value(main_table, main_item)
                
                for note_item in matching_note_items:
                    note_value = self._extract_value(note_table, note_item)
                    
                    if main_value is not None and note_value is not None:
                        diff = abs(main_value - note_value)
                        
                        if diff > self.tolerance:
                            differences.append({
                                'type': '勾稽差异',
                                'main_table': main_name,
                                'note_table': note_name,
                                'main_item': main_item,
                                'note_item': note_item,
                                'main_value': main_value,
                                'note_value': note_value,
                                'difference': diff,
                                'difference_rate': (diff / main_value * 100) if main_value != 0 else 0,
                                'severity': self._assess_severity(diff, main_value)
                            })
                            
                            logger.info(f"勾稽差异: {main_item} vs {note_item}, 差异={diff:.2f}")
        
        return differences
    
    def auto_validate_summation(self, report: Dict) -> List[Dict]:
        """
        自动识别并验证加总关系（新增）
        
        参数:
            report: 年报数据
        
        返回:
            差异列表
        """
        all_differences = []
        tables = report.get('tables', {})
        
        for table_name, table_df in tables.items():
            logger.info(f"分析表格 {table_name} 的加总关系...")
            
            # 自动识别加总关系
            summation_relationships = ReconciliationRules.identify_summation_relationships(table_df)
            
            if summation_relationships:
                logger.info(f"发现 {len(summation_relationships)} 个加总关系")
                
                # 验证每个加总关系
                differences = self.validate_summation(table_df, summation_relationships)
                
                # 添加表格名称信息
                for diff in differences:
                    diff['table_name'] = table_name
                
                all_differences.extend(differences)
        
        return all_differences
    
    def comprehensive_validation(self, reports: Dict[str, Dict]) -> Dict:
        """
        综合验证（增强版）
        
        参数:
            reports: 年报数据字典 {年份: 报告数据}
        
        返回:
            验证结果汇总
        """
        all_differences = []
        
        # 按年份排序
        sorted_years = sorted(reports.keys())
        
        # 1. 跨年度验证
        for i in range(len(sorted_years) - 1):
            current_year = sorted_years[i + 1]
            previous_year = sorted_years[i]
            
            cross_year_diffs = self.validate_cross_year(
                reports[current_year],
                reports[previous_year],
                ReconciliationRules.CROSS_YEAR_ITEMS
            )
            all_differences.extend(cross_year_diffs)
        
        # 2. 每个年报的内部验证
        for year, report in reports.items():
            logger.info(f"验证 {year} 年报内部数据...")
            
            # 2.1 智能主表与附注勾稽
            reconciliation_diffs = self.smart_reconciliation(report)
            all_differences.extend(reconciliation_diffs)
            
            # 2.2 自动加总关系验证
            summation_diffs = self.auto_validate_summation(report)
            all_differences.extend(summation_diffs)
        
        # 3. 统计结果
        result = {
            'total_differences': len(all_differences),
            'by_severity': {
                'High': len([d for d in all_differences if d.get('severity') == 'High']),
                'Medium': len([d for d in all_differences if d.get('severity') == 'Medium']),
                'Low': len([d for d in all_differences if d.get('severity') == 'Low'])
            },
            'by_type': {},
            'differences': all_differences
        }
        
        # 按类型统计
        for diff in all_differences:
            diff_type = diff.get('type', 'Unknown')
            if diff_type not in result['by_type']:
                result['by_type'][diff_type] = 0
            result['by_type'][diff_type] += 1
        
        logger.info(f"验证完成: 发现 {len(all_differences)} 处差异")
        logger.info(f"  - 勾稽差异: {result['by_type'].get('勾稽差异', 0)}个")
        logger.info(f"  - 跨年不一致: {result['by_type'].get('跨年不一致', 0)}个")
        logger.info(f"  - 加总错误: {result['by_type'].get('加总错误', 0)}个")
        
        return result


class ReconciliationRules:
    """勾稽规则库（增强版）"""
    
    # 资产负债表勾稽规则
    BALANCE_SHEET_RULES = {
        '资产总计': ['资产合计', '资产总额', '总资产'],
        '负债总计': ['负债合计', '负债总额', '总负债'],
        '净资产': ['所有者权益', '基金净资产', '净资产合计'],
        '流动资产': ['流动资产合计', '流动资产总计'],
        '非流动资产': ['非流动资产合计', '非流动资产总计'],
        '货币资金': ['银行存款', '现金', '货币资金合计'],
        '交易性金融资产': ['以公允价值计量且其变动计入当期损益的金融资产', '交易性金融资产合计'],
        '应收款项': ['应收账款', '应收票据', '应收款项合计'],
        '流动负债': ['流动负债合计', '流动负债总计'],
        '应付款项': ['应付账款', '应付票据', '应付款项合计']
    }
    
    # 利润表勾稽规则
    INCOME_STATEMENT_RULES = {
        '营业收入': ['收入合计', '营业收入合计', '总收入'],
        '营业成本': ['成本合计', '营业成本合计', '总成本'],
        '净利润': ['本期利润', '净利润合计', '利润总额'],
        '投资收益': ['投资收益合计', '投资收益总额'],
        '公允价值变动收益': ['公允价值变动损益', '公允价值变动收益合计']
    }
    
    # 加总规则（自动识别）
    SUMMATION_RULES = {
        '资产总计': ['流动资产', '非流动资产'],
        '流动资产': ['货币资金', '交易性金融资产', '应收款项', '预付款项', '存出保证金', '其他流动资产'],
        '非流动资产': ['长期股权投资', '固定资产', '无形资产', '递延所得税资产', '其他非流动资产'],
        '负债总计': ['流动负债', '非流动负债'],
        '流动负债': ['短期借款', '应付款项', '预收款项', '应付职工薪酬', '应交税费', '其他流动负债'],
        '非流动负债': ['长期借款', '应付债券', '递延所得税负债', '其他非流动负债'],
        '营业收入': ['利息收入', '投资收益', '公允价值变动收益', '其他收入'],
        '营业成本': ['利息支出', '业务及管理费', '其他费用']
    }
    
    # 跨年对比项目
    CROSS_YEAR_ITEMS = [
        '资产总计',
        '负债总计',
        '净资产',
        '营业收入',
        '营业成本',
        '净利润',
        '基金份额总额',
        '基金份额净值'
    ]
    
    @staticmethod
    def find_matching_items(main_item: str, note_items: List[str]) -> List[str]:
        """
        在附注项目中查找与主表项目匹配的项目
        
        参数:
            main_item: 主表项目名称
            note_items: 附注项目列表
        
        返回:
            匹配的附注项目列表
        """
        matches = []
        
        # 获取主表项目的同义词
        synonyms = ReconciliationRules.BALANCE_SHEET_RULES.get(main_item, [])
        if not synonyms:
            synonyms = ReconciliationRules.INCOME_STATEMENT_RULES.get(main_item, [])
        
        # 如果没有预定义的同义词，使用主表项目本身
        if not synonyms:
            synonyms = [main_item]
        
        # 在附注项目中查找匹配
        for note_item in note_items:
            for synonym in synonyms:
                if synonym in note_item or note_item in synonym:
                    matches.append(note_item)
                    break
        
        return matches
    
    @staticmethod
    def identify_summation_relationships(table: pd.DataFrame) -> Dict[str, List[str]]:
        """
        自动识别表格中的加总关系
        
        参数:
            table: 数据表
        
        返回:
            加总关系字典 {总计项: [小项列表]}
        """
        if table is None or table.empty:
            return {}
        
        relationships = {}
        
        # 获取第一列（通常是项目名称列）
        if len(table.columns) == 0:
            return {}
        
        first_col = table.iloc[:, 0].astype(str).tolist()
        
        # 查找包含"合计"、"总计"、"总额"的行
        total_indices = []
        for idx, item in enumerate(first_col):
            if any(keyword in item for keyword in ['合计', '总计', '总额', '小计']):
                total_indices.append((idx, item))
        
        # 对每个总计项，查找其上方的小项
        for total_idx, total_item in total_indices:
            sub_items = []
            
            # 向上查找，直到遇到另一个总计项或表格开始
            for i in range(total_idx - 1, -1, -1):
                item = first_col[i]
                
                # 如果遇到另一个总计项，停止
                if any(keyword in item for keyword in ['合计', '总计', '总额']):
                    break
                
                # 如果是有效的项目名称（不为空且不是纯数字）
                if item and item.strip() and not item.replace('.', '').replace(',', '').isdigit():
                    sub_items.append(item)
            
            # 如果找到了小项，记录这个加总关系
            if sub_items:
                relationships[total_item] = list(reversed(sub_items))  # 反转以保持原始顺序
        
        return relationships


def main():
    """测试函数"""
    validator = DataValidator(tolerance=2.0)
    
    # 创建测试数据
    test_table = pd.DataFrame({
        '项目': ['资产总计', '流动资产', '非流动资产'],
        '本期金额': ['1000000', '600000', '400000'],
        '上期金额': ['900000', '500000', '400000']
    })
    
    # 测试加总验证
    summation_rules = {
        '资产总计': ['流动资产', '非流动资产']
    }
    
    differences = validator.validate_summation(test_table, summation_rules)
    
    print(f"发现 {len(differences)} 处差异")
    for diff in differences:
        print(f"- {diff['type']}: {diff['total_item']}, 差异={diff['difference']:.2f}")


if __name__ == '__main__':
    main()