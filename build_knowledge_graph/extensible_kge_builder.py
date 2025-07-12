#!/usr/bin/env python
# coding: utf-8
"""
可扩展中层特征知识图谱构建器
支持从middle_features_config.json加载配置，使用真实数据构建知识图谱
"""

import os
import json
import re
import hashlib
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional, Any
from datetime import datetime

class ExtensibleKGEBuilder:
    """可扩展中层特征知识图谱构建器"""
    
    def __init__(self, middle_features_config: str = "input_demo/build_middle_feature_result/middle_features_config.json"):
        """
        初始化构建器
        
        Args:
            middle_features_config: 中层特征配置文件路径
        """
        self.middle_features_config = middle_features_config
        self.middle_features = {}
        self.knowledge_bases = {}
        
        # 知识图谱数据
        self.entities = set()
        self.relations = set()
        self.triples = []
        
        # 多层次实体
        self.banner_features = set()      # 底层：banner特征
        self.device_types = set()         # 中层：设备类型
        self.manufacturers = set()        # 中层：厂商
        self.models = set()               # 中层：型号
        self.device_manufacturer_pairs = set()  # 中层：设备厂商组合
        self.manufacturer_model_pairs = set()   # 中层：厂商型号组合
        self.specific_devices = set()     # 高层：具体设备
        
        # 加载中层特征配置
        self.load_middle_features_config()
    
    def load_middle_features_config(self):
        """加载中层特征配置"""
        print(f"正在加载中层特征配置: {self.middle_features_config}")
        
        if not os.path.exists(self.middle_features_config):
            print(f"错误: 配置文件不存在 {self.middle_features_config}")
            return
        
        with open(self.middle_features_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.middle_features = config.get('middle_features', {})
        self.stats = config.get('statistics', {})
        self.summary = config.get('summary', {})
        
        print(f"加载完成:")
        print(f"  设备类型: {self.summary.get('total_device_types', 0)}")
        print(f"  厂商: {self.summary.get('total_manufacturers', 0)}")
        print(f"  型号: {self.summary.get('total_models', 0)}")
        print(f"  设备厂商组合: {self.summary.get('total_device_manufacturer_pairs', 0)}")
        print(f"  厂商型号组合: {self.summary.get('total_manufacturer_model_pairs', 0)}")
    
    def extract_features_from_banner(self, banner_text: str) -> Dict[str, List[str]]:
        """
        从banner中提取中层特征
        
        Args:
            banner_text: banner文本
            
        Returns:
            Dict[str, List[str]]: 提取的特征
        """
        features = {
            'device_types': [],
            'manufacturers': [],
            'models': [],
            'device_manufacturer_combinations': [],
            'manufacturer_model_combinations': []
        }
        
        banner_lower = banner_text.lower()
        
        # 遍历所有中层特征层
        for layer_name, layer_config in self.middle_features.items():
            if not layer_config.get('enabled', True):
                continue
            
            keywords = layer_config.get('extraction_rules', {}).get('keywords', [])
            found_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in banner_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                features[layer_name] = found_keywords
        
        return features
    
    def parse_device_entity(self, device_entity: str) -> Dict[str, str]:
        """解析设备实体"""
        # 格式：type_manufacturer_model
        parts = device_entity.split('_')
        
        device_info = {
            'type': '',
            'manufacturer': '',
            'model': ''
        }
        
        if len(parts) >= 1:
            device_info['type'] = parts[0]
        
        if len(parts) >= 2:
            device_info['manufacturer'] = parts[1]
        
        if len(parts) >= 3:
            device_info['model'] = '_'.join(parts[2:])
        
        return device_info
    
    def build_knowledge_graph(self, training_data: List[Tuple[str, str]]) -> Dict:
        """
        构建知识图谱
        
        Args:
            training_data: 训练数据 [(banner_text, device_entity), ...]
            
        Returns:
            Dict: 知识图谱数据
        """
        print("开始构建可扩展知识图谱...")
        
        # 清空之前的数据
        self.entities.clear()
        self.relations.clear()
        self.triples.clear()
        
        # 处理每个训练样本
        for i, (banner_text, device_entity) in enumerate(training_data):
            if i % 100 == 0:
                print(f"处理进度: {i}/{len(training_data)}")
            
            # 提取中层特征
            features = self.extract_features_from_banner(banner_text)
            
            # 解析设备实体
            device_info = self.parse_device_entity(device_entity)
            
            # 创建多层次实体
            self._create_multi_level_entities(device_info, features)
            
            # 创建增强三元组
            self._create_enhanced_triples(banner_text, device_info, features)
        
        # 构建中层特征关系
        self._build_middle_layer_relations()
        
        # 生成知识图谱
        knowledge_graph = self._get_knowledge_graph()
        
        print(f"知识图谱构建完成！")
        print(f"实体数量: {len(self.entities)}")
        print(f"关系数量: {len(self.relations)}")
        print(f"三元组数量: {len(self.triples)}")
        
        return knowledge_graph
    
    def _create_multi_level_entities(self, device_info: Dict, features: Dict[str, List[str]]):
        """创建多层次实体"""
        # 底层：banner特征
        for feature_list in features.values():
            for feature in feature_list:
                self.banner_features.add(feature)
                self.entities.add(feature)
        
        # 中层：设备类型
        for device_type in features.get('device_types', []):
            self.device_types.add(device_type)
            self.entities.add(device_type)
        
        # 中层：厂商
        for manufacturer in features.get('manufacturers', []):
            self.manufacturers.add(manufacturer)
            self.entities.add(manufacturer)
        
        # 中层：型号
        for model in features.get('models', []):
            self.models.add(model)
            self.entities.add(model)
        
        # 中层：设备厂商组合
        for combo in features.get('device_manufacturer_combinations', []):
            self.device_manufacturer_pairs.add(combo)
            self.entities.add(combo)
        
        # 中层：厂商型号组合
        for combo in features.get('manufacturer_model_combinations', []):
            self.manufacturer_model_pairs.add(combo)
            self.entities.add(combo)
        
        # 高层：具体设备
        device_entity = f"{device_info['type']}_{device_info['manufacturer']}"
        if device_info['model']:
            device_entity += f"_{device_info['model']}"
        
        self.specific_devices.add(device_entity)
        self.entities.add(device_entity)
    
    def _create_enhanced_triples(self, banner_text: str, device_info: Dict, features: Dict[str, List[str]]):
        """创建增强三元组"""
        banner_id = self._create_banner_id(banner_text)
        self.entities.add(banner_id)
        
        device_entity = f"{device_info['type']}_{device_info['manufacturer']}"
        if device_info['model']:
            device_entity += f"_{device_info['model']}"
        
        # 1. Banner到设备的基本关系
        self.triples.append((banner_id, "indicates_device", device_entity))
        self.relations.add("indicates_device")
        
        # 2. Banner到中层特征的关系
        for layer_name, layer_features in features.items():
            for feature in layer_features:
                # Banner包含中层特征
                relation = f"contains_{layer_name}"
                self.triples.append((banner_id, relation, feature))
                self.relations.add(relation)
                
                # 中层特征到设备的关系映射
                self._create_middle_layer_to_device_mappings(feature, layer_name, device_info)
        
        # 3. 设备到厂商和类型的关系
        if device_info['manufacturer']:
            self.triples.append((device_entity, "has_manufacturer", device_info['manufacturer']))
            self.relations.add("has_manufacturer")
        
        if device_info['type']:
            self.triples.append((device_entity, "is_type", device_info['type']))
            self.relations.add("is_type")
        
        if device_info['model']:
            self.triples.append((device_entity, "has_model", device_info['model']))
            self.relations.add("has_model")
    
    def _create_middle_layer_to_device_mappings(self, feature: str, layer_name: str, device_info: Dict):
        """创建中层特征到设备的映射关系"""
        layer_config = self.middle_features.get(layer_name, {})
        relations = layer_config.get('relations', {})
        
        # 基于设备信息的直接映射
        if device_info['manufacturer'] and 'indicates_manufacturer' in relations:
            self.triples.append((feature, "indicates_manufacturer", device_info['manufacturer']))
            self.relations.add("indicates_manufacturer")
        
        if device_info['type'] and 'indicates_device_type' in relations:
            self.triples.append((feature, "indicates_device_type", device_info['type']))
            self.relations.add("indicates_device_type")
        
        if device_info['model'] and 'indicates_model' in relations:
            self.triples.append((feature, "indicates_model", device_info['model']))
            self.relations.add("indicates_model")
        
        # 特殊关系映射
        if layer_name == 'device_manufacturer_combinations' and 'typical_for' in relations:
            device_entity = f"{device_info['type']}_{device_info['manufacturer']}"
            self.triples.append((feature, "typical_for", device_entity))
            self.relations.add("typical_for")
        
        if layer_name == 'manufacturer_model_combinations' and 'produces' in relations:
            if device_info['manufacturer'] and device_info['model']:
                self.triples.append((feature, "produces", f"{device_info['manufacturer']}_{device_info['model']}"))
                self.relations.add("produces")
    
    def _build_middle_layer_relations(self):
        """构建中层特征之间的关系"""
        # 设备类型与厂商的关系
        for device_type in self.device_types:
            for manufacturer in self.manufacturers:
                # 检查是否存在设备厂商组合
                combo = f"{device_type}_{manufacturer}"
                if combo in self.device_manufacturer_pairs:
                    self.triples.append((device_type, "typical_for", manufacturer))
                    self.relations.add("typical_for")
        
        # 厂商与型号的关系
        for manufacturer in self.manufacturers:
            for model in self.models:
                # 检查是否存在厂商型号组合
                combo = f"{manufacturer}_{model}"
                if combo in self.manufacturer_model_pairs:
                    self.triples.append((manufacturer, "produces", model))
                    self.relations.add("produces")
    
    def _create_banner_id(self, banner_text: str) -> str:
        """创建banner ID"""
        normalized_banner = self._normalize_banner(banner_text)
        banner_hash = hashlib.md5(normalized_banner.encode()).hexdigest()[:8]
        return f"banner_{banner_hash}"
    
    def _normalize_banner(self, banner_text: str) -> str:
        """标准化banner文本"""
        # 移除多余空白字符
        normalized = re.sub(r'\s+', ' ', banner_text.strip())
        # 转换为小写
        normalized = normalized.lower()
        return normalized
    
    def _get_knowledge_graph(self) -> Dict:
        """获取知识图谱数据"""
        return {
            'entities': list(self.entities),
            'relations': list(self.relations),
            'triples': self.triples,
            'entity_count': len(self.entities),
            'relation_count': len(self.relations),
            'triple_count': len(self.triples),
            'middle_layers': list(self.middle_features.keys()),
            'banner_features': list(self.banner_features),
            'device_types': list(self.device_types),
            'manufacturers': list(self.manufacturers),
            'models': list(self.models),
            'device_manufacturer_pairs': list(self.device_manufacturer_pairs),
            'manufacturer_model_pairs': list(self.manufacturer_model_pairs),
            'specific_devices': list(self.specific_devices),
            'created_at': datetime.now().isoformat()
        }
    
    def save_knowledge_graph(self, output_dir: str, knowledge_graph: Dict):
        """保存知识图谱"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存三元组
        triples_file = os.path.join(output_dir, 'extensible_triples.txt')
        with open(triples_file, 'w', encoding='utf-8') as f:
            for head, relation, tail in knowledge_graph['triples']:
                f.write(f"{head}\t{relation}\t{tail}\n")
        
        # 保存实体词汇表
        entity_vocab_file = os.path.join(output_dir, 'entity.vocab')
        with open(entity_vocab_file, 'w', encoding='utf-8') as f:
            for i, entity in enumerate(sorted(knowledge_graph['entities'])):
                f.write(f"{entity}\t{i}\n")
        
        # 保存关系词汇表
        relation_vocab_file = os.path.join(output_dir, 'relation.vocab')
        with open(relation_vocab_file, 'w', encoding='utf-8') as f:
            for i, relation in enumerate(sorted(knowledge_graph['relations'])):
                f.write(f"{relation}\t{i}\n")
        
        # 保存中层特征信息
        middle_layers_file = os.path.join(output_dir, 'middle_layers.json')
        with open(middle_layers_file, 'w', encoding='utf-8') as f:
            json.dump({
                'middle_layers': knowledge_graph['middle_layers'],
                'entity_counts': {
                    'banner_features': len(knowledge_graph['banner_features']),
                    'device_types': len(knowledge_graph['device_types']),
                    'manufacturers': len(knowledge_graph['manufacturers']),
                    'models': len(knowledge_graph['models']),
                    'device_manufacturer_pairs': len(knowledge_graph['device_manufacturer_pairs']),
                    'manufacturer_model_pairs': len(knowledge_graph['manufacturer_model_pairs']),
                    'specific_devices': len(knowledge_graph['specific_devices'])
                }
            }, f, ensure_ascii=False, indent=2)
        
        # 保存完整知识图谱
        graph_file = os.path.join(output_dir, 'extensible_knowledge_graph.json')
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
        
        print(f"知识图谱已保存到: {output_dir}")


def load_training_data_from_files(input_dir: str) -> List[Tuple[str, str]]:
    """从input目录加载训练数据"""
    training_data = []
    
    # 首先尝试加载JSON格式的示例文件
    json_file = os.path.join(input_dir, 'graph_entities.json')
    if os.path.exists(json_file):
        print(f"正在加载JSON格式训练数据: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            banner_text = item.get('banner', '')
            true_vendor = item.get('true_vendor', '')
            true_product = item.get('true_product', '')
            device_type = item.get('device_type', 'unknown')
            
            # 构建设备实体标识符
            device_entity = f"{device_type}_{true_vendor}_{true_product}"
            training_data.append((banner_text, device_entity))
        
        print(f"从JSON文件加载了 {len(training_data)} 条训练数据")
        return training_data
    
    # 如果没有JSON文件，尝试加载旧的文本格式
    banner_dir = os.path.join(input_dir, 'banner_and_lables')
    if not os.path.exists(banner_dir):
        print(f"错误: 没有找到训练数据文件")
        print(f"请确保以下文件之一存在:")
        print(f"  - {json_file}")
        print(f"  - {banner_dir}/")
        return training_data
    
    # 处理所有banner文件
    for filename in os.listdir(banner_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(banner_dir, filename)
            print(f"正在处理文件: {filename}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # 尝试解析JSON格式
                        data = json.loads(line)
                        banner_text = data.get('banner', '')
                        true_vendor = data.get('true_vendor', '')
                        true_product = data.get('true_product', '')
                        device_type = data.get('device_type', 'unknown')
                        
                        # 构建设备实体标识符
                        device_entity = f"{device_type}_{true_vendor}_{true_product}"
                        training_data.append((banner_text, device_entity))
                        
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，尝试其他格式
                        if '\t' in line:
                            parts = line.split('\t')
                            if len(parts) >= 2:
                                banner_text = parts[0]
                                device_entity = parts[1]
                                training_data.append((banner_text, device_entity))
                        elif ',' in line:
                            # 尝试CSV格式
                            parts = line.split(',')
                            if len(parts) >= 2:
                                banner_text = parts[0]
                                device_entity = parts[1]
                                training_data.append((banner_text, device_entity))
    
    print(f"加载了 {len(training_data)} 条训练数据")
    return training_data


def main():
    """主函数"""
    print("=" * 60)
    print("可扩展中层特征知识图谱构建器")
    print("=" * 60)
    
    # 1. 初始化构建器
    builder = ExtensibleKGEBuilder()
    
    # 2. 加载训练数据
    print("正在加载训练数据...")
    training_data = load_training_data_from_files('input')
    
    if not training_data:
        print("错误: 没有找到训练数据")
        print("请确保以下文件之一存在:")
        print("  - input/graph_entities.json (推荐)")
        print("  - input/banner_and_lables/ (旧格式)")
        return
    
    print(f"成功加载 {len(training_data)} 条训练数据")
    
    # 3. 构建知识图谱
    knowledge_graph = builder.build_knowledge_graph(training_data)
    
    # 4. 保存知识图谱
    output_dir = 'output/extensible_kge'
    builder.save_knowledge_graph(output_dir, knowledge_graph)
    
    # 5. 显示统计信息
    print(f"\n知识图谱统计:")
    print(f"  实体数量: {knowledge_graph['entity_count']}")
    print(f"  关系数量: {knowledge_graph['relation_count']}")
    print(f"  三元组数量: {knowledge_graph['triple_count']}")
    print(f"  中层特征层数: {len(knowledge_graph['middle_layers'])}")
    print(f"  设备类型: {len(knowledge_graph['device_types'])}")
    print(f"  厂商: {len(knowledge_graph['manufacturers'])}")
    print(f"  型号: {len(knowledge_graph['models'])}")
    print(f"  具体设备: {len(knowledge_graph['specific_devices'])}")
    
    print(f"\n输出文件:")
    print(f"  - {output_dir}/extensible_triples.txt")
    print(f"  - {output_dir}/entity.vocab")
    print(f"  - {output_dir}/relation.vocab")
    print(f"  - {output_dir}/extensible_knowledge_graph.json")


if __name__ == "__main__":
    main() 