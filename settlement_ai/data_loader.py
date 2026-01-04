# -*- coding: utf-8 -*-
"""
标的交收AI助手 - 数据加载器
加载和处理TradeFile数据
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SettlementDataLoader:
    """交收数据加载器"""
    
    def __init__(self, data_base_path: str = "自动化课题数据/自动化课题数据"):
        """
        初始化数据加载器
        
        Args:
            data_base_path: 数据基础路径
        """
        self.data_path = Path(data_base_path)
        self.trade_file_path = self.data_path / "Trade file"
        self.testing_data_path = self.data_path / "Testing Data"
        
        # 数据容器
        self.all_trades = None
        self.accounts = []
        self.dates = []
        
    def scan_available_data(self) -> Tuple[List[str], List[str]]:
        """
        扫描可用的账户和日期
        
        Returns:
            (账户列表, 日期列表)
        """
        accounts = []
        dates_set = set()
        
        if not self.trade_file_path.exists():
            logger.error(f"Trade file路径不存在: {self.trade_file_path}")
            return [], []
        
        # 扫描所有账户文件夹
        for account_folder in self.trade_file_path.iterdir():
            if account_folder.is_dir() and not account_folder.name.startswith('.'):
                accounts.append(account_folder.name)
                
                # 扫描该账户下的所有文件
                for file in account_folder.iterdir():
                    if file.suffix == '.xlsx' and file.name.startswith('TBLT_'):
                        # 提取日期：TBLT_ACCOUNT_20240709.xlsx
                        parts = file.stem.split('_')
                        if len(parts) >= 3:
                            date_str = parts[-1]
                            if len(date_str) == 8 and date_str.isdigit():
                                dates_set.add(date_str)
        
        self.accounts = sorted(accounts)
        self.dates = sorted(list(dates_set))
        
        logger.info(f"扫描到 {len(self.accounts)} 个账户，{len(self.dates)} 个交易日期")
        
        return self.accounts, self.dates
    
    def load_trade_file(self, account: str, date: str, sheet_name: str = 'Fundcode') -> pd.DataFrame:
        """
        加载单个TradeFile
        
        Args:
            account: 账户名称
            date: 日期字符串 (yyyymmdd)
            sheet_name: 工作表名称 ('Fundcode' 或 'Fundcode_Repo')
        
        Returns:
            DataFrame
        """
        file_path = self.trade_file_path / account / f"TBLT_{account}_{date}.xlsx"
        
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            
            # 清理列名：去除前后空格
            df.columns = df.columns.str.strip()
            
            # 添加元数据列
            df['Account'] = account
            df['Date'] = date
            df['Sheet'] = sheet_name
            
            # 标准化日期格式
            date_columns = ['Trade Date', 'As of Date', 'Settlement Date', 'Repo Termination Date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # 标准化金额格式
            amount_columns = ['Amount (Pennies)', 'Accrued Interest',
                            'Settlement Amount', 'Full Net Amount', 'Trade price']
            for col in amount_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"加载文件失败 {file_path}: {e}")
            return pd.DataFrame()
    
    def load_all_trades(self, accounts: List[str] = None, 
                       dates: List[str] = None,
                       include_repo: bool = True) -> pd.DataFrame:
        """
        加载所有交易数据
        
        Args:
            accounts: 要加载的账户列表（None表示全部）
            dates: 要加载的日期列表（None表示全部）
            include_repo: 是否包含Fundcode_Repo工作表
        
        Returns:
            合并后的DataFrame
        """
        if accounts is None:
            accounts = self.accounts
        if dates is None:
            dates = self.dates
        
        all_data = []
        
        for account in accounts:
            for date in dates:
                # 加载Fundcode工作表
                df_fundcode = self.load_trade_file(account, date, 'Fundcode')
                if not df_fundcode.empty:
                    all_data.append(df_fundcode)
                
                # 加载Fundcode_Repo工作表
                if include_repo:
                    df_repo = self.load_trade_file(account, date, 'Fundcode_Repo')
                    if not df_repo.empty:
                        all_data.append(df_repo)
        
        if all_data:
            self.all_trades = pd.concat(all_data, ignore_index=True)
            logger.info(f"加载完成，共 {len(self.all_trades)} 条交易记录")
        else:
            self.all_trades = pd.DataFrame()
            logger.warning("未加载到任何交易数据")
        
        return self.all_trades
    
    def get_match_statistics(self) -> Dict:
        """
        获取匹配统计信息
        
        Returns:
            统计字典
        """
        if self.all_trades is None or self.all_trades.empty:
            return {}
        
        total = len(self.all_trades)
        matched = (self.all_trades['Matched?'] == 'Y').sum()
        unmatched = total - matched
        match_rate = (matched / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': match_rate
        }
    
    def get_duplicate_statistics(self) -> Dict:
        """
        获取重复交易统计
        
        Returns:
            统计字典
        """
        if self.all_trades is None or self.all_trades.empty:
            return {}
        
        total = len(self.all_trades)
        duplicated = (self.all_trades['Duplicated?'] == 'Y').sum()
        duplicate_rate = (duplicated / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'duplicated': duplicated,
            'duplicate_rate': duplicate_rate
        }
    
    def get_transaction_type_distribution(self) -> pd.Series:
        """
        获取交易类型分布
        
        Returns:
            Series with counts
        """
        if self.all_trades is None or self.all_trades.empty:
            return pd.Series()
        
        return self.all_trades['Blotter Transaction Type'].value_counts()
    
    def get_currency_distribution(self) -> pd.Series:
        """
        获取货币分布
        
        Returns:
            Series with counts
        """
        if self.all_trades is None or self.all_trades.empty:
            return pd.Series()
        
        return self.all_trades['Currency'].value_counts()
    
    def filter_trades(self, 
                     account: str = None,
                     date: str = None,
                     matched_only: bool = False,
                     duplicated_only: bool = False,
                     transaction_type: str = None) -> pd.DataFrame:
        """
        筛选交易数据
        
        Args:
            account: 账户名称
            date: 日期
            matched_only: 只返回已匹配的
            duplicated_only: 只返回重复的
            transaction_type: 交易类型
        
        Returns:
            筛选后的DataFrame
        """
        if self.all_trades is None or self.all_trades.empty:
            return pd.DataFrame()
        
        df = self.all_trades.copy()
        
        if account:
            df = df[df['Account'] == account]
        
        if date:
            df = df[df['Date'] == date]
        
        if matched_only:
            df = df[df['Matched?'] == 'Y']
        
        if duplicated_only:
            df = df[df['Duplicated?'] == 'Y']
        
        if transaction_type:
            df = df[df['Blotter Transaction Type'] == transaction_type]
        
        return df
    
    def load_testing_data(self, date: str, file_type: str) -> pd.DataFrame:
        """
        加载Testing Data文件
        
        Args:
            date: 日期字符串 (yyyymmdd)
            file_type: 文件类型 ('confirm', 'bbg', 'match')
        
        Returns:
            DataFrame
        """
        if file_type == 'confirm':
            file_path = self.testing_data_path / f"Confirm_TBLT_OPS_{date}.xlsx"
        elif file_type == 'bbg':
            file_path = self.testing_data_path / f"BBG TH TBLT_OPS_{date}.xlsx"
        elif file_type == 'match':
            date_obj = datetime.strptime(date, '%Y%m%d')
            match_date = date_obj.strftime('%Y-%b-%d')
            file_path = self.testing_data_path / f"Combined Match Agreed Allocations {match_date}.xlsx"
        else:
            logger.error(f"未知的文件类型: {file_type}")
            return pd.DataFrame()
        
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return pd.DataFrame()
        
        try:
            if file_type == 'match':
                # Combined Match文件需要跳过标题行
                df = pd.read_excel(file_path, header=5, engine='openpyxl')
            else:
                df = pd.read_excel(file_path, engine='openpyxl')
            
            return df
            
        except Exception as e:
            logger.error(f"加载文件失败 {file_path}: {e}")
            return pd.DataFrame()


if __name__ == '__main__':
    # 测试代码
    loader = SettlementDataLoader()
    accounts, dates = loader.scan_available_data()
    print(f"账户: {accounts[:5]}...")
    print(f"日期: {dates}")
    
    # 加载所有数据
    df = loader.load_all_trades(dates=['20240709'])
    print(f"\n加载了 {len(df)} 条交易")
    print(f"\n匹配统计: {loader.get_match_statistics()}")
    print(f"\n重复统计: {loader.get_duplicate_statistics()}")