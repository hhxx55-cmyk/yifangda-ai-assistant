# -*- coding: utf-8 -*-
"""
文档解析模块
解析年报PDF文件，提取表格和文字内容
"""

import pdfplumber
import pandas as pd
import re
import os
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnnualReportParser:
    """年报解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.current_file = None
        self.pdf = None
        
    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        解析PDF年报
        
        参数:
            pdf_path: PDF文件路径
        
        返回:
            解析结果字典
        """
        logger.info(f"开始解析: {os.path.basename(pdf_path)}")
        
        self.current_file = pdf_path
        result = {
            'file_path': pdf_path,
            'file_name': os.path.basename(pdf_path),
            'fund_name': self._extract_fund_name(pdf_path),
            'year': self._extract_year(pdf_path),
            'tables': {},
            'text_content': '',
            'metadata': {}
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.pdf = pdf
                
                # 提取所有文本
                result['text_content'] = self._extract_all_text(pdf)
                
                # 提取关键表格
                result['tables'] = self._extract_key_tables(pdf)
                
                # 提取元数据
                result['metadata'] = self._extract_metadata(pdf)
                
                logger.info(f"解析完成: 找到 {len(result['tables'])} 个表格")
                
        except Exception as e:
            logger.error(f"解析失败: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _extract_fund_name(self, pdf_path: str) -> str:
        """从文件名提取基金名称"""
        filename = os.path.basename(pdf_path)
        # 移除年份和"年度报告"
        name = re.sub(r'\d{4}年年度报告\.pdf$', '', filename)
        return name.strip()
    
    def _extract_year(self, pdf_path: str) -> int:
        """从文件名提取年份"""
        filename = os.path.basename(pdf_path)
        match = re.search(r'(\d{4})年', filename)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_all_text(self, pdf) -> str:
        """提取所有文本内容"""
        text_parts = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return '\n'.join(text_parts)
    
    def _extract_key_tables(self, pdf) -> Dict[str, pd.DataFrame]:
        """
        提取关键财务表格
        
        返回:
            表格字典 {表格名称: DataFrame}
        """
        tables = {}
        
        # 遍历所有页面查找表格
        for page_num, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables()
            
            if not page_tables:
                continue
            
            # 分析每个表格
            for table_idx, table in enumerate(page_tables):
                if not table or len(table) < 2:
                    continue
                
                # 识别表格类型
                table_type = self._identify_table_type(table, page.extract_text())
                
                if table_type:
                    # 转换为DataFrame
                    df = self._table_to_dataframe(table)
                    
                    # 保存表格
                    table_key = f"{table_type}_page{page_num}"
                    tables[table_key] = df
                    
                    logger.info(f"找到表格: {table_type} (第{page_num}页)")
        
        return tables
    
    def _identify_table_type(self, table: List[List], page_text: str) -> Optional[str]:
        """
        识别表格类型（增强版）
        
        参数:
            table: 表格数据
            page_text: 页面文本
        
        返回:
            表格类型或None
        """
        # 获取表格标题（通常在第一行或表格上方文本中）
        first_row = ' '.join([str(cell) if cell else '' for cell in table[0]])
        
        # 获取表格前几行文本用于更准确的识别
        table_text = '\n'.join([' '.join([str(cell) if cell else '' for cell in row]) for row in table[:3]])
        combined_text = first_row + '\n' + page_text + '\n' + table_text
        
        # 资产负债表（主表）
        if any(keyword in combined_text for keyword in ['资产负债表', '资产和负债']):
            if '附注' not in combined_text[:50]:  # 前50字符内没有"附注"说明是主表
                return '资产负债表_主表'
        
        # 资产负债表（附注）
        if any(keyword in combined_text for keyword in ['资产负债表附注', '附注', '明细']):
            if any(keyword in combined_text for keyword in ['资产', '负债']):
                return '资产负债表_附注'
        
        # 利润表（主表）
        if any(keyword in combined_text for keyword in ['利润表', '收益表']):
            if '附注' not in combined_text[:50]:
                return '利润表_主表'
        
        # 利润表（附注）
        if any(keyword in combined_text for keyword in ['利润表附注', '收益表附注']):
            return '利润表_附注'
        
        # 现金流量表
        if any(keyword in combined_text for keyword in ['现金流量表', '现金流', '经营活动']):
            if '附注' not in combined_text[:50]:
                return '现金流量表_主表'
            else:
                return '现金流量表_附注'
        
        # 投资组合
        if any(keyword in combined_text for keyword in ['投资组合', '持仓明细', '股票投资', '债券投资']):
            return '投资组合'
        
        # 所有者权益变动表
        if any(keyword in combined_text for keyword in ['所有者权益', '净资产变动', '权益变动']):
            return '所有者权益变动表'
        
        # 通用附注表（根据"附注"关键词和表格内容判断）
        if '附注' in combined_text[:100]:
            if '资产' in combined_text:
                return '资产附注明细'
            elif '负债' in combined_text:
                return '负债附注明细'
            elif '收入' in combined_text or '费用' in combined_text:
                return '损益附注明细'
        
        return None
    
    def _table_to_dataframe(self, table: List[List]) -> pd.DataFrame:
        """
        将表格转换为DataFrame
        
        参数:
            table: 表格数据
        
        返回:
            DataFrame
        """
        if not table or len(table) < 2:
            return pd.DataFrame()
        
        # 使用第一行作为列名
        headers = [str(cell) if cell else f'Col{i}' for i, cell in enumerate(table[0])]
        
        # 数据行
        data_rows = table[1:]
        
        # 创建DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # 清理数据
        df = df.applymap(lambda x: str(x).strip() if x else '')
        
        return df
    
    def _extract_metadata(self, pdf) -> Dict:
        """提取元数据"""
        metadata = {
            'total_pages': len(pdf.pages),
            'pdf_metadata': pdf.metadata if hasattr(pdf, 'metadata') else {}
        }
        return metadata
    
    def extract_balance_sheet(self, tables: Dict) -> Optional[pd.DataFrame]:
        """
        提取资产负债表
        
        参数:
            tables: 表格字典
        
        返回:
            资产负债表DataFrame
        """
        for key, df in tables.items():
            if '资产负债表' in key:
                return df
        return None
    
    def extract_income_statement(self, tables: Dict) -> Optional[pd.DataFrame]:
        """
        提取利润表
        
        参数:
            tables: 表格字典
        
        返回:
            利润表DataFrame
        """
        for key, df in tables.items():
            if '利润表' in key:
                return df
        return None
    
    def extract_key_figures(self, text_content: str) -> Dict[str, float]:
        """
        从文本中提取关键数据
        
        参数:
            text_content: 文本内容
        
        返回:
            关键数据字典
        """
        figures = {}
        
        # 定义关键指标的正则表达式
        patterns = {
            '资产总计': r'资产总计[：:]\s*([\d,]+\.?\d*)',
            '负债总计': r'负债总计[：:]\s*([\d,]+\.?\d*)',
            '净资产': r'净资产[：:]\s*([\d,]+\.?\d*)',
            '营业收入': r'营业收入[：:]\s*([\d,]+\.?\d*)',
            '净利润': r'净利润[：:]\s*([\d,]+\.?\d*)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text_content)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    figures[key] = float(value_str)
                except ValueError:
                    pass
        
        return figures
    
    def parse_multiple_reports(self, pdf_paths: List[str]) -> Dict[str, Dict]:
        """
        批量解析多个年报
        
        参数:
            pdf_paths: PDF文件路径列表
        
        返回:
            解析结果字典 {文件名: 解析结果}
        """
        results = {}
        
        for pdf_path in pdf_paths:
            try:
                result = self.parse_pdf(pdf_path)
                results[result['file_name']] = result
            except Exception as e:
                logger.error(f"解析 {pdf_path} 失败: {str(e)}")
                results[os.path.basename(pdf_path)] = {'error': str(e)}
        
        return results


class TableExtractor:
    """表格提取器（辅助类）"""
    
    @staticmethod
    def extract_table_by_keyword(pdf_path: str, keyword: str) -> List[pd.DataFrame]:
        """
        根据关键词提取表格
        
        参数:
            pdf_path: PDF文件路径
            keyword: 关键词
        
        返回:
            匹配的表格列表
        """
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                
                if keyword in page_text:
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        if table and len(table) > 1:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            tables.append(df)
        
        return tables
    
    @staticmethod
    def extract_table_by_page(pdf_path: str, page_num: int) -> List[pd.DataFrame]:
        """
        提取指定页面的所有表格
        
        参数:
            pdf_path: PDF文件路径
            page_num: 页码（从1开始）
        
        返回:
            表格列表
        """
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            if 0 < page_num <= len(pdf.pages):
                page = pdf.pages[page_num - 1]
                page_tables = page.extract_tables()
                
                for table in page_tables:
                    if table and len(table) > 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append(df)
        
        return tables


def main():
    """测试函数"""
    # 测试解析器
    parser = AnnualReportParser()
    
    # 测试文件路径
    test_files = [
        '课题1/年报/易方达香港恒生综合小型股指数证券投资基金（LOF）年报/易方达香港恒生综合小型股指数证券投资基金（LOF）2024年年度报告.pdf'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            result = parser.parse_pdf(file_path)
            print(f"\n解析结果: {result['file_name']}")
            print(f"基金名称: {result['fund_name']}")
            print(f"年份: {result['year']}")
            print(f"总页数: {result['metadata']['total_pages']}")
            print(f"找到表格数: {len(result['tables'])}")
            print(f"表格类型: {list(result['tables'].keys())}")
        else:
            print(f"文件不存在: {file_path}")


if __name__ == '__main__':
    main()