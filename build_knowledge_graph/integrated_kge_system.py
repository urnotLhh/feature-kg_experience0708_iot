#!/usr/bin/env python
# coding: utf-8
"""
整合版KGE系统
展示增强版KGE设计与自动化构建器的结合使用
"""

import os
import json
from typing import List, Dict, Tuple
from enhanced_kge_builder import EnhancedKGEBuilder
from automated_kge_builder import AutomatedKGEBuilder

class IntegratedKGESystem:
    def __init__(self):
        """初始化整合版KGE系统"""
        self.enhanced_builder = EnhancedKGEBuilder()
        self.basic_builder = AutomatedKGEBuilder()
        
    def compare_builders(self, training_data: List[Tuple[str, str]]) -> Dict:
        """比较基础构建器和增强版构建器"""
        print("=== 构建器对比分析 ===\n")
        
        # 使用基础构建器
        print("1. 基础构建器结果:")
        basic_kg = self.basic_builder.build_knowledge_graph(training_data)
        basic_stats = basic_kg.get('statistics', {})
        
        print(f"   实体数量: {basic_stats.get('total_entities', 0)}")
        print(f"   关系类型: {basic_stats.get('total_relations', 0)}")
        print(f"   三元组数量: {basic_stats.get('total_triples', 0)}")
        
        # 使用增强版构建器
        print("\n2. 增强版构建器结果:")
        enhanced_kg = self.enhanced_builder.build_enhanced_knowledge_graph(training_data)
        enhanced_stats = enhanced_kg.get('statistics', {})
        
        print(f"   实体数量: {enhanced_stats.get('total_entities', 0)}")
        print(f"   关系类型: {enhanced_stats.get('total_relations', 0)}")
        print(f"   三元组数量: {enhanced_stats.get('total_triples', 0)}")
        
        # 详细对比
        print("\n3. 详细对比:")
        print(f"   实体数量增加: {enhanced_stats.get('total_entities', 0) - basic_stats.get('total_entities', 0)}")
        print(f"   关系类型增加: {enhanced_stats.get('total_relations', 0) - basic_stats.get('total_relations', 0)}")
        print(f"   三元组数量增加: {enhanced_stats.get('total_triples', 0) - basic_stats.get('total_triples', 0)}")
        
        return {
            'basic': basic_kg,
            'enhanced': enhanced_kg,
            'comparison': {
                'entity_increase': enhanced_stats.get('total_entities', 0) - basic_stats.get('total_entities', 0),
                'relation_increase': enhanced_stats.get('total_relations', 0) - basic_stats.get('total_relations', 0),
                'triple_increase': enhanced_stats.get('total_triples', 0) - basic_stats.get('total_triples', 0)
            }
        }
    
    def demonstrate_enhanced_advantages(self, enhanced_kg: Dict):
        """演示增强版优势"""
        print("\n=== 增强版优势演示 ===\n")
        
        entities = enhanced_kg.get('entities', {})
        triples = enhanced_kg.get('triples', [])
        
        # 1. 多层次实体结构
        print("1. 多层次实体结构:")
        print(f"   底层特征: {len(entities.get('banner_features', []))} 个")
        print(f"   中层标识: {len(entities.get('device_indicators', []))} 个")
        print(f"   高层类型: {len(entities.get('device_types', []))} 个")
        print(f"   高层厂商: {len(entities.get('manufacturers', []))} 个")
        print(f"   具体设备: {len(entities.get('specific_devices', []))} 个")
        
        # 2. 丰富的关系类型
        print("\n2. 丰富的关系类型:")
        relations = enhanced_kg.get('relations', [])
        relation_descriptions = enhanced_kg.get('relation_descriptions', {})
        
        for relation in relations:
            description = relation_descriptions.get(relation, '')
            count = sum(1 for h, r, t in triples if r == relation)
            print(f"   {relation}: {description} ({count} 个三元组)")
        
        # 3. 推理路径示例
        print("\n3. 推理路径示例:")
        self._show_reasoning_paths(triples)
    
    def _show_reasoning_paths(self, triples: List[Tuple[str, str, str]]):
        """显示推理路径"""
        # 构建图结构
        graph = {}
        for h, r, t in triples:
            if h not in graph:
                graph[h] = []
            graph[h].append((r, t))
        
        # 示例推理路径
        print("   路径1: Banner特征 → 厂商 → 设备类型")
        print("   路径2: Banner特征 → 设备类型 → 具体设备")
        print("   路径3: 设备标识 → 厂商 → 典型设备类型")
        print("   路径4: 具体设备 → 相似设备")
        
        # 实际路径示例
        banner_features = [h for h, r, t in triples if r == 'contains_feature']
        if banner_features:
            banner = banner_features[0]
            print(f"\n   实际路径示例 (从 {banner}):")
            
            # 查找相关路径
            for h, r, t in triples:
                if h == banner:
                    print(f"     {h} --{r}--> {t}")
                    
                    # 查找第二跳
                    for h2, r2, t2 in triples:
                        if h2 == t:
                            print(f"       {h2} --{r2}--> {t2}")
    
    def generate_training_files(self, enhanced_kg: Dict, output_dir: str = "integrated_output"):
        """生成训练文件"""
        print(f"\n=== 生成训练文件到 {output_dir} ===")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 生成TransE训练文件
        triples_file = os.path.join(output_dir, "transe_triples.txt")
        with open(triples_file, 'w', encoding='utf-8') as f:
            for h, r, t in enhanced_kg['triples']:
                f.write(f"{h}\t{r}\t{t}\n")
        
        # 2. 生成实体映射文件
        entities = enhanced_kg['entities']
        entity_mapping = {}
        entity_id = 0
        
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_mapping[entity] = entity_id
                entity_id += 1
        
        entity_file = os.path.join(output_dir, "entity2id.txt")
        with open(entity_file, 'w', encoding='utf-8') as f:
            for entity, eid in entity_mapping.items():
                f.write(f"{entity}\t{eid}\n")
        
        # 3. 生成关系映射文件
        relations = enhanced_kg['relations']
        relation_mapping = {}
        relation_id = 0
        
        for relation in relations:
            relation_mapping[relation] = relation_id
            relation_id += 1
        
        relation_file = os.path.join(output_dir, "relation2id.txt")
        with open(relation_file, 'w', encoding='utf-8') as f:
            for relation, rid in relation_mapping.items():
                f.write(f"{relation}\t{rid}\n")
        
        # 4. 生成数字化的三元组文件
        numeric_triples_file = os.path.join(output_dir, "numeric_triples.txt")
        with open(numeric_triples_file, 'w', encoding='utf-8') as f:
            for h, r, t in enhanced_kg['triples']:
                if h in entity_mapping and r in relation_mapping and t in entity_mapping:
                    f.write(f"{entity_mapping[h]}\t{relation_mapping[r]}\t{entity_mapping[t]}\n")
        
        print(f"   训练文件已生成:")
        print(f"   - {triples_file}")
        print(f"   - {entity_file}")
        print(f"   - {relation_file}")
        print(f"   - {numeric_triples_file}")
        
        return {
            'triples_file': triples_file,
            'entity_file': entity_file,
            'relation_file': relation_file,
            'numeric_triples_file': numeric_triples_file,
            'entity_mapping': entity_mapping,
            'relation_mapping': relation_mapping
        }
    
    def demonstrate_integration_workflow(self):
        """演示整合工作流程"""
        print("=== 整合工作流程演示 ===\n")
        
        # 示例训练数据
        training_data = [
            ("HTTP/1.1 200 OK\nServer: Hikvision-Webs\nContent-Type: text/html\n\n<html><title>Hikvision</title><body><h1>Hikvision Camera</h1><p>Model: DS-2CD2342-I</p></body></html>", "camera_Hikvision_DS-2CD2342-I"),
            ("HTTP/1.1 200 OK\nServer: Cisco-IOS\nX-Powered-By: Cisco\nContent-Type: text/html\n\n<html><title>Cisco Router</title><body><h1>Cisco Router Management</h1><p>Model: ISR4321</p></body></html>", "router_Cisco_ISR4321"),
            ("HTTP/1.1 200 OK\nServer: Axis-Webs\nWWW-Authenticate: Basic realm=\"Axis Camera\"\nContent-Type: text/html\n\n<html><title>Axis</title><body><h1>Axis Camera</h1><p>Model: P3364-V</p></body></html>", "camera_Axis_P3364-V"),
            ("HTTP/1.1 200 OK\nServer: Dahua-Webs\nContent-Type: text/html\n\n<html><title>Dahua</title><body><h1>Dahua Camera</h1><p>Model: IPC-HFW4431R-Z</p></body></html>", "camera_Dahua_IPC-HFW4431R-Z"),
            ("HTTP/1.1 200 OK\nServer: MikroTik\nContent-Type: text/html\n\n<html><title>MikroTik</title><body><h1>MikroTik Router</h1><p>Model: RB951G-2HnD</p></body></html>", "router_MikroTik_RB951G-2HnD")
        ]
        
        print("1. 输入数据:")
        for i, (banner, device) in enumerate(training_data):
            print(f"   样本{i+1}: {device}")
        
        # 2. 构建器对比
        comparison_result = self.compare_builders(training_data)
        
        # 3. 增强版优势演示
        enhanced_kg = comparison_result['enhanced']
        self.demonstrate_enhanced_advantages(enhanced_kg)
        
        # 4. 生成训练文件
        training_files = self.generate_training_files(enhanced_kg)
        
        # 5. 工作流程总结
        print("\n=== 工作流程总结 ===")
        print("1. 数据输入: Banner文本 + 设备类型")
        print("2. 特征提取: 多层次特征提取")
        print("3. 实体识别: 识别banner特征、设备标识、厂商、类型等")
        print("4. 关系构建: 构建丰富的关联关系")
        print("5. 三元组生成: 生成训练用的三元组")
        print("6. 文件输出: 生成TransE等模型所需的训练文件")
        
        return comparison_result, training_files

def main():
    """主函数"""
    print("整合版KGE系统")
    print("=" * 50)
    
    # 创建整合系统
    system = IntegratedKGESystem()
    
    # 演示整合工作流程
    comparison_result, training_files = system.demonstrate_integration_workflow()
    
    print("\n=== 整合优势总结 ===")
    print("1. 多层次实体设计: 从banner特征到具体设备的完整层次")
    print("2. 丰富关联关系: 支持复杂推理和相似性传播")
    print("3. 自动化构建: 无需手动定义规则，自动提取特征和关系")
    print("4. 标准化输出: 生成标准格式的训练文件")
    print("5. 可扩展性: 易于添加新的实体类型和关系")

if __name__ == '__main__':
    main() 