#!/usr/bin/env python
# coding: utf-8
"""
创建样本数据脚本
从完整数据中提取样本，用于快速测试
"""

import os
import json
import random
from typing import List, Dict, Any

def create_sample_data(input_file: str, output_file: str, sample_size: int = 1000):
    """从完整数据中创建样本"""
    print(f"正在从 {input_file} 创建样本数据...")
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件不存在 {input_file}")
        return
    
    # 读取完整数据
    print("正在读取完整数据...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"完整数据包含 {len(data)} 条记录")
    
    # 随机采样
    if len(data) <= sample_size:
        sample_data = data
    else:
        sample_data = random.sample(data, sample_size)
    
    # 重新编号
    for i, record in enumerate(sample_data):
        record['id'] = f"device_{i:06d}"
    
    # 保存样本数据
    print(f"正在保存 {len(sample_data)} 条样本记录...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    # 显示统计信息
    vendors = set(record['true_vendor'] for record in sample_data)
    device_types = set(record['device_type'] for record in sample_data)
    
    print(f"\n样本数据统计:")
    print(f"记录数量: {len(sample_data)}")
    print(f"厂商数量: {len(vendors)}")
    print(f"设备类型数量: {len(device_types)}")
    
    print(f"\n设备类型分布:")
    type_counts = {}
    for record in sample_data:
        device_type = record['device_type']
        type_counts[device_type] = type_counts.get(device_type, 0) + 1
    
    for device_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {device_type}: {count}")
    
    print(f"\n✅ 样本数据创建完成！")
    print(f"输出文件: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("样本数据创建工具")
    print("=" * 60)
    
    input_file = 'input/graph_entities.json'
    output_file = 'input/graph_entities_sample.json'
    
    if not os.path.exists(input_file):
        print(f"错误: 完整数据文件不存在 {input_file}")
        print("请先运行 convert_training_data.py 创建完整数据")
        return
    
    # 获取文件大小
    file_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
    print(f"完整数据文件大小: {file_size:.1f} MB")
    
    if file_size > 100:  # 大于100MB
        print("文件较大，建议创建样本数据进行测试")
        sample_size = 1000
    else:
        print("文件大小适中，可以使用完整数据")
        sample_size = 5000
    
    create_sample_data(input_file, output_file, sample_size)
    
    print(f"\n建议:")
    print(f"1. 使用样本数据 {output_file} 进行快速测试")
    print(f"2. 测试通过后，可以使用完整数据 {input_file}")
    print(f"3. 如果内存不足，可以调整样本大小")

if __name__ == "__main__":
    main() 