#!/usr/bin/env python
# coding: utf-8
"""
增强版知识图谱构建器
结合多层次实体设计和丰富的关联关系
"""

import os
import json
import re
import hashlib
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional

class EnhancedKGEBuilder:
    def __init__(self, custom_features: Optional[Dict[str, List[str]]] = None):
        """初始化增强版知识图谱构建器"""
        # 多层次实体
        self.banner_features = set()      # 底层：banner特征
        self.device_indicators = set()    # 中层：设备标识
        self.device_types = set()         # 高层：设备类型
        self.manufacturers = set()        # 高层：厂商
        self.specific_devices = set()     # 高层：具体设备
        
        # 关系类型
        self.relations = set()
        self.training_triples = []
        
        # 用户自定义特征
        self.custom_features = custom_features or {
            'banner_features': [],
            'device_indicators': [],
            'models': []
        }
        
        # 增强版关系类型
        self.enhanced_relations = {
            # Banner特征层关系
            'contains_feature': 'banner特征包含关系',
            'indicates_manufacturer': '特征指示厂商',
            'indicates_device_type': '特征指示设备类型',
            'indicates_model': '特征指示型号',
            
            # 设备标识层关系
            'brand_of': '品牌属于厂商',
            'typical_for': '典型用于设备类型',
            'derived_from': '来源于',
            
            # 设备层关系
            'has_manufacturer': '设备有厂商',
            'is_type': '设备属于类型',
            'has_model': '设备有型号',
            'similar_to': '设备相似关系',
            
            # 复合关系
            'composed_of': '由...组成',
            'correlates_with': '与...相关',
            'indicates_device': '指示设备'
        }
        
        # 预定义的知识库
        self.knowledge_base = self._initialize_knowledge_base()
        
        # 分词器（可选使用jieba等）
        self.tokenizer = None
        try:
            import jieba
            self.tokenizer = jieba
        except ImportError:
            print("jieba未安装，使用基础分词方法")
            self.tokenizer = None
    
    def _initialize_knowledge_base(self) -> Dict:
        """初始化知识库"""
        return {
            # Banner特征到厂商的映射
            'banner_to_manufacturer': {
                'Server:Hikvision-Webs': 'Hikvision',
                'Server:Cisco-IOS': 'Cisco',
                'Server:Axis-Webs': 'Axis',
                'Server:Dahua-Webs': 'Dahua',
                'Server:MikroTik': 'MikroTik',
                'X-Powered-By:Cisco': 'Cisco',
                'WWW-Authenticate:Basic realm="Axis Camera"': 'Axis',
                'Hikvision': 'Hikvision',
                'Cisco': 'Cisco',
                'Axis': 'Axis',
                'Dahua': 'Dahua',
                'MikroTik': 'MikroTik',
                'D-Link': 'D-Link'
            },
            
            # Banner特征到设备类型的映射
            'banner_to_device_type': {
                'Server:Hikvision-Webs': 'camera',
                'Server:Cisco-IOS': 'router',
                'Server:Axis-Webs': 'camera',
                'Server:Dahua-Webs': 'camera',
                'Server:MikroTik': 'router',
                'X-Powered-By:Cisco': 'router',
                'camera': 'camera',
                'router': 'router',
                'printer': 'printer',
                'switch': 'switch',
                'firewall': 'firewall',
                'IPC': 'camera',
                'NVR': 'recorder',
                'DVR': 'recorder'
            },
            
            # 厂商典型设备类型
            'manufacturer_typical_types': {
                'Hikvision': 'camera',
                'Cisco': 'router',
                'Axis': 'camera',
                'Dahua': 'camera',
                'MikroTik': 'router',
                'D-Link': 'router',
                'TP-Link': 'router'
            },
            
            # 设备相似关系
            'similar_devices': {
                'camera_Hikvision': ['camera_Axis', 'camera_Dahua'],
                'camera_Axis': ['camera_Hikvision', 'camera_Dahua'],
                'camera_Dahua': ['camera_Hikvision', 'camera_Axis'],
                'router_Cisco': ['router_MikroTik', 'router_D-Link'],
                'router_MikroTik': ['router_Cisco', 'router_D-Link'],
                'router_D-Link': ['router_Cisco', 'router_MikroTik']
            }
        }
    

    
    def set_custom_features(self, custom_features: Dict[str, List[str]]):
        """设置用户自定义特征"""
        self.custom_features = custom_features
    
    def add_custom_features(self, feature_type: str, features: List[str]):
        """添加用户自定义特征"""
        if feature_type not in self.custom_features:
            self.custom_features[feature_type] = []
        self.custom_features[feature_type].extend(features)
    
    def extract_enhanced_features(self, banner_text: str, device_entity: Optional[str] = None) -> Dict[str, List[str]]:
        """增强版特征提取 - 支持训练集提取和用户自定义特征"""
        features = {
            'banner_features': [],    # 底层特征
            'device_indicators': [],  # 中层标识
            'models': []              # 型号信息
        }
        
        # 1. 从用户自定义特征中添加
        features['banner_features'].extend(self.custom_features.get('banner_features', []))
        features['device_indicators'].extend(self.custom_features.get('device_indicators', []))
        features['models'].extend(self.custom_features.get('models', []))
        
        # 2. 从banner文本中提取特征
        banner_features = self._extract_banner_features(banner_text)
        features['banner_features'].extend(banner_features)
        
        # 3. 从设备实体中提取特征（如果有）
        if device_entity:
            device_features = self._extract_device_features(device_entity)
            features['device_indicators'].extend(device_features['device_indicators'])
            features['models'].extend(device_features['models'])
        
        # 去重
        features['banner_features'] = list(set(features['banner_features']))
        features['device_indicators'] = list(set(features['device_indicators']))
        features['models'] = list(set(features['models']))
        
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
        
        # 3. 提取特殊模式
        pattern_features = self._extract_pattern_features(banner_text)
        features.extend(pattern_features)
        
        return list(set(features))  # 去重
    
    def _tokenize_banner(self, banner_text: str) -> List[str]:
        """对banner进行分词"""
        features = []
        
        # 预处理：移除HTTP状态行和常见HTTP头
        text = re.sub(r'HTTP/\d\.\d\s+\d+\s+[^\r\n]+', '', banner_text)
        text = re.sub(r'[A-Za-z-]+:\s*[^\r\n]+', '', text)
        
        # 使用分词器或基础分词
        if self.tokenizer:
            # 使用jieba分词
            words = self.tokenizer.lcut(text)
        else:
            # 基础分词：按标点符号和空格分割
            words = re.split(r'[^\w\u4e00-\u9fff]+', text)
        
        # 过滤和清理
        for word in words:
            word = word.strip()
            if len(word) >= 2 and word.isalnum():  # 至少2个字符且为字母数字
                # 过滤常见无意义词汇
                if word.lower() not in ['html', 'body', 'head', 'title', 'div', 'span', 'p', 'h1', 'h2', 'h3']:
                    features.append(word)
        
        return features
    
    def _extract_pattern_features(self, banner_text: str) -> List[str]:
        """提取特殊模式特征"""
        features = []
        
        # 提取版本号模式
        version_patterns = [
            r'\b\d+\.\d+(?:\.\d+)?\b',  # 1.0, 1.0.1, 2.1.3
            r'\bv\d+\.\d+\b',           # v1.0, v2.1
            r'\b[A-Z]+\d+\.\d+\b'       # HTTP1.1, TLS1.2
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, banner_text, re.IGNORECASE)
            features.extend(matches)
        
        # 提取端口号
        port_matches = re.findall(r':(\d{4,5})\b', banner_text)
        features.extend([f"port_{port}" for port in port_matches])
        
        # 提取协议
        protocol_matches = re.findall(r'\b(https?|ftp|ssh|telnet|smtp|pop3|imap)\b', banner_text, re.IGNORECASE)
        features.extend(protocol_matches)
        
        return features
    
    def _extract_device_features(self, device_entity: str) -> Dict[str, List[str]]:
        """从设备实体中提取特征"""
        features = {
            'device_indicators': [],
            'models': []
        }
        
        # 按_分割设备实体
        parts = device_entity.split('_')
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 判断是否为型号（包含数字的模式）
            if re.search(r'\d', part):
                features['models'].append(part)
            else:
                # 判断是否为设备类型或厂商
                if part.lower() in ['camera', 'router', 'printer', 'switch', 'firewall', 'recorder', 'server', 'nas']:
                    features['device_indicators'].append(part)
                elif part.lower() in ['hikvision', 'cisco', 'axis', 'dahua', 'mikrotik', 'dlink', 'tplink', 'netgear', 'asus']:
                    features['device_indicators'].append(part)
                else:
                    # 其他可能是型号或特殊标识
                    features['models'].append(part)
        
        return features
    
    def parse_enhanced_device_entity(self, device_entity: str) -> Dict[str, str]:
        """增强版设备实体解析"""
        parts = device_entity.split('_')
        
        if len(parts) >= 3:
            device_type = parts[0]  # 设备类型
            manufacturer = parts[1]  # 厂商
            model = '_'.join(parts[2:])  # 型号
        elif len(parts) == 2:
            device_type = parts[0]
            manufacturer = parts[1]
            model = 'unknown'
        else:
            device_type = 'unknown'
            manufacturer = parts[0]     # 如果只有一个就是厂商
            model = 'unknown'
        
        return {
            'device_type': device_type,
            'manufacturer': manufacturer,
            'model': model,
            'full_entity': device_entity,
            'specific_device': f"{device_type}_{manufacturer}" if device_type != 'unknown' and manufacturer != 'unknown' else 'unknown'
        }
    
    def build_enhanced_knowledge_graph(self, training_data: List[Tuple[str, str]]) -> Dict:
        """构建增强版知识图谱"""
        print("开始构建增强版知识图谱...")
        
        # 第一步：处理训练数据
        for banner_text, device_entity in training_data:
            # 解析设备实体
            device_info = self.parse_enhanced_device_entity(device_entity)
            
            # 提取增强特征
            features = self.extract_enhanced_features(banner_text)
            
            # 创建多层次实体
            self._create_multi_level_entities(device_info, features)
            
            # 创建增强三元组
            self._create_enhanced_triples(banner_text, device_info, features)
        
        # 第二步：构建增强关系
        self._build_enhanced_relations()
        
        # 第三步：构建知识图谱
        return self._get_enhanced_knowledge_graph()
    
    def _create_multi_level_entities(self, device_info: Dict, features: Dict[str, List[str]]):
        """创建多层次实体"""
        # 底层：banner特征
        self.banner_features.update(features['banner_features'])
        
        # 中层：设备标识
        self.device_indicators.update(features['device_indicators'])
        
        # 高层：设备类型和厂商
        if device_info['device_type'] != 'unknown':
            self.device_types.add(device_info['device_type'])
        if device_info['manufacturer'] != 'unknown':
            self.manufacturers.add(device_info['manufacturer'])
        
        # 高层：具体设备
        if device_info['specific_device'] != 'unknown':
            self.specific_devices.add(device_info['specific_device'])
    
    def _create_enhanced_triples(self, banner_text: str, device_info: Dict, features: Dict[str, List[str]]):
        """创建增强版三元组"""
        banner_id = self._create_banner_id(banner_text)
        
        # 1. Banner与特征的关系（底层）
        for feature in features['banner_features']:
            self.training_triples.append((banner_id, 'contains_feature', feature))
            self.relations.add('contains_feature')
        
        # 2. Banner与设备标识的关系（中层）
        for indicator in features['device_indicators']:
            self.training_triples.append((banner_id, 'indicates_device', indicator))
            self.relations.add('indicates_device')
        
        # 3. 特征与厂商的关系
        for feature in features['banner_features'] + features['device_indicators']:
            if feature in self.knowledge_base['banner_to_manufacturer']:
                manufacturer = self.knowledge_base['banner_to_manufacturer'][feature]
                self.training_triples.append((feature, 'indicates_manufacturer', manufacturer))
                self.relations.add('indicates_manufacturer')
        
        # 4. 特征与设备类型的关系
        for feature in features['banner_features'] + features['device_indicators']:
            if feature in self.knowledge_base['banner_to_device_type']:
                device_type = self.knowledge_base['banner_to_device_type'][feature]
                self.training_triples.append((feature, 'indicates_device_type', device_type))
                self.relations.add('indicates_device_type')
        
        # 5. 厂商与设备类型的关系
        if device_info['manufacturer'] != 'unknown' and device_info['manufacturer'] in self.knowledge_base['manufacturer_typical_types']:
            typical_type = self.knowledge_base['manufacturer_typical_types'][device_info['manufacturer']]
            self.training_triples.append((device_info['manufacturer'], 'typical_for', typical_type))
            self.relations.add('typical_for')
        
        # 6. 具体设备的关系
        if device_info['specific_device'] != 'unknown':
            if device_info['manufacturer'] != 'unknown':
                self.training_triples.append((device_info['specific_device'], 'has_manufacturer', device_info['manufacturer']))
                self.relations.add('has_manufacturer')
            
            if device_info['device_type'] != 'unknown':
                self.training_triples.append((device_info['specific_device'], 'is_type', device_info['device_type']))
                self.relations.add('is_type')
            
            if device_info['model'] != 'unknown':
                self.training_triples.append((device_info['specific_device'], 'has_model', device_info['model']))
                self.relations.add('has_model')
        
        # 7. 复合关系
        if device_info['specific_device'] != 'unknown':
            if device_info['manufacturer'] != 'unknown':
                self.training_triples.append((device_info['specific_device'], 'composed_of', device_info['manufacturer']))
                self.relations.add('composed_of')
            
            if device_info['device_type'] != 'unknown':
                self.training_triples.append((device_info['specific_device'], 'composed_of', device_info['device_type']))
                self.relations.add('composed_of')
    
    def _build_enhanced_relations(self):
        """构建增强关系"""
        # 1. 设备相似关系
        for device, similar_devices in self.knowledge_base['similar_devices'].items():
            if device in self.specific_devices:
                for similar_device in similar_devices:
                    if similar_device in self.specific_devices:
                        self.training_triples.append((device, 'similar_to', similar_device))
                        self.relations.add('similar_to')
        
        # 2. 特征相关性关系
        for feature in self.banner_features:
            if feature in self.knowledge_base['banner_to_manufacturer']:
                manufacturer = self.knowledge_base['banner_to_manufacturer'][feature]
                if manufacturer in self.knowledge_base['manufacturer_typical_types']:
                    device_type = self.knowledge_base['manufacturer_typical_types'][manufacturer]
                    self.training_triples.append((feature, 'correlates_with', device_type))
                    self.relations.add('correlates_with')
        
        # 3. 派生关系
        for feature in self.banner_features:
            if feature in self.knowledge_base['banner_to_manufacturer']:
                manufacturer = self.knowledge_base['banner_to_manufacturer'][feature]
                self.training_triples.append((feature, 'derived_from', manufacturer))
                self.relations.add('derived_from')
    
    def _create_banner_id(self, banner_text: str) -> str:
        """为banner创建ID"""
        normalized = self._normalize_banner(banner_text)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()[:16]
    
    def _normalize_banner(self, banner_text: str) -> str:
        """标准化banner"""
        if not banner_text:
            return ""
        
        banner = banner_text.lower()
        banner = re.sub(r'\s+', ' ', banner)
        banner = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', banner)
        banner = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '[TIME]', banner)
        
        return banner.strip()
    
    def _get_enhanced_knowledge_graph(self) -> Dict:
        """获取增强版知识图谱"""
        return {
            'entities': {
                'banner_features': list(self.banner_features),
                'device_indicators': list(self.device_indicators),
                'device_types': list(self.device_types),
                'manufacturers': list(self.manufacturers),
                'specific_devices': list(self.specific_devices)
            },
            'relations': list(self.relations),
            'triples': self.training_triples,
            'relation_descriptions': {rel: self.enhanced_relations.get(rel, '') for rel in self.relations},
            'statistics': {
                'total_entities': len(self.banner_features) + len(self.device_indicators) + 
                                len(self.device_types) + len(self.manufacturers) + len(self.specific_devices),
                'total_relations': len(self.relations),
                'total_triples': len(self.training_triples),
                'banner_features': len(self.banner_features),
                'device_indicators': len(self.device_indicators),
                'device_types': len(self.device_types),
                'manufacturers': len(self.manufacturers),
                'specific_devices': len(self.specific_devices)
            }
        }
    
    def save_enhanced_knowledge_graph(self, output_dir: str, knowledge_graph: Dict):
        """保存增强版知识图谱"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存三元组数据
        triples_file = os.path.join(output_dir, 'enhanced_triples.txt')
        with open(triples_file, 'w', encoding='utf-8') as f:
            for h, r, t in knowledge_graph['triples']:
                f.write(f"{h}\t{r}\t{t}\n")
        
        # 保存实体和关系映射
        entity_file = os.path.join(output_dir, 'enhanced_entities.json')
        relation_file = os.path.join(output_dir, 'enhanced_relations.json')
        
        with open(entity_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_graph['entities'], f, ensure_ascii=False, indent=2)
        
        with open(relation_file, 'w', encoding='utf-8') as f:
            json.dump({
                'relations': knowledge_graph['relations'],
                'descriptions': knowledge_graph['relation_descriptions']
            }, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = os.path.join(output_dir, 'enhanced_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_graph['statistics'], f, ensure_ascii=False, indent=2)
        
        print(f"增强版知识图谱已保存到: {output_dir}")
        print(f"三元组数量: {knowledge_graph['statistics']['total_triples']}")
        print(f"实体数量: {knowledge_graph['statistics']['total_entities']}")
        print(f"关系类型: {knowledge_graph['statistics']['total_relations']}")

def load_training_data(data_file: str) -> List[Tuple[str, str]]:
    """加载训练数据"""
    training_data = []
    
    if data_file.endswith('.txt'):
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '\t' in line:
                    banner, device = line.split('\t', 1)
                    training_data.append((banner, device))
    
    return training_data

def main():
    """主函数"""
    print("=== 增强版知识图谱构建器 ===")
    
    # 示例训练数据
    sample_data = [
        ("HTTP/1.1 200 OK\nServer: Hikvision-Webs\nContent-Type: text/html\n\n<html><title>Hikvision</title><body><h1>Hikvision Camera</h1><p>Model: DS-2CD2342-I</p></body></html>", "camera_Hikvision_DS-2CD2342-I"),
        ("HTTP/1.1 200 OK\nServer: Cisco-IOS\nX-Powered-By: Cisco\nContent-Type: text/html\n\n<html><title>Cisco Router</title><body><h1>Cisco Router Management</h1><p>Model: ISR4321</p></body></html>", "router_Cisco_ISR4321"),
        ("HTTP/1.1 200 OK\nServer: Axis-Webs\nWWW-Authenticate: Basic realm=\"Axis Camera\"\nContent-Type: text/html\n\n<html><title>Axis</title><body><h1>Axis Camera</h1><p>Model: P3364-V</p></body></html>", "camera_Axis_P3364-V")
    ]
    
    # 创建增强版构建器
    builder = EnhancedKGEBuilder()
    
    # 构建知识图谱
    knowledge_graph = builder.build_enhanced_knowledge_graph(sample_data)
    
    # 保存结果
    output_dir = "enhanced_knowledge_graph"
    builder.save_enhanced_knowledge_graph(output_dir, knowledge_graph)
    
    # 显示统计信息
    print("\n=== 增强版知识图谱统计 ===")
    stats = knowledge_graph['statistics']
    print(f"Banner特征: {stats['banner_features']}")
    print(f"设备标识: {stats['device_indicators']}")
    print(f"设备类型: {stats['device_types']}")
    print(f"厂商: {stats['manufacturers']}")
    print(f"具体设备: {stats['specific_devices']}")
    print(f"关系类型: {stats['total_relations']}")
    print(f"三元组总数: {stats['total_triples']}")
    
    # 显示部分三元组示例
    print("\n=== 三元组示例 ===")
    for i, (h, r, t) in enumerate(knowledge_graph['triples'][:10]):
        print(f"{i+1}. ({h}, {r}, {t})")

if __name__ == '__main__':
    main() 