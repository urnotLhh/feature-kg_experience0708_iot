#!/usr/bin/env python
# coding: utf-8
"""
修复实体词汇表中的重复项
"""
import os

def fix_duplicate_entities():
    """修复实体词汇表中的重复项"""
    entity_vocab_file = "data/iot0708/entity.vocab"
    
    print("=== 修复实体词汇表重复项 ===")
    
    # 读取所有行
    with open(entity_vocab_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"原始行数: {len(lines)}")
    
    # 检查重复项
    entity_dict = {}
    duplicates = []
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if '\t' in line:
            idx, entity = line.split('\t', 1)
        else:
            continue
            
        if entity in entity_dict:
            duplicates.append((entity, entity_dict[entity], int(idx)))
        else:
            entity_dict[entity] = int(idx)
    
    print(f"发现 {len(duplicates)} 个重复项")
    
    if duplicates:
        print("重复项详情:")
        for entity, first_idx, second_idx in duplicates[:10]:  # 只显示前10个
            print(f"  {entity}: {first_idx} vs {second_idx}")
        
        # 重新生成词汇表，保留第一次出现的
        new_lines = []
        seen_entities = set()
        
        for line in lines:
            line = line.strip()
            if '\t' in line:
                idx, entity = line.split('\t', 1)
                if entity not in seen_entities:
                    new_lines.append(f"{idx}\t{entity}\n")
                    seen_entities.add(entity)
        
        # 备份原文件
        backup_file = entity_vocab_file + ".backup"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"原文件已备份到: {backup_file}")
        
        # 写入修复后的文件
        with open(entity_vocab_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"修复完成！新文件行数: {len(new_lines)}")
        print(f"移除了 {len(lines) - len(new_lines)} 个重复项")
    else:
        print("没有发现重复项")

if __name__ == '__main__':
    fix_duplicate_entities() 