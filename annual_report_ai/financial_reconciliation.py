# -*- coding: utf-8 -*-
"""
财务报表勾稽验证模块
实现同年度不同报表间的勾稽关系验证，以及跨年度数据一致性验证
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialReconciliation:
    """财务报表勾稽验证器"""
    
    def __init__(self, tolerance=0.01):
        """
        初始化验证器
        
        参数:
            tolerance: 允许的差异容忍度（元）
        """
        self.tolerance = tolerance
        self.reconciliation_rules = self._init_reconciliation_rules()
    
    def _init_reconciliation_rules(self) -> Dict:
        """初始化勾稽规则"""
        return {
            # 资产负债表内部勾稽
            'balance_sheet_internal': [
                {
                    'name': '资产负债平衡',
                    'formula': '资产总计 = 负债合计 + 净资产合计',
                    'items': ['资产总计', '负债合计', '净资产合计'],
                    'check': lambda data: abs(data.get('资产总计', 0) - (data.get('负债合计', 0) + data.get('净资产合计', 0)))
                },
                {
                    'name': '净资产构成',
                    'formula': '净资产合计 = 实收基金 + 未分配利润',
                    'items': ['净资产合计', '实收基金', '未分配利润'],
                    'check': lambda data: abs(data.get('净资产合计', 0) - (data.get('实收基金', 0) + data.get('未分配利润', 0)))
                },
                {
                    'name': '负债和净资产总计',
                    'formula': '负债和净资产总计 = 资产总计',
                    'items': ['负债和净资产总计', '资产总计'],
                    'check': lambda data: abs(data.get('负债和净资产总计', 0) - data.get('资产总计', 0))
                },
                {
                    'name': '交易性金融资产分解',
                    'formula': '交易性金融资产 = 股票投资 + 基金投资 + 债券投资 + 资产支持证券投资 + 贵金属投资 + 其他投资',
                    'items': ['交易性金融资产', '股票投资', '基金投资', '债券投资', '资产支持证券投资', '贵金属投资', '其他投资'],
                    'check': lambda data: abs(data.get('交易性金融资产', 0) - (
                        data.get('股票投资', 0) + data.get('基金投资', 0) + data.get('债券投资', 0) + 
                        data.get('资产支持证券投资', 0) + data.get('贵金属投资', 0) + data.get('其他投资', 0)
                    ))
                }
            ],
            
            # 利润表内部勾稽
            'income_statement_internal': [
                {
                    'name': '利润总额计算',
                    'formula': '利润总额 = 营业总收入 - 营业总支出',
                    'items': ['利润总额', '营业总收入', '营业总支出'],
                    'check': lambda data: abs(data.get('利润总额', 0) - (data.get('营业总收入', 0) - data.get('营业总支出', 0)))
                },
                {
                    'name': '净利润计算',
                    'formula': '净利润 = 利润总额 - 所得税费用',
                    'items': ['净利润', '利润总额', '所得税费用'],
                    'check': lambda data: abs(data.get('净利润', 0) - (data.get('利润总额', 0) - data.get('所得税费用', 0)))
                }
            ],
            
            # 利润表与资产负债表勾稽
            'income_to_balance': [
                {
                    'name': '净利润与未分配利润勾稽',
                    'formula': '期末未分配利润 = 期初未分配利润 + 本期净利润 - 本期分配利润',
                    'items': ['期末未分配利润', '期初未分配利润', '本期净利润', '本期分配利润'],
                    'check': lambda data: abs(data.get('期末未分配利润', 0) - (
                        data.get('期初未分配利润', 0) + 
                        data.get('本期净利润', 0) - 
                        data.get('本期分配利润', 0)
                    ))
                }
            ],
            
            # 净资产变动表勾稽
            'net_asset_changes': [
                {
                    'name': '期末净资产勾稽',
                    'formula': '本期期末净资产（基金净值）= 本期期初净资产（基金净值）+ 本期增减变动额',
                    'items': ['本期期末净资产', '本期期初净资产', '本期增减变动额'],
                    'check': lambda data: abs(data.get('本期期末净资产', 0) - (
                        data.get('本期期初净资产', 0) + data.get('本期增减变动额', 0)
                    ))
                },
                {
                    'name': '实收基金变动',
                    'formula': '期末实收基金 = 期初实收基金 + 本期实收基金变动',
                    'items': ['期末实收基金', '期初实收基金', '本期实收基金变动'],
                    'check': lambda data: abs(data.get('期末实收基金', 0) - (
                        data.get('期初实收基金', 0) + data.get('本期实收基金变动', 0)
                    ))
                },
                {
                    'name': '未分配利润变动',
                    'formula': '期末未分配利润 = 期初未分配利润 + 本期未分配利润变动',
                    'items': ['期末未分配利润', '期初未分配利润', '本期未分配利润变动'],
                    'check': lambda data: abs(data.get('期末未分配利润', 0) - (
                        data.get('期初未分配利润', 0) + data.get('本期未分配利润变动', 0)
                    ))
                },
                {
                    'name': '综合收益总额计算',
                    'formula': '综合收益总额 = 净利润 + 其他综合收益的税后净额',
                    'items': ['综合收益总额', '净利润', '其他综合收益的税后净额'],
                    'check': lambda data: abs(data.get('综合收益总额', 0) - (
                        data.get('净利润', 0) + data.get('其他综合收益的税后净额', 0)
                    ))
                }
            ]
        }
    
    def load_excel_data(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        加载Excel文件中的所有工作表
        
        参数:
            file_path: Excel文件路径
        
        返回:
            工作表字典 {工作表名: DataFrame}
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets[sheet_name] = df
                logger.info(f"成功加载工作表: {sheet_name}, 形状: {df.shape}")
            
            return sheets
        
        except Exception as e:
            logger.error(f"加载Excel文件失败: {str(e)}")
            raise
    
    def extract_financial_data(self, sheets: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        从工作表中提取关键财务数据
        
        参数:
            sheets: 工作表字典
        
        返回:
            财务数据字典
        """
        financial_data = {}
        
        # 从资产负债表提取数据
        if '资产负债表' in sheets:
            balance_sheet = sheets['资产负债表']
            financial_data.update(self._extract_from_balance_sheet(balance_sheet))
        
        # 从利润表提取数据
        if '利润表' in sheets:
            income_statement = sheets['利润表']
            financial_data.update(self._extract_from_income_statement(income_statement))
        
        # 从净资产变动表提取数据
        if '净资产变动表' in sheets:
            net_asset_changes = sheets['净资产变动表']
            financial_data.update(self._extract_from_net_asset_changes(net_asset_changes))
        
        return financial_data
    
    def _extract_from_balance_sheet(self, df: pd.DataFrame) -> Dict[str, float]:
        """从资产负债表提取数据"""
        data = {}
        
        # 定义需要提取的项目
        items_to_extract = {
            '资产总计': ['资产总计', '资产合计'],
            '负债合计': ['负债合计', '负债总计'],
            '净资产合计': ['净资产合计', '净资产：', '净资产'],
            '实收基金': ['实收基金'],
            '未分配利润': ['未分配利润'],
            '负债和净资产总计': ['负债和净资产总计', '负债和所有者权益总计'],
            '交易性金融资产': ['交易性金融资产'],
            '股票投资': ['股票投资'],
            '基金投资': ['基金投资'],
            '债券投资': ['债券投资'],
            '资产支持证券投资': ['资产支持证券投资'],
            '贵金属投资': ['贵金属投资'],
            '其他投资': ['其他投资']
        }
        
        # 提取本期末数据（通常在第3列）
        for key, aliases in items_to_extract.items():
            value = self._find_value_in_df(df, aliases, col_index=2)
            if value is not None:
                data[key] = value
                data[f'期末{key}'] = value  # 同时保存为期末数据
        
        # 提取上年度末数据（通常在第4列）- 用于期初数据和跨年度对比
        for key, aliases in items_to_extract.items():
            value = self._find_value_in_df(df, aliases, col_index=3)
            if value is not None:
                data[f'期初{key}'] = value
                data[f'上年度可比区间{key}'] = value  # 用于跨年度对比
        
        return data
    
    def _extract_from_income_statement(self, df: pd.DataFrame) -> Dict[str, float]:
        """从利润表提取数据"""
        data = {}
        
        items_to_extract = {
            '营业总收入': ['一、营业总收入', '营业总收入'],
            '营业总支出': ['二、营业总支出', '营业总支出'],
            '利润总额': ['三、利润总额', '利润总额'],
            '净利润': ['四、净利润', '净利润'],
            '所得税费用': ['五、所得税费用', '所得税费用'],
            '其他综合收益的税后净额': ['五、其他综合收益的税后净额', '其他综合收益的税后净额'],
            '综合收益总额': ['六、综合收益总额', '综合收益总额']
        }
        
        # 提取本期数据（通常在第3列）
        for key, aliases in items_to_extract.items():
            value = self._find_value_in_df(df, aliases, col_index=2)
            if value is not None:
                data[key] = value
                data[f'本期{key}'] = value
        
        # 提取上期数据（通常在第4列）用于跨年度对比
        for key, aliases in items_to_extract.items():
            value = self._find_value_in_df(df, aliases, col_index=3)
            if value is not None:
                data[f'上期{key}'] = value
        
        return data
    
    def _extract_from_net_asset_changes(self, df: pd.DataFrame) -> Dict[str, float]:
        """从净资产变动表提取数据"""
        data = {}
        
        # 提取净资产合计列的关键数据
        items_to_extract = {
            '本期期初净资产': ['二、本期期初净资产（基金净值）', '二、本期期初净资产'],
            '本期期末净资产': ['四、本期期末净资产（基金净值）', '四、本期期末净资产'],
            '本期增减变动额': ['三、本期增减变动额（减少以"-"号填列）', '三、本期增减变动额'],
            '综合收益总额': ['（一）、综合收益总额', '综合收益总额'],
            '本期分配利润': ['（三）、本期向基金份额持有人分配利润产生的基金净值变动', '（三）、本期向基金份额持有人分配利润']
        }
        
        # 在净资产合计列（通常是最后一列）查找
        for key, aliases in items_to_extract.items():
            value = self._find_value_in_df(df, aliases, col_index=-1)
            if value is not None:
                data[key] = value
                # 为了兼容性，也保存不带"本期"前缀的版本
                if key.startswith('本期'):
                    simple_key = key.replace('本期', '')
                    data[simple_key] = value
        
        # 提取实收基金和未分配利润的期初期末值
        fund_items = {
            '期初实收基金': ['二、本期期初净资产（基金净值）', '二、本期期初净资产'],
            '期末实收基金': ['四、本期期末净资产（基金净值）', '四、本期期末净资产'],
            '期初未分配利润': ['二、本期期初净资产（基金净值）', '二、本期期初净资产'],
            '期末未分配利润': ['四、本期期末净资产（基金净值）', '四、本期期末净资产']
        }
        
        for key, aliases in fund_items.items():
            if '实收基金' in key:
                value = self._find_value_in_df(df, aliases, col_index=1)
            else:
                value = self._find_value_in_df(df, aliases, col_index=2)
            
            if value is not None:
                data[key] = value
        
        # 计算变动额
        if '期初实收基金' in data and '期末实收基金' in data:
            data['本期实收基金变动'] = data['期末实收基金'] - data['期初实收基金']
        
        if '期初未分配利润' in data and '期末未分配利润' in data:
            data['本期未分配利润变动'] = data['期末未分配利润'] - data['期初未分配利润']
        
        return data
    
    def _find_value_in_df(self, df: pd.DataFrame, item_names: List[str], 
                         col_index: int = 2) -> Optional[float]:
        """
        在DataFrame中查找指定项目的数值
        
        参数:
            df: DataFrame
            item_names: 项目名称列表（别名）
            col_index: 列索引
        
        返回:
            数值或None
        """
        if df is None or df.empty:
            return None
        
        # 确保列索引有效
        if col_index < 0:
            col_index = len(df.columns) + col_index
        
        if col_index >= len(df.columns):
            return None
        
        # 在第一列查找项目名称
        for idx, row in df.iterrows():
            if len(row) == 0:
                continue
            
            first_col = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''
            
            # 检查是否匹配任何别名
            for item_name in item_names:
                if item_name in first_col:
                    # 提取对应列的数值
                    value_str = str(row.iloc[col_index]) if col_index < len(row) else ''
                    value = self._parse_number(value_str)
                    if value is not None:
                        return value
        
        return None
    
    def _parse_number(self, value_str: str) -> Optional[float]:
        """解析数字字符串"""
        if not value_str or value_str in ['', 'None', 'nan', '-', 'NaN']:
            return None
        
        try:
            # 移除逗号和空格
            value_str = str(value_str).replace(',', '').replace(' ', '').strip()
            
            # 处理负数
            is_negative = False
            if value_str.startswith('-') or value_str.startswith('('):
                is_negative = True
                value_str = value_str.replace('-', '').replace('(', '').replace(')', '')
            
            # 转换为浮点数
            value = float(value_str)
            return -value if is_negative else value
        
        except (ValueError, AttributeError):
            return None
    
    def validate_reconciliation(self, financial_data: Dict[str, float]) -> List[Dict]:
        """
        执行勾稽验证
        
        参数:
            financial_data: 财务数据字典
        
        返回:
            验证结果列表
        """
        results = []
        
        # 验证资产负债表内部勾稽
        for rule in self.reconciliation_rules['balance_sheet_internal']:
            result = self._check_rule(rule, financial_data, '资产负债表内部勾稽')
            if result:
                results.append(result)
        
        # 验证利润表内部勾稽
        for rule in self.reconciliation_rules['income_statement_internal']:
            result = self._check_rule(rule, financial_data, '利润表内部勾稽')
            if result:
                results.append(result)
        
        # 验证利润表与资产负债表勾稽
        for rule in self.reconciliation_rules['income_to_balance']:
            result = self._check_rule(rule, financial_data, '利润表与资产负债表勾稽')
            if result:
                results.append(result)
        
        # 验证净资产变动表勾稽
        for rule in self.reconciliation_rules['net_asset_changes']:
            result = self._check_rule(rule, financial_data, '净资产变动表勾稽')
            if result:
                results.append(result)
        
        return results
    
    def _check_rule(self, rule: Dict, financial_data: Dict[str, float], 
                   category: str) -> Optional[Dict]:
        """
        检查单个勾稽规则
        
        参数:
            rule: 勾稽规则
            financial_data: 财务数据
            category: 勾稽类别
        
        返回:
            验证结果或None
        """
        try:
            # 检查所需数据是否都存在
            missing_items = [item for item in rule['items'] if item not in financial_data]
            
            if missing_items:
                logger.warning(f"规则 '{rule['name']}' 缺少数据项: {missing_items}")
                return None
            
            # 执行勾稽检查
            difference = rule['check'](financial_data)
            
            # 提取相关数值
            values = {item: financial_data.get(item, 0) for item in rule['items']}
            
            # 判断是否通过
            is_pass = difference <= self.tolerance
            
            return {
                'category': category,
                'name': rule['name'],
                'formula': rule['formula'],
                'items': rule['items'],
                'values': values,
                'difference': difference,
                'is_pass': is_pass,
                'status': '✓ 通过' if is_pass else '❌ 不通过'
            }
        
        except Exception as e:
            logger.error(f"检查规则 '{rule['name']}' 时出错: {str(e)}")
            return None
    
    def validate_cross_year_consistency(self, current_year_data: Dict[str, float],
                                       previous_year_data: Dict[str, float]) -> List[Dict]:
        """
        验证跨年度数据一致性
        
        参数:
            current_year_data: 当前年度财务数据
            previous_year_data: 上一年度财务数据
        
        返回:
            验证结果列表
        """
        results = []
        
        # 定义需要对比的项目（根据用户要求）
        # 所有项目统一逻辑：当年上年度可比区间 = 上一年本期数值
        # 格式：(当年数据key, 上年数据key, 显示名称)
        cross_year_items = [
            # 资产负债表项目
            ('上年度可比区间资产总计', '期末资产总计', '资产总计'),
            ('上年度可比区间负债合计', '期末负债合计', '负债合计'),
            ('上年度可比区间净资产合计', '期末净资产合计', '净资产合计'),
            # 利润表项目
            ('上期营业总收入', '本期营业总收入', '营业总收入'),
            ('上期综合收益总额', '本期综合收益总额', '综合收益总额'),
            # 净资产变动表项目
            ('上年度可比区间实收基金', '期末实收基金', '实收基金'),
            ('上年度可比区间未分配利润', '期末未分配利润', '未分配利润')
        ]
        
        for current_key, previous_key, item_name in cross_year_items:
            current_value = current_year_data.get(current_key)
            previous_value = previous_year_data.get(previous_key)
            
            if current_value is not None and previous_value is not None:
                # 统一逻辑：当年上年度可比区间 = 上一年本期数值
                difference = abs(current_value - previous_value)
                is_pass = difference <= self.tolerance
                
                results.append({
                    'item': item_name,
                    'current_year_comparable': current_value,  # 当年的上年度可比区间数值
                    'previous_year_current': previous_value,   # 上一年度的本期数值
                    'difference': difference,
                    'is_pass': is_pass,
                    'status': '✓ 一致' if is_pass else '❌ 不一致',
                    'formula': f'当年上年度可比区间{item_name} = 上一年本期{item_name}'
                })
        
        return results


def main():
    """测试函数"""
    reconciliation = FinancialReconciliation(tolerance=0.01)
    
    # 测试加载Excel文件
    file_path = "易方达香港恒生综合小型股指数基金2022年财务报表_20251229.xlsx"
    
    try:
        sheets = reconciliation.load_excel_data(file_path)
        print(f"成功加载 {len(sheets)} 个工作表")
        
        financial_data = reconciliation.extract_financial_data(sheets)
        print(f"\n提取的财务数据:")
        for key, value in financial_data.items():
            print(f"  {key}: {value:,.2f}")
        
        results = reconciliation.validate_reconciliation(financial_data)
        print(f"\n勾稽验证结果: 共 {len(results)} 项")
        for result in results:
            print(f"  {result['status']} {result['name']}: 差异 {result['difference']:.2f}")
    
    except Exception as e:
        print(f"测试失败: {str(e)}")


if __name__ == '__main__':
    main()