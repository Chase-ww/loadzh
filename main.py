import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import csv


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.point_file = ""
        self.combo_file = ""
        self.output_file = ""
        self.create_widgets()

    def create_widgets(self):
        # 窗口设置
        self.master.title("荷载组合计算（2025.03.27）")
        self.master.geometry("485x300")

        # 荷载点数据选择
        self.btn_point = tk.Button(self.master, text="选择荷载点文件", command=self.select_point_file)
        self.btn_point.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.lbl_point = tk.Label(self.master, text="请选择文件", wraplength=400)
        self.lbl_point.grid(row=0, column=1, padx=10, sticky="w")

        # 荷载组合配置选择
        self.btn_combo = tk.Button(self.master, text="选择组合配置文件", command=self.select_combo_file)
        self.btn_combo.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.lbl_combo = tk.Label(self.master, text="请选择文件", wraplength=400)
        self.lbl_combo.grid(row=1, column=1, padx=10, sticky="w")

        # 生成按钮
        self.btn_generate = tk.Button(self.master, text="生成结果文件", command=self.generate_output)
        self.btn_generate.grid(row=2, column=0, columnspan=2, pady=20)

        # 状态提示
        self.lbl_status = tk.Label(self.master, text="By Chase Wang", fg="gray")
        self.lbl_status.grid(row=3, column=0, columnspan=2, pady=10)

        # 添加右下角署名（新增部分）
        self.signature = tk.Label(
            self.master,
            text="(*´∀`)~♥",
            fg="gray60",
            font=("Arial", 13)
        )
        self.signature.grid(row=4, column=1, padx=10, pady=5, sticky="se")

        # 配置网格布局权重（新增部分）
        self.master.grid_rowconfigure(4, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def select_point_file(self):
        self.point_file = filedialog.askopenfilename(
            title="选择荷载点数据文件",
            filetypes=[("CSV文件", "*.csv")]
        )
        self.lbl_point.config(text=self.point_file if self.point_file else "未选择文件")

    def select_combo_file(self):
        self.combo_file = filedialog.askopenfilename(
            title="选择组合配置文件",
            filetypes=[("CSV文件", "*.csv")]
        )
        self.lbl_combo.config(text=self.combo_file if self.combo_file else "未选择文件")

    def generate_output(self):
        if not self.point_file or not self.combo_file:
            messagebox.showerror("错误", "请先选择输入文件！")
            return

        self.output_file = filedialog.asksaveasfilename(
            title="保存结果文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")]
        )
        if not self.output_file:
            return

        try:
            self.lbl_status.config(text="计算中...", fg="blue")
            self.update()

            # 执行计算逻辑
            points = self.load_point_data()
            combinations = self.load_combinations()

            all_results = []
            for point_id in sorted(points.keys()):
                point_data = points[point_id]
                point_results = [self.calculate_combination(point_data, combo) for combo in combinations]
                all_results.append(point_results)

            self.save_results(all_results)
            messagebox.showinfo("完成", f"结果文件已生成：\n{self.output_file}")
            self.lbl_status.config(text="By Chase Wang", fg="gray")

        except Exception as e:
            messagebox.showerror("错误", f"计算过程中发生错误：\n{str(e)}")
            self.lbl_status.config(text="By Chase Wang", fg="gray")

    def load_point_data(self):
        df = pd.read_csv(self.point_file)
        points = {}
        for (point_id, load_type), group in df.groupby(['PointID', 'LoadType']):
            if point_id not in points:
                points[point_id] = {}
            values = group[['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']].values[0].tolist()
            points[point_id][load_type] = values
        return points

    def load_combinations(self):
        df = pd.read_csv(self.combo_file)
        required_columns = ['D', 'EX', 'EY', 'EZ', 'T']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"组合配置文件中缺少必要列: {col}")
        return df.to_dict('records')

    def calculate_combination(self, point_data, combo):
        result = np.zeros(6)
        for load_type in ['D', 'EX', 'EY', 'EZ', 'T']:
            coeff = combo.get(load_type, 0.0)
            load_values = np.array(point_data.get(load_type, [0] * 6))
            result += coeff * load_values
        return result.tolist()

    def save_results(self, all_results):
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PointID', 'ComboID', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz'])
            for point_idx, point_res in enumerate(all_results):
                for combo_idx, combo_res in enumerate(point_res):
                    writer.writerow([point_idx, combo_idx] + combo_res)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()