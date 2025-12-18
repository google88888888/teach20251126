import pandas as pd
import os
import re

def safe_str_contains(series, pattern, regex=False):
    """安全地检查字符串包含关系"""
    try:
        if pd.api.types.is_string_dtype(series):
            return series.str.contains(str(pattern), na=False, regex=regex)
        else:
            # 如果系列不是字符串类型，先转换
            return series.astype(str).str.contains(str(pattern), na=False, regex=regex)
    except:
        # 如果出错，返回一个全False的Series
        return pd.Series([False] * len(series), index=series.index)

def enhanced_process_shoe_mall_files():
    """
    增强版本：使用更精确的匹配逻辑，确保多行记录都能正确匹配
    """
    # 文件路径
    current_file = '鞋城序202511.xlsx'
    prev_file = '鞋城序202510.xlsx'
    output_file = '填充后的鞋城序202511_增强版.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(current_file):
        print(f"错误: 找不到文件 {current_file}")
        return None
    
    if not os.path.exists(prev_file):
        print(f"错误: 找不到文件 {prev_file}")
        return None
    
    print("开始处理鞋城序文件（增强版）...")
    print("=" * 60)
    
    # 读取文件
    try:
        df_current = pd.read_excel(current_file)
        df_prev = pd.read_excel(prev_file)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None
    
    print(f"当前文件行数: {len(df_current)}")
    print(f"历史文件行数: {len(df_prev)}")
    
    # 创建结果DataFrame
    result_df = df_current.copy()
    
    # 确保期间列是数值类型
    df_current['期间'] = pd.to_numeric(df_current['期间'], errors='coerce')
    df_prev['期间'] = pd.to_numeric(df_prev['期间'], errors='coerce')
    
    # 获取所有期间
    all_periods = sorted(set(df_current['期间'].dropna()))
    print(f"所有期间: {all_periods}")
    
    # 用于统计
    total_matches = 0
    
    # 处理每个期间
    for period in all_periods:
        print(f"\n处理期间 {period}:")
        
        # 获取当前期间的所有行
        current_period_rows = df_current[df_current['期间'] == period]
        prev_period_rows = df_prev[df_prev['期间'] == period]
        
        print(f"  当前文件: {len(current_period_rows)} 行")
        print(f"  历史文件: {len(prev_period_rows)} 行")
        
        if len(prev_period_rows) == 0:
            print(f"  历史文件中没有期间 {period} 的记录")
            continue
        
        # 对当前期间的每一行，在历史文件中查找匹配
        for idx_current, row_current in current_period_rows.iterrows():
            best_match = None
            best_match_score = 0
            
            # 在历史文件中查找最佳匹配
            for idx_prev, row_prev in prev_period_rows.iterrows():
                match_score = 0
                
                # 检查日期是否匹配
                if '日期' in row_current and '日期' in row_prev:
                    try:
                        date_current = pd.to_datetime(row_current['日期']).date()
                        date_prev = pd.to_datetime(row_prev['日期']).date()
                        if date_current == date_prev:
                            match_score += 3  # 日期匹配权重最高
                    except:
                        pass
                
                # 检查凭证字号是否匹配
                if '凭证字号' in row_current and '凭证字号' in row_prev:
                    if str(row_current['凭证字号']).strip() == str(row_prev['凭证字号']).strip():
                        match_score += 2
                
                # 检查科目代码是否匹配
                if '科目代码' in row_current and '科目代码' in row_prev:
                    if str(row_current['科目代码']).strip() == str(row_prev['科目代码']).strip():
                        match_score += 3  # 科目代码匹配权重也很高
                
                # 检查科目名称是否相似
                if '科目名称' in row_current and '科目名称' in row_prev:
                    name_current = str(row_current['科目名称']).strip()
                    name_prev = str(row_prev['科目名称']).strip()
                    if name_current == name_prev:
                        match_score += 2
                    elif name_current in name_prev or name_prev in name_current:
                        match_score += 1
                
                # 检查借方金额是否匹配
                if '借方金额' in row_current and '借方金额' in row_prev:
                    try:
                        debit_current = float(row_current['借方金额'])
                        debit_prev = float(row_prev['借方金额'])
                        if abs(debit_current - debit_prev) < 0.01:  # 允许微小误差
                            match_score += 2
                    except:
                        pass
                
                # 检查贷方金额是否匹配
                if '贷方金额' in row_current and '贷方金额' in row_prev:
                    try:
                        credit_current = float(row_current['贷方金额'])
                        credit_prev = float(row_prev['贷方金额'])
                        if abs(credit_current - credit_prev) < 0.01:
                            match_score += 2
                    except:
                        pass
                
                # 检查摘要是否相似
                if '摘要' in row_current and '摘要' in row_prev:
                    summary_current = str(row_current['摘要']).strip()
                    summary_prev = str(row_prev['摘要']).strip()
                    if summary_current == summary_prev:
                        match_score += 2
                    elif summary_current in summary_prev or summary_prev in summary_current:
                        match_score += 1
                    # 检查是否有共同的数字（如年份）
                    elif re.search(r'\d+', summary_current) and re.search(r'\d+', summary_prev):
                        current_numbers = set(re.findall(r'\d+', summary_current))
                        prev_numbers = set(re.findall(r'\d+', summary_prev))
                        if current_numbers & prev_numbers:  # 有共同的数字
                            match_score += 1
                
                # 更新最佳匹配
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match = row_prev
            
            # 如果有足够好的匹配，填充自定义项目
            if best_match_score >= 5 and best_match is not None:  # 设置匹配阈值
                if '自定义项目' in best_match and pd.notna(best_match['自定义项目']):
                    result_df.at[idx_current, '自定义项目'] = best_match['自定义项目']
                    total_matches += 1
                    print(f"  行 {idx_current+2}: 匹配成功（得分: {best_match_score}），已填充自定义项目")
                else:
                    print(f"  行 {idx_current+2}: 匹配成功（得分: {best_match_score}），但自定义项目为空")
            elif best_match_score > 0:
                print(f"  行 {idx_current+2}: 匹配不充分（得分: {best_match_score}），需要 {5-best_match_score} 分才能填充")
            else:
                print(f"  行 {idx_current+2}: 未找到匹配行")
    
    # 格式化日期列 - 只显示年-月-日
    if '日期' in result_df.columns:
        try:
            result_df['日期'] = pd.to_datetime(result_df['日期'], errors='coerce')
            result_df['日期'] = result_df['日期'].dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"格式化日期时出错: {e}")
    
    # 保存结果
    result_df.to_excel(output_file, index=False)
    
    print("\n" + "=" * 60)
    print("增强版处理完成!")
    print(f"总计匹配并填充: {total_matches} 行")
    print(f"结果已保存到: {output_file}")
    
    # 显示期间1的结果
    print("\n期间1的结果预览:")
    period_1_rows = result_df[result_df['期间'] == 1]
    print(period_1_rows[['期间', '日期', '凭证字号', '科目代码', '科目名称', '自定义项目']])
    
    # 检查填充情况
    period_1_filled = period_1_rows['自定义项目'].dropna()
    print(f"\n期间1中自定义项目已填充的行数: {len(period_1_filled)} / {len(period_1_rows)}")
    
    return result_df

# 简化版本：使用精确匹配
def simple_exact_match():
    """
    简化版本：使用精确匹配逻辑
    """
    # 文件路径
    current_file = '鞋城序202511.xlsx'
    prev_file = '鞋城序202510.xlsx'
    output_file = '填充后的鞋城序202511_简化版.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(current_file):
        print(f"错误: 找不到文件 {current_file}")
        return None
    
    if not os.path.exists(prev_file):
        print(f"错误: 找不到文件 {prev_file}")
        return None
    
    print("开始处理鞋城序文件（简化版）...")
    
    # 读取文件
    try:
        df_current = pd.read_excel(current_file)
        df_prev = pd.read_excel(prev_file)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None
    
    # 创建结果DataFrame
    result_df = df_current.copy()
    
    # 确保期间列是数值类型
    df_current['期间'] = pd.to_numeric(df_current['期间'], errors='coerce')
    df_prev['期间'] = pd.to_numeric(df_prev['期间'], errors='coerce')
    
    # 用于统计
    total_matches = 0
    
    # 处理每个期间
    for period in sorted(df_current['期间'].dropna().unique()):
        print(f"\n处理期间 {period}:")
        
        # 获取当前期间的所有行
        current_rows = df_current[df_current['期间'] == period]
        prev_rows = df_prev[df_prev['期间'] == period]
        
        # 按科目代码分组，因为同一个期间内科目代码通常唯一
        for account_code in current_rows['科目代码'].dropna().unique():
            current_account_rows = current_rows[current_rows['科目代码'] == account_code]
            prev_account_rows = prev_rows[prev_rows['科目代码'] == account_code]
            
            if len(current_account_rows) == len(prev_account_rows) and len(current_account_rows) > 0:
                # 如果行数相同，直接按顺序匹配
                for i in range(len(current_account_rows)):
                    idx_current = current_account_rows.index[i]
                    if i < len(prev_account_rows):
                        idx_prev = prev_account_rows.index[i]
                        if '自定义项目' in df_prev.columns and pd.notna(df_prev.loc[idx_prev, '自定义项目']):
                            result_df.at[idx_current, '自定义项目'] = df_prev.loc[idx_prev, '自定义项目']
                            total_matches += 1
                            print(f"  行 {idx_current+2}: 按科目代码匹配成功")
    
    # 格式化日期列
    if '日期' in result_df.columns:
        result_df['日期'] = pd.to_datetime(result_df['日期'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # 保存结果
    result_df.to_excel(output_file, index=False)
    print(f"\n简化版处理完成! 填充了 {total_matches} 行")
    
    return result_df

# 直接运行
if __name__ == "__main__":
    print("请选择处理方式:")
    print("1. 增强版本（推荐，智能匹配）")
    print("2. 简化版本（按科目代码顺序匹配）")
    
    choice = input("请输入选择 (1或2): ").strip()
    
    if choice == "1":
        print("\n使用增强版本处理...")
        result = enhanced_process_shoe_mall_files()
    else:
        print("\n使用简化版本处理...")
        result = simple_exact_match()
    
    if result is not None:
        print("\n处理完成！请检查输出文件。")
    else:
        print("\n处理失败，请检查错误信息。")