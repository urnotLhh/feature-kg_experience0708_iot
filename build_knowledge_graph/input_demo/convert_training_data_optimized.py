#!/usr/bin/env python
# coding: utf-8
"""
优化版训练数据格式转换脚本
支持分批处理和内存优化，适合处理大规模数据
"""

import os
import json
import re
from typing import List, Dict, Any, Generator
from datetime import datetime

class OptimizedTrainingDataConverter:
    """优化版训练数据转换器"""
    
    def __init__(self, batch_size: int = 1000):
        """初始化转换器"""
        self.batch_size = batch_size
        self.stats = {
            'total_files': 0,
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'vendors': set(),
            'products': set(),
            'device_types': set()
        }
    
    def extract_device_type_from_banner(self, banner: str, vendor: str, product: str) -> str:
        """从banner中提取设备类型"""
        banner_lower = banner.lower()
        
        # 基于厂商和产品名称推断设备类型
        if vendor.lower() in ['sharp', 'hp', 'canon', 'epson', 'brother']:
            if any(keyword in banner_lower for keyword in ['printer', 'print', 'laser', 'inkjet']):
                return 'printer'
            elif any(keyword in banner_lower for keyword in ['scanner', 'scan']):
                return 'scanner'
            elif any(keyword in banner_lower for keyword in ['copier', 'copy']):
                return 'copier'
            elif any(keyword in banner_lower for keyword in ['multifunction', 'mfp']):
                return 'multifunction'
            else:
                return 'printer'  # 默认打印机
        
        elif vendor.lower() in ['axis', 'hikvision', 'dahua', 'foscam', 'd-link']:
            if any(keyword in banner_lower for keyword in ['camera', 'ipc', 'ptz']):
                return 'camera'
            elif any(keyword in banner_lower for keyword in ['dvr', 'nvr']):
                return 'recorder'
            else:
                return 'camera'  # 默认摄像头
        
        elif vendor.lower() in ['cisco', 'netgear', 'tp-link', 'asus', 'linksys']:
            if any(keyword in banner_lower for keyword in ['router', 'gateway']):
                return 'router'
            elif any(keyword in banner_lower for keyword in ['switch']):
                return 'switch'
            elif any(keyword in banner_lower for keyword in ['access point', 'ap']):
                return 'access_point'
            else:
                return 'router'  # 默认路由器
        
        else:
            # 通用设备类型检测
            if any(keyword in banner_lower for keyword in ['printer', 'print']):
                return 'printer'
            elif any(keyword in banner_lower for keyword in ['camera', 'ipc']):
                return 'camera'
            elif any(keyword in banner_lower for keyword in ['router', 'gateway']):
                return 'router'
            elif any(keyword in banner_lower for keyword in ['switch']):
                return 'switch'
            elif any(keyword in banner_lower for keyword in ['server']):
                return 'server'
            elif any(keyword in banner_lower for keyword in ['firewall']):
                return 'firewall'
            else:
                return 'unknown'
    
    def extract_version_from_banner(self, banner: str) -> str:
        """从banner中提取版本信息"""
        version_patterns = [
            r'ver\s+([\d\.]+)',
            r'version\s+([\d\.]+)',
            r'v([\d\.]+)',
            r'([\d\.]+(?:\.[a-z0-9]+)*)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, banner, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def extract_model_from_banner(self, banner: str, product: str) -> str:
        """从banner中提取型号信息"""
        if product and product != '':
            return product
        
        model_patterns = [
            r'([A-Z]{2,}-[A-Z0-9-]+)',
            r'([A-Z]{2,}[A-Z0-9-]+)',
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, banner)
            if match:
                return match.group(1)
        
        return 'unknown'
    
    def extract_protocol_from_banner(self, banner: str) -> str:
        """从banner中提取协议信息"""
        banner_lower = banner.lower()
        
        if 'ftp' in banner_lower:
            return 'ftp'
        elif 'http' in banner_lower:
            return 'http'
        elif 'ssh' in banner_lower:
            return 'ssh'
        elif 'telnet' in banner_lower:
            return 'telnet'
        elif 'smtp' in banner_lower:
            return 'smtp'
        elif 'pop3' in banner_lower:
            return 'pop3'
        else:
            return 'unknown'
    
    def convert_record(self, record: Dict[str, Any], record_id: int) -> Dict[str, Any]:
        """转换单条记录"""
        banner = record.get('banner', '')
        vendor = record.get('true_vendor', '')
        product = record.get('true_product', '')
        
        device_type = self.extract_device_type_from_banner(banner, vendor, product)
        model = self.extract_model_from_banner(banner, product)
        version = self.extract_version_from_banner(banner)
        protocol = self.extract_protocol_from_banner(banner)
        
        converted_record = {
            "banner": banner,
            "id": f"device_{record_id:06d}",
            "port": record.get('port', 21),
            "protocol": protocol,
            "true_vendor": vendor,
            "true_product": product,
            "device_type": device_type,
            "model": model,
            "version": version
        }
        
        return converted_record
    
    def process_file_batch(self, file_path: str) -> Generator[List[Dict[str, Any]], None, None]:
        """分批处理单个文件"""
        print(f"正在处理文件: {os.path.basename(file_path)}")
        
        batch = []
        record_id = 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    
                    if not record.get('banner') or not record.get('true_vendor'):
                        self.stats['invalid_records'] += 1
                        continue
                    
                    converted_record = self.convert_record(record, record_id)
                    batch.append(converted_record)
                    
                    # 更新统计信息
                    self.stats['valid_records'] += 1
                    self.stats['vendors'].add(record.get('true_vendor', ''))
                    self.stats['products'].add(record.get('true_product', ''))
                    self.stats['device_types'].add(converted_record['device_type'])
                    
                    record_id += 1
                    
                    # 当批次满了时，返回当前批次
                    if len(batch) >= self.batch_size:
                        yield batch
                        batch = []
                        
                except json.JSONDecodeError:
                    self.stats['invalid_records'] += 1
                    continue
                except Exception as e:
                    print(f"  错误: 第{line_num}行处理失败: {e}")
                    self.stats['invalid_records'] += 1
                    continue
        
        # 返回最后一批
        if batch:
            yield batch
        
        print(f"  处理完成: {record_id} 条有效记录")
    
    def convert_all_data_optimized(self, input_dir: str, output_file: str, max_records: int = None):
        """优化版数据转换"""
        print("=" * 60)
        print("优化版训练数据格式转换")
        print("=" * 60)
        
        banner_dir = os.path.join(input_dir, 'banner_and_lables')
        if not os.path.exists(banner_dir):
            print(f"错误: banner目录不存在 {banner_dir}")
            return
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 分批处理所有文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('[\n')  # 开始JSON数组
            
            first_record = True
            total_processed = 0
            
            for filename in os.listdir(banner_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(banner_dir, filename)
                    self.stats['total_files'] += 1
                    
                    for batch in self.process_file_batch(file_path):
                        for record in batch:
                            # 检查是否达到最大记录数
                            if max_records and total_processed >= max_records:
                                break
                            
                            # 写入JSON记录
                            if not first_record:
                                f.write(',\n')
                            else:
                                first_record = False
                            
                            json.dump(record, f, ensure_ascii=False, indent=2)
                            total_processed += 1
                            
                            # 每1000条记录显示进度
                            if total_processed % 1000 == 0:
                                print(f"  已处理: {total_processed} 条记录")
                        
                        if max_records and total_processed >= max_records:
                            break
                    
                    if max_records and total_processed >= max_records:
                        break
            
            f.write('\n]')  # 结束JSON数组
        
        print(f"\n✅ 成功保存 {total_processed} 条记录到: {output_file}")
        self.show_statistics()
    
    def create_sample_data(self, input_dir: str, output_file: str, sample_size: int = 1000):
        """创建样本数据用于测试"""
        print("=" * 60)
        print(f"创建样本数据 ({sample_size} 条记录)")
        print("=" * 60)
        
        self.convert_all_data_optimized(input_dir, output_file, max_records=sample_size)
    
    def show_statistics(self):
        """显示统计信息"""
        print("\n" + "=" * 60)
        print("转换统计信息")
        print("=" * 60)
        print(f"处理文件数: {self.stats['total_files']}")
        print(f"有效记录数: {self.stats['valid_records']}")
        print(f"无效记录数: {self.stats['invalid_records']}")
        print(f"厂商数量: {len(self.stats['vendors'])}")
        print(f"产品数量: {len(self.stats['products'])}")
        print(f"设备类型数量: {len(self.stats['device_types'])}")


def main():
    """主函数"""
    print("选择处理模式:")
    print("1. 创建样本数据 (1000条记录，用于测试)")
    print("2. 创建完整数据 (所有记录，需要较长时间)")
    print("3. 自定义数量")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    converter = OptimizedTrainingDataConverter(batch_size=1000)
    input_dir = 'input'
    
    if choice == '1':
        # 创建样本数据
        output_file = 'input/graph_entities_sample.json'
        converter.create_sample_data(input_dir, output_file, sample_size=1000)
        print(f"\n✅ 样本数据创建完成！")
        print(f"输出文件: {output_file}")
        print(f"建议使用样本数据先测试知识图谱构建器")
        
    elif choice == '2':
        # 创建完整数据
        output_file = 'input/graph_entities.json'
        converter.convert_all_data_optimized(input_dir, output_file)
        print(f"\n✅ 完整数据创建完成！")
        print(f"输出文件: {output_file}")
        
    elif choice == '3':
        # 自定义数量
        try:
            size = int(input("请输入记录数量: "))
            output_file = f'input/graph_entities_{size}.json'
            converter.convert_all_data_optimized(input_dir, output_file, max_records=size)
            print(f"\n✅ 自定义数据创建完成！")
            print(f"输出文件: {output_file}")
        except ValueError:
            print("输入无效，使用默认1000条记录")
            output_file = 'input/graph_entities_sample.json'
            converter.create_sample_data(input_dir, output_file, sample_size=1000)
    
    else:
        print("输入无效，使用默认样本数据")
        output_file = 'input/graph_entities_sample.json'
        converter.create_sample_data(input_dir, output_file, sample_size=1000)


if __name__ == "__main__":
    main() 