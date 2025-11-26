import xlwings as xw
from IPython import get_ipython


def excel_to_df(line):

    if line.strip() == 'i':
        return xw.load()
    else:
        return xw.load(index=False)

# 确保自定义魔术函数已正确注册
get_ipython().register_magic_function(excel_to_df, 'line', 'xl_get')


def write_df_to_excel(line):

    # 分割输入参数
    args = line.replace(' ','').split('--')
    print(args)
    
    # 解析参数
    if len(args) == 1:
        
        # 从行参数中获取 DataFrame 的变量名
        df_name = line.strip()
        # 使用 get_ipython().user_ns 获取用户命名空间
        user_ns = get_ipython().user_ns
        df = eval(df_name, user_ns)
        
        xw.view(df, sheet=xw.sheets.add(), table=False)
        
    elif len(args) == 2:
        
        # 使用 get_ipython().user_ns 获取用户命名空间
        user_ns = get_ipython().user_ns
        df = eval(args[0], user_ns)
        
        if args[1]=='t':
            xw.view(df, sheet=xw.sheets.add())
        else:
            # 1. 写入 DataFrame 到工作表
            sheet = xw.sheets.active
            sht_range = sheet.range(f'{args[1]}')
            sht_range.options(expand='table').value = df

    elif len(args) == 3:

        # 使用 get_ipython().user_ns 获取用户命名空间
        user_ns = get_ipython().user_ns
        df = eval(args[0], user_ns)
        
        # 1. 写入 DataFrame 到工作表
        sheet = xw.sheets.active
        sht_range = sheet.range(f'{args[1]}')
        sht_range.options(expand='table').value = df

        if args[2] == 't':
            
            # 2. 找到最后一个单元格
            # last_cell = sht_range.end('down').end('right')
            # data_range = sheet.range(sht_range, last_cell)
            data_range = sht_range.current_region
            print(data_range)
            
            # 3.将范围转换为超级表
            table = sheet.api.ListObjects.Add(
                # SourceType=0,  # xlSrcRange = 0
                Source=data_range.api,
                XlListObjectHasHeaders=1  # 表示数据区域有标题
            )
    
            # 4. 生成 1-10000 的随机数作为表名
            table_name = '表' + str(random.randint(1, 10000)) 
            table.Name = table_name

# 确保自定义魔术函数已正确注册
get_ipython().register_magic_function(write_df_to_excel, 'line', 'xl_set')


def save_fig_to_excel(line):
    
    # 分割输入参数
    args = line.replace(' ','').split('--')
    print(args)
    
    if len(args) == 1:
        
        # 从行参数中获取 DataFrame 的变量名
        fig_name = line.strip()
        # 使用 get_ipython().user_ns 获取用户命名空间
        user_ns = get_ipython().user_ns
        fig = eval(fig_name, user_ns)
        
        sht = xw.sheets.active
        relative_path = 'plot.png'  # 相对路径
        absolute_path = os.path.abspath(relative_path)  # 转换为绝对路径

        if isinstance(fig, matplotlib.axes._axes.Axes):
            sht.pictures.add(fig.get_figure())
        elif fig.__class__.__module__.startswith('holoviews'):
            hv.save(fig, absolute_path, fmt='png')
            sht.pictures.add(absolute_path)
        elif fig.__class__.__module__.startswith('altair'):
            fig.save(absolute_path, ppi=200)
            sht.pictures.add(absolute_path)
        else:
            sht.pictures.add(fig)

    elif len(args) == 2:
        
        # 使用 get_ipython().user_ns 获取用户命名空间
        user_ns = get_ipython().user_ns
        fig = eval(args[0], user_ns)
        
        sht = xw.sheets.active
        relative_path = 'plot.png'  # 相对路径
        absolute_path = os.path.abspath(relative_path)  # 转换为绝对路径
        sht_range = sht.range(f'{args[1]}')
        
        if isinstance(fig, matplotlib.axes._axes.Axes):
            sht.pictures.add(fig.get_figure(), left=sht_range.left, top=sht_range.top)
        elif fig.__class__.__module__.startswith('holoviews'):
            hv.save(fig, absolute_path, fmt='png')
            sht.pictures.add(absolute_path, left=sht_range.left, top=sht_range.top)
        elif fig.__class__.__module__.startswith('altair'):
            fig.save(absolute_path)
            sht.pictures.add(absolute_path, left=sht_range.left, top=sht_range.top)            
        else:
            sht.pictures.add(fig, left=sht_range.left, top=sht_range.top)

# 确保自定义魔术函数已正确注册
get_ipython().register_magic_function(save_fig_to_excel, 'line', 'xl_plot')
