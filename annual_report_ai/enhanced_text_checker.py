# -*- coding: utf-8 -*-
"""
增强的文字检查模块
支持PDF文本提取、错误检测、上下文展示和错误高亮
"""

import re
import jieba
import pdfplumber
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTextChecker:
    """增强的文字检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.grammar_patterns = self._init_grammar_patterns()
        self.terminology_dict = self._init_terminology_dict()
        self.expression_patterns = self._init_expression_patterns()
    
    def _init_grammar_patterns(self) -> List[Dict]:
        """初始化语法检查模式"""
        return [
            {
                'name': '标点符号错误',
                'pattern': r'[，。！？；：""''（）【】《》][\s]+[，。！？；：""''（）【】《》]',
                'description': '标点符号之间不应有空格'
            },
            # 注释掉数字格式错误检查，避免表格数据误报
            # {
            #     'name': '数字格式错误',
            #     'pattern': r'\d+\s+\d+',
            #     'description': '数字之间不应有空格'
            # },
            {
                'name': '中英文混排空格',
                'pattern': r'[\u4e00-\u9fa5][a-zA-Z]|[a-zA-Z][\u4e00-\u9fa5]',
                'description': '中英文之间建议添加空格'
            },
            {
                'name': '重复标点',
                'pattern': r'([，。！？；：])\1+',
                'description': '存在重复的标点符号'
            }
            # 注释掉括号不匹配检查，避免表格跨行括号误报
            # {
            #     'name': '括号不匹配',
            #     'pattern': r'（[^）]*$|^[^（]*）',
            #     'description': '括号不匹配'
            # }
        ]
    
    def _init_terminology_dict(self) -> Dict[str, List[str]]:
        """初始化术语字典"""
        return {
            '基金': ['基金', '基金产品'],
            '净值': ['净值', '基金净值', '单位净值'],
            '份额': ['份额', '基金份额'],
            '收益': ['收益', '投资收益', '收益率'],
            '风险': ['风险', '投资风险', '市场风险'],
            '资产': ['资产', '净资产', '资产总额'],
            '负债': ['负债', '负债总额'],
            '利润': ['利润', '净利润', '利润总额']
        }
    
    def _init_expression_patterns(self) -> List[Dict]:
        """初始化表述检查模式 - 仅检查语病"""
        return [
            # 注释掉口语化和模糊表述检查
            # {
            #     'name': '口语化表述',
            #     'patterns': ['很多', '非常', '特别', '十分', '极其'],
            #     'description': '建议使用更正式的表述'
            # },
            # {
            #     'name': '模糊表述',
            #     'patterns': ['大概', '可能', '也许', '差不多', '基本上'],
            #     'description': '财务报告应使用准确表述'
            # },
            {
                'name': '语病检查',
                'patterns': [
                    '的的', '了了', '是是',  # 重复词
                    '不不', '没没', '无无',
                ],
                'description': '存在语病或重复用词'
            }
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, any]:
        """
        从PDF文件提取文本
        
        参数:
            pdf_path: PDF文件路径
        
        返回:
            包含文本内容和页面信息的字典
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_text = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_text.append({
                            'page_num': page_num,
                            'text': text,
                            'paragraphs': self._split_into_paragraphs(text)
                        })
                
                full_text = '\n\n'.join([p['text'] for p in pages_text])
                
                return {
                    'full_text': full_text,
                    'pages': pages_text,
                    'total_pages': len(pdf.pages),
                    'total_chars': len(full_text)
                }
        
        except Exception as e:
            logger.error(f"提取PDF文本失败: {str(e)}")
            raise
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文本分割成段落"""
        # 按双换行符或单换行符分割
        paragraphs = re.split(r'\n\s*\n|\n', text)
        # 过滤空段落
        return [p.strip() for p in paragraphs if p.strip()]
    
    def check_text_with_context(self, text_data: Dict) -> List[Dict]:
        """
        检查文本并返回带上下文的错误信息
        
        参数:
            text_data: 从PDF提取的文本数据
        
        返回:
            错误列表，每个错误包含上下文信息
        """
        all_issues = []
        
        # 遍历每一页
        for page_data in text_data['pages']:
            page_num = page_data['page_num']
            paragraphs = page_data['paragraphs']
            
            # 遍历每个段落
            for para_idx, paragraph in enumerate(paragraphs):
                # 跳过表格内容（简单判断：包含多个连续空格或制表符的段落）
                if self._is_table_content(paragraph):
                    continue
                
                # 语法检查
                grammar_issues = self._check_grammar_with_context(
                    paragraph, page_num, para_idx
                )
                all_issues.extend(grammar_issues)
                
                # 术语检查 - 已禁用
                # terminology_issues = self._check_terminology_with_context(
                #     paragraph, page_num, para_idx
                # )
                # all_issues.extend(terminology_issues)
                
                # 表述检查（仅检查语病）
                expression_issues = self._check_expression_with_context(
                    paragraph, page_num, para_idx
                )
                all_issues.extend(expression_issues)
        
        return all_issues
    
    def _is_table_content(self, paragraph: str) -> bool:
        """
        判断段落是否为表格内容
        
        参数:
            paragraph: 段落文本
        
        返回:
            是否为表格内容
        """
        # 判断标准：
        # 1. 包含多个连续空格（表格列分隔）
        # 2. 包含制表符
        # 3. 数字和空格的比例较高
        # 4. 包含大量括号（表格中的数据）
        # 5. 短段落且包含多个数字
        
        if not paragraph:
            return False
        
        # 检查是否包含多个连续空格（2个或以上，降低阈值）
        if re.search(r'\s{2,}', paragraph):
            return True
        
        # 检查是否包含制表符
        if '\t' in paragraph:
            return True
        
        # 统计各种字符
        digit_count = sum(c.isdigit() for c in paragraph)
        space_count = sum(c.isspace() for c in paragraph)
        bracket_count = paragraph.count('（') + paragraph.count('）') + paragraph.count('(') + paragraph.count(')')
        comma_count = paragraph.count(',')
        total_chars = len(paragraph)
        
        if total_chars > 0:
            digit_ratio = digit_count / total_chars
            space_ratio = space_count / total_chars
            bracket_ratio = bracket_count / total_chars
            
            # 如果数字占比>25%且空格占比>15%，可能是表格（降低阈值）
            if digit_ratio > 0.25 and space_ratio > 0.15:
                return True
            
            # 如果括号数量较多（>3个）且数字占比>20%，可能是表格
            if bracket_count > 3 and digit_ratio > 0.2:
                return True
            
            # 如果包含大量逗号（数字分隔符）且数字占比高，可能是表格
            if comma_count > 2 and digit_ratio > 0.3:
                return True
        
        # 短段落（<50字符）且包含多个数字和空格，可能是表格行
        if total_chars < 50 and digit_count > 5 and space_count > 3:
            return True
        
        # 检查是否包含典型的表格模式：数字+空格+数字
        if re.search(r'\d+[\s,]+\d+[\s,]+\d+', paragraph):
            return True
        
        return False
    
    def _check_grammar_with_context(self, paragraph: str, page_num: int,
                                    para_idx: int) -> List[Dict]:
        """检查语法错误并返回上下文"""
        issues = []
        
        for pattern_dict in self.grammar_patterns:
            pattern = pattern_dict['pattern']
            matches = re.finditer(pattern, paragraph)
            
            for match in matches:
                start, end = match.span()
                
                # 使用完整段落作为上下文
                context = paragraph
                
                # 计算错误在完整段落中的位置
                error_start_in_context = start
                error_end_in_context = end
                
                issues.append({
                    'type': '语法问题',
                    'issue_name': pattern_dict['name'],
                    'description': pattern_dict['description'],
                    'page_num': page_num,
                    'paragraph_index': para_idx,
                    'matched_text': match.group(),
                    'context': context,
                    'error_position': (error_start_in_context, error_end_in_context),
                    'full_paragraph': paragraph
                })
        
        return issues
    
    def _check_terminology_with_context(self, paragraph: str, page_num: int,
                                       para_idx: int) -> List[Dict]:
        """检查术语一致性并返回上下文"""
        issues = []
        
        # 统计段落中使用的术语
        term_usage = {}
        for standard_term, variants in self.terminology_dict.items():
            found_variants = []
            for variant in variants:
                if variant in paragraph:
                    found_variants.append(variant)
            
            if len(found_variants) > 1:
                # 发现同一概念使用了多个不同术语
                term_usage[standard_term] = found_variants
        
        # 为每个不一致的术语创建问题记录
        for standard_term, variants in term_usage.items():
            # 找到所有变体的位置
            for variant in variants:
                for match in re.finditer(re.escape(variant), paragraph):
                    start, end = match.span()
                    
                    # 使用完整段落作为上下文
                    context = paragraph
                    
                    # 计算错误在完整段落中的位置
                    error_start_in_context = start
                    error_end_in_context = end
                    
                    issues.append({
                        'type': '术语问题',
                        'issue_name': '术语不一致',
                        'description': f'同一段落中"{standard_term}"使用了多个表述: {", ".join(variants)}',
                        'page_num': page_num,
                        'paragraph_index': para_idx,
                        'matched_text': variant,
                        'context': context,
                        'error_position': (error_start_in_context, error_end_in_context),
                        'full_paragraph': paragraph,
                        'suggestion': f'建议统一使用: {variants[0]}'
                    })
        
        return issues
    
    def _check_expression_with_context(self, paragraph: str, page_num: int,
                                      para_idx: int) -> List[Dict]:
        """检查表述规范性并返回上下文"""
        issues = []
        
        for pattern_dict in self.expression_patterns:
            for pattern_text in pattern_dict['patterns']:
                for match in re.finditer(re.escape(pattern_text), paragraph):
                    start, end = match.span()
                    
                    # 使用完整段落作为上下文
                    context = paragraph
                    
                    # 计算错误在完整段落中的位置
                    error_start_in_context = start
                    error_end_in_context = end
                    
                    issues.append({
                        'type': '表述问题',
                        'issue_name': pattern_dict['name'],
                        'description': pattern_dict['description'],
                        'page_num': page_num,
                        'paragraph_index': para_idx,
                        'matched_text': match.group(),
                        'context': context,
                        'error_position': (error_start_in_context, error_end_in_context),
                        'full_paragraph': paragraph
                    })
        
        return issues
    
    def highlight_error_in_text(self, text: str, error_start: int, 
                               error_end: int) -> str:
        """
        在文本中高亮错误位置
        
        参数:
            text: 原文本
            error_start: 错误开始位置
            error_end: 错误结束位置
        
        返回:
            带高亮标记的HTML文本
        """
        before = text[:error_start]
        error = text[error_start:error_end]
        after = text[error_end:]
        
        return f'{before}<mark style="background-color: #ffcccc; font-weight: bold;">{error}</mark>{after}'


def main():
    """测试函数"""
    checker = EnhancedTextChecker()
    
    # 测试文本检查
    test_text = {
        'full_text': '测试文本',
        'pages': [{
            'page_num': 1,
            'text': '本基金的净值很多，收益率非常高。基金份额总计为1000万份。',
            'paragraphs': ['本基金的净值很多，收益率非常高。基金份额总计为1000万份。']
        }],
        'total_pages': 1,
        'total_chars': 100
    }
    
    issues = checker.check_text_with_context(test_text)
    print(f"发现 {len(issues)} 个问题:")
    for issue in issues:
        print(f"\n{issue['type']} - {issue['issue_name']}")
        print(f"  页码: {issue['page_num']}")
        print(f"  错误文本: {issue['matched_text']}")
        print(f"  上下文: {issue['context']}")


if __name__ == '__main__':
    main()