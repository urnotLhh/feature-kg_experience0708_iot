#!/usr/bin/env python
# coding: utf-8
"""
自动去重并修复 entity.vocab 文件，确保每个实体只出现一次且编号唯一。
解决 TensorFlow HashTable 初始化失败的问题。
"""
import os
import shutil

def fix_entity_vocab():
    """修复entity.vocab文件中的重复实体问题"""
    print("=== 修复 entity.vocab 文件 ===")
    
    input_file = "data/iot0708/entity.vocab"
    tmp_file = "data/iot0708/entity.vocab.tmp"
    
    if not os.path.exists(input_file):
        print(f"错误: 找不到文件 {input_file}")
        return False
    
    # 读取并去重
    seen = {}
    conflicts = []
    total_lines = 0
    valid_lines = 0
    
    print("读取并分析 entity.vocab 文件...")
    with open(input_file, "r", encoding="utf-8") as fin:
        for line_num, line in enumerate(fin, 1):
            total_lines += 1
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) != 2:
                print(f"警告: 第 {line_num} 行格式不正确: {line}")
                continue
            
            entity, idx = parts
            if entity not in seen:
                seen[entity] = idx
                valid_lines += 1
            elif seen[entity] != idx:
                conflicts.append((entity, seen[entity], idx))
                print(f"发现冲突: {entity} -> {seen[entity]} / {idx}")
    
    print(f"总行数: {total_lines}")
    print(f"有效实体数: {valid_lines}")
    print(f"冲突数量: {len(conflicts)}")
    
    # 写入去重后的文件
    print("写入去重后的文件...")
    with open(tmp_file, "w", encoding="utf-8") as fout:
        for entity, idx in sorted(seen.items(), key=lambda x: int(x[1])):
            fout.write(f"{entity}\t{idx}\n")
    
    # 备份原文件并替换
    backup_file = input_file + ".backup"
    print(f"备份原文件到: {backup_file}")
    shutil.copy2(input_file, backup_file)
    
    print(f"替换原文件: {input_file}")
    shutil.move(tmp_file, input_file)
    
    print("修复完成！")
    return True

def verify_fix():
    """验证修复结果"""
    print("\n=== 验证修复结果 ===")
    
    input_file = "data/iot0708/entity.vocab"
    seen = {}
    duplicates = []
    
    with open(input_file, "r", encoding="utf-8") as fin:
        for line_num, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) != 2:
                continue
            
            entity, idx = parts
            if entity in seen:
                duplicates.append((entity, seen[entity], idx))
            else:
                seen[entity] = idx
    
    if duplicates:
        print("警告: 仍存在重复实体:")
        for entity, idx1, idx2 in duplicates:
            print(f"  {entity}: {idx1} / {idx2}")
        return False
    else:
        print("✓ 验证通过: 无重复实体")
        print(f"✓ 实体总数: {len(seen)}")
        return True

if __name__ == '__main__':
    # 修复文件
    if fix_entity_vocab():
        # 验证修复结果
        if verify_fix():
            print("\n=== 修复成功 ===")
            print("现在可以重新运行训练脚本了！")
        else:
            print("\n=== 修复失败 ===")
            print("请检查文件格式或手动修复")
    else:
        print("\n=== 修复失败 ===") 