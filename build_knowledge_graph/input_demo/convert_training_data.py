#!/usr/bin/env python
# coding: utf-8
"""
训练数据格式转换脚本
将banner_and_lables目录中的真实训练数据转换为标准的JSON格式
"""

import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

class TrainingDataConverter:
    """训练数据转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.converted_data = []
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
        # 常见的版本号模式
        version_patterns = [
            r'ver\s+([\d\.]+)',  # Ver 01.05.00.0s.12
            r'version\s+([\d\.]+)',  # Version 1.0
            r'v([\d\.]+)',  # v1.0
            r'([\d\.]+(?:\.[a-z0-9]+)*)',  # 01.05.00.0s.12
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
        
        # 从banner中提取型号
        # 常见的型号模式：厂商名 + 字母数字组合
        model_patterns = [
            r'([A-Z]{2,}-[A-Z0-9-]+)',  # MX-M264N, AR-267FP
            r'([A-Z]{2,}[A-Z0-9-]+)',   # SHARP MX-M264N
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
    
    def convert_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """转换单条记录"""
        banner = record.get('banner', '')
        vendor = record.get('true_vendor', '')
        product = record.get('true_product', '')
        
        # 提取设备类型
        device_type = self.extract_device_type_from_banner(banner, vendor, product)
        
        # 提取型号
        model = self.extract_model_from_banner(banner, product)
        
        # 提取版本
        version = self.extract_version_from_banner(banner)
        
        # 提取协议
        protocol = self.extract_protocol_from_banner(banner)
        
        # 生成设备ID
        device_id = f"device_{len(self.converted_data):06d}"
        
        # 构建转换后的记录
        converted_record = {
            "banner": banner,
            "id": device_id,
            "port": record.get('port', 21),  # 默认FTP端口
            "protocol": protocol,
            "true_vendor": vendor,
            "true_product": product,
            "device_type": device_type,
            "model": model,
            "version": version
        }
        
        return converted_record
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """处理单个文件"""
        print(f"正在处理文件: {os.path.basename(file_path)}")
        
        file_records = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析JSON格式的记录
                    record = json.loads(line)
                    
                    # 验证必需字段
                    if not record.get('banner') or not record.get('true_vendor'):
                        self.stats['invalid_records'] += 1
                        continue
                    
                    # 转换记录
                    converted_record = self.convert_record(record)
                    file_records.append(converted_record)
                    
                    # 更新统计信息
                    self.stats['valid_records'] += 1
                    self.stats['vendors'].add(record.get('true_vendor', ''))
                    self.stats['products'].add(record.get('true_product', ''))
                    self.stats['device_types'].add(converted_record['device_type'])
                    
                except json.JSONDecodeError as e:
                    print(f"  警告: 第{line_num}行JSON解析失败: {e}")
                    self.stats['invalid_records'] += 1
                    continue
                except Exception as e:
                    print(f"  错误: 第{line_num}行处理失败: {e}")
                    self.stats['invalid_records'] += 1
                    continue
        
        print(f"  处理完成: {len(file_records)} 条有效记录")
        return file_records
    
    def convert_all_data(self, input_dir: str, output_file: str):
        """转换所有数据"""
        print("=" * 60)
        print("训练数据格式转换")
        print("=" * 60)
        
        banner_dir = os.path.join(input_dir, 'banner_and_lables')
        if not os.path.exists(banner_dir):
            print(f"错误: banner目录不存在 {banner_dir}")
            return
        
        # 处理所有banner文件
        for filename in os.listdir(banner_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(banner_dir, filename)
                self.stats['total_files'] += 1
                
                file_records = self.process_file(file_path)
                self.converted_data.extend(file_records)
        
        # 保存转换后的数据
        self.save_converted_data(output_file)
        
        # 显示统计信息
        self.show_statistics()
    
    def save_converted_data(self, output_file: str):
        """保存转换后的数据"""
        print(f"\n正在保存转换后的数据到: {output_file}")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 保存JSON数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.converted_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功保存 {len(self.converted_data)} 条记录")
    
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
        
        print(f"\n设备类型分布:")
        device_type_counts = {}
        for record in self.converted_data:
            device_type = record['device_type']
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
        
        for device_type, count in sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {device_type}: {count}")
        
        print(f"\n厂商分布 (前10):")
        vendor_counts = {}
        for record in self.converted_data:
            vendor = record['true_vendor']
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        
        for vendor, count in sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {vendor}: {count}")


def main():
    """主函数"""
    converter = TrainingDataConverter()
    
    # 转换数据
    input_dir = 'input'
    output_file = 'input/graph_entities.json'
    
    converter.convert_all_data(input_dir, output_file)
    
    print(f"\n✅ 转换完成！")
    print(f"输出文件: {output_file}")
    print(f"现在可以运行知识图谱构建器了")


if __name__ == "__main__":
    main() 