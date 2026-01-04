# -*- coding: utf-8 -*-
"""
年报数据下载器
从易方达官网自动下载年报PDF文件
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnnualReportDownloader:
    """年报下载器"""
    
    def __init__(self, output_dir="annual_reports"):
        """
        初始化下载器
        
        参数:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.base_url = "https://www.efunds.com.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def download_fund_reports(self, fund_code, fund_name, years=[2022, 2023, 2024]):
        """
        下载指定基金的年报
        
        参数:
            fund_code: 基金代码
            fund_name: 基金名称
            years: 年份列表
        
        返回:
            下载成功的文件列表
        """
        logger.info(f"开始下载基金 {fund_code} ({fund_name}) 的年报...")
        
        # 创建基金目录
        fund_dir = os.path.join(self.output_dir, fund_code)
        os.makedirs(fund_dir, exist_ok=True)
        
        downloaded_files = []
        
        for year in years:
            try:
                # 尝试下载年报
                file_path = self._download_single_report(
                    fund_code, fund_name, year, fund_dir
                )
                
                if file_path:
                    downloaded_files.append(file_path)
                    logger.info(f"✓ 成功下载: {os.path.basename(file_path)}")
                else:
                    logger.warning(f"✗ 未找到 {year} 年报")
                
                # 延迟避免请求过快
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"✗ 下载 {year} 年报失败: {str(e)}")
        
        logger.info(f"完成！共下载 {len(downloaded_files)}/{len(years)} 个文件")
        return downloaded_files
    
    def _download_single_report(self, fund_code, fund_name, year, output_dir):
        """
        下载单个年报
        
        参数:
            fund_code: 基金代码
            fund_name: 基金名称
            year: 年份
            output_dir: 输出目录
        
        返回:
            文件路径或None
        """
        # 构建文件名
        filename = f"{fund_code}_{year}年度报告.pdf"
        file_path = os.path.join(output_dir, filename)
        
        # 如果文件已存在，跳过
        if os.path.exists(file_path):
            logger.info(f"文件已存在，跳过: {filename}")
            return file_path
        
        # 方法1: 尝试通过产品页面查找
        report_url = self._find_report_url_from_product_page(fund_code, year)
        
        # 方法2: 如果方法1失败，尝试通过信息披露页面
        if not report_url:
            report_url = self._find_report_url_from_disclosure_page(fund_code, year)
        
        # 方法3: 如果都失败，尝试直接构建URL
        if not report_url:
            report_url = self._construct_direct_url(fund_code, year)
        
        # 下载文件
        if report_url:
            return self._download_file(report_url, file_path)
        
        return None
    
    def _find_report_url_from_product_page(self, fund_code, year):
        """从产品页面查找年报URL"""
        try:
            # 构建产品页面URL
            product_url = f"{self.base_url}/products/{fund_code}"
            
            response = self.session.get(product_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找年报链接
            # 通常在"信息披露"或"公告"栏目
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 匹配年报关键词
                if f'{year}' in text and ('年度报告' in text or '年报' in text):
                    if href.endswith('.pdf'):
                        return urljoin(self.base_url, href)
            
        except Exception as e:
            logger.debug(f"从产品页面查找失败: {str(e)}")
        
        return None
    
    def _find_report_url_from_disclosure_page(self, fund_code, year):
        """从信息披露页面查找年报URL"""
        try:
            # 构建信息披露页面URL
            disclosure_url = f"{self.base_url}/disclosure/{fund_code}"
            
            response = self.session.get(disclosure_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找年报链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if f'{year}' in text and '年度报告' in text:
                    if href.endswith('.pdf'):
                        return urljoin(self.base_url, href)
            
        except Exception as e:
            logger.debug(f"从信息披露页面查找失败: {str(e)}")
        
        return None
    
    def _construct_direct_url(self, fund_code, year):
        """尝试直接构建URL"""
        # 常见的URL模式
        patterns = [
            f"{self.base_url}/uploads/reports/{fund_code}/{year}_annual_report.pdf",
            f"{self.base_url}/reports/{fund_code}_{year}.pdf",
            f"{self.base_url}/disclosure/{fund_code}/{year}年度报告.pdf"
        ]
        
        for url in patterns:
            try:
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    return url
            except:
                continue
        
        return None
    
    def _download_file(self, url, file_path):
        """
        下载文件
        
        参数:
            url: 文件URL
            file_path: 保存路径
        
        返回:
            文件路径或None
        """
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 检查是否是PDF文件
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"文件类型不是PDF: {content_type}")
                return None
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # 小于1KB可能是错误页面
                os.remove(file_path)
                logger.warning(f"文件太小，可能下载失败: {file_size} bytes")
                return None
            
            logger.info(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
            return file_path
            
        except Exception as e:
            logger.error(f"下载文件失败: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    def download_recommended_funds(self, years=[2022, 2023, 2024]):
        """
        下载推荐的基金年报
        
        参数:
            years: 年份列表
        
        返回:
            下载统计信息
        """
        # 推荐的境外基金列表
        funds = [
            {
                'code': '159920',
                'name': '易方达香港恒生综合小型股指数ETF'
            },
            {
                'code': '513050',
                'name': '易方达中证海外中国互联网50ETF'
            },
            {
                'code': '161125',
                'name': '易方达标普500指数(QDII-LOF)'
            }
        ]
        
        logger.info("=" * 60)
        logger.info("开始批量下载年报...")
        logger.info(f"基金数量: {len(funds)}")
        logger.info(f"年份范围: {years}")
        logger.info("=" * 60)
        
        all_downloaded = []
        
        for fund in funds:
            logger.info("")
            downloaded = self.download_fund_reports(
                fund['code'],
                fund['name'],
                years
            )
            all_downloaded.extend(downloaded)
            logger.info("-" * 60)
        
        # 统计信息
        logger.info("")
        logger.info("=" * 60)
        logger.info("下载完成！")
        logger.info(f"总计下载: {len(all_downloaded)} 个文件")
        logger.info(f"保存位置: {os.path.abspath(self.output_dir)}")
        logger.info("=" * 60)
        
        return {
            'total': len(all_downloaded),
            'files': all_downloaded,
            'output_dir': os.path.abspath(self.output_dir)
        }


def main():
    """主函数"""
    print("=" * 60)
    print("易方达基金年报自动下载工具")
    print("=" * 60)
    print("")
    
    # 创建下载器
    downloader = AnnualReportDownloader(output_dir="annual_reports")
    
    # 下载推荐基金的年报
    result = downloader.download_recommended_funds(years=[2022, 2023, 2024])
    
    print("")
    print("下载结果:")
    print(f"- 成功下载: {result['total']} 个文件")
    print(f"- 保存位置: {result['output_dir']}")
    print("")
    
    if result['files']:
        print("已下载文件:")
        for file_path in result['files']:
            print(f"  [OK] {os.path.basename(file_path)}")
    else:
        print("[!] 未能下载任何文件")
        print("")
        print("可能的原因:")
        print("1. 网络连接问题")
        print("2. 易方达官网结构变化")
        print("3. 年报尚未发布")
        print("")
        print("建议:")
        print("1. 检查网络连接")
        print("2. 手动访问 https://www.efunds.com.cn/ 下载")
        print("3. 查看日志了解详细错误信息")
        print("4. 参考 年报数据下载指南.md 手动下载")


if __name__ == '__main__':
    main()