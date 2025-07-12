#!/usr/bin/env python
# coding: utf-8
"""
知识图谱嵌入(KGE)模型详解
解释TransE等模型的工作原理和在IoT设备识别中的作用
"""

import numpy as np
import matplotlib.pyplot as plt

class KGEExplanation:
    def __init__(self):
        """初始化KGE解释器"""
        self.embedding_dim = 50  # 嵌入维度
        self.entities = {
            'Server:Hikvision-Webs': [0, 1],
            'Hikvision': [1, 2], 
            'camera': [2, 3],
            'camera_Hikvision': [3, 4],
            'Server:Cisco-IOS': [4, 5],
            'Cisco': [5, 6],
            'router': [6, 7],
            'router_Cisco': [7, 8]
        }
        self.relations = {
            'indicates_manufacturer': [8, 9],
            'typical_for': [9, 10],
            'has_manufacturer': [10, 11],
            'is_type': [11, 12]
        }
        
    def explain_embedding_learning(self):
        """解释嵌入学习过程"""
        print("=== 知识图谱嵌入学习过程 ===\n")
        
        print("1. 实体和关系的向量化表示:")
        print("   每个实体和关系都被映射到低维向量空间")
        print("   例如: Hikvision → [0.2, -0.1, 0.5, ...]")
        print("   例如: indicates_manufacturer → [0.3, 0.1, -0.2, ...]\n")
        
        print("2. TransE模型的数学原理:")
        print("   对于三元组 (h, r, t):")
        print("   h + r ≈ t")
        print("   其中 h, r, t 分别是头实体、关系、尾实体的向量表示\n")
        
        print("3. 训练目标:")
        print("   最小化正样本的 ||h + r - t||")
        print("   最大化负样本的 ||h + r - t||")
        print("   使得正样本的得分高，负样本的得分低\n")
        
        # 演示向量计算
        self._demonstrate_vector_calculation()
        
    def _demonstrate_vector_calculation(self):
        """演示向量计算过程"""
        print("=== 向量计算演示 ===\n")
        
        # 生成示例向量
        np.random.seed(42)
        
        # 实体向量
        hikvision_vec = np.random.randn(self.embedding_dim)
        camera_vec = np.random.randn(self.embedding_dim)
        indicates_manuf_vec = np.random.randn(self.embedding_dim)
        
        # 计算 h + r
        h_plus_r = hikvision_vec + indicates_manuf_vec
        
        # 计算与目标向量的距离
        target_vec = camera_vec
        distance = np.linalg.norm(h_plus_r - target_vec)
        
        print(f"Hikvision向量: {hikvision_vec[:5]}...")
        print(f"indicates_manufacturer向量: {indicates_manuf_vec[:5]}...")
        print(f"Hikvision + indicates_manufacturer: {h_plus_r[:5]}...")
        print(f"camera向量: {camera_vec[:5]}...")
        print(f"距离: {distance:.4f}")
        print(f"得分: {1.0 / (1.0 + distance):.4f}")
        
    def explain_scoring_function(self):
        """解释评分函数"""
        print("\n=== 评分函数详解 ===\n")
        
        print("TransE评分函数:")
        print("score(h, r, t) = -||h + r - t||")
        print("其中 ||·|| 表示L2范数\n")
        
        print("评分函数的作用:")
        print("1. 正样本: h + r ≈ t，所以 ||h + r - t|| 小，得分高")
        print("2. 负样本: h + r ≠ t，所以 ||h + r - t|| 大，得分低")
        print("3. 训练时最小化负对数似然损失\n")
        
        # 演示不同样本的得分
        self._demonstrate_scoring()
        
    def _demonstrate_scoring(self):
        """演示评分过程"""
        print("=== 评分演示 ===\n")
        
        np.random.seed(42)
        
        # 正样本: (Server:Hikvision-Webs, indicates_manufacturer, Hikvision)
        h1 = np.random.randn(self.embedding_dim)
        r1 = np.random.randn(self.embedding_dim)
        t1 = np.random.randn(self.embedding_dim)
        
        # 负样本: (Server:Hikvision-Webs, indicates_manufacturer, Cisco)
        h2 = h1  # 相同的头实体
        r2 = r1  # 相同的关系
        t2 = np.random.randn(self.embedding_dim)  # 不同的尾实体
        
        # 计算得分
        score_positive = -np.linalg.norm(h1 + r1 - t1)
        score_negative = -np.linalg.norm(h2 + r2 - t2)
        
        print(f"正样本得分: {score_positive:.4f}")
        print(f"负样本得分: {score_negative:.4f}")
        print(f"得分差异: {score_positive - score_negative:.4f}")
        
    def explain_inference_process(self):
        """解释推理过程"""
        print("\n=== 推理过程详解 ===\n")
        
        print("1. 链接预测:")
        print("   给定 (h, r, ?)，预测最可能的尾实体 t")
        print("   计算所有候选实体的得分，选择得分最高的\n")
        
        print("2. 实体预测:")
        print("   给定 (?, r, t)，预测最可能的头实体 h")
        print("   计算所有候选实体的得分，选择得分最高的\n")
        
        print("3. 关系预测:")
        print("   给定 (h, ?, t)，预测最可能的关系 r")
        print("   计算所有候选关系的得分，选择得分最高的\n")
        
        # 演示推理过程
        self._demonstrate_inference()
        
    def _demonstrate_inference(self):
        """演示推理过程"""
        print("=== 推理演示 ===\n")
        
        np.random.seed(42)
        
        # 模拟训练好的嵌入
        embeddings = {
            'Server:Hikvision-Webs': np.random.randn(self.embedding_dim),
            'Hikvision': np.random.randn(self.embedding_dim),
            'Cisco': np.random.randn(self.embedding_dim),
            'camera': np.random.randn(self.embedding_dim),
            'router': np.random.randn(self.embedding_dim),
            'indicates_manufacturer': np.random.randn(self.embedding_dim)
        }
        
        # 链接预测: (Server:Hikvision-Webs, indicates_manufacturer, ?)
        h = embeddings['Server:Hikvision-Webs']
        r = embeddings['indicates_manufacturer']
        
        candidates = ['Hikvision', 'Cisco', 'camera', 'router']
        scores = {}
        
        for candidate in candidates:
            t = embeddings[candidate]
            score = -np.linalg.norm(h + r - t)
            scores[candidate] = score
        
        print("链接预测: (Server:Hikvision-Webs, indicates_manufacturer, ?)")
        for candidate, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  {candidate}: {score:.4f}")
        
        print(f"\n预测结果: {max(scores, key=scores.get)}")
        
    def explain_iot_application(self):
        """解释在IoT设备识别中的应用"""
        print("\n=== IoT设备识别中的应用 ===\n")
        
        print("1. 语义相似性学习:")
        print("   相似的设备在向量空间中距离更近")
        print("   例如: camera_Hikvision 和 camera_Axis 的向量相似\n")
        
        print("2. 关系建模:")
        print("   学习banner特征与设备类型的关系")
        print("   例如: Server:Hikvision-Webs + indicates_device_type ≈ camera\n")
        
        print("3. 泛化能力:")
        print("   即使没见过某个具体设备，也能通过相似性推理")
        print("   例如: 新设备有Hikvision特征 → 可能是摄像头\n")
        
        print("4. 多跳推理:")
        print("   通过关系链进行复杂推理")
        print("   例如: Server:Hikvision-Webs → Hikvision → camera\n")
        
        # 演示IoT应用
        self._demonstrate_iot_application()
        
    def _demonstrate_iot_application(self):
        """演示IoT应用"""
        print("=== IoT应用演示 ===\n")
        
        np.random.seed(42)
        
        # 模拟设备相似性
        camera_embeddings = {
            'camera_Hikvision': np.random.randn(self.embedding_dim),
            'camera_Axis': np.random.randn(self.embedding_dim),
            'camera_Dahua': np.random.randn(self.embedding_dim)
        }
        
        # 计算相似性
        hikvision_vec = camera_embeddings['camera_Hikvision']
        axis_vec = camera_embeddings['camera_Axis']
        dahua_vec = camera_embeddings['camera_Dahua']
        
        sim_hikvision_axis = 1.0 / (1.0 + np.linalg.norm(hikvision_vec - axis_vec))
        sim_hikvision_dahua = 1.0 / (1.0 + np.linalg.norm(hikvision_vec - dahua_vec))
        
        print("设备相似性:")
        print(f"camera_Hikvision vs camera_Axis: {sim_hikvision_axis:.4f}")
        print(f"camera_Hikvision vs camera_Dahua: {sim_hikvision_dahua:.4f}")
        
        # 演示推理
        print("\n推理示例:")
        print("已知: Server:Hikvision-Webs indicates_manufacturer Hikvision")
        print("已知: Hikvision typical_for camera")
        print("推理: 这是一个摄像头设备")
        
    def explain_training_process(self):
        """解释训练过程"""
        print("\n=== 训练过程详解 ===\n")
        
        print("1. 数据准备:")
        print("   正样本: 真实存在的三元组")
        print("   负样本: 随机替换头实体或尾实体生成\n")
        
        print("2. 损失函数:")
        print("   L = -log(σ(score_positive)) - log(1 - σ(score_negative))")
        print("   其中 σ 是sigmoid函数\n")
        
        print("3. 优化目标:")
        print("   最小化正样本的损失")
        print("   最大化负样本的损失")
        print("   使得模型能区分正负样本\n")
        
        print("4. 训练技巧:")
        print("   - 负采样: 为每个正样本生成多个负样本")
        print("   - 学习率调度: 逐渐降低学习率")
        print("   - 正则化: 防止过拟合")
        
    def create_visualization(self):
        """创建可视化"""
        print("\n=== 可视化演示 ===\n")
        
        # 简单的2D可视化
        np.random.seed(42)
        
        # 生成2D嵌入
        entities_2d = {
            'Server:Hikvision-Webs': np.random.randn(2),
            'Hikvision': np.random.randn(2),
            'camera': np.random.randn(2),
            'Server:Cisco-IOS': np.random.randn(2),
            'Cisco': np.random.randn(2),
            'router': np.random.randn(2)
        }
        
        relations_2d = {
            'indicates_manufacturer': np.random.randn(2),
            'typical_for': np.random.randn(2)
        }
        
        # 绘制实体
        plt.figure(figsize=(12, 8))
        
        # 绘制实体点
        for entity, pos in entities_2d.items():
            plt.scatter(pos[0], pos[1], s=100, label=entity)
            plt.annotate(entity, (pos[0], pos[1]), xytext=(5, 5), 
                        textcoords='offset points', fontsize=8)
        
        # 绘制关系向量
        for relation, vec in relations_2d.items():
            plt.arrow(0, 0, vec[0], vec[1], head_width=0.05, 
                     head_length=0.1, fc='red', ec='red', alpha=0.7, label=relation)
        
        plt.title('知识图谱嵌入可视化')
        plt.xlabel('维度1')
        plt.ylabel('维度2')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图片
        plt.savefig('kge_visualization.png', dpi=300, bbox_inches='tight')
        print("可视化图片已保存为 kge_visualization.png")

def main():
    """主函数"""
    print("知识图谱嵌入(KGE)模型详解")
    print("=" * 50)
    
    explainer = KGEExplanation()
    
    # 解释各个部分
    explainer.explain_embedding_learning()
    explainer.explain_scoring_function()
    explainer.explain_inference_process()
    explainer.explain_iot_application()
    explainer.explain_training_process()
    
    # 创建可视化
    explainer.create_visualization()
    
    print("\n=== 总结 ===")
    print("KGE模型通过向量化表示实体和关系，学习它们之间的语义关联")
    print("在IoT设备识别中，可以:")
    print("1. 学习banner特征与设备类型的关联")
    print("2. 发现设备间的相似性")
    print("3. 支持推理和预测")
    print("4. 处理未见过的设备类型")

if __name__ == '__main__':
    main() 