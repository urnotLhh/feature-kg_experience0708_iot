#!/usr/bin/env python
# coding: utf-8
"""
IoT设备识别推理过程详解
演示从底层banner到高层设备识别的完整推理流程
"""

class IoTReasoningEngine:
    def __init__(self):
        """初始化推理引擎"""
        # 构建知识图谱（实际应用中这些会从训练好的模型中获取）
        self.knowledge_graph = self._build_knowledge_graph()
        
    def _build_knowledge_graph(self):
        """构建知识图谱"""
        return {
            # 底层：banner特征 → 中层：关键词
            'banner_to_keywords': {
                'Server:Hikvision-Webs': ['Hikvision', 'camera'],
                'Server:Cisco-IOS': ['Cisco', 'router'],
                'Server:Axis-Webs': ['Axis', 'camera'],
                'WWW-Authenticate:Basic realm="Axis Camera"': ['Axis', 'camera'],
                'X-Powered-By:Cisco': ['Cisco', 'router'],
                'Content-Type:text/html': ['web_interface'],
                'Hikvision': ['Hikvision', 'camera'],
                'camera': ['camera'],
                'vh2300': ['vh2300', 'model'],
                'DS-2CD': ['DS-2CD', 'model', 'Hikvision'],
                'IPC': ['IPC', 'camera'],
                'NVR': ['NVR', 'recorder'],
                'DVR': ['DVR', 'recorder']
            },
            
            # 中层：关键词 → 高层：设备信息
            'keywords_to_device': {
                'Hikvision': {'manufacturer': 'Hikvision', 'typical_type': 'camera'},
                'Cisco': {'manufacturer': 'Cisco', 'typical_type': 'router'},
                'Axis': {'manufacturer': 'Axis', 'typical_type': 'camera'},
                'camera': {'device_type': 'camera'},
                'router': {'device_type': 'router'},
                'vh2300': {'model': 'vh2300', 'series': 'VH'},
                'DS-2CD': {'model_series': 'DS-2CD', 'manufacturer': 'Hikvision'},
                'IPC': {'device_type': 'camera', 'category': 'IP_camera'},
                'NVR': {'device_type': 'recorder', 'category': 'network_recorder'},
                'DVR': {'device_type': 'recorder', 'category': 'digital_recorder'}
            },
            
            # 设备相似关系
            'similar_devices': {
                'camera_Hikvision': ['camera_Axis', 'camera_Dahua'],
                'camera_Axis': ['camera_Hikvision', 'camera_Dahua'],
                'router_Cisco': ['router_MikroTik', 'router_D-Link']
            }
        }
    
    def extract_features_from_banner(self, banner_text):
        """从banner中提取特征"""
        features = []
        
        # 提取HTTP头信息
        import re
        
        # 服务器信息
        server_match = re.search(r'Server:\s*([^\r\n]+)', banner_text, re.IGNORECASE)
        if server_match:
            features.append(f"Server:{server_match.group(1)}")
        
        # 认证信息
        auth_match = re.search(r'WWW-Authenticate:\s*([^\r\n]+)', banner_text, re.IGNORECASE)
        if auth_match:
            features.append(f"WWW-Authenticate:{auth_match.group(1)}")
        
        # 其他HTTP头
        powered_by_match = re.search(r'X-Powered-By:\s*([^\r\n]+)', banner_text, re.IGNORECASE)
        if powered_by_match:
            features.append(f"X-Powered-By:{powered_by_match.group(1)}")
        
        # 从内容中提取关键词
        content_keywords = [
            'Hikvision', 'Cisco', 'Axis', 'Dahua', 'MikroTik', 'D-Link',
            'camera', 'router', 'printer', 'vh2300', 'DS-2CD', 'IPC', 'NVR', 'DVR'
        ]
        
        for keyword in content_keywords:
            if re.search(keyword, banner_text, re.IGNORECASE):
                features.append(keyword)
        
        return features
    
    def reasoning_process(self, banner_text):
        """完整的推理过程"""
        print("=" * 80)
        print("IoT设备识别推理过程")
        print("=" * 80)
        print(f"输入Banner:\n{banner_text}")
        print("\n" + "=" * 80)
        
        # 第一步：特征提取（底层）
        print("第一步：特征提取（底层）")
        print("-" * 40)
        features = self.extract_features_from_banner(banner_text)
        print(f"提取的特征: {features}")
        
        # 第二步：关键词映射（中层）
        print("\n第二步：关键词映射（中层）")
        print("-" * 40)
        keywords = self._map_features_to_keywords(features)
        print(f"映射的关键词: {keywords}")
        
        # 第三步：设备信息推理（高层）
        print("\n第三步：设备信息推理（高层）")
        print("-" * 40)
        device_info = self._infer_device_info(keywords)
        print(f"推理的设备信息: {device_info}")
        
        # 第四步：相似性推理
        print("\n第四步：相似性推理")
        print("-" * 40)
        similar_devices = self._find_similar_devices(device_info)
        print(f"相似设备: {similar_devices}")
        
        # 第五步：置信度计算
        print("\n第五步：置信度计算")
        print("-" * 40)
        confidence = self._calculate_confidence(features, keywords, device_info)
        print(f"置信度: {confidence:.4f}")
        
        # 最终结果
        print("\n" + "=" * 80)
        print("最终推理结果")
        print("=" * 80)
        result = {
            'banner_text': banner_text,
            'extracted_features': features,
            'mapped_keywords': keywords,
            'device_info': device_info,
            'similar_devices': similar_devices,
            'confidence': confidence,
            'final_prediction': self._make_final_prediction(device_info, confidence)
        }
        
        print(f"设备类型: {result['final_prediction']['device_type']}")
        print(f"厂商: {result['final_prediction']['manufacturer']}")
        print(f"型号: {result['final_prediction']['model']}")
        print(f"置信度: {result['confidence']:.4f}")
        
        return result
    
    def _map_features_to_keywords(self, features):
        """将特征映射到关键词"""
        keywords = set()
        
        for feature in features:
            if feature in self.knowledge_graph['banner_to_keywords']:
                keywords.update(self.knowledge_graph['banner_to_keywords'][feature])
        
        return list(keywords)
    
    def _infer_device_info(self, keywords):
        """从关键词推理设备信息"""
        device_info = {
            'manufacturer': None,
            'device_type': None,
            'model': None,
            'category': None
        }
        
        # 推理厂商
        manufacturers = [kw for kw in keywords if kw in ['Hikvision', 'Cisco', 'Axis', 'Dahua', 'MikroTik', 'D-Link']]
        if manufacturers:
            device_info['manufacturer'] = manufacturers[0]
        
        # 推理设备类型
        device_types = [kw for kw in keywords if kw in ['camera', 'router', 'printer', 'recorder']]
        if device_types:
            device_info['device_type'] = device_types[0]
        
        # 推理型号
        models = [kw for kw in keywords if kw in ['vh2300', 'DS-2CD', 'IPC', 'NVR', 'DVR']]
        if models:
            device_info['model'] = models[0]
        
        # 推理类别
        categories = [kw for kw in keywords if kw in ['IP_camera', 'network_recorder', 'digital_recorder']]
        if categories:
            device_info['category'] = categories[0]
        
        # 使用知识图谱进行推理
        for keyword in keywords:
            if keyword in self.knowledge_graph['keywords_to_device']:
                info = self.knowledge_graph['keywords_to_device'][keyword]
                for key, value in info.items():
                    if device_info[key] is None:
                        device_info[key] = value
        
        return device_info
    
    def _find_similar_devices(self, device_info):
        """查找相似设备"""
        if device_info['manufacturer'] and device_info['device_type']:
            device_key = f"{device_info['device_type']}_{device_info['manufacturer']}"
            return self.knowledge_graph['similar_devices'].get(device_key, [])
        return []
    
    def _calculate_confidence(self, features, keywords, device_info):
        """计算置信度"""
        confidence = 0.0
        
        # 特征匹配度
        feature_score = len(features) / 10.0  # 假设最多10个特征
        
        # 关键词匹配度
        keyword_score = len(keywords) / 15.0  # 假设最多15个关键词
        
        # 设备信息完整度
        info_completeness = sum(1 for v in device_info.values() if v is not None) / len(device_info)
        
        # 综合置信度
        confidence = (feature_score + keyword_score + info_completeness) / 3.0
        
        return min(confidence, 1.0)
    
    def _make_final_prediction(self, device_info, confidence):
        """生成最终预测"""
        return {
            'device_type': device_info['device_type'] or 'unknown',
            'manufacturer': device_info['manufacturer'] or 'unknown',
            'model': device_info['model'] or 'unknown',
            'category': device_info['category'] or 'unknown',
            'confidence': confidence
        }

def demonstrate_reasoning_examples():
    """演示推理示例"""
    engine = IoTReasoningEngine()
    
    # 示例1：Hikvision摄像头
    banner1 = """HTTP/1.1 200 OK
Server: Hikvision-Webs
Content-Type: text/html
Content-Length: 1234

<html><title>Hikvision</title>
<body>
<h1>Hikvision Camera Management</h1>
<p>Model: DS-2CD2342-I</p>
<p>Type: IP Camera</p>
<p>Version: V5.5.0</p>
</body></html>"""
    
    print("示例1：Hikvision摄像头")
    result1 = engine.reasoning_process(banner1)
    
    print("\n" + "="*80 + "\n")
    
    # 示例2：Cisco路由器
    banner2 = """HTTP/1.1 200 OK
Server: Cisco-IOS
X-Powered-By: Cisco
Content-Type: text/html

<html><title>Cisco Router</title>
<body>
<h1>Cisco Router Management</h1>
<p>Model: ISR4321</p>
<p>Type: Router</p>
<p>IOS Version: 16.9.4</p>
</body></html>"""
    
    print("示例2：Cisco路由器")
    result2 = engine.reasoning_process(banner2)
    
    print("\n" + "="*80 + "\n")
    
    # 示例3：复杂banner（包含多个关键词）
    banner3 = """HTTP/1.1 200 OK
Server: Hikvision-Webs
Content-Type: text/html

<html><title>Hikvision</title>
<body>
<h1>Hikvision VH2300 Camera</h1>
<p>Model: VH2300</p>
<p>Type: IP Camera</p>
<p>Features: IPC, NVR Support</p>
<p>Manufacturer: Hikvision</p>
</body></html>"""
    
    print("示例3：复杂banner（VH2300摄像头）")
    result3 = engine.reasoning_process(banner3)

def main():
    """主函数"""
    print("IoT设备识别推理过程详解")
    print("演示从底层banner到高层设备识别的完整推理流程")
    print("\n推理层次结构:")
    print("底层：Banner特征提取")
    print("中层：关键词映射")
    print("高层：设备信息推理")
    print("补充：相似性推理和置信度计算")
    
    demonstrate_reasoning_examples()

if __name__ == '__main__':
    main() 