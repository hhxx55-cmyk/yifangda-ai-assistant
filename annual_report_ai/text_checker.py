# -*- coding: utf-8 -*-
"""
文字检查模块
检查年报文字内容的语法、术语一致性和表述规范性
"""

import re
import jieba
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextChecker:
    """文字检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.grammar_rules = self._load_grammar_rules()
        self.terminology_dict = self._load_terminology_dict()
        self.expression_rules = self._load_expression_rules()
    
    def check_text(self, text: str) -> Dict:
        """
        检查文本内容
        
        参数:
            text: 文本内容
        
        返回:
            检查结果字典
        """
        logger.info("开始文字检查...")
        
        results = {
            'grammar_issues': self.check_grammar(text),
            'terminology_issues': self.check_terminology(text),
            'expression_issues': self.check_expression(text),
            'statistics': self._calculate_statistics(text)
        }
        
        total_issues = (len(results['grammar_issues']) + 
                       len(results['terminology_issues']) + 
                       len(results['expression_issues']))
        
        logger.info(f"检查完成: 发现 {total_issues} 个问题")
        
        return results
    
    def check_grammar(self, text: str) -> List[Dict]:
        """
        检查语法问题
        
        参数:
            text: 文本内容
        
        返回:
            问题列表
        """
        issues = []
        
        for rule in self.grammar_rules:
            pattern = rule['pattern']
            issue_type = rule['type']
            description = rule['description']
            
            matches = re.finditer(pattern, text)
            for match in matches:
                # 获取上下文
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end]
                
                issues.append({
                    'type': '语法问题',
                    'issue_type': issue_type,
                    'description': description,
                    'matched_text': match.group(),
                    'context': context,
                    'position': match.start(),
                    'severity': 'Medium'
                })
        
        return issues
    
    def check_terminology(self, text: str) -> List[Dict]:
        """
        检查术语一致性
        
        参数:
            text: 文本内容
        
        返回:
            问题列表
        """
        issues = []
        
        for term, config in self.terminology_dict.items():
            standard = config['standard']
            synonyms = config.get('synonyms', [])
            avoid = config.get('avoid', [])
            
            # 检查是否使用了应避免的术语
            for avoid_term in avoid:
                if avoid_term in text:
                    # 统计出现次数
                    count = text.count(avoid_term)
                    
                    issues.append({
                        'type': '术语不一致',
                        'term': avoid_term,
                        'standard': standard,
                        'description': f'应使用"{standard}"而非"{avoid_term}"',
                        'count': count,
                        'severity': 'Medium'
                    })
            
            # 检查同义词混用
            used_terms = []
            for syn in synonyms:
                if syn in text:
                    used_terms.append(syn)
            
            if len(used_terms) > 1:
                issues.append({
                    'type': '术语不一致',
                    'term': term,
                    'standard': standard,
                    'description': f'同时使用了多个同义词: {", ".join(used_terms)}',
                    'used_terms': used_terms,
                    'severity': 'High'
                })
        
        return issues
    
    def check_expression(self, text: str) -> List[Dict]:
        """
        检查表述规范性
        
        参数:
            text: 文本内容
        
        返回:
            问题列表
        """
        issues = []
        
        for rule in self.expression_rules:
            context = rule['context']
            standard = rule['standard']
            check_type = rule.get('check', '')
            
            # 根据不同的检查类型执行检查
            if 'pattern' in rule:
                pattern = rule['pattern']
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    issues.append({
                        'type': '表述不规范',
                        'context': context,
                        'matched_text': match.group(),
                        'standard': standard,
                        'description': rule.get('description', ''),
                        'severity': 'Low'
                    })
        
        return issues
    
    def _load_grammar_rules(self) -> List[Dict]:
        """加载语法检查规则"""
        return [
            {
                'type': '重复标点',
                'pattern': r'[。，、；：！？]{2,}',
                'description': '存在重复的标点符号'
            },
            {
                'type': '空格问题',
                'pattern': r'[\u4e00-\u9fa5]\s+[\u4e00-\u9fa5]',
                'description': '中文之间不应有空格'
            },
            {
                'type': '数字格式',
                'pattern': r'\d+\.\d+\.\d+',
                'description': '数字格式可能有误'
            },
            {
                'type': '括号不匹配',
                'pattern': r'\([^)]*$|^[^(]*\)',
                'description': '括号可能不匹配'
            },
            {
                'type': '引号不匹配',
                'pattern': r'"[^"]*$|^[^"]*"',
                'description': '引号可能不匹配'
            }
        ]
    
    def _load_terminology_dict(self) -> Dict:
        """加载术语字典"""
        return {
            '净资产': {
                'standard': '净资产',
                'synonyms': ['净资产', '所有者权益', '基金净值'],
                'avoid': ['该基金净值', '基金资产净值'],
                'rule': '全文必须使用统一术语'
            },
            '本基金': {
                'standard': '本基金',
                'synonyms': ['本基金'],
                'avoid': ['该基金', '这个基金', '此基金', '这只基金'],
                'rule': '使用标准表述'
            },
            '报告期': {
                'standard': '报告期',
                'synonyms': ['报告期', '本报告期'],
                'avoid': ['这个期间', '该期间'],
                'rule': '使用标准表述'
            },
            '基金管理人': {
                'standard': '基金管理人',
                'synonyms': ['基金管理人', '管理人'],
                'avoid': ['基金公司', '管理公司'],
                'rule': '使用标准表述'
            },
            '基金托管人': {
                'standard': '基金托管人',
                'synonyms': ['基金托管人', '托管人'],
                'avoid': ['托管银行', '托管方'],
                'rule': '使用标准表述'
            }
        }
    
    def _load_expression_rules(self) -> List[Dict]:
        """加载表述规范规则"""
        return [
            {
                'context': '日期格式',
                'standard': 'YYYY年MM月DD日',
                'pattern': r'\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}',
                'description': '日期格式应为"YYYY年MM月DD日"'
            },
            {
                'context': '金额单位',
                'standard': '元',
                'pattern': r'[\d,]+块|[\d,]+圆',
                'description': '金额单位应使用"元"'
            },
            {
                'context': '百分比',
                'standard': '%',
                'pattern': r'\d+percent|\d+百分之',
                'description': '百分比应使用"%"符号'
            }
        ]
    
    def _calculate_statistics(self, text: str) -> Dict:
        """计算文本统计信息"""
        return {
            'total_chars': len(text),
            'total_words': len(jieba.lcut(text)),
            'total_sentences': len(re.findall(r'[。！？]', text)),
            'total_paragraphs': len(text.split('\n\n'))
        }
    
    def generate_suggestions(self, check_results: Dict) -> List[Dict]:
        """
        生成优化建议
        
        参数:
            check_results: 检查结果
        
        返回:
            建议列表
        """
        suggestions = []
        
        # 语法问题建议
        grammar_issues = check_results['grammar_issues']
        if grammar_issues:
            suggestions.append({
                'category': '语法优化',
                'priority': 'High' if len(grammar_issues) > 10 else 'Medium',
                'issue_count': len(grammar_issues),
                'suggestion': f'发现{len(grammar_issues)}处语法问题，建议逐一修正',
                'details': [
                    f"{issue['issue_type']}: {issue['matched_text']}"
                    for issue in grammar_issues[:5]
                ]
            })
        
        # 术语问题建议
        terminology_issues = check_results['terminology_issues']
        if terminology_issues:
            suggestions.append({
                'category': '术语统一',
                'priority': 'High',
                'issue_count': len(terminology_issues),
                'suggestion': f'发现{len(terminology_issues)}处术语不一致，建议统一使用标准术语',
                'details': [
                    f"{issue['term']} → {issue['standard']}"
                    for issue in terminology_issues[:5]
                ]
            })
        
        # 表述问题建议
        expression_issues = check_results['expression_issues']
        if expression_issues:
            suggestions.append({
                'category': '表述规范',
                'priority': 'Medium',
                'issue_count': len(expression_issues),
                'suggestion': f'发现{len(expression_issues)}处表述不规范，建议按标准格式修改',
                'details': [
                    f"{issue['context']}: {issue['matched_text']} → {issue['standard']}"
                    for issue in expression_issues[:5]
                ]
            })
        
        return suggestions


class TextComparator:
    """文本对比器（用于跨年度文本对比）- 增强版"""
    
    @staticmethod
    def compare_texts(text1: str, text2: str,
                     section_name: str = '') -> Dict:
        """
        对比两段文本（增强版）
        
        参数:
            text1: 文本1（当前年）
            text2: 文本2（上一年）
            section_name: 章节名称
        
        返回:
            对比结果
        """
        # 1. 计算多种相似度指标
        word_similarity = TextComparator._calculate_word_similarity(text1, text2)
        char_similarity = TextComparator._calculate_char_similarity(text1, text2)
        structure_similarity = TextComparator._calculate_structure_similarity(text1, text2)
        
        # 综合相似度（加权平均）
        overall_similarity = (word_similarity * 0.5 +
                            char_similarity * 0.3 +
                            structure_similarity * 0.2)
        
        # 2. 查找详细差异
        differences = TextComparator._find_detailed_differences(text1, text2)
        
        # 3. 识别关键变化
        key_changes = TextComparator._identify_key_changes(text1, text2)
        
        # 4. 分析变化类型
        change_analysis = TextComparator._analyze_changes(text1, text2)
        
        return {
            'section': section_name,
            'similarity': {
                'overall': overall_similarity,
                'word_level': word_similarity,
                'char_level': char_similarity,
                'structure_level': structure_similarity
            },
            'differences': differences,
            'key_changes': key_changes,
            'change_analysis': change_analysis,
            'text1_length': len(text1),
            'text2_length': len(text2),
            'text1_words': len(jieba.lcut(text1)),
            'text2_words': len(jieba.lcut(text2))
        }
    
    @staticmethod
    def _calculate_word_similarity(text1: str, text2: str) -> float:
        """计算词级别相似度（Jaccard相似度）"""
        words1 = set(jieba.lcut(text1))
        words2 = set(jieba.lcut(text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def _calculate_char_similarity(text1: str, text2: str) -> float:
        """计算字符级别相似度（编辑距离）"""
        # 使用简化的编辑距离算法
        if not text1 or not text2:
            return 0.0
        
        # 限制长度以提高性能
        max_len = 1000
        t1 = text1[:max_len]
        t2 = text2[:max_len]
        
        # 计算编辑距离
        distance = TextComparator._levenshtein_distance(t1, t2)
        max_len = max(len(t1), len(t2))
        
        return 1 - (distance / max_len) if max_len > 0 else 0.0
    
    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return TextComparator._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def _calculate_structure_similarity(text1: str, text2: str) -> float:
        """计算结构相似度（段落、句子结构）"""
        # 按段落分割
        paragraphs1 = [p.strip() for p in text1.split('\n') if p.strip()]
        paragraphs2 = [p.strip() for p in text2.split('\n') if p.strip()]
        
        # 段落数量相似度
        para_count_sim = 1 - abs(len(paragraphs1) - len(paragraphs2)) / max(len(paragraphs1), len(paragraphs2), 1)
        
        # 句子数量相似度
        sentences1 = len(re.findall(r'[。！？]', text1))
        sentences2 = len(re.findall(r'[。！？]', text2))
        sent_count_sim = 1 - abs(sentences1 - sentences2) / max(sentences1, sentences2, 1)
        
        return (para_count_sim + sent_count_sim) / 2
    
    @staticmethod
    def _find_detailed_differences(text1: str, text2: str) -> List[Dict]:
        """查找详细差异"""
        differences = []
        
        # 1. 长度差异
        len_diff = abs(len(text1) - len(text2))
        if len_diff > 100:
            differences.append({
                'type': '长度差异',
                'description': f'文本长度相差{len_diff}字符',
                'severity': 'High' if len_diff > 1000 else 'Medium'
            })
        
        # 2. 词汇差异
        words1 = set(jieba.lcut(text1))
        words2 = set(jieba.lcut(text2))
        
        added_words = words1 - words2
        removed_words = words2 - words1
        
        if added_words:
            differences.append({
                'type': '新增词汇',
                'description': f'新增{len(added_words)}个词汇',
                'examples': list(added_words)[:10],
                'severity': 'Low'
            })
        
        if removed_words:
            differences.append({
                'type': '删除词汇',
                'description': f'删除{len(removed_words)}个词汇',
                'examples': list(removed_words)[:10],
                'severity': 'Low'
            })
        
        # 3. 数字差异
        numbers1 = set(re.findall(r'\d+\.?\d*', text1))
        numbers2 = set(re.findall(r'\d+\.?\d*', text2))
        
        if numbers1 != numbers2:
            differences.append({
                'type': '数字差异',
                'description': '文本中的数字发生变化',
                'severity': 'High'
            })
        
        # 4. 段落结构差异
        para_count1 = len([p for p in text1.split('\n') if p.strip()])
        para_count2 = len([p for p in text2.split('\n') if p.strip()])
        
        if abs(para_count1 - para_count2) > 2:
            differences.append({
                'type': '结构差异',
                'description': f'段落数量从{para_count2}变为{para_count1}',
                'severity': 'Medium'
            })
        
        return differences
    
    @staticmethod
    def _identify_key_changes(text1: str, text2: str) -> List[str]:
        """识别关键变化"""
        key_changes = []
        
        # 识别关键词变化
        key_terms = ['基金', '投资', '收益', '风险', '管理', '策略', '业绩', '净值']
        
        for term in key_terms:
            count1 = text1.count(term)
            count2 = text2.count(term)
            
            if abs(count1 - count2) > 3:
                key_changes.append(f'"{term}"出现次数从{count2}次变为{count1}次')
        
        return key_changes
    
    @staticmethod
    def _analyze_changes(text1: str, text2: str) -> Dict:
        """分析变化类型"""
        return {
            'is_major_change': TextComparator._calculate_word_similarity(text1, text2) < 0.7,
            'is_minor_change': 0.7 <= TextComparator._calculate_word_similarity(text1, text2) < 0.9,
            'is_minimal_change': TextComparator._calculate_word_similarity(text1, text2) >= 0.9,
            'change_magnitude': 'High' if TextComparator._calculate_word_similarity(text1, text2) < 0.7
                              else 'Medium' if TextComparator._calculate_word_similarity(text1, text2) < 0.9
                              else 'Low'
        }
    
    @staticmethod
    def compare_sections(report1: Dict, report2: Dict,
                        section_keywords: List[str]) -> List[Dict]:
        """
        对比年报中的特定章节
        
        参数:
            report1: 年报1
            report2: 年报2
            section_keywords: 章节关键词列表
        
        返回:
            章节对比结果列表
        """
        results = []
        
        text1 = report1.get('text_content', '')
        text2 = report2.get('text_content', '')
        
        for keyword in section_keywords:
            # 提取包含关键词的段落
            section1 = TextComparator._extract_section(text1, keyword)
            section2 = TextComparator._extract_section(text2, keyword)
            
            if section1 and section2:
                comparison = TextComparator.compare_texts(section1, section2, keyword)
                results.append(comparison)
        
        return results
    
    @staticmethod
    def _extract_section(text: str, keyword: str, context_size: int = 500) -> str:
        """提取包含关键词的章节"""
        # 查找关键词位置
        pos = text.find(keyword)
        
        if pos == -1:
            return ''
        
        # 提取前后文
        start = max(0, pos - context_size)
        end = min(len(text), pos + len(keyword) + context_size)
        
        return text[start:end]


def main():
    """测试函数"""
    checker = TextChecker()
    
    # 测试文本
    test_text = """
    本基金在报告期内的投资策略保持稳健。该基金的净资产为1000000元。
    报告期内，，基金管理人严格遵守相关法律法规。。
    截至2024-12-31，基金净值为1.234元。
    """
    
    # 执行检查
    results = checker.check_text(test_text)
    
    print(f"\n检查结果:")
    print(f"语法问题: {len(results['grammar_issues'])}个")
    print(f"术语问题: {len(results['terminology_issues'])}个")
    print(f"表述问题: {len(results['expression_issues'])}个")
    
    # 生成建议
    suggestions = checker.generate_suggestions(results)
    print(f"\n优化建议: {len(suggestions)}条")
    for sug in suggestions:
        print(f"- {sug['category']}: {sug['suggestion']}")


if __name__ == '__main__':
    main()