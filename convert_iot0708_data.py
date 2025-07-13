#!/usr/bin/env python
# coding: utf-8
"""
转换IoT0708数据格式用于TransE训练
将空格分隔的三元组转换为制表符分隔格式
修复包含空格的实体名问题
"""
import os
import shutil

def convert_iot0708_data():
    """转换IoT0708数据格式"""
    print("=== 转换IoT0708数据格式 ===")
    
    # 源文件路径
    source_triples = "data/iot0708/extensible_triples.txt"
    source_entity_vocab = "data/iot0708/entity.vocab"
    source_relation_vocab = "data/iot0708/relation.vocab"
    
    # 检查源文件是否存在
    if not os.path.exists(source_triples):
        print(f"错误: 找不到源文件 {source_triples}")
        return
    
    # 目标目录
    target_dir = "data/iot0708_train"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"创建目标目录: {target_dir}")
    
    # 复制词汇文件
    print("复制词汇文件...")
    shutil.copy2(source_entity_vocab, os.path.join(target_dir, "entity.vocab"))
    shutil.copy2(source_relation_vocab, os.path.join(target_dir, "relation.vocab"))
    
    # 转换triples格式 - 修复包含空格的实体名问题
    print("转换triples格式...")
    target_triples = os.path.join(target_dir, "train.txt")
    
    total_lines = 0
    converted_lines = 0
    error_lines = 0
    
    with open(source_triples, 'r', encoding='utf-8') as f_in, \
         open(target_triples, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in):
            total_lines += 1
            
            if line_num % 100000 == 0:
                print(f"处理第 {line_num} 行...")
            
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            # 修复分割逻辑：正确处理包含空格的实体名
            parts = line.split()
            if len(parts) >= 3:
                # 前两个部分通常是head和relation
                head = parts[0]
                relation = parts[1]
                
                # 剩余部分作为tail，需要重新组合
                tail_parts = parts[2:]
                tail = ' '.join(tail_parts)
                
                # 写入制表符分隔的格式
                f_out.write(f"{head}\t{relation}\t{tail}\n")
                converted_lines += 1
            else:
                error_lines += 1
                if error_lines <= 10:  # 只显示前10个错误
                    print(f"警告: 第 {line_num + 1} 行格式不正确: {line}")
    
    print(f"转换完成！")
    print(f"- 总行数: {total_lines}")
    print(f"- 成功转换: {converted_lines}")
    print(f"- 错误行数: {error_lines}")
    print(f"- 训练数据: {target_triples}")
    print(f"- 实体词汇: {os.path.join(target_dir, 'entity.vocab')}")
    print(f"- 关系词汇: {os.path.join(target_dir, 'relation.vocab')}")
    
    # 验证转换结果
    print("\n验证转换结果...")
    with open(target_triples, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 5:
                parts = line.strip().split('\t')
                print(f"第{i+1}行: {parts}")
            else:
                break
    
    return target_dir

def create_sample_data():
    """创建小样本数据用于快速测试"""
    print("\n=== 创建小样本数据 ===")
    
    source_triples = "data/iot0708/extensible_triples.txt"
    sample_dir = "data/iot0708_sample"
    
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
    
    # 复制词汇文件
    shutil.copy2("data/iot0708/entity.vocab", os.path.join(sample_dir, "entity.vocab"))
    shutil.copy2("data/iot0708/relation.vocab", os.path.join(sample_dir, "relation.vocab"))
    
    # 创建样本数据 (前10000行)
    sample_triples = os.path.join(sample_dir, "train.txt")
    
    converted_lines = 0
    with open(source_triples, 'r', encoding='utf-8') as f_in, \
         open(sample_triples, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in):
            if converted_lines >= 10000:  # 只取前10000个有效行
                break
                
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            if len(parts) >= 3:
                head = parts[0]
                relation = parts[1]
                tail = ' '.join(parts[2:])
                f_out.write(f"{head}\t{relation}\t{tail}\n")
                converted_lines += 1
    
    print(f"样本数据创建完成: {sample_triples}")
    print(f"样本数据行数: {converted_lines}")
    return sample_dir

if __name__ == '__main__':
    # 转换完整数据
    convert_iot0708_data()
    
    # 创建样本数据
    create_sample_data()
    
    print("\n=== 数据转换完成 ===")
    print("现在可以开始训练:")
    print("1. 完整数据训练: python train_iot0708.py")
    print("2. 样本数据训练: python train_iot0708.py (使用data/iot0708_sample)") 