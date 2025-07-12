#!/usr/bin/env python
# coding: utf-8
"""
标签数据处理脚本 - 生成中层特征
从lable.txt文件中提取设备类型、厂商、型号信息，生成中层特征配置
"""

import os
import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

class LabelProcessor:
    def __init__(self):
        """初始化标签处理器"""
        self.device_types = set()
        self.manufacturers = set()
        self.models = set()
        self.device_manufacturer_pairs = set()
        self.manufacturer_model_pairs = set()
        
        # 统计信息
        self.stats = {
            'total_lines': 0,
            'valid_lines': 0,
            'device_types_count': 0,
            'manufacturers_count': 0,
            'models_count': 0
        }
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        if not text or text.strip() == '':
            return ''
        
        # 移除特殊字符和多余空格
        cleaned = re.sub(r'[^\w\s\-\.]', '', text.strip())
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.lower()
    
    def is_valid_device_type(self, device_type: str) -> bool:
        """检查是否为有效的设备类型"""
        if not device_type or device_type == 'nil':
            return False
        
        # 常见的设备类型
        valid_types = {
            'camera', 'router', 'switch', 'printer', 'firewall', 'bridge',
            'server', 'nas', 'dvr', 'nvr', 'ipc', 'ptz', 'encoder', 'decoder',
            'gateway', 'modem', 'hub', 'repeater', 'access_point', 'controller'
        }
        
        return device_type.lower() in valid_types or len(device_type) > 2
    
    def is_valid_manufacturer(self, manufacturer: str) -> bool:
        """检查是否为有效的厂商"""
        if not manufacturer or manufacturer == 'nil':
            return False
        
        # 过滤掉太短的厂商名
        return len(manufacturer) > 1
    
    def is_valid_model(self, model: str) -> bool:
        """检查是否为有效的型号"""
        if not model or model == 'nil':
            return False
        
        # 过滤掉太短的型号名
        return len(model) > 1
    
    def process_label_file(self, file_path: str) -> Dict:
        """处理标签文件"""
        print(f"正在处理标签文件: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        self.stats['total_lines'] = len(lines)
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # 解析CSV格式：设备类型,厂商,型号
            parts = line.split(',')
            if len(parts) < 3:
                continue
            
            device_type = self.clean_text(parts[0])
            manufacturer = self.clean_text(parts[1])
            model = self.clean_text(parts[2])
            
            # 验证数据有效性
            if self.is_valid_device_type(device_type):
                self.device_types.add(device_type)
                self.stats['device_types_count'] += 1
            
            if self.is_valid_manufacturer(manufacturer):
                self.manufacturers.add(manufacturer)
                self.stats['manufacturers_count'] += 1
            
            if self.is_valid_model(model):
                self.models.add(model)
                self.stats['models_count'] += 1
            
            # 记录有效组合
            if (self.is_valid_device_type(device_type) and 
                self.is_valid_manufacturer(manufacturer)):
                self.device_manufacturer_pairs.add((device_type, manufacturer))
            
            if (self.is_valid_manufacturer(manufacturer) and 
                self.is_valid_model(model)):
                self.manufacturer_model_pairs.add((manufacturer, model))
            
            self.stats['valid_lines'] += 1
        
        return self.generate_middle_features()
    
    def generate_middle_features(self) -> Dict:
        """生成中层特征配置"""
        print("正在生成中层特征配置...")
        
        middle_features = {
            "device_types": {
                "name": "设备类型层",
                "description": "从标签中提取的设备类型信息",
                "enabled": True,
                "priority": 1,
                "extraction_rules": {
                    "keywords": list(self.device_types),
                    "regex_patterns": []
                },
                "relations": {
                    "indicates_device_type": "指示设备类型",
                    "is_type": "是类型"
                },
                "knowledge_base": {}
            },
            "manufacturers": {
                "name": "厂商层",
                "description": "从标签中提取的厂商信息",
                "enabled": True,
                "priority": 2,
                "extraction_rules": {
                    "keywords": list(self.manufacturers),
                    "regex_patterns": []
                },
                "relations": {
                    "indicates_manufacturer": "指示厂商",
                    "has_manufacturer": "有厂商"
                },
                "knowledge_base": {}
            },
            "models": {
                "name": "型号层",
                "description": "从标签中提取的型号信息",
                "enabled": True,
                "priority": 3,
                "extraction_rules": {
                    "keywords": list(self.models),
                    "regex_patterns": []
                },
                "relations": {
                    "indicates_model": "指示型号",
                    "has_model": "有型号"
                },
                "knowledge_base": {}
            },
            "device_manufacturer_combinations": {
                "name": "设备厂商组合层",
                "description": "设备类型和厂商的组合信息",
                "enabled": True,
                "priority": 4,
                "extraction_rules": {
                    "keywords": [f"{dt}_{mf}" for dt, mf in self.device_manufacturer_pairs],
                    "regex_patterns": []
                },
                "relations": {
                    "typical_for": "典型设备",
                    "has_manufacturer": "有厂商"
                },
                "knowledge_base": {}
            },
            "manufacturer_model_combinations": {
                "name": "厂商型号组合层",
                "description": "厂商和型号的组合信息",
                "enabled": True,
                "priority": 5,
                "extraction_rules": {
                    "keywords": [f"{mf}_{md}" for mf, md in self.manufacturer_model_pairs],
                    "regex_patterns": []
                },
                "relations": {
                    "produces": "生产",
                    "has_model": "有型号"
                },
                "knowledge_base": {}
            }
        }
        
        # 为每个中层特征添加知识库
        for feature_name, feature_config in middle_features.items():
            if feature_name == "device_types":
                feature_config["knowledge_base"] = {
                    "camera": "摄像头设备",
                    "router": "路由器设备",
                    "switch": "交换机设备",
                    "printer": "打印机设备",
                    "firewall": "防火墙设备",
                    "bridge": "网桥设备",
                    "server": "服务器设备",
                    "nas": "网络存储设备",
                    "dvr": "数字视频录像机",
                    "nvr": "网络视频录像机"
                }
            elif feature_name == "manufacturers":
                # 添加知名厂商的知识库
                feature_config["knowledge_base"] = {
                    "axis": "Axis Communications - 专业网络视频设备厂商",
                    "hikvision": "Hikvision - 海康威视，全球领先的视频监控设备厂商",
                    "dahua": "Dahua Technology - 大华技术，视频监控设备厂商",
                    "cisco": "Cisco Systems - 思科系统，网络设备厂商",
                    "d-link": "D-Link Corporation - 友讯科技，网络设备厂商",
                    "tp-link": "TP-Link Technologies - 普联技术，网络设备厂商",
                    "mikrotik": "MikroTik - 路由器OS和网络设备厂商",
                    "netgear": "NETGEAR - 网件，网络设备厂商",
                    "asus": "ASUS - 华硕，电脑和网络设备厂商",
                    "hp": "HP - 惠普，打印机和网络设备厂商"
                }
        
        return {
            "middle_features": middle_features,
            "statistics": self.stats,
            "summary": {
                "total_device_types": len(self.device_types),
                "total_manufacturers": len(self.manufacturers),
                "total_models": len(self.models),
                "total_device_manufacturer_pairs": len(self.device_manufacturer_pairs),
                "total_manufacturer_model_pairs": len(self.manufacturer_model_pairs)
            }
        }
    
    def save_middle_features_config(self, config: Dict, output_path: str):
        """保存中层特征配置到文件"""
        print(f"正在保存配置到: {output_path}")
        
        # 确保输出目录存在（只有当路径包含目录时才创建）
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 只有当目录不为空时才创建
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"配置已保存到: {output_path}")
    
    def generate_summary_report(self, config: Dict) -> str:
        """生成处理报告"""
        stats = config["statistics"]
        summary = config["summary"]
        
        report = f"""
# 标签数据处理报告

## 处理统计
- 总行数: {stats['total_lines']}
- 有效行数: {stats['valid_lines']}
- 设备类型数量: {summary['total_device_types']}
- 厂商数量: {summary['total_manufacturers']}
- 型号数量: {summary['total_models']}
- 设备厂商组合: {summary['total_device_manufacturer_pairs']}
- 厂商型号组合: {summary['total_manufacturer_model_pairs']}

## 生成的中层特征
1. **设备类型层** - {len(config['middle_features']['device_types']['extraction_rules']['keywords'])} 个设备类型
2. **厂商层** - {len(config['middle_features']['manufacturers']['extraction_rules']['keywords'])} 个厂商
3. **型号层** - {len(config['middle_features']['models']['extraction_rules']['keywords'])} 个型号
4. **设备厂商组合层** - {len(config['middle_features']['device_manufacturer_combinations']['extraction_rules']['keywords'])} 个组合
5. **厂商型号组合层** - {len(config['middle_features']['manufacturer_model_combinations']['extraction_rules']['keywords'])} 个组合

## 主要设备类型 (前10个)
{list(self.device_types)[:10]}

## 主要厂商 (前10个)
{list(self.manufacturers)[:10]}

## 使用说明
生成的配置文件可以直接用于可扩展中层特征系统，支持：
- 从HTTP banner中提取设备类型、厂商、型号信息
- 构建多层次知识图谱
- 进行IoT设备识别和推理
"""
        return report

def main():
    """主函数"""
    print("=" * 60)
    print("标签数据处理脚本 - 生成中层特征")
    print("=" * 60)
    
    # 文件路径
    label_file = "../input/lable.txt"
    output_dir = "build_middle_feature_result"
    output_config = os.path.join(output_dir, "middle_features_config.json")
    output_report = os.path.join(output_dir, "processing_report.md")
    
    # 创建处理器
    processor = LabelProcessor()
    
    # 处理标签文件
    config = processor.process_label_file(label_file)
    
    if not config:
        print("处理失败，请检查文件路径")
        return
    
    # 保存配置
    processor.save_middle_features_config(config, output_config)
    
    # 生成报告
    report = processor.generate_summary_report(config)
    # 确保报告目录存在
    os.makedirs(output_dir, exist_ok=True)
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print("=" * 60)
    print(f"配置文件: {output_config}")
    print(f"处理报告: {output_report}")
    print("\n下一步:")
    print("1. 检查生成的配置文件")
    print("2. 将配置集成到可扩展中层特征系统")
    print("3. 添加banner和标签的关系映射")

if __name__ == "__main__":
    main() 