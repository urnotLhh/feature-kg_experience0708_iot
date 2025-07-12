#!/usr/bin/env python
# coding: utf-8
"""
可扩展中层特征系统使用示例
演示如何动态添加中层特征，重构知识图谱
"""

import os
import json
from typing import List, Dict, Tuple

from extensible_middle_layer import ExtensibleMiddleLayer, KnowledgeGraphRebuilder
from enhanced_kge_builder_with_extensible_layers import EnhancedKGEBuilderWithExtensibleLayers

def demo_basic_middle_layer_management():
    """演示基本的中层特征管理"""
    print("=== 基本中层特征管理演示 ===")
    
    # 1. 初始化中层特征管理器
    manager = ExtensibleMiddleLayer("demo_middle_layer_config.json")
    
    # 2. 查看当前中层特征
    print("\n当前中层特征:")
    layers = manager.list_middle_layers()
    for layer in layers:
        print(f"  - {layer['id']}: {layer['name']} (优先级: {layer['priority']})")
    
    # 3. 添加新的中层特征
    print("\n添加新的中层特征...")
    
    # 添加地理位置特征层
    geo_config = {
        'name': '地理位置特征',
        'description': '设备地理位置相关特征',
        'type': 'text',
        'priority': 4,
        'enabled': True,
        'examples': ['CN', 'US', 'EU', 'Asia'],
        'extraction_rules': {
            'patterns': [
                r'Country:\s*([A-Z]{2})',
                r'Region:\s*([A-Za-z]+)',
                r'Location:\s*([^\r\n]+)'
            ],
            'keywords': ['CN', 'US', 'EU', 'Asia', 'Europe', 'America'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_region': 'located_in_region',
            'to_country': 'located_in_country'
        }
    }
    
    success = manager.add_middle_layer('geographic_features', geo_config)
    print(f"添加地理位置特征层: {'成功' if success else '失败'}")
    
    # 添加时间特征层
    time_config = {
        'name': '时间特征',
        'description': '设备时间相关特征',
        'type': 'datetime',
        'priority': 5,
        'enabled': True,
        'examples': ['2024-01-01', 'UTC', 'GMT'],
        'extraction_rules': {
            'patterns': [
                r'Date:\s*([^\r\n]+)',
                r'Time:\s*([^\r\n]+)',
                r'UTC|GMT'
            ],
            'keywords': ['UTC', 'GMT', 'EST', 'PST'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_timezone': 'uses_timezone',
            'to_date': 'created_on_date'
        }
    }
    
    success = manager.add_middle_layer('time_features', time_config)
    print(f"添加时间特征层: {'成功' if success else '失败'}")
    
    # 4. 添加知识库条目
    print("\n添加知识库条目...")
    
    # 地理位置知识库
    manager.add_knowledge_base_entry('geographic_features', 'CN', {
        'region': 'Asia',
        'country': 'China'
    })
    manager.add_knowledge_base_entry('geographic_features', 'US', {
        'region': 'America',
        'country': 'United States'
    })
    manager.add_knowledge_base_entry('geographic_features', 'EU', {
        'region': 'Europe',
        'country': 'European Union'
    })
    
    # 时间知识库
    manager.add_knowledge_base_entry('time_features', 'UTC', {
        'timezone': 'Coordinated Universal Time',
        'offset': '+00:00'
    })
    manager.add_knowledge_base_entry('time_features', 'GMT', {
        'timezone': 'Greenwich Mean Time',
        'offset': '+00:00'
    })
    
    # 5. 特征提取测试
    print("\n特征提取测试...")
    test_banner = """
    HTTP/1.1 200 OK
    Server: Hikvision-Webs
    Date: Mon, 15 Jan 2024 10:30:00 GMT
    Country: CN
    Content-Type: text/html
    """
    
    features = manager.extract_middle_layer_features(test_banner)
    print("提取的特征:")
    for layer_id, layer_features in features.items():
        print(f"  {layer_id}: {layer_features}")
    
    # 6. 更新中层特征
    print("\n更新中层特征...")
    updates = {
        'priority': 3,  # 提高优先级
        'examples': ['CN', 'US', 'EU', 'Asia', 'Europe', 'America'],
        'extraction_rules': {
            'patterns': [
                r'Country:\s*([A-Z]{2})',
                r'Region:\s*([A-Za-z]+)',
                r'Location:\s*([^\r\n]+)',
                r'Geo:\s*([^\r\n]+)'  # 添加新模式
            ],
            'keywords': ['CN', 'US', 'EU', 'Asia', 'Europe', 'America', 'Global'],
            'extraction_method': 'regex_and_keyword'
        }
    }
    
    success = manager.update_middle_layer('geographic_features', updates)
    print(f"更新地理位置特征层: {'成功' if success else '失败'}")
    
    # 7. 禁用中层特征
    print("\n禁用中层特征...")
    success = manager.disable_middle_layer('time_features')
    print(f"禁用时间特征层: {'成功' if success else '失败'}")
    
    # 8. 重新启用
    success = manager.enable_middle_layer('time_features')
    print(f"重新启用时间特征层: {'成功' if success else '失败'}")
    
    # 9. 导出配置
    print("\n导出配置...")
    manager.export_config('demo_config_export.json')
    
    print("\n=== 基本中层特征管理演示完成 ===")


def demo_knowledge_graph_rebuilding():
    """演示知识图谱重构"""
    print("\n=== 知识图谱重构演示 ===")
    
    # 1. 初始化中层特征管理器
    manager = ExtensibleMiddleLayer("rebuild_demo_config.json")
    
    # 2. 添加一些中层特征
    security_config = {
        'name': '安全特征',
        'description': '设备安全相关特征',
        'type': 'text',
        'priority': 1,
        'enabled': True,
        'examples': ['SSL', 'TLS', 'Basic Auth'],
        'extraction_rules': {
            'patterns': [
                r'WWW-Authenticate:\s*(Basic|Digest)',
                r'SSL|TLS',
                r'Certificate'
            ],
            'keywords': ['SSL', 'TLS', 'Basic', 'Digest', 'Certificate'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_security_level': 'indicates_security_level',
            'to_authentication': 'indicates_authentication_type'
        }
    }
    
    manager.add_middle_layer('security_features', security_config)
    
    # 3. 添加知识库
    manager.add_knowledge_base_entry('security_features', 'SSL', {
        'security_level': 'high',
        'authentication_type': 'certificate_based'
    })
    manager.add_knowledge_base_entry('security_features', 'Basic Auth', {
        'security_level': 'low',
        'authentication_type': 'password_based'
    })
    
    # 4. 模拟原始三元组
    original_triples = [
        ("banner_001", "indicates_device", "camera_Hikvision"),
        ("banner_002", "indicates_device", "router_Cisco"),
        ("banner_003", "indicates_device", "camera_Axis")
    ]
    
    # 5. 创建重构器
    rebuilder = KnowledgeGraphRebuilder(manager)
    
    # 6. 重构知识图谱
    print("开始重构知识图谱...")
    report = rebuilder.rebuild_knowledge_graph(original_triples)
    
    # 7. 显示重构结果
    print(f"\n重构结果:")
    print(f"  原始三元组数量: {report['original_triples_count']}")
    print(f"  重构后三元组数量: {report['rebuilt_triples_count']}")
    print(f"  新增实体数量: {report['new_entities_count']}")
    print(f"  新增关系数量: {report['new_relations_count']}")
    
    print(f"\n新增实体:")
    for entity in report['new_entities'][:10]:  # 只显示前10个
        print(f"  - {entity}")
    
    print(f"\n新增关系:")
    for relation in report['new_relations']:
        print(f"  - {relation}")
    
    # 8. 保存重构后的知识图谱
    print("\n保存重构后的知识图谱...")
    rebuilder.save_rebuilt_knowledge_graph('output/rebuild_demo', report)
    
    print("\n=== 知识图谱重构演示完成 ===")


def demo_extensible_kge_builder():
    """演示可扩展KGE构建器"""
    print("\n=== 可扩展KGE构建器演示 ===")
    
    # 1. 初始化可扩展KGE构建器
    builder = EnhancedKGEBuilderWithExtensibleLayers("extensible_kge_demo_config.json")
    
    # 2. 添加自定义中层特征
    print("添加自定义中层特征...")
    
    # 添加协议特征层
    protocol_config = {
        'name': '协议特征',
        'description': '网络协议相关特征',
        'type': 'text',
        'priority': 1,
        'enabled': True,
        'examples': ['HTTP/1.1', 'HTTPS', 'FTP', 'SSH'],
        'extraction_rules': {
            'patterns': [
                r'HTTP/\d+\.\d+',
                r'HTTPS',
                r'FTP',
                r'SSH'
            ],
            'keywords': ['HTTP', 'HTTPS', 'FTP', 'SSH', 'TCP', 'UDP'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_device_type': 'typical_protocol_for',
            'to_security': 'indicates_protocol_security'
        }
    }
    
    success = builder.add_custom_middle_layer(protocol_config)
    print(f"添加协议特征层: {'成功' if success else '失败'}")
    
    # 添加厂商特征层
    vendor_config = {
        'name': '厂商特征',
        'description': '设备厂商相关特征',
        'type': 'text',
        'priority': 2,
        'enabled': True,
        'examples': ['Hikvision', 'Cisco', 'Axis', 'Dahua'],
        'extraction_rules': {
            'patterns': [
                r'Server:\s*([^\r\n]+)',
                r'X-Powered-By:\s*([^\r\n]+)',
                r'Hikvision|Cisco|Axis|Dahua'
            ],
            'keywords': ['Hikvision', 'Cisco', 'Axis', 'Dahua', 'MikroTik'],
            'extraction_method': 'regex_and_keyword'
        },
        'relation_mappings': {
            'to_manufacturer': 'indicates_manufacturer',
            'to_device_type': 'typical_vendor_for'
        }
    }
    
    success = builder.add_custom_middle_layer(vendor_config)
    print(f"添加厂商特征层: {'成功' if success else '失败'}")
    
    # 3. 添加知识库条目
    print("添加知识库条目...")
    
    # 协议知识库
    builder.add_knowledge_base_entry('protocol_features', 'HTTP/1.1', {
        'device_type': 'web_device',
        'security': 'insecure'
    })
    builder.add_knowledge_base_entry('protocol_features', 'HTTPS', {
        'device_type': 'secure_web_device',
        'security': 'secure'
    })
    builder.add_knowledge_base_entry('protocol_features', 'SSH', {
        'device_type': 'network_device',
        'security': 'secure'
    })
    
    # 厂商知识库
    builder.add_knowledge_base_entry('vendor_features', 'Hikvision', {
        'manufacturer': 'Hikvision',
        'device_type': 'camera'
    })
    builder.add_knowledge_base_entry('vendor_features', 'Cisco', {
        'manufacturer': 'Cisco',
        'device_type': 'router'
    })
    builder.add_knowledge_base_entry('vendor_features', 'Axis', {
        'manufacturer': 'Axis',
        'device_type': 'camera'
    })
    
    # 4. 构建知识图谱
    print("构建知识图谱...")
    
    # 模拟训练数据
    training_data = [
        ("HTTP/1.1 401 Unauthorized\nServer: Hikvision-Webs\nWWW-Authenticate: Basic realm=\"Hikvision Camera\"", "camera_Hikvision_IPC"),
        ("HTTP/1.1 200 OK\nServer: Cisco-IOS\nX-Powered-By: Cisco", "router_Cisco_ISR"),
        ("SSH-2.0-OpenSSH_7.4\nServer: Axis-Webs", "camera_Axis_P3364"),
        ("HTTPS/1.1 200 OK\nServer: Dahua-Webs\nX-Powered-By: Dahua", "camera_Dahua_IPC")
    ]
    
    knowledge_graph = builder.build_extensible_knowledge_graph(training_data)
    
    # 5. 显示构建结果
    print(f"\n知识图谱构建结果:")
    print(f"  实体数量: {knowledge_graph['entity_count']}")
    print(f"  关系数量: {knowledge_graph['relation_count']}")
    print(f"  三元组数量: {knowledge_graph['triple_count']}")
    print(f"  中层特征层数: {len(knowledge_graph['middle_layers'])}")
    
    print(f"\n中层特征层:")
    for layer in knowledge_graph['middle_layers']:
        print(f"  - {layer['id']}: {layer['name']}")
    
    # 6. 保存知识图谱
    print("\n保存知识图谱...")
    builder.save_extensible_knowledge_graph('output/extensible_kge_demo', knowledge_graph)
    
    # 7. 演示动态添加新特征层
    print("\n演示动态添加新特征层...")
    
    # 添加新的端口特征层
    port_config = {
        'name': '端口特征',
        'description': '网络端口相关特征',
        'type': 'numeric',
        'priority': 3,
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
    
    success = builder.add_custom_middle_layer(port_config)
    print(f"动态添加端口特征层: {'成功' if success else '失败'}")
    
    # 添加端口知识库
    builder.add_knowledge_base_entry('port_features', '80', {
        'service': 'http',
        'security': 'insecure'
    })
    builder.add_knowledge_base_entry('port_features', '443', {
        'service': 'https',
        'security': 'secure'
    })
    
    # 8. 重新构建知识图谱（包含新特征层）
    print("重新构建知识图谱（包含新特征层）...")
    knowledge_graph_v2 = builder.build_extensible_knowledge_graph(training_data)
    
    print(f"\n重新构建结果:")
    print(f"  实体数量: {knowledge_graph_v2['entity_count']} (之前: {knowledge_graph['entity_count']})")
    print(f"  关系数量: {knowledge_graph_v2['relation_count']} (之前: {knowledge_graph['relation_count']})")
    print(f"  三元组数量: {knowledge_graph_v2['triple_count']} (之前: {knowledge_graph['triple_count']})")
    print(f"  中层特征层数: {len(knowledge_graph_v2['middle_layers'])} (之前: {len(knowledge_graph['middle_layers'])})")
    
    # 9. 保存新版本知识图谱
    builder.save_extensible_knowledge_graph('output/extensible_kge_demo_v2', knowledge_graph_v2)
    
    print("\n=== 可扩展KGE构建器演示完成 ===")


def main():
    """主函数"""
    print("可扩展中层特征系统完整演示")
    print("=" * 50)
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    
    # 1. 基本中层特征管理演示
    demo_basic_middle_layer_management()
    
    # 2. 知识图谱重构演示
    demo_knowledge_graph_rebuilding()
    
    # 3. 可扩展KGE构建器演示
    demo_extensible_kge_builder()
    
    print("\n" + "=" * 50)
    print("所有演示完成！")
    print("\n生成的文件:")
    print("  - demo_middle_layer_config.json: 基本中层特征配置")
    print("  - rebuild_demo_config.json: 重构演示配置")
    print("  - extensible_kge_demo_config.json: 可扩展KGE配置")
    print("  - output/: 输出目录")
    print("    - rebuild_demo/: 重构演示结果")
    print("    - extensible_kge_demo/: 可扩展KGE演示结果")
    print("    - extensible_kge_demo_v2/: 可扩展KGE演示结果（v2）")


if __name__ == "__main__":
    main() 