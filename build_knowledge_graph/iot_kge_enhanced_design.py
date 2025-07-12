#!/usr/bin/env python
# coding: utf-8
"""
增强版IoT设备识别知识图谱设计
充分利用实体间的关联关系
"""

def design_enhanced_knowledge_graph():
    """
    设计增强版知识图谱，充分利用关联优势
    """
    
    # 1. 多层次实体设计
    entities = {
        # 底层：banner特征
        'banner_features': [
            'Server:Hikvision-Webs',
            'Server:Cisco-IOS', 
            'Server:Axis-Webs',
            'WWW-Authenticate:Basic realm="Axis Camera"',
            'X-Powered-By:Cisco',
            'Content-Type:text/html'
        ],
        
        # 中层：设备标识
        'device_indicators': [
            'Hikvision',
            'Cisco', 
            'Axis',
            'Dahua',
            'MikroTik',
            'D-Link'
        ],
        
        # 高层：设备类型和厂商
        'device_types': ['camera', 'router', 'printer'],
        'manufacturers': ['Hikvision', 'Cisco', 'Axis', 'Dahua', 'MikroTik', 'D-Link'],
        
        # 复合实体：具体设备
        'specific_devices': [
            'camera_Hikvision',
            'camera_Axis', 
            'camera_Dahua',
            'router_Cisco',
            'router_MikroTik',
            'router_D-Link'
        ]
    }
    
    # 2. 丰富的关联关系
    relations = {
        # Banner特征层关系
        'contains_feature': 'banner特征包含关系',
        'indicates_manufacturer': '特征指示厂商',
        'indicates_device_type': '特征指示设备类型',
        
        # 设备标识层关系  
        'brand_of': '品牌属于厂商',
        'typical_for': '典型用于设备类型',
        
        # 设备层关系
        'has_manufacturer': '设备有厂商',
        'is_type': '设备属于类型',
        'similar_to': '设备相似关系',
        
        # 复合关系
        'composed_of': '由...组成',
        'derived_from': '来源于...',
        'correlates_with': '与...相关'
    }
    
    # 3. 三元组示例
    triples = [
        # Banner特征 → 设备标识
        ('Server:Hikvision-Webs', 'indicates_manufacturer', 'Hikvision'),
        ('Server:Cisco-IOS', 'indicates_manufacturer', 'Cisco'),
        ('WWW-Authenticate:Basic realm="Axis Camera"', 'indicates_manufacturer', 'Axis'),
        
        # Banner特征 → 设备类型
        ('Server:Hikvision-Webs', 'indicates_device_type', 'camera'),
        ('Server:Cisco-IOS', 'indicates_device_type', 'router'),
        ('X-Powered-By:Cisco', 'indicates_device_type', 'router'),
        
        # 设备标识 → 厂商
        ('Hikvision', 'brand_of', 'Hikvision'),
        ('Cisco', 'brand_of', 'Cisco'),
        ('Axis', 'brand_of', 'Axis'),
        
        # 设备标识 → 设备类型
        ('Hikvision', 'typical_for', 'camera'),
        ('Cisco', 'typical_for', 'router'),
        ('Axis', 'typical_for', 'camera'),
        
        # 具体设备关系
        ('camera_Hikvision', 'has_manufacturer', 'Hikvision'),
        ('camera_Hikvision', 'is_type', 'camera'),
        ('router_Cisco', 'has_manufacturer', 'Cisco'),
        ('router_Cisco', 'is_type', 'router'),
        
        # 设备相似关系
        ('camera_Hikvision', 'similar_to', 'camera_Axis'),
        ('camera_Hikvision', 'similar_to', 'camera_Dahua'),
        ('router_Cisco', 'similar_to', 'router_MikroTik'),
        
        # 复合关系
        ('camera_Hikvision', 'composed_of', 'Hikvision'),
        ('camera_Hikvision', 'composed_of', 'camera'),
        ('Server:Hikvision-Webs', 'derived_from', 'Hikvision'),
        ('Hikvision', 'correlates_with', 'camera')
    ]
    
    return entities, relations, triples

def demonstrate_advantages():
    """
    演示知识图谱关联的优势
    """
    
    print("=== 知识图谱关联优势演示 ===\n")
    
    # 1. 推理能力
    print("1. 推理能力:")
    print("   已知: Server:Hikvision-Webs indicates_manufacturer Hikvision")
    print("   已知: Hikvision typical_for camera")
    print("   推理: Server:Hikvision-Webs → Hikvision → camera")
    print("   结论: 这是一个摄像头设备\n")
    
    # 2. 相似性传播
    print("2. 相似性传播:")
    print("   已知: camera_Hikvision similar_to camera_Axis")
    print("   已知: camera_Axis has_manufacturer Axis")
    print("   推理: 如果Hikvision摄像头有特征X，Axis摄像头也可能有类似特征\n")
    
    # 3. 多路径推理
    print("3. 多路径推理:")
    print("   路径1: Server:Hikvision-Webs → Hikvision → camera_Hikvision")
    print("   路径2: Server:Hikvision-Webs → camera → camera_Hikvision")
    print("   多条路径增强预测置信度\n")
    
    # 4. 知识补全
    print("4. 知识补全:")
    print("   已知: 新设备有Server:Dahua-Webs")
    print("   已知: Dahua typical_for camera")
    print("   补全: 可以推断这是一个Dahua摄像头\n")
    
    # 5. 异常检测
    print("5. 异常检测:")
    print("   已知: Cisco typical_for router")
    print("   发现: Server:Cisco-Webs indicates_device_type camera")
    print("   异常: 这可能是配置错误或特殊设备\n")

def create_enhanced_training_data():
    """
    创建增强版训练数据
    """
    
    # 构建更丰富的三元组
    enhanced_triples = []
    
    # Banner特征与厂商的关联
    banner_manufacturer_pairs = [
        ('Server:Hikvision-Webs', 'Hikvision'),
        ('Server:Cisco-IOS', 'Cisco'),
        ('Server:Axis-Webs', 'Axis'),
        ('Server:Dahua-Webs', 'Dahua'),
        ('Server:MikroTik', 'MikroTik'),
        ('X-Powered-By:Cisco', 'Cisco'),
        ('WWW-Authenticate:Basic realm="Axis Camera"', 'Axis')
    ]
    
    for banner_feature, manufacturer in banner_manufacturer_pairs:
        enhanced_triples.append((banner_feature, 'indicates_manufacturer', manufacturer))
    
    # Banner特征与设备类型的关联
    banner_type_pairs = [
        ('Server:Hikvision-Webs', 'camera'),
        ('Server:Cisco-IOS', 'router'),
        ('Server:Axis-Webs', 'camera'),
        ('Server:Dahua-Webs', 'camera'),
        ('Server:MikroTik', 'router'),
        ('X-Powered-By:Cisco', 'router')
    ]
    
    for banner_feature, device_type in banner_type_pairs:
        enhanced_triples.append((banner_feature, 'indicates_device_type', device_type))
    
    # 厂商与设备类型的关联
    manufacturer_type_pairs = [
        ('Hikvision', 'camera'),
        ('Cisco', 'router'),
        ('Axis', 'camera'),
        ('Dahua', 'camera'),
        ('MikroTik', 'router'),
        ('D-Link', 'router')
    ]
    
    for manufacturer, device_type in manufacturer_type_pairs:
        enhanced_triples.append((manufacturer, 'typical_for', device_type))
    
    # 具体设备的关系
    specific_devices = [
        ('camera_Hikvision', 'Hikvision'),
        ('camera_Axis', 'Axis'),
        ('camera_Dahua', 'Dahua'),
        ('router_Cisco', 'Cisco'),
        ('router_MikroTik', 'MikroTik'),
        ('router_D-Link', 'D-Link')
    ]
    
    for device, manufacturer in specific_devices:
        enhanced_triples.append((device, 'has_manufacturer', manufacturer))
        device_type = device.split('_')[0]
        enhanced_triples.append((device, 'is_type', device_type))
    
    # 设备相似关系
    similar_devices = [
        ('camera_Hikvision', 'camera_Axis'),
        ('camera_Hikvision', 'camera_Dahua'),
        ('camera_Axis', 'camera_Dahua'),
        ('router_Cisco', 'router_MikroTik'),
        ('router_Cisco', 'router_D-Link'),
        ('router_MikroTik', 'router_D-Link')
    ]
    
    for device1, device2 in similar_devices:
        enhanced_triples.append((device1, 'similar_to', device2))
        enhanced_triples.append((device2, 'similar_to', device1))  # 双向关系
    
    return enhanced_triples

def main():
    """主函数"""
    print("=== 增强版IoT设备识别知识图谱设计 ===\n")
    
    # 设计知识图谱
    entities, relations, triples = design_enhanced_knowledge_graph()
    
    print("实体类型:")
    for entity_type, entity_list in entities.items():
        print(f"  {entity_type}: {len(entity_list)} 个")
    
    print(f"\n关系类型: {len(relations)} 个")
    for relation, description in relations.items():
        print(f"  {relation}: {description}")
    
    print(f"\n三元组数量: {len(triples)} 个")
    
    # 演示优势
    demonstrate_advantages()
    
    # 创建增强版训练数据
    enhanced_triples = create_enhanced_training_data()
    print(f"增强版三元组数量: {len(enhanced_triples)} 个")
    
    print("\n=== 设计总结 ===")
    print("优势:")
    print("1. 多层次实体：从特征到设备类型的完整层次")
    print("2. 丰富关系：多种类型的关系连接实体")
    print("3. 推理能力：可以通过关系链进行推理")
    print("4. 相似性传播：相似设备可以共享特征")
    print("5. 知识补全：可以推断缺失的信息")

if __name__ == '__main__':
    main() 