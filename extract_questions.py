#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Question Extractor
通用HTML题目提取工具
Author: 橘子海 (QQ: 347870660)
GitHub: https://github.com/yourusername/html-question-extractor
"""

import re
import os
import sys
import glob
from bs4 import BeautifulSoup

class QuestionExtractor:
    """HTML题目提取器"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.author = "橘子海"
        self.contact = "QQ: 347870660"
    
    def extract_questions(self, html_content):
        """
        从HTML内容中提取所有题目
        
        Args:
            html_content (str): HTML内容
            
        Returns:
            list: 题目列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有题目元素
        question_elements = soup.find_all('div', class_='questionLi')
        
        results = []
        
        for question_element in question_elements:
            try:
                # 提取题目信息
                question_data = self._parse_question_element(question_element)
                if question_data:
                    results.append(question_data)
            except Exception as e:
                print(f"警告: 解析题目时出错 - {str(e)}")
                continue
        
        return results
    
    def _parse_question_element(self, question_element):
        """解析单个题目元素"""
        # 提取题目ID
        question_id = question_element.get('data', '')
        
        # 提取题目文本
        question_title = question_element.find('h3', class_='mark_name')
        if not question_title:
            return None
            
        question_text = self._extract_question_text(question_title)
        
        # 判断题目类型
        question_type = self._detect_question_type(question_title)
        
        # 提取答案
        answer = self._extract_answer(question_element)
        
        # 提取选项
        options = self._extract_options(question_element, question_type)
        
        return {
            'id': question_id,
            'type': question_type,
            'question': question_text,
            'answer': answer,
            'options': options,
            'is_multiple_choice': len(options) > 0
        }
    
    def _extract_question_text(self, question_title):
        """提取题目文本"""
        question_text = ''
        for content in question_title.contents:
            if content.name != 'span' and content.string:
                question_text += content.string.strip()
        return question_text
    
    def _detect_question_type(self, question_title):
        """检测题目类型"""
        question_type = "单选题"
        type_span = question_title.find('span', class_='colorShallow')
        if type_span:
            question_type = type_span.get_text(strip=True).replace('(', '').replace(')', '')
        return question_type
    
    def _extract_answer(self, question_element):
        """提取答案"""
        answer = ""
        
        # 方式1：查找隐藏的答案输入框（单选题）
        answer_input = question_element.find('input', id=re.compile(r'^answer\d+$'))
        if answer_input:
            answer = answer_input.get('value', '')
        
        # 方式2：查找文本输入区域（主观题）
        if not answer:
            textarea = question_element.find('textarea')
            if textarea:
                answer = textarea.get_text(strip=True)
        
        # 方式3：查找已填写的答案（主观题）
        if not answer:
            answer_div = question_element.find('div', class_=re.compile(r'ans-|answer'))
            if answer_div:
                answer = answer_div.get_text(strip=True)
        
        return answer
    
    def _extract_options(self, question_element, question_type):
        """提取选项"""
        options = []
        if "单选题" in question_type or "选择题" in question_type:
            option_elements = question_element.find_all('div', class_='answerBg')
            for option_element in option_elements:
                option_span = option_element.find('span', class_=re.compile(r'choice\d+'))
                option_text_div = option_element.find('div', class_='answer_p')
                
                if option_span and option_text_div:
                    option_letter = option_span.get_text(strip=True)
                    option_content = option_text_div.get_text(strip=True)
                    options.append(f"{option_letter}. {option_content}")
        return options
    
    def save_questions(self, results, output_filename):
        """
        保存题目到文件
        
        Args:
            results (list): 题目列表
            output_filename (str): 输出文件名
        """
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                # 写入文件头
                self._write_file_header(f, results)
                
                # 保存选择题
                self._save_multiple_choice_questions(f, results)
                
                # 保存主观题
                self._save_subjective_questions(f, results)
                
            return True
        except Exception as e:
            print(f"保存文件时出错: {str(e)}")
            return False
    
    def _write_file_header(self, file_obj, results):
        """写入文件头"""
        multiple_choice_count = sum(1 for q in results if q['is_multiple_choice'])
        subjective_count = len(results) - multiple_choice_count
        
        file_obj.write("=" * 60 + "\n")
        file_obj.write("HTML题目提取结果\n")
        file_obj.write("=" * 60 + "\n")
        file_obj.write(f"工具: HTML Question Extractor v{self.version}\n")
        file_obj.write(f"作者: {self.author}\n")
        file_obj.write(f"联系: {self.contact}\n")
        file_obj.write(f"总题数: {len(results)}题\n")
        file_obj.write(f"选择题: {multiple_choice_count}题\n")
        file_obj.write(f"主观题: {subjective_count}题\n")
        file_obj.write("=" * 60 + "\n\n")
    
    def _save_multiple_choice_questions(self, file_obj, results):
        """保存选择题"""
        multiple_choice = [q for q in results if q['is_multiple_choice']]
        if multiple_choice:
            file_obj.write("【选择题】\n")
            file_obj.write("-" * 50 + "\n")
            for i, result in enumerate(multiple_choice, 1):
                file_obj.write(f"{i}. {result['question']}\n")
                for option in result['options']:
                    file_obj.write(f"   {option}\n")
                file_obj.write(f"   答案: {result['answer']}\n\n")
    
    def _save_subjective_questions(self, file_obj, results):
        """保存主观题"""
        subjective = [q for q in results if not q['is_multiple_choice']]
        if subjective:
            file_obj.write("\n【主观题】\n")
            file_obj.write("-" * 50 + "\n")
            for i, result in enumerate(subjective, 1):
                file_obj.write(f"{i}. {result['question']}\n")
                if result['answer'] and result['answer'].strip():
                    clean_answer = self._clean_html_tags(result['answer'])
                    file_obj.write(f"   参考答案: {clean_answer}\n")
                file_obj.write("\n")
    
    def _clean_html_tags(self, text):
        """清理HTML标签"""
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&nbsp;', ' ')
        return clean_text

def check_dependencies():
    """检查依赖库"""
    try:
        from bs4 import BeautifulSoup
        return True
    except ImportError:
        print("错误: 缺少必要的依赖库")
        print("请安装 BeautifulSoup4: pip install beautifulsoup4")
        return False

def process_files():
    """处理文件"""
    extractor = QuestionExtractor()
    
    # 显示欢迎信息
    print("=" * 60)
    print("HTML Question Extractor")
    print("通用HTML题目提取工具")
    print("=" * 60)
    print(f"版本: {extractor.version}")
    print(f"作者: {extractor.author}")
    print(f"联系: {extractor.contact}")
    print("GitHub: https://github.com/yourusername/html-question-extractor")
    print("=" * 60)
    
    # 检查HTML文件
    html_files = glob.glob("*.html")
    if not html_files:
        print("当前目录下没有找到HTML文件！")
        print("请将HTML文件放在脚本同一目录下。")
        input("按回车键退出...")
        return
    
    print(f"找到 {len(html_files)} 个HTML文件:")
    for file in html_files:
        print(f"  📄 {file}")
    
    input("\n按回车键开始处理...")
    print("\n开始处理文件...")
    
    # 处理每个文件
    success_count = 0
    for html_file in html_files:
        try:
            print(f"\n处理中: {html_file}")
            
            # 读取文件
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 提取题目
            results = extractor.extract_questions(html_content)
            
            if not results:
                print(f"  ⚠️  未找到题目: {html_file}")
                continue
            
            # 生成输出文件
            base_name = os.path.splitext(html_file)[0]
            output_file = f"{base_name}.txt"
            
            # 保存题目
            if extractor.save_questions(results, output_file):
                multiple_choice = sum(1 for q in results if q['is_multiple_choice'])
                subjective = len(results) - multiple_choice
                print(f"  ✅ 成功: {output_file} (共{len(results)}题)")
                print(f"     选择题: {multiple_choice}题, 主观题: {subjective}题")
                success_count += 1
            else:
                print(f"  ❌ 失败: 保存文件出错")
                
        except UnicodeDecodeError:
            print(f"  ❌ 编码错误: 请检查文件编码是否为UTF-8")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
    
    # 显示结果
    print("\n" + "=" * 60)
    if success_count > 0:
        print(f"处理完成！成功处理 {success_count} 个文件")
    else:
        print("处理完成，但没有成功提取任何题目")
    print("=" * 60)

def main():
    """主函数"""
    if not check_dependencies():
        sys.exit(1)
    
    try:
        process_files()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
