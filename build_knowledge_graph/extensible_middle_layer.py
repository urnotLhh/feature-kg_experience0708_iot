#!/usr/bin/env python
# coding: utf-8
"""
可扩展中层特征管理系统
支持动态添加中层特征，重构知识图谱数据库和关系
"""

import os
import json
import re
import hashlib
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional, Any
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtensibleMiddleLayer:
    """可扩展中层特征管理系统"""
    
    def __init__(self, config_file: str = "middle_layer_config.json"):
        """
        初始化可扩展中层特征管理系统
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.middle_layers = {}  # 中层特征定义
        self.extraction_rules = {}  # 提取规则
        self.relation_mappings = {}  # 关系映射
        self.knowledge_base = {}  # 知识库
        
        # 加载配置
        self.load_config()
        
        # 初始化默认中层特征
        self._initialize_default_layers()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.middle_layers = config.get('middle_layers', {})
                    self.extraction_rules = config.get('extraction_rules', {})
                    self.relation_mappings = config.get('relation_mappings', {})
                    self.knowledge_base = config.get('knowledge_base', {})
                logger.info(f"成功加载配置文件: {self.config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                self._initialize_default_layers()
        else:
            logger.info("配置文件不存在，使用默认配置")
            self._initialize_default_layers()
    
    def save_config(self):
        """保存配置文件"""
        config = {
            'middle_layers': self.middle_layers,
            'extraction_rules': self.extraction_rules,
            'relation_mappings': self.relation_mappings,
            'knowledge_base': self.knowledge_base,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置文件已保存: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def _initialize_default_layers(self):
        """初始化默认中层特征"""
        # 默认中层特征定义
        self.middle_layers = {
            'device_indicators': {
                'name': '设备标识',
                'description': '从banner中提取的设备标识特征',
                'type': 'text',
                'priority': 1,
                'enabled': True,
                'examples': ['Hikvision', 'Cisco', 'Axis', 'Dahua']
            },
            'protocol_features': {
                'name': '协议特征',
                'description': '网络协议相关特征',
                'type': 'text',
                'priority': 2,
                'enabled': True,
                'examples': ['HTTP/1.1', 'HTTPS', 'FTP', 'SSH']
            },
            'server_features': {
                'name': '服务器特征',
                'description': '服务器软件特征',
                'type': 'text',
                'priority': 3,
                'enabled': True,
                'examples': ['Apache', 'nginx', 'IIS', 'Tomcat']
            }
        }
        
        # 默认提取规则
        self.extraction_rules = {
            'device_indicators': {
                'patterns': [
                    r'Server:\s*([^\r\n]+)',
                    r'X-Powered-By:\s*([^\r\n]+)',
                    r'WWW-Authenticate:\s*([^\r\n]+)'
                ],
                'keywords': ['Hikvision', 'Cisco', 'Axis', 'Dahua', 'MikroTik'],
                'extraction_method': 'regex_and_keyword'
            },
            'protocol_features': {
                'patterns': [
                    r'HTTP/\d+\.\d+',
                    r'HTTPS',
                    r'FTP',
                    r'SSH'
                ],
                'keywords': ['HTTP', 'HTTPS', 'FTP', 'SSH', 'TCP', 'UDP'],
                'extraction_method': 'regex_and_keyword'
            },
            'server_features': {
                'patterns': [
                    r'Server:\s*(Apache|nginx|IIS|Tomcat)',
                    r'X-Powered-By:\s*(PHP|ASP\.NET|Java)'
                ],
                'keywords': ['Apache', 'nginx', 'IIS', 'Tomcat', 'PHP', 'ASP.NET'],
                'extraction_method': 'regex_and_keyword'
            }
        }
        
        # 默认关系映射
        self.relation_mappings = {
            'device_indicators': {
                'to_manufacturer': 'indicates_manufacturer',
                'to_device_type': 'indicates_device_type',
                'to_model': 'indicates_model'
            },
            'protocol_features': {
                'to_device_type': 'typical_protocol_for',
                'to_security': 'indicates_security_level'
            },
            'server_features': {
                'to_device_type': 'typical_server_for',
                'to_technology': 'indicates_technology'
            }
        }
    
    def add_middle_layer(self, layer_id: str, layer_config: Dict[str, Any]) -> bool:
        """
        添加新的中层特征
        
        Args:
            layer_id: 特征ID
            layer_config: 特征配置
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 验证配置
            required_fields = ['name', 'description', 'type']
            for field in required_fields:
                if field not in layer_config:
                    logger.error(f"缺少必需字段: {field}")
                    return False
            
            # 添加中层特征
            self.middle_layers[layer_id] = {
                'name': layer_config['name'],
                'description': layer_config['description'],
                'type': layer_config['type'],
                'priority': layer_config.get('priority', len(self.middle_layers) + 1),
                'enabled': layer_config.get('enabled', True),
                'examples': layer_config.get('examples', []),
                'created_at': datetime.now().isoformat()
            }
            
            # 添加提取规则
            if 'extraction_rules' in layer_config:
                self.extraction_rules[layer_id] = layer_config['extraction_rules']
            
            # 添加关系映射
            if 'relation_mappings' in layer_config:
                self.relation_mappings[layer_id] = layer_config['relation_mappings']
            
            logger.info(f"成功添加中层特征: {layer_id}")
            self.save_config()
            return True
            
        except Exception as e:
            logger.error(f"添加中层特征失败: {e}")
            return False
    
    def update_middle_layer(self, layer_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新中层特征
        
        Args:
            layer_id: 特征ID
            updates: 更新内容
            
        Returns:
            bool: 是否更新成功
        """
        if layer_id not in self.middle_layers:
            logger.error(f"中层特征不存在: {layer_id}")
            return False
        
        try:
            # 更新特征定义
            for key, value in updates.items():
                if key in self.middle_layers[layer_id]:
                    self.middle_layers[layer_id][key] = value
            
            # 更新提取规则
            if 'extraction_rules' in updates:
                self.extraction_rules[layer_id] = updates['extraction_rules']
            
            # 更新关系映射
            if 'relation_mappings' in updates:
                self.relation_mappings[layer_id] = updates['relation_mappings']
            
            self.middle_layers[layer_id]['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"成功更新中层特征: {layer_id}")
            self.save_config()
            return True
            
        except Exception as e:
            logger.error(f"更新中层特征失败: {e}")
            return False
    
    def remove_middle_layer(self, layer_id: str) -> bool:
        """
        删除中层特征
        
        Args:
            layer_id: 特征ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if layer_id in self.middle_layers:
                del self.middle_layers[layer_id]
            
            if layer_id in self.extraction_rules:
                del self.extraction_rules[layer_id]
            
            if layer_id in self.relation_mappings:
                del self.relation_mappings[layer_id]
            
            logger.info(f"成功删除中层特征: {layer_id}")
            self.save_config()
            return True
            
        except Exception as e:
            logger.error(f"删除中层特征失败: {e}")
            return False
    
    def enable_middle_layer(self, layer_id: str) -> bool:
        """启用中层特征"""
        return self.update_middle_layer(layer_id, {'enabled': True})
    
    def disable_middle_layer(self, layer_id: str) -> bool:
        """禁用中层特征"""
        return self.update_middle_layer(layer_id, {'enabled': False})
    
    def extract_middle_layer_features(self, banner_text: str, device_entity: Optional[str] = None) -> Dict[str, List[str]]:
        """
        提取所有启用的中层特征
        
        Args:
            banner_text: banner文本
            device_entity: 设备实体
            
        Returns:
            Dict[str, List[str]]: 提取的特征
        """
        features = {}
        
        # 按优先级排序
        sorted_layers = sorted(
            self.middle_layers.items(),
            key=lambda x: x[1].get('priority', 999)
        )
        
        for layer_id, layer_config in sorted_layers:
            if not layer_config.get('enabled', True):
                continue
            
            if layer_id in self.extraction_rules:
                layer_features = self._extract_layer_features(
                    layer_id, banner_text, device_entity
                )
                features[layer_id] = layer_features
        
        return features
    
    def _extract_layer_features(self, layer_id: str, banner_text: str, device_entity: Optional[str] = None) -> List[str]:
        """提取特定层的特征"""
        features = []
        rules = self.extraction_rules.get(layer_id, {})
        
        # 正则表达式提取
        patterns = rules.get('patterns', [])
        for pattern in patterns:
            matches = re.findall(pattern, banner_text, re.IGNORECASE)
            features.extend([match.strip() for match in matches if match.strip()])
        
        # 关键词匹配
        keywords = rules.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in banner_text.lower():
                features.append(keyword)
        
        # 自定义提取方法
        extraction_method = rules.get('extraction_method', 'regex_and_keyword')
        if extraction_method == 'custom' and 'custom_function' in rules:
            # 这里可以添加自定义提取函数
            pass
        
        # 去重
        features = list(set(features))
        
        return features
    
    def get_relation_mappings(self, layer_id: str) -> Dict[str, str]:
        """获取特定层的关系映射"""
        return self.relation_mappings.get(layer_id, {})
    
    def add_knowledge_base_entry(self, layer_id: str, key: str, value: Any) -> bool:
        """添加知识库条目"""
        if layer_id not in self.knowledge_base:
            self.knowledge_base[layer_id] = {}
        
        self.knowledge_base[layer_id][key] = value
        self.save_config()
        return True
    
    def get_knowledge_base(self, layer_id: Optional[str] = None) -> Dict:
        """获取知识库"""
        if layer_id:
            return self.knowledge_base.get(layer_id, {})
        return self.knowledge_base
    
    def list_middle_layers(self) -> List[Dict]:
        """列出所有中层特征"""
        layers = []
        for layer_id, config in self.middle_layers.items():
            layer_info = {
                'id': layer_id,
                'name': config['name'],
                'description': config['description'],
                'type': config['type'],
                'priority': config.get('priority', 999),
                'enabled': config.get('enabled', True),
                'examples': config.get('examples', []),
                'created_at': config.get('created_at'),
                'updated_at': config.get('updated_at')
            }
            layers.append(layer_info)
        
        return sorted(layers, key=lambda x: x['priority'])
    
    def export_config(self, output_file: str) -> bool:
        """导出配置到文件"""
        try:
            config = {
                'middle_layers': self.middle_layers,
                'extraction_rules': self.extraction_rules,
                'relation_mappings': self.relation_mappings,
                'knowledge_base': self.knowledge_base,
                'exported_at': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已导出到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, input_file: str) -> bool:
        """从文件导入配置"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.middle_layers = config.get('middle_layers', {})
            self.extraction_rules = config.get('extraction_rules', {})
            self.relation_mappings = config.get('relation_mappings', {})
            self.knowledge_base = config.get('knowledge_base', {})
            
            self.save_config()
            logger.info(f"配置已从文件导入: {input_file}")
            return True
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False


class KnowledgeGraphRebuilder:
    """知识图谱重构器"""
    
    def __init__(self, middle_layer_manager: ExtensibleMiddleLayer):
        """
        初始化知识图谱重构器
        
        Args:
            middle_layer_manager: 中层特征管理器
        """
        self.middle_layer_manager = middle_layer_manager
        self.original_triples = []
        self.rebuilt_triples = []
        self.new_entities = set()
        self.new_relations = set()
    
    def rebuild_knowledge_graph(self, original_triples: List[Tuple[str, str, str]]) -> Dict:
        """
        重构知识图谱
        
        Args:
            original_triples: 原始三元组列表
            
        Returns:
            Dict: 重构后的知识图谱
        """
        self.original_triples = original_triples
        self.rebuilt_triples = []
        self.new_entities = set()
        self.new_relations = set()
        
        logger.info("开始重构知识图谱...")
        
        # 1. 分析原始三元组
        banner_entities = set()
        device_entities = set()
        
        for head, relation, tail in original_triples:
            if relation == 'indicates_device':
                banner_entities.add(head)
                device_entities.add(tail)
        
        # 2. 为每个banner提取中层特征
        for banner_entity in banner_entities:
            # 这里需要从原始数据中获取banner文本
            banner_text = self._get_banner_text(banner_entity)
            if banner_text:
                self._process_banner_with_middle_layers(banner_entity, banner_text)
        
        # 3. 构建新的三元组
        self._build_new_triples()
        
        # 4. 生成重构报告
        report = self._generate_rebuild_report()
        
        logger.info("知识图谱重构完成")
        return report
    
    def _get_banner_text(self, banner_entity: str) -> Optional[str]:
        """获取banner文本（这里需要根据实际情况实现）"""
        # 这里应该从原始数据中获取banner文本
        # 暂时返回None，实际使用时需要实现
        return None
    
    def _process_banner_with_middle_layers(self, banner_entity: str, banner_text: str):
        """使用中层特征处理banner"""
        # 提取中层特征
        middle_features = self.middle_layer_manager.extract_middle_layer_features(banner_text)
        
        # 为每个中层特征创建三元组
        for layer_id, features in middle_features.items():
            for feature in features:
                # 创建特征实体
                feature_entity = f"{layer_id}_{feature}"
                self.new_entities.add(feature_entity)
                
                # 创建banner到特征的关系
                relation = f"contains_{layer_id}"
                self.new_relations.add(relation)
                self.rebuilt_triples.append((banner_entity, relation, feature_entity))
                
                # 创建特征到设备的关系映射
                self._create_feature_to_device_mappings(feature_entity, layer_id, feature)
    
    def _create_feature_to_device_mappings(self, feature_entity: str, layer_id: str, feature: str):
        """创建特征到设备的映射关系"""
        relation_mappings = self.middle_layer_manager.get_relation_mappings(layer_id)
        knowledge_base = self.middle_layer_manager.get_knowledge_base(layer_id)
        
        # 根据知识库创建映射关系
        if feature in knowledge_base:
            mappings = knowledge_base[feature]
            for target_type, target_value in mappings.items():
                if target_type in relation_mappings:
                    relation = relation_mappings[target_type]
                    self.new_relations.add(relation)
                    self.rebuilt_triples.append((feature_entity, relation, target_value))
    
    def _build_new_triples(self):
        """构建新的三元组"""
        # 添加原始三元组
        self.rebuilt_triples.extend(self.original_triples)
        
        # 添加中层特征之间的关联关系
        self._add_middle_layer_relations()
    
    def _add_middle_layer_relations(self):
        """添加中层特征之间的关联关系"""
        # 这里可以添加不同中层特征之间的关联关系
        # 例如：协议特征与服务器特征的关联
        pass
    
    def _generate_rebuild_report(self) -> Dict:
        """生成重构报告"""
        return {
            'original_triples_count': len(self.original_triples),
            'rebuilt_triples_count': len(self.rebuilt_triples),
            'new_entities_count': len(self.new_entities),
            'new_relations_count': len(self.new_relations),
            'new_entities': list(self.new_entities),
            'new_relations': list(self.new_relations),
            'rebuilt_triples': self.rebuilt_triples,
            'middle_layers_used': list(self.middle_layer_manager.middle_layers.keys()),
            'rebuild_timestamp': datetime.now().isoformat()
        }
    
    def save_rebuilt_knowledge_graph(self, output_dir: str, report: Dict):
        """保存重构后的知识图谱"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存三元组
        triples_file = os.path.join(output_dir, 'rebuilt_triples.txt')
        with open(triples_file, 'w', encoding='utf-8') as f:
            for head, relation, tail in report['rebuilt_triples']:
                f.write(f"{head}\t{relation}\t{tail}\n")
        
        # 保存实体词汇表
        entities = set()
        relations = set()
        for head, relation, tail in report['rebuilt_triples']:
            entities.add(head)
            entities.add(tail)
            relations.add(relation)
        
        entity_vocab_file = os.path.join(output_dir, 'entity.vocab')
        with open(entity_vocab_file, 'w', encoding='utf-8') as f:
            for i, entity in enumerate(sorted(entities)):
                f.write(f"{entity}\t{i}\n")
        
        relation_vocab_file = os.path.join(output_dir, 'relation.vocab')
        with open(relation_vocab_file, 'w', encoding='utf-8') as f:
            for i, relation in enumerate(sorted(relations)):
                f.write(f"{relation}\t{i}\n")
        
        # 保存重构报告
        report_file = os.path.join(output_dir, 'rebuild_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"重构后的知识图谱已保存到: {output_dir}")


def demo_extensible_middle_layer():
    """演示可扩展中层特征系统"""
    print("=== 可扩展中层特征系统演示 ===")
    
    # 1. 初始化系统
    middle_layer_manager = ExtensibleMiddleLayer()
    
    # 2. 查看当前中层特征
    print("\n当前中层特征:")
    layers = middle_layer_manager.list_middle_layers()
    for layer in layers:
        print(f"  - {layer['id']}: {layer['name']} (优先级: {layer['priority']})")
    
    # 3. 添加新的中层特征
    print("\n添加新的中层特征...")
    new_layer_config = {
        'name': '安全特征',
        'description': '设备安全相关特征',
        'type': 'text',
        'priority': 4,
        'enabled': True,
        'examples': ['SSL', 'TLS', 'Basic Auth', 'Digest Auth'],
        'extraction_rules': {
            'patterns': [
                r'WWW-Authenticate:\s*(Basic|Digest)',
                r'SSL|TLS',
                r'Certificate'
            ],
            'keywords': ['SSL', 'TLS', 'Basic', 'Digest', 'Certificate', 'Auth'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_security_level': 'indicates_security_level',
            'to_authentication': 'indicates_authentication_type'
        }
    }
    
    success = middle_layer_manager.add_middle_layer('security_features', new_layer_config)
    print(f"添加安全特征层: {'成功' if success else '失败'}")
    
    # 4. 添加知识库条目
    print("\n添加知识库条目...")
    middle_layer_manager.add_knowledge_base_entry('security_features', 'SSL', {
        'security_level': 'high',
        'authentication_type': 'certificate_based'
    })
    middle_layer_manager.add_knowledge_base_entry('security_features', 'Basic Auth', {
        'security_level': 'low',
        'authentication_type': 'password_based'
    })
    
    # 5. 提取特征示例
    print("\n特征提取示例:")
    banner_text = """
    HTTP/1.1 401 Unauthorized
    Server: Hikvision-Webs
    WWW-Authenticate: Basic realm="Hikvision Camera"
    Content-Type: text/html
    """
    
    features = middle_layer_manager.extract_middle_layer_features(banner_text)
    for layer_id, layer_features in features.items():
        print(f"  {layer_id}: {layer_features}")
    
    # 6. 知识图谱重构示例
    print("\n知识图谱重构示例:")
    rebuilder = KnowledgeGraphRebuilder(middle_layer_manager)
    
    # 模拟原始三元组
    original_triples = [
        ("banner_001", "indicates_device", "camera_Hikvision"),
        ("banner_002", "indicates_device", "router_Cisco")
    ]
    
    # 这里需要实际的banner文本才能完整演示重构过程
    print("  注意: 完整重构需要实际的banner文本数据")
    
    # 7. 导出配置
    print("\n导出配置...")
    middle_layer_manager.export_config('middle_layer_config_export.json')
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    demo_extensible_middle_layer() 