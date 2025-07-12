#!/usr/bin/env python
# coding: utf-8
"""
集成可扩展中层特征的增强版知识图谱构建器
支持动态添加中层特征，自动重构知识图谱
"""

import os
import json
import re
import hashlib
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional, Any
from datetime import datetime

from extensible_middle_layer import ExtensibleMiddleLayer, KnowledgeGraphRebuilder

class EnhancedKGEBuilderWithExtensibleLayers:
    """集成可扩展中层特征的增强版知识图谱构建器"""
    
    def __init__(self, config_file: str = "../input_demo/build_middle_feature_result/middle_feature_config.json"):
        """
        初始化增强版构建器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        
        # 初始化可扩展中层特征管理器
        self.middle_layer_manager = ExtensibleMiddleLayer()
        
        # 知识图谱数据
        self.entities = set()
        self.relations = set()
        self.triples = []
        
        # 多层次实体
        self.banner_features = set()      # 底层：banner特征
        self.device_types = set()         # 高层：设备类型
        self.manufacturers = set()        # 高层：厂商
        self.specific_devices = set()     # 高层：具体设备
        
        # 用户自定义特征
        self.custom_features = {
            'banner_features': [],
            'device_indicators': [],
            'models': []
        }
        
        # 分词器（可选使用jieba等）
        self.tokenizer = None
        try:
            import jieba
            self.tokenizer = jieba
        except ImportError:
            print("jieba未安装，使用基础分词方法")
            self.tokenizer = None
    
    def add_custom_middle_layer(self, layer_config: Dict[str, Any]) -> bool:
        """
        添加自定义中层特征
        
        Args:
            layer_config: 中层特征配置
            
        Returns:
            bool: 是否添加成功
        """
        layer_id = layer_config.get('id', f"custom_layer_{len(self.middle_layer_manager.middle_layers)}")
        return self.middle_layer_manager.add_middle_layer(layer_id, layer_config)
    
    def update_middle_layer(self, layer_id: str, updates: Dict[str, Any]) -> bool:
        """更新中层特征"""
        return self.middle_layer_manager.update_middle_layer(layer_id, updates)
    
    def remove_middle_layer(self, layer_id: str) -> bool:
        """删除中层特征"""
        return self.middle_layer_manager.remove_middle_layer(layer_id)
    
    def enable_middle_layer(self, layer_id: str) -> bool:
        """启用中层特征"""
        return self.middle_layer_manager.enable_middle_layer(layer_id)
    
    def disable_middle_layer(self, layer_id: str) -> bool:
        """禁用中层特征"""
        return self.middle_layer_manager.disable_middle_layer(layer_id)
    
    def list_middle_layers(self) -> List[Dict]:
        """列出所有中层特征"""
        return self.middle_layer_manager.list_middle_layers()
    
    def add_knowledge_base_entry(self, layer_id: str, key: str, value: Any) -> bool:
        """添加知识库条目"""
        return self.middle_layer_manager.add_knowledge_base_entry(layer_id, key, value)
    
    def extract_enhanced_features_with_middle_layers(self, banner_text: str, device_entity: Optional[str] = None) -> Dict[str, List[str]]:
        """
        使用可扩展中层特征提取增强特征
        
        Args:
            banner_text: banner文本
            device_entity: 设备实体
            
        Returns:
            Dict[str, List[str]]: 提取的特征
        """
        features = {
            'banner_features': [],    # 底层特征
            'models': []              # 型号信息
        }
        
        # 1. 从用户自定义特征中添加
        features['banner_features'].extend(self.custom_features.get('banner_features', []))
        features['models'].extend(self.custom_features.get('models', []))
        
        # 2. 从banner文本中提取底层特征
        banner_features = self._extract_banner_features(banner_text)
        features['banner_features'].extend(banner_features)
        
        # 3. 从设备实体中提取特征（如果有）
        if device_entity:
            device_features = self._extract_device_features(device_entity)
            features['models'].extend(device_features['models'])
        
        # 4. 使用可扩展中层特征管理器提取中层特征
        middle_layer_features = self.middle_layer_manager.extract_middle_layer_features(banner_text, device_entity)
        features.update(middle_layer_features)
        
        # 去重
        for key in features:
            features[key] = list(set(features[key]))
        
        return features
    
    def _extract_banner_features(self, banner_text: str) -> List[str]:
        """从banner文本中提取底层特征"""
        features = []
        
        # 1. 提取HTTP头特征
        header_patterns = [
            r'Server:\s*([^\r\n]+)',
            r'WWW-Authenticate:\s*([^\r\n]+)',
            r'X-Powered-By:\s*([^\r\n]+)',
            r'Content-Type:\s*([^\r\n]+)',
            r'User-Agent:\s*([^\r\n]+)',
            r'Accept:\s*([^\r\n]+)',
            r'Accept-Language:\s*([^\r\n]+)',
            r'Accept-Encoding:\s*([^\r\n]+)',
            r'Connection:\s*([^\r\n]+)',
            r'Cache-Control:\s*([^\r\n]+)'
        ]
        
        for pattern in header_patterns:
            matches = re.findall(pattern, banner_text, re.IGNORECASE)
            for match in matches:
                features.append(match.strip())
        
        # 2. 分词提取特征
        word_features = self._tokenize_banner(banner_text)
        features.extend(word_features)
        
        # 3. 模式特征提取
        pattern_features = self._extract_pattern_features(banner_text)
        features.extend(pattern_features)
        
        return list(set(features))
    
    def _tokenize_banner(self, banner_text: str) -> List[str]:
        """分词处理banner文本"""
        features = []
        
        # 使用jieba分词（如果可用）
        if self.tokenizer:
            words = self.tokenizer.lcut(banner_text)
            features.extend([word for word in words if len(word) > 1])
        else:
            # 基础分词：按空格和特殊字符分割
            words = re.split(r'[\s\-_/\\]+', banner_text)
            features.extend([word for word in words if len(word) > 1])
        
        return features
    
    def _extract_pattern_features(self, banner_text: str) -> List[str]:
        """提取模式特征"""
        features = []
        
        # 提取版本号模式
        version_patterns = [
            r'\d+\.\d+\.\d+',
            r'\d+\.\d+',
            r'v\d+',
            r'version\s*\d+'
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, banner_text, re.IGNORECASE)
            features.extend(matches)
        
        # 提取IP地址模式
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_matches = re.findall(ip_pattern, banner_text)
        features.extend(ip_matches)
        
        return features
    
    def _extract_device_features(self, device_entity: str) -> Dict[str, List[str]]:
        """从设备实体中提取特征"""
        features = {
            'device_indicators': [],
            'models': []
        }
        
        # 解析设备实体
        device_info = self.parse_device_entity(device_entity)
        
        if device_info['manufacturer']:
            features['device_indicators'].append(device_info['manufacturer'])
        
        if device_info['model']:
            features['models'].append(device_info['model'])
        
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
    
    def build_extensible_knowledge_graph(self, training_data: List[Tuple[str, str]]) -> Dict:
        """
        构建可扩展的知识图谱
        
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
            
            # 提取增强特征（包含中层特征）
            features = self.extract_enhanced_features_with_middle_layers(banner_text, device_entity)
            
            # 解析设备实体
            device_info = self.parse_device_entity(device_entity)
            
            # 创建多层次实体
            self._create_multi_level_entities(device_info, features)
            
            # 创建增强三元组
            self._create_enhanced_triples_with_middle_layers(banner_text, device_info, features)
        
        # 构建中层特征关系
        self._build_middle_layer_relations()
        
        # 生成知识图谱
        knowledge_graph = self._get_extensible_knowledge_graph()
        
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
        
        # 高层：设备类型和厂商
        if device_info['type']:
            self.device_types.add(device_info['type'])
            self.entities.add(device_info['type'])
        
        if device_info['manufacturer']:
            self.manufacturers.add(device_info['manufacturer'])
            self.entities.add(device_info['manufacturer'])
        
        # 具体设备
        device_entity = f"{device_info['type']}_{device_info['manufacturer']}"
        if device_info['model']:
            device_entity += f"_{device_info['model']}"
        
        self.specific_devices.add(device_entity)
        self.entities.add(device_entity)
    
    def _create_enhanced_triples_with_middle_layers(self, banner_text: str, device_info: Dict, features: Dict[str, List[str]]):
        """创建包含中层特征的增强三元组"""
        banner_id = self._create_banner_id(banner_text)
        self.entities.add(banner_id)
        
        device_entity = f"{device_info['type']}_{device_info['manufacturer']}"
        if device_info['model']:
            device_entity += f"_{device_info['model']}"
        
        # 1. Banner到设备的基本关系
        self.triples.append((banner_id, "indicates_device", device_entity))
        self.relations.add("indicates_device")
        
        # 2. Banner到中层特征的关系
        for layer_id, layer_features in features.items():
            if layer_id in ['banner_features', 'models']:
                continue  # 跳过底层和高层特征
            
            for feature in layer_features:
                feature_entity = f"{layer_id}_{feature}"
                self.entities.add(feature_entity)
                
                # Banner包含中层特征
                relation = f"contains_{layer_id}"
                self.triples.append((banner_id, relation, feature_entity))
                self.relations.add(relation)
                
                # 中层特征到设备的关系映射
                self._create_middle_layer_to_device_mappings(feature_entity, layer_id, feature, device_info)
        
        # 3. Banner到底层特征的关系
        for feature in features.get('banner_features', []):
            self.triples.append((banner_id, "contains_feature", feature))
            self.relations.add("contains_feature")
        
        # 4. 设备到厂商和类型的关系
        if device_info['manufacturer']:
            self.triples.append((device_entity, "has_manufacturer", device_info['manufacturer']))
            self.relations.add("has_manufacturer")
        
        if device_info['type']:
            self.triples.append((device_entity, "is_type", device_info['type']))
            self.relations.add("is_type")
    
    def _create_middle_layer_to_device_mappings(self, feature_entity: str, layer_id: str, feature: str, device_info: Dict):
        """创建中层特征到设备的映射关系"""
        relation_mappings = self.middle_layer_manager.get_relation_mappings(layer_id)
        knowledge_base = self.middle_layer_manager.get_knowledge_base(layer_id)
        
        # 根据知识库创建映射关系
        if feature in knowledge_base:
            mappings = knowledge_base[feature]
            for target_type, target_value in mappings.items():
                if target_type in relation_mappings:
                    relation = relation_mappings[target_type]
                    self.triples.append((feature_entity, relation, target_value))
                    self.relations.add(relation)
        
        # 基于设备信息的直接映射
        if device_info['manufacturer'] and 'to_manufacturer' in relation_mappings:
            relation = relation_mappings['to_manufacturer']
            self.triples.append((feature_entity, relation, device_info['manufacturer']))
            self.relations.add(relation)
        
        if device_info['type'] and 'to_device_type' in relation_mappings:
            relation = relation_mappings['to_device_type']
            self.triples.append((feature_entity, relation, device_info['type']))
            self.relations.add(relation)
    
    def _build_middle_layer_relations(self):
        """构建中层特征之间的关系"""
        # 这里可以添加不同中层特征之间的关联关系
        # 例如：协议特征与安全特征的关联
        
        # 获取所有中层特征
        middle_layers = self.middle_layer_manager.list_middle_layers()
        
        # 创建中层特征之间的相似关系
        for layer1 in middle_layers:
            for layer2 in middle_layers:
                if layer1['id'] != layer2['id']:
                    # 可以基于知识库或规则创建关联关系
                    pass
    
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
    
    def _get_extensible_knowledge_graph(self) -> Dict:
        """获取可扩展知识图谱数据"""
        return {
            'entities': list(self.entities),
            'relations': list(self.relations),
            'triples': self.triples,
            'entity_count': len(self.entities),
            'relation_count': len(self.relations),
            'triple_count': len(self.triples),
            'middle_layers': self.middle_layer_manager.list_middle_layers(),
            'banner_features': list(self.banner_features),
            'device_types': list(self.device_types),
            'manufacturers': list(self.manufacturers),
            'specific_devices': list(self.specific_devices),
            'created_at': datetime.now().isoformat()
        }
    
    def save_extensible_knowledge_graph(self, output_dir: str, knowledge_graph: Dict):
        """保存可扩展知识图谱"""
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
                    'specific_devices': len(knowledge_graph['specific_devices'])
                }
            }, f, ensure_ascii=False, indent=2)
        
        # 保存完整知识图谱
        graph_file = os.path.join(output_dir, 'extensible_knowledge_graph.json')
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
        
        print(f"可扩展知识图谱已保存到: {output_dir}")
    
    def rebuild_knowledge_graph_with_new_layers(self, original_triples: List[Tuple[str, str, str]]) -> Dict:
        """使用新的中层特征重构知识图谱"""
        rebuilder = KnowledgeGraphRebuilder(self.middle_layer_manager)
        return rebuilder.rebuild_knowledge_graph(original_triples)


def load_training_data(data_file: str) -> List[Tuple[str, str]]:
    """加载训练数据"""
    training_data = []
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        banner_text = parts[0]
                        device_entity = parts[1]
                        training_data.append((banner_text, device_entity))
    
    return training_data


def demo_extensible_kge_builder():
    """演示可扩展KGE构建器"""
    print("=== 可扩展KGE构建器演示 ===")
    
    # 1. 初始化构建器
    builder = EnhancedKGEBuilderWithExtensibleLayers()
    
    # 2. 查看当前中层特征
    print("\n当前中层特征:")
    layers = builder.list_middle_layers()
    for layer in layers:
        print(f"  - {layer['id']}: {layer['name']} (优先级: {layer['priority']})")
    
    # 3. 添加新的中层特征
    print("\n添加新的中层特征...")
    new_layer_config = {
        'name': '端口特征',
        'description': '网络端口相关特征',
        'type': 'numeric',
        'priority': 5,
        'enabled': True,
        'examples': ['80', '443', '22', '21'],
        'extraction_rules': {
            'patterns': [
                r'port\s*(\d+)',
                r':(\d+)/',
                r'(\d{4,5})'
            ],
            'keywords': ['80', '443', '22', '21', '8080', '8443'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_service': 'indicates_service',
            'to_security': 'indicates_port_security'
        }
    }
    
    success = builder.add_custom_middle_layer(new_layer_config)
    print(f"添加端口特征层: {'成功' if success else '失败'}")
    
    # 4. 添加知识库条目
    print("\n添加知识库条目...")
    builder.add_knowledge_base_entry('port_features', '80', {
        'service': 'http',
        'security': 'insecure'
    })
    builder.add_knowledge_base_entry('port_features', '443', {
        'service': 'https',
        'security': 'secure'
    })
    builder.add_knowledge_base_entry('port_features', '22', {
        'service': 'ssh',
        'security': 'secure'
    })
    
    # 5. 模拟训练数据
    print("\n构建知识图谱...")
    training_data = [
        ("HTTP/1.1 401 Unauthorized\nServer: Hikvision-Webs\nWWW-Authenticate: Basic realm=\"Hikvision Camera\"", "camera_Hikvision_IPC"),
        ("HTTP/1.1 200 OK\nServer: Cisco-IOS\nX-Powered-By: Cisco", "router_Cisco_ISR"),
        ("HTTP/1.1 200 OK\nServer: Axis-Webs\nContent-Type: text/html", "camera_Axis_P3364")
    ]
    
    # 6. 构建知识图谱
    knowledge_graph = builder.build_extensible_knowledge_graph(training_data)
    
    # 7. 保存知识图谱
    print("\n保存知识图谱...")
    builder.save_extensible_knowledge_graph('output/extensible_kge', knowledge_graph)
    
    # 8. 显示统计信息
    print(f"\n知识图谱统计:")
    print(f"  实体数量: {knowledge_graph['entity_count']}")
    print(f"  关系数量: {knowledge_graph['relation_count']}")
    print(f"  三元组数量: {knowledge_graph['triple_count']}")
    print(f"  中层特征层数: {len(knowledge_graph['middle_layers'])}")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    demo_extensible_kge_builder() 