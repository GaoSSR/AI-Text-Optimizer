import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re

class TextSpaceRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("TXT文本空格去除工具 - 专为大模型优化")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="TXT文本空格去除工具", 
                               font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 说明文字
        desc_label = ttk.Label(main_frame, text="专为大模型优化 - 彻底去除文本中的所有空格，减少Token消耗", 
                              font=("微软雅黑", 10), foreground="blue")
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="选择文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        self.browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        self.browse_btn.grid(row=0, column=2)
        
        # 处理选项区域
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.preserve_line_breaks = tk.BooleanVar(value=False)
        self.connect_all_lines = tk.BooleanVar(value=True)
        
        ttk.Label(options_frame, text="✓ 去除所有空格（包括全角空格）", 
                 font=("微软雅黑", 10, "bold"), foreground="green").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="所有文字连在一起（推荐）", 
                       variable=self.connect_all_lines, 
                       command=self.on_connect_option_change).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="保留换行符", 
                       variable=self.preserve_line_breaks).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="文本预览", padding="10")
        preview_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(preview_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.preview_text = tk.Text(text_frame, height=12, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        self.preview_btn = ttk.Button(button_frame, text="预览处理结果", 
                                     command=self.preview_result, state="disabled")
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_btn = ttk.Button(button_frame, text="处理并保存", 
                                     command=self.process_file, state="disabled")
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="清空", command=self.clear_all)
        self.clear_btn.pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar(value="请选择要处理的txt文件")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                foreground="blue", font=("微软雅黑", 9))
        status_label.grid(row=6, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)
        
    def browse_file(self):
        """浏览并选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.preview_btn.config(state="normal")
            self.process_btn.config(state="normal")
            self.status_var.set(f"已选择文件: {os.path.basename(file_path)}")
            
            # 显示原始文件内容预览
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:800] + "..." if len(content) > 800 else content
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, f"原始内容预览:\n{'-'*60}\n{preview}")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")
    
    def on_connect_option_change(self):
        """当选择连接所有文字时，自动取消保留换行符"""
        if self.connect_all_lines.get():
            self.preserve_line_breaks.set(False)
    
    def remove_all_spaces(self, text):
        """彻底去除所有空格 - 专为大模型优化"""
        if self.connect_all_lines.get():
            # 所有文字完全连在一起 - 去除所有空白字符包括换行符
            text = re.sub(r'[\s\u00A0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]+', '', text)
        elif self.preserve_line_breaks.get():
            # 保留换行符，去除所有其他空白字符
            # 包括：普通空格、制表符、全角空格、不间断空格等
            text = re.sub(r'[ \t\f\v\u00A0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]+', '', text)
        else:
            # 去除所有空白字符包括换行符
            text = re.sub(r'[\s\u00A0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]+', '', text)
        
        return text
    
    def preview_result(self):
        """预览处理结果"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择文件")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            processed_content = self.remove_all_spaces(original_content)
            
            # 显示处理前后的对比
            preview = processed_content[:800] + "..." if len(processed_content) > 800 else processed_content
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"处理后内容预览（所有空格已去除）:\n{'-'*60}\n{preview}")
            
            # 显示统计信息
            original_chars = len(original_content)
            processed_chars = len(processed_content)
            saved_chars = original_chars - processed_chars
            saved_percentage = (saved_chars / original_chars * 100) if original_chars > 0 else 0
            
            self.status_var.set(f"原始: {original_chars}字符 → 处理后: {processed_chars}字符 | 节省: {saved_chars}字符 ({saved_percentage:.1f}%)")
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def process_file(self):
        """处理文件并保存"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择文件")
            return
        
        try:
            # 读取原始文件
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 处理文本 - 彻底去除所有空格
            processed_content = self.remove_all_spaces(original_content)
            
            # 生成输出文件名
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_无空格.txt"
            
            # 如果文件已存在，询问是否覆盖
            if os.path.exists(output_path):
                if not messagebox.askyesno("确认", f"文件 {os.path.basename(output_path)} 已存在，是否覆盖？"):
                    return
            
            # 保存处理后的文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # 显示成功信息
            original_chars = len(original_content)
            processed_chars = len(processed_content)
            saved_chars = original_chars - processed_chars
            saved_percentage = (saved_chars / original_chars * 100) if original_chars > 0 else 0
            
            messagebox.showinfo("处理完成！", 
                              f"文件已成功处理并保存！\n\n"
                              f"📁 输出文件: {os.path.basename(output_path)}\n"
                              f"📊 原始字符数: {original_chars:,}\n"
                              f"📊 处理后字符数: {processed_chars:,}\n"
                              f"💰 节省字符数: {saved_chars:,} ({saved_percentage:.1f}%)\n\n"
                              f"✅ 所有空格已彻底去除，大模型Token消耗已优化！")
            
            self.status_var.set(f"✅ 处理完成！已保存到: {os.path.basename(output_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理文件失败: {str(e)}")
    
    def clear_all(self):
        """清空所有内容"""
        self.file_path_var.set("")
        self.preview_text.delete(1.0, tk.END)
        self.preview_btn.config(state="disabled")
        self.process_btn.config(state="disabled")
        self.status_var.set("请选择要处理的txt文件")

def main():
    root = tk.Tk()
    app = TextSpaceRemover(root)
    root.mainloop()

if __name__ == "__main__":
    main()