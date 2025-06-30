import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import DatabaseConnection
# import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

teacher_title_map = {
    1: "博士后",
    2: "助教",
    3: "讲师",
    4: "副教授",
    5: "特任教授",
    6: "教授",
    7: "助理研究员",
    8: "特任副研究员",
    9: "副研究员",
    10: "特任研究员",
    11: "研究员"
}
paper_type_map = {
    1: "full paper",
    2: "short paper",
    3: "poster paper",
    4: "demo paper"
}
paper_level_map = {
    1: "CCF-A",
    2: "CCF-B",
    3: "CCF-C",
    4: "中文CCF-A",
    5: "中文CCF-B",
    6: "无级别"
}
project_type_map = {
    1: "国家级项目",
    2: "省部级项目",
    3: "市厅级项目",
    4: "企业合作项目",
    5: "其他类型项目",
}
semester_map = {
    1: "春季学期",
    2: "夏季学期",
    3: "秋季学期"
}
semester_reverse_map = {v: k for k, v in semester_map.items()}
course_property_map = {
    1: "本科生课程",
    2: "研究生课程",
}
# pdfmetrics.registerFont(TTFont('方正清刻本悦宋简体', '方正清刻本悦宋简体.TTF'))
# 使用系统自带的中文字体（Windows）
try:
    # Windows 系统使用宋体
    pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
    chinese_font = 'SimSun'
except:
    # 如果失败则使用默认字体（可能不支持中文）
    chinese_font = 'Helvetica'
    print("警告：未找到中文字体，PDF报告中的中文可能无法显示。")

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("教师教学科研系统")
        self.root.geometry("800x600")
        self.db = DatabaseConnection()
        self.create_main_interface()

    def create_main_interface(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        btn_add = tk.Button(frame, text="教师管理", width=20, height=2, command=self.teacher_management)
        btn_login = tk.Button(frame, text="教师登录", width=20, height=2, command=self.teacher_login)
        btn_query = tk.Button(frame, text="查询统计", width=20, height=2, command=self.query_stats)
        btn_export = tk.Button(frame, text="导出报告", width=20, height=2, command=self.export_report)

        btn_add.grid(row=0, column=0, padx=20, pady=20)
        btn_login.grid(row=0, column=1, padx=20, pady=20)
        btn_query.grid(row=1, column=0, padx=20, pady=20)
        btn_export.grid(row=1, column=1, padx=20, pady=20)


    def teacher_management(self):
        win = tk.Toplevel(self.root)
        win.title("教师管理")
        win.geometry("400x600")
        top_frame = tk.Frame(win)
        top_frame.pack(pady=10)
        tk.Button(win, text="添加教师", command=self.add_teacher).pack(pady=20)

        # ? frame用于放置教师列表
        list_frame = tk.Frame(win)
        # ? fill=tk.BOTH, expand=True表示填充整个窗口并允许扩展
        list_frame.pack(fill=tk.BOTH, expand=True)
        # ? 创建一个Canvas用于显示教师列表
        canvas = tk.Canvas(list_frame)
        # ? 创建一个垂直滚动条
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        # ? 创建一个Frame用于放置教师列表内容
        scroll_frame = tk.Frame(canvas)
        # ? 绑定Frame的配置事件，以便Canvas可以正确计算滚动区域
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # ? 在Canvas中创建一个窗口，将scroll_frame放入其中
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        # ? 设置Canvas的滚动条
        canvas.configure(yscrollcommand=scrollbar.set)
        # ? 将Canvas和滚动条放置在list_frame中
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # ? 将滚动条放置在list_frame的右侧
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        teachers = self.db.execute_query(
            "SELECT * FROM Teacher ORDER BY teacher_id ASC"
        )
        for teacher_id, name, gender, title in teachers:
            frame_row = tk.Frame(scroll_frame, bd=1, relief="solid")
            frame_row.pack(fill=tk.X, pady=2, padx=2)
            title_str = teacher_title_map.get(title, "未知职称")
            info = f"{teacher_id} | {name} | {'男' if gender == 1 else '女'} | 职称:{title_str}"
            tk.Label(frame_row, text=info).pack(side=tk.LEFT, padx=5, fill=tk.X)
            tk.Button(frame_row, text="修改", command=lambda tid=teacher_id: self.modify_teacher(tid, win)).pack(side=tk.RIGHT, padx=5)
            tk.Button(frame_row, text="删除", command=lambda tid=teacher_id: self.delete_teacher(tid)).pack(side=tk.RIGHT)

    def add_teacher(self):
        win = tk.Toplevel(self.root)
        win.title("添加教师")
        win.geometry("400x300")

        tk.Label(win, text="工号:").grid(row=0, column=0, padx=10, pady=5)
        entry_id = tk.Entry(win)
        entry_id.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(win, text="姓名:").grid(row=1, column=0, padx=10, pady=5)
        entry_name = tk.Entry(win)
        entry_name.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(win, text="性别:").grid(row=2, column=0, padx=10, pady=5)
        gender_var = tk.StringVar()
        combo_gender = ttk.Combobox(win, textvariable=gender_var, values=["1-男", "2-女"], state='readonly')
        combo_gender.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(win, text="职称:").grid(row=3, column=0, padx=10, pady=5)
        title_var = tk.StringVar()
        combo_title = ttk.Combobox(win, textvariable=title_var,
                                   values=["1-博士后", "2-助教", "3-讲师", "4-副教授", "5-特任教授", "6-教授", "7-助理研究员", "8-特任副研究员", "9-副研究员", "10-特任研究员", "11-研究员"],
                                   state='readonly')
        combo_title.grid(row=3, column=1, padx=10, pady=5)

        def save():
            tid = entry_id.get().strip()
            name = entry_name.get().strip()
            gender = gender_var.get()
            title = title_var.get()
            if not all([tid, name, gender, title]):
                messagebox.showerror("错误", "所有字段必须填写")
                return
            if len(tid) > 5:
                messagebox.showerror("错误", "工号不能超过5位")
                return
            g = int(gender.split('-')[0])
            t = int(title.split('-')[0])
            # 检查是否存在
            exist = self.db.execute_query("SELECT teacher_id FROM Teacher WHERE teacher_id=%s", (tid,))
            if exist:
                messagebox.showerror("错误", "工号已存在")
                return
            res = self.db.execute_update("INSERT INTO Teacher (teacher_id,name,gender,title) VALUES (%s,%s,%s,%s)", (tid, name, g, t))
            if res > 0:
                messagebox.showinfo("成功", "教师添加成功")
                win.destroy()
                self.teacher_management()
            else:
                messagebox.showerror("错误", "教师添加失败")

        tk.Button(win, text="保存", command=save).grid(row=4, column=0, columnspan=2, pady=20)

    def modify_teacher(self, tid, parent):
        teacher_info = self.db.execute_query(
            "SELECT teacher_id, name, gender, title " \
            "FROM Teacher " \
            "WHERE teacher_id=%s", (tid,)
        )
        if not teacher_info:
            messagebox.showerror("错误", "教师不存在")
            return
        old_tid, old_name, old_gender, old_title = teacher_info[0]
        
        win = tk.Toplevel(parent)
        win.title("修改教师信息")
        win.geometry("400x300")

        tk.Label(win, text="工号:").grid(row=0, column=0, padx=10, pady=5)
        entry_id = tk.Entry(win)
        entry_id.insert(0, old_tid)
        entry_id.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(win, text="姓名:").grid(row=1, column=0, padx=10, pady=5)
        entry_name = tk.Entry(win)
        entry_name.insert(0, str(old_name))
        entry_name.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(win, text="性别:").grid(row=2, column=0, padx=10, pady=5)
        gender_var = tk.StringVar()
        combo_gender = ttk.Combobox(
            win, 
            textvariable=gender_var, 
            values=["1-男", "2-女"], 
            state='readonly'
        )
        combo_gender.set(f"{old_gender}-" + combo_gender.cget("values")[old_gender-1].split('-',1)[1])
        combo_gender.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(win, text="职称:").grid(row=3, column=0, padx=10, pady=5)
        title_var = tk.StringVar()
        combo_title = ttk.Combobox(
            win,
            textvariable=title_var,
            values=["1-博士后", "2-助教", "3-讲师", "4-副教授", "5-特任教授", "6-教授", "7-助理研究员", "8-特任副研究员", "9-副研究员", "10-特任研究员", "11-研究员"],
            state='readonly'
        )
        combo_title.set(f"{old_title}-" + combo_title.cget("values")[old_title-1].split('-',1)[1])
        combo_title.grid(row=3, column=1, padx=10, pady=5)

        def save():
            new_tid = entry_id.get().strip()
            new_name = entry_name.get().strip()
            try:
                new_gender = int(gender_var.get().split('-')[0])
                new_title = int(title_var.get().split('-')[0])
            except:
                messagebox.showerror("错误", "请检查输入格式")
                return
            if not all([new_tid, new_name]):
                messagebox.showerror("错误", "所有字段必须填写")
                return
            if len(new_tid) > 5:
                messagebox.showerror("错误", "工号不能超过5位")
                return
            res = self.db.execute_update(
                "UPDATE Teacher SET teacher_id=%s, name=%s, gender=%s, title=%s " \
                "WHERE teacher_id=%s",(new_tid, new_name, new_gender, new_title, tid)
            )
            if res > 0:
                messagebox.showinfo("成功", "教师信息修改成功")
                win.destroy()
                parent.destroy()
                self.teacher_management()
            else:
                messagebox.showerror("错误", "教师信息修改失败")

        tk.Button(win, text="保存", command=save).grid(row=4, column=0, columnspan=2, pady=20)

    def delete_teacher(self, tid):
        if messagebox.askyesno("确认", "确定删除该教师吗?"):
            res = self.db.execute_update("DELETE FROM Teacher WHERE teacher_id=%s", (tid,))
            if res > 0:
                messagebox.showinfo("成功", "教师删除成功")
                self.teacher_management()

    def teacher_login(self):
        win = tk.Toplevel(self.root)
        win.title("教师登录")
        win.geometry("300x150")
        tk.Label(win, text="工号:").grid(row=0, column=0, padx=10, pady=10)
        entry_id = tk.Entry(win)
        entry_id.grid(row=0, column=1, padx=10, pady=10)

        def login():
            tid = entry_id.get().strip()
            if not tid:
                messagebox.showerror("错误", "请输入工号")
                return
            info = self.db.execute_query(
                "SELECT name, CASE title WHEN 1 THEN '博士后' WHEN 2 THEN '助教' WHEN 3 THEN '讲师' WHEN 4 THEN '副教授' WHEN 5 THEN '特任教授' WHEN 6 THEN '教授' WHEN 7 THEN '助理研究员' WHEN 8 THEN '特任副研究员' WHEN 9 THEN '副研究员' WHEN 10 THEN '特任研究员' WHEN 11 THEN '研究员' END as title FROM Teacher WHERE teacher_id=%s", (tid,))
            if not info:
                messagebox.showerror("错误", "教师不存在")
                return
            name, title = info[0]
            win.destroy()
            self.open_teacher_dashboard(tid, name, title)

        tk.Button(win, text="登录", command=login).grid(row=1, column=0, columnspan=2, pady=10)

    def open_teacher_dashboard(self, tid, name, title):
        dash = tk.Toplevel(self.root)
        dash.title(f"教师-{tid}")
        dash.geometry("600x500")
        tk.Label(dash, text=f"你好, {name} {title}", font=("方正清刻本悦宋简体", 16)).pack(pady=10)
        frame = tk.Frame(dash)
        frame.pack(pady=20)
        btn_paper = tk.Button(frame, text="论文管理", width=15, command=lambda: self.paper_management(tid))
        btn_course = tk.Button(frame, text="课程管理", width=15, command=lambda: self.course_management(tid))
        btn_project = tk.Button(frame, text="项目管理", width=15, command=lambda: self.project_management(tid))
        btn_paper.grid(row=0, column=0, padx=10)
        btn_course.grid(row=0, column=1, padx=10)
        btn_project.grid(row=0, column=2, padx=10)


    def paper_management(self, tid):
        win = tk.Toplevel(self.root)
        win.title("论文管理")
        win.geometry("1000x600")
        top_frame = tk.Frame(win)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="新论文", command=lambda: self.add_new_paper(tid, win)).grid(row=0, column=0, padx=5)
        tk.Button(top_frame, text="合作论文", command=lambda: self.coop_paper(tid, win)).grid(row=0, column=1, padx=5)
        tk.Button(top_frame, text="查询论文", command=lambda: self.search_paper_window(tid)).grid(row=0, column=2, padx=5)

        # 论文列表
        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(list_frame)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 获取教师论文
        papers = self.db.execute_query(
            "SELECT p.paper_id, p.paper_name, p.pub_source, p.pub_year, p.paper_type, p.paper_level, tp.author_rank, tp.is_corresponding " \
            "FROM Teacher_Paper tp JOIN Paper p ON tp.paper_id=p.paper_id " \
            "WHERE tp.teacher_id=%s ORDER BY p.paper_id ASC", (tid,)
        )
        for idx, (pid, name, src, yr, ptype, plevel, rank, corr) in enumerate(papers):
            frame_row = tk.Frame(scroll_frame, bd=1, relief="solid")
            frame_row.pack(fill=tk.X, pady=2, padx=2)
            ptype_str = paper_type_map.get(ptype, "未知类型")
            plevel_str = paper_level_map.get(plevel, "未知级别")
            info = f"{pid} | {name} | {src} | {yr} | 类型:{ptype_str} | 级别:{plevel_str} | 排名:{rank} | {'是通讯作者' if corr else ''}"            
            tk.Button(frame_row, text="修改", command=lambda p=pid, r=rank, c=corr: self.modify_teacher_paper(tid, p, r, c, win))\
                .pack(side=tk.RIGHT, padx=5)
            tk.Button(frame_row, text="删除", command=lambda p=pid: self.delete_teacher_paper(tid, p, win))\
                .pack(side=tk.RIGHT)
            tk.Label(frame_row, text=info).pack(side=tk.LEFT, fill=tk.X, padx=5)

    def add_new_paper(self, tid, parent):
        win = tk.Toplevel(parent)
        win.title("新论文")
        win.geometry("1000x500")
        labels = ["论文序号", "论文名称", "发表源", "发表年份", "论文类型", "论文级别", "作者排名", "是否通讯作者"]
        entries = {}
        for i, text in enumerate(labels):
            tk.Label(win, text=f"{text}:").grid(row=i, column=0, padx=10, pady=5, sticky='w')
            if text in ["论文类型"]:
                var = tk.StringVar()
                combo = ttk.Combobox(win, width=100, textvariable=var, values=["1-full paper", "2-short paper", "3-poster paper", "4-demo paper"], state='readonly')
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = combo
            elif text in ["论文级别"]:
                var = tk.StringVar()
                combo = ttk.Combobox(win, width=100, textvariable=var, values=["1-CCF-A", "2-CCF-B", "3-CCF-C", "4-中文CCF-A", "5-中文CCF-B", "6-无级别"], state='readonly')
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = combo
            elif text in ["是否通讯作者"]:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(win, variable=var)
                chk.grid(row=i, column=1, padx=10, pady=5, sticky='w')
                entries[text] = var
            else:
                entry = tk.Entry(win, width=100)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = entry

        def save():
            try:
                pid = int(entries["论文序号"].get().strip())
                pname = entries["论文名称"].get().strip()
                src = entries["发表源"].get().strip()
                pyr = int(entries["发表年份"].get().strip())
                ptype = int(entries["论文类型"].get().split('-')[0])
                plevel = int(entries["论文级别"].get().split('-')[0])
                prank = int(entries["作者排名"].get().strip())
                pcorr = entries["是否通讯作者"].get()
                if not all([pname, src]):   # ? 
                    messagebox.showerror("错误", "论文名称和发表源不能为空")
                    raise ValueError
            except:
                messagebox.showerror("错误", "请检查所有输入项，确保格式正确")
                return
            # ? 检查论文序号是否已存在
            existing = self.db.execute_query("SELECT paper_id FROM Paper WHERE paper_id=%s", (pid,))
            if existing:
                messagebox.showerror("错误", "论文序号已存在")
                return
            # 检查排名是否合法
            if prank < 1:
                messagebox.showerror("错误", "作者排名必须大于0")
                return
            # 检查年份是否合法
            if pyr < 1958 or pyr > 2030:
                messagebox.showerror("错误", "发表年份必须在1958到2030之间")
                return
            # 检查通讯作者唯一
            if pcorr:
                cnt = self.db.execute_query("SELECT COUNT(*) FROM Teacher_Paper WHERE paper_id=%s AND is_corresponding=1", (pid,))
                if cnt and cnt[0][0] > 0:
                    messagebox.showerror("错误", "该论文已有通讯作者")
                    return
                
            # 插入 Paper
            res1 = self.db.execute_update(
                "INSERT INTO Paper (paper_id,paper_name,pub_source,pub_year,paper_type,paper_level) " \
                "VALUES (%s,%s,%s,%s,%s,%s)", 
                (pid, pname, src, pyr, ptype, plevel)
            )
            if res1 < 1:
                messagebox.showerror("错误", "论文添加失败，可能序号已存在")
                return
            # 插入 Teacher_Paper
            res2 = self.db.execute_update(
                "INSERT INTO Teacher_Paper (teacher_id,paper_id,author_rank,is_corresponding) " \
                "VALUES (%s,%s,%s,%s)", 
                (tid, pid, prank, pcorr)
            )
            if res2 > 0:
                messagebox.showinfo("成功", "新论文添加成功")
                win.destroy()
                parent.destroy()
                self.paper_management(tid)
            else:
                messagebox.showerror("错误", "关联教师论文失败")

        tk.Button(win, text="保存", command=save).grid(row=len(labels), column=0, columnspan=2, pady=20)

    def coop_paper(self, tid, parent):
        win = tk.Toplevel(parent)
        win.title("合作论文")
        win.geometry("1000x300")
        # 获取可选论文
        papers = self.db.execute_query(
            "SELECT paper_id, paper_name " \
            "FROM Paper " \
            "WHERE paper_id NOT IN "
                "(SELECT paper_id " \
                "FROM Teacher_Paper " \
                "WHERE teacher_id=%s)", (tid,)
        )

        choices = [
            f"{pid}-{pname}" 
            for pid, pname in papers
        ]

        tk.Label(win, text="选择论文:").grid(row=0, column=0, padx=10, pady=5)
        var = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=var, values=choices, state='readonly', width=100)
        combo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(win, text="作者排名:").grid(row=1, column=0, padx=10, pady=5)
        entry_rank = tk.Entry(win, width=100)
        entry_rank.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(win, text="是否通讯作者:").grid(row=2, column=0, padx=10, pady=5)
        corr_var = tk.BooleanVar()
        tk.Checkbutton(win, variable=corr_var).grid(row=2, column=1, padx=10, pady=5, sticky='w')

        def save():
            sel = var.get().strip()
            if not sel:
                messagebox.showerror("错误", "请选择论文")
                return
            pid = int(sel.split('-')[0])
            try:
                prank = int(entry_rank.get().strip())
            except:
                messagebox.showerror("错误", "排名必须为数字")
                return
            # 检查排名是否合法
            if prank < 1:
                messagebox.showerror("错误", "作者排名必须大于0")
                return
            # 通讯作者的唯一性
            pcorr = corr_var.get()
            if pcorr:
                cnt = self.db.execute_query("SELECT COUNT(*) FROM Teacher_Paper WHERE paper_id=%s AND is_corresponding=1", (pid,))
                if cnt and cnt[0][0] > 0:
                    messagebox.showerror("错误", "该论文已有通讯作者")
                    return
            # 检查排名是否唯一
            # ? cnt是查询结果，cnt[0][0]是查询到的行数，若没查到则为0
            cnt = self.db.execute_query(
                "SELECT COUNT(*) FROM Teacher_Paper WHERE paper_id=%s AND author_rank=%s AND teacher_id<>%s",
                (pid, prank, tid)
            )
            if cnt and cnt[0][0] > 0:
                messagebox.showerror("错误", f"排名 {prank} 已被其他作者使用，请换一个")
                return
            
            res = self.db.execute_update("INSERT INTO Teacher_Paper (teacher_id,paper_id,author_rank,is_corresponding) VALUES (%s,%s,%s,%s)", (tid, pid, prank, pcorr))
            if res > 0:
                messagebox.showinfo("成功", "合作论文添加成功")
                win.destroy()
                parent.destroy()
                self.paper_management(tid)
            else:
                messagebox.showerror("错误", "添加失败，可能重复")

        tk.Button(win, text="保存", command=save).grid(row=3, column=0, columnspan=2, pady=20)

    def search_paper_window(self, tid):
        term = simpledialog.askstring("查询", "请输入论文名称或序号:")
        if term is None:
            return
        try:
            pid = int(term)
            query = "SELECT p.paper_id, p.paper_name, p.pub_source, p.pub_year, tp.author_rank, tp.is_corresponding FROM Teacher_Paper tp JOIN Paper p ON tp.paper_id=p.paper_id WHERE tp.teacher_id=%s AND p.paper_id=%s"
            params = (tid, pid)
        except:
            query = "SELECT p.paper_id, p.paper_name, p.pub_source, p.pub_year, tp.author_rank, tp.is_corresponding FROM Teacher_Paper tp JOIN Paper p ON tp.paper_id=p.paper_id WHERE tp.teacher_id=%s AND p.paper_name LIKE %s"
            params = (tid, f"%{term}%")
        results = self.db.execute_query(query, params)
        if not results:
            messagebox.showinfo("结果", "未找到相关论文")
            return
        win = tk.Toplevel(self.root)
        win.title("查询结果")
        for i, (pid, name, src, yr, rank, corr) in enumerate(results):
            text = f"{pid} | {name} | {src} | {yr} | 排名:{rank} | {'通讯作者' if corr else ''}"
            tk.Label(win, text=text).pack(anchor='w', padx=10, pady=2)

    def modify_teacher_paper(self, tid, pid, old_rank, old_corr, parent):
        paper_info = self.db.execute_query(
            "SELECT paper_name, pub_source, pub_year, paper_type, paper_level " \
            "FROM Paper " \
            "WHERE paper_id=%s", (pid,)
        )
        if not paper_info:
            messagebox.showerror("错误", "论文不存在")
            return
        paper_name, pub_source, pub_year, paper_type, paper_level = paper_info[0]
        
        win = tk.Toplevel(parent)
        win.title("修改论文信息")
        win.geometry("600x400")

        # 论文字段
        tk.Label(win, text=f"论文序号:                  " + str(pid)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        tk.Label(win, text="论文名称:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        entry_name = tk.Entry(win, width=100)
        entry_name.insert(0, paper_name)
        entry_name.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(win, text="发表源:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        entry_src = tk.Entry(win, width=100)
        entry_src.insert(0, pub_source)
        entry_src.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(win, text="发表年份:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        entry_year = tk.Entry(win, width=100)
        entry_year.insert(0, str(pub_year))
        entry_year.grid(row=3, column=1, padx=10, pady=5)
        tk.Label(win, text="论文类型:").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        type_var = tk.StringVar()
        # ? ComboBox下拉文本框，创建属性
        combo_type = ttk.Combobox(win, textvariable=type_var, values=["1-full paper", "2-short paper", "3-poster paper", "4-demo paper"], state='readonly')
        # ? 设置默认值，数字-(该数字对应的文本按照-拆开成两部分的第二部分[1])
        combo_type.set(f"{paper_type}-" + combo_type.cget("values")[paper_type-1].split('-',1)[1])
        combo_type.grid(row=4, column=1, padx=10, pady=5)
        tk.Label(win, text="论文级别:").grid(row=5, column=0, padx=10, pady=5, sticky='w')
        level_var = tk.StringVar()
        combo_level = ttk.Combobox(win, textvariable=level_var, values=["1-CCF-A", "2-CCF-B", "3-CCF-C", "4-中文CCF-A", "5-中文CCF-B", "6-无级别"], state='readonly')
        combo_level.set(f"{paper_level}-" + combo_level.cget("values")[paper_level-1].split('-',1)[1])
        combo_level.grid(row=5, column=1, padx=10, pady=5)

        # 关联字段
        tk.Label(win, text="作者排名:").grid(row=6, column=0, padx=10, pady=5, sticky='w')
        entry_rank = tk.Entry(win)
        entry_rank.insert(0, str(old_rank))
        entry_rank.grid(row=6, column=1, padx=10, pady=5)
        tk.Label(win, text="是否通讯作者:").grid(row=7, column=0, padx=10, pady=5, sticky='w')
        corr_var = tk.BooleanVar(value=old_corr)
        tk.Checkbutton(win, variable=corr_var).grid(row=7, column=1, padx=10, pady=5, sticky='w')

        def save():
            new_name = entry_name.get().strip()
            new_src = entry_src.get().strip()
            try:
                new_year = int(entry_year.get().strip())
                new_type = int(type_var.get().split('-')[0])
                new_level = int(level_var.get().split('-')[0])
                new_rank = int(entry_rank.get().strip())
            except:
                messagebox.showerror("错误", "请检查输入格式")
                return
            new_corr = corr_var.get()
            if not all([new_name, new_src]):
                messagebox.showerror("错误", "论文名称和发表源不能为空")
                return
            # 检查排名是否合法
            if new_rank < 1:
                messagebox.showerror("错误", "作者排名必须大于0")
                return
            # 检查年份是否合法
            if new_year < 1958 or new_year > 2030:
                messagebox.showerror("错误", "发表年份必须在1958到2030之间")
                return
            # 检查通讯作者唯一性
            if new_corr and not old_corr:
                cnt = self.db.execute_query(
                    "SELECT COUNT(*) FROM Teacher_Paper WHERE paper_id=%s AND is_corresponding=1 AND teacher_id<>%s", (pid, tid)
                )
                if cnt and cnt[0][0] > 0:
                    messagebox.showerror("错误", "该论文已有其他通讯作者")
                    return
            # 检查排名是否唯一
            # ? cnt是查询结果，cnt[0][0]是查询到的行数，若没查到则为0
            cnt = self.db.execute_query(
                "SELECT COUNT(*) FROM Teacher_Paper WHERE paper_id=%s AND author_rank=%s AND teacher_id<>%s",
                (pid, new_rank, tid)
            )
            if cnt and cnt[0][0] > 0:
                messagebox.showerror("错误", f"排名 {new_rank} 已被其他作者使用，请换一个")
                return

            # 更新 Paper, res是影响的行数，不变则返回0
            res1 = self.db.execute_update(
                "UPDATE Paper SET paper_name=%s, pub_source=%s, pub_year=%s, paper_type=%s, paper_level=%s WHERE paper_id=%s",
                (new_name, new_src, new_year, new_type, new_level, pid)
            )
            # 更新 Teacher_Paper, res是影响的行数，不变则返回0
            res2 = self.db.execute_update(
                "UPDATE Teacher_Paper SET author_rank=%s, is_corresponding=%s WHERE teacher_id=%s AND paper_id=%s",
                (new_rank, new_corr, tid, pid)
            )
            if res1 > 0 or res2 > 0:    # ! 只要有一条记录被更新就算成功
                messagebox.showinfo("成功", "论文信息修改成功")
                win.destroy()
                parent.destroy()
                self.paper_management(tid)
            else:
                messagebox.showerror("错误", "修改失败")    #现在修改会失败(已解决)

        tk.Button(win, text="保存", command=save).grid(row=7, column=0, columnspan=2, pady=20)

    def delete_teacher_paper(self, tid, pid, parent=None):
        if messagebox.askyesno("确认", "确定删除该记录吗?"):
            this_author_rank = self.db.execute_query("SELECT author_rank FROM Teacher_paper WHERE teacher_id=%s AND paper_id=%s", (tid, pid,))
            self.db.execute_update("DELETE FROM Teacher_Paper WHERE teacher_id=%s AND paper_id=%s", (tid, pid))
            # 如果是第一作者，直接把论文从 Paper 表中删除
            if this_author_rank and this_author_rank[0][0] == 1:
                if messagebox.askyesno("确认", "该论文是第一作者，是否同时删除论文记录?"):
                    self.db.execute_update("DELETE FROM Paper WHERE paper_id=%s", (pid,))
            messagebox.showinfo("成功", "删除成功")
            if parent:  #
                parent.destroy()


    def course_management(self, tid):
        win = tk.Toplevel(self.root)
        win.title("课程管理")
        win.geometry("700x600")
        top_frame = tk.Frame(win)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="新增授课", command=lambda: self.add_new_course(tid, win)).grid(row=0, column=0, padx=5)
        tk.Button(top_frame, text="共同授课", command=lambda: self.coop_course(tid, win)).grid(row=0, column=1, padx=5)
        tk.Button(top_frame, text="查询课程", command=lambda: self.search_course_window(tid)).grid(row=0, column=2, padx=5)

        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(list_frame)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        entries = self.db.execute_query(
            "SELECT c.course_id, c.course_name, tc.year, tc.semester, c.property, c.total_hours, tc.my_hours " \
            "FROM Teacher_Course tc JOIN Course c ON tc.course_id=c.course_id " \
            "WHERE tc.teacher_id=%s ORDER BY tc.year, tc.semester", (tid,)
        )
        for idx, (cid, cname, yr, sem, prop, ttl_hrs, my_hrs) in enumerate(entries):
            frame_row = tk.Frame(scroll_frame, bd=1, relief="solid")
            frame_row.pack(fill=tk.X, pady=2, padx=2)
            sem_str = semester_map.get(sem, "未知学期")
            prop_str = course_property_map.get(prop, "未知属性")
            info = f"{cid} | {cname} | 年度:{yr} | 学期:{sem_str} | 性质:{prop_str} | 总学时:{ttl_hrs} | 我的学时:{my_hrs}"
            tk.Label(frame_row, text=info).pack(side=tk.LEFT, padx=5)
            tk.Button(frame_row, text="修改", command=lambda c=cid: self.modify_teacher_course(tid, c, cname, yr, sem, my_hrs, win)).pack(side=tk.RIGHT, padx=5)
            tk.Button(frame_row, text="删除", command=lambda c=cid: self.delete_teacher_course(tid, c, win)).pack(side=tk.RIGHT)

    def add_new_course(self, tid, parent):
        win = tk.Toplevel(parent)
        win.title("新增授课")
        win.geometry("1000x500")
        labels = ["课程号", "课程名称", "年度", "学期", "课程性质", "我的学时"]
        entries = {}
        for i, text in enumerate(labels):
            tk.Label(win, text=f"{text}:").grid(row=i, column=0, padx=10, pady=5, sticky='w')
            if text in ["课程性质"]:
                var = tk.StringVar()
                combo = ttk.Combobox(win, width=100, textvariable=var, values=["1-本科生课程", "2-研究生课程",], state='readonly')
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = combo
            elif text in ["学期"]:
                var = tk.StringVar()
                combo = ttk.Combobox(win, width=100, textvariable=var, values=["1-春季学期", "2-夏季学期", "3-秋季学期",], state='readonly')
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = combo
            else:
                entry = tk.Entry(win, width=100)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = entry
        
        def save():
            try:
                cid = entries["课程号"].get().strip()
                cname = entries["课程名称"].get().strip()
                cyr = int(entries["年度"].get().strip())
                csem = int(entries["学期"].get().split('-')[0])
                cprop = int(entries["课程性质"].get().split('-')[0])
                # cttl_hrs = entries["总学时"].get().strip()
                my_hrs = entries["我的学时"].get().strip()
                if not all([cid, cname, cyr, my_hrs]):
                    messagebox.showerror("错误", "所有字段必须填写")
                    raise ValueError
            except:
                messagebox.showerror("错误", "请检查输入格式")
                return

            # 检查课程是否已存在
            existing = self.db.execute_query(
                "SELECT course_id FROM Course WHERE course_id=%s", (cid,)
            )
            if existing:
                messagebox.showerror("错误", "课程号已存在，请使用其他课程号")
                return
            # 检查年度格式
            if cyr < 1958 or cyr > 2030:
                messagebox.showerror("错误", "发表年份必须在1958到2030之间")
                return
            # 插入 Course
            # ! 新课程当前总学时为0，直接加上我的学时
            res1 = self.db.execute_update(
                "INSERT INTO Course (course_id, course_name, property, total_hours) " \
                "VALUES (%s, %s, %s, %s)",
                (cid, cname, cprop, my_hrs)
            )
            if res1 < 1:
                messagebox.showerror("错误", "课程添加失败，可能课程号已存在")
                return
            # 插入 Teacher_Course
            res2 = self.db.execute_update(
                "INSERT INTO Teacher_Course (teacher_id, course_id, year, semester, my_hours) " \
                "VALUES (%s, %s, %s, %s, %s)",
                (tid, cid, cyr, csem, my_hrs)
            )
            if res2 > 0:
                messagebox.showinfo("成功", "新授课添加成功")
                win.destroy()
                parent.destroy()
                self.course_management(tid)
            else:
                messagebox.showerror("错误", "关联教师课程失败")

        tk.Button(win, text="保存", command=save).grid(row=7, column=0, columnspan=2, pady=20)

    def coop_course(self, tid, parent):
        """共同授课：把当前教师添加到一个已有的课程开设记录中"""
        win = tk.Toplevel(parent)
        win.title("共同授课")
        win.geometry("600x300")

        # 1. 查询所有已有的“课程+学年+学期”记录，排除当前教师已参与的
        offerings = self.db.execute_query(
            "SELECT DISTINCT tc.course_id, c.course_name, tc.year, tc.semester, c.total_hours "
            "FROM Teacher_Course tc "
            "JOIN Course c ON tc.course_id=c.course_id "
            "WHERE NOT EXISTS ("
            "  SELECT 1 FROM Teacher_Course tc2 "
            "  WHERE tc2.teacher_id=%s AND tc2.course_id=tc.course_id "
            "    AND tc2.year=tc.year AND tc2.semester=tc.semester"
            ")",
            (tid,)
        )

        choices = [
            f"{cid}-{cname}-{yr}-{semester_map.get(sem, '未知学期')}" 
            for cid, cname, yr, sem, _ in offerings
        ]

        tk.Label(win, text="选择课程开设:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        var = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=var, values=choices, state='readonly', width=50)
        combo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="我的学时:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        entry_hrs = tk.Entry(win)
        entry_hrs.grid(row=1, column=1, padx=10, pady=5)

        def save():
            sel = var.get().strip()
            if not sel:
                messagebox.showerror("错误", "请选择一个课程开设")
                return
            try:
                my_hrs = int(entry_hrs.get().strip())
            except:
                messagebox.showerror("错误", "学时必须为整数")
                return
            
            cid, cname, yr, sem_label = sel.split('-', 3)
            yr = int(yr)
            sem = semester_reverse_map.get(sem_label, 0)
            if sem == 0:
                messagebox.showerror("错误", "学期选择无效")
                return
            # 插入关联
            res = self.db.execute_update(
                "INSERT INTO Teacher_Course (teacher_id,course_id,year,semester,my_hours) "
                "VALUES (%s,%s,%s,%s,%s)",
                (tid, cid, yr, sem, my_hrs)
            )
            if res > 0:
                total = self.db.execute_query(
                    "SELECT SUM(my_hours) " \
                    "FROM Teacher_Course " \
                    "WHERE course_id=%s AND year=%s AND semester=%s",
                    (cid, yr, sem)
                )[0][0] or 0
                self.db.execute_update(
                    "UPDATE Course SET total_hours=%s WHERE course_id=%s",
                    (total, cid)
                )
                messagebox.showinfo("成功", "共同授课添加成功")
                win.destroy()
                parent.destroy()
                self.course_management(tid)
            else:
                messagebox.showerror("错误", "添加失败，可能已存在记录")

        tk.Button(win, text="保存", command=save).grid(row=2, column=0, columnspan=2, pady=20)
    
    def modify_teacher_course(self, tid, cid, cname, year, semester, old_hrs, parent):
        """修改当前教师在某课程开设中的学时"""
        win = tk.Toplevel(parent)
        win.title("修改授课信息")
        win.geometry("500x400")

        tk.Label(win, text=f"课程号: {cid}").pack(anchor='w', padx=10, pady=10)
        entry_cid = tk.Entry(win)
        entry_cid.insert(0, cid)
        entry_cid.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(win, text=f"课程名称: {cname}").pack(anchor='w', padx=10)
        entry_cname = tk.Entry(win)
        entry_cname.insert(0, cname)
        entry_cname.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(win, text=f"年度: {year}").pack(anchor='w', padx=10)
        entry_year = tk.Entry(win)
        entry_year.insert(0, str(year))
        entry_year.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(win, text=f"学期: {semester_map.get(semester, '未知学期')}").pack(anchor='w', padx=10)
        sem_var = tk.StringVar()
        combo_sem = ttk.Combobox(win, textvariable=sem_var, values=list(semester_map.values()), state='readonly')
        combo_sem.set(f"{semester}-" + semester_map.get(semester, "未知学期"))
        combo_sem.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(win, text="我的学时:").pack(anchor='w', padx=10)
        entry_hrs = tk.Entry(win)
        entry_hrs.insert(0, str(old_hrs))
        entry_hrs.pack(fill=tk.X, padx=10, pady=5)

        def save():
            try:
                new_cid = entry_cid.get().strip()
                new_cname = entry_cname.get().strip()
                new_year = int(entry_year.get().strip())
                new_sem = sem_var.get().split('-')[0]
                new_hrs = int(entry_hrs.get().strip())
            except:
                messagebox.showerror("错误", "学时必须为整数")
                return
            # 检查课程号是否已存在
            existing = self.db.execute_query(
                "SELECT course_id FROM Course WHERE course_id=%s AND course_id<>%s", (new_cid, cid)
            )
            if existing:
                messagebox.showerror("错误", "课程号已存在，请使用其他课程号")
                return
            # 检查年度格式
            if new_year < 1958 or new_year > 2030:
                messagebox.showerror("错误", "年度必须在1958到2030之间")
                return
            # 更新 Course
            res1 = self.db.execute_update(
                "UPDATE Course SET course_id=%s, course_name=%s WHERE course_id=%s",
                (new_cid, new_cname, cid)
            )
            # 更新Teacher_Course
            res2 = self.db.execute_update(
                "UPDATE Teacher_Course " \
                "SET my_hours=%s, course_id=%s, year=%s, semester=%s "
                "WHERE teacher_id=%s AND course_id=%s AND year=%s AND semester=%s",
                (new_hrs, new_cid, new_year, new_sem, tid, cid, year, semester)
            )
            if res2 >= 0 or res1 >= 0:  # ! 完全没变也是可以的
                total = self.db.execute_query(
                    "SELECT SUM(my_hours) FROM Teacher_Course "
                    "WHERE course_id=%s AND year=%s AND semester=%s",
                    (new_cid, new_year, new_sem)
                )[0][0] or 0
                self.db.execute_update(
                    "UPDATE Course SET total_hours=%s WHERE course_id=%s",
                    (total, new_cid)
                )
                messagebox.showinfo("成功", "授课信息修改成功")
                win.destroy()
                parent.destroy()
                self.course_management(tid)
            else:
                messagebox.showerror("错误", "修改失败")

        tk.Button(win, text="保存", command=save).pack(pady=15)

    def delete_teacher_course(self, tid, cid, parent):
        if messagebox.askyesno("确认", "确定删除该记录吗?"):
            # 1. 查出这一条关联记录对应的 course_id 和 my_hours
            row = self.db.execute_query(
                "SELECT course_id, my_hours " \
                "FROM Teacher_Course WHERE teacher_id=%s AND course_id=%s",
                (tid, cid,)
            )
            if row:
                course_id, my_hours = row[0]
                # 2. 读 Course.total_hours
                total = self.db.execute_query(
                    "SELECT total_hours " \
                    "FROM Course WHERE course_id=%s",
                    (course_id,)
                )
                total = total[0][0] or 0

                # 3. 删除这条关联
                self.db.execute_update(
                    "DELETE FROM Teacher_Course " \
                    "WHERE teacher_id=%s AND course_id=%s",
                    (tid, cid,)
                )

                # 4. 如果原来只有这一个老师，就删除 Course 表中该课程
                if total == my_hours:
                    self.db.execute_update(
                        "DELETE FROM Course " \
                        "WHERE course_id=%s",
                        (course_id,)
                    )
                else:
                    # 5. 否则更新总学时为删除后的新和
                    new_total = total - my_hours
                    self.db.execute_update(
                        "UPDATE Course SET total_hours=%s " \
                        "WHERE course_id=%s",
                        (new_total, course_id)
                    )

            messagebox.showinfo("成功", "删除成功")
            parent.destroy()
            self.course_management(tid)

    def search_course_window(self, tid):
        term = simpledialog.askstring("查询", "请输入课程名称或课程号:")
        if term is None:
            return
        query = "SELECT c.course_id, c.course_name, tc.year, tc.semester, tc.my_hours FROM Teacher_Course tc JOIN Course c ON tc.course_id=c.course_id WHERE tc.teacher_id=%s AND (c.course_id LIKE %s OR c.course_name LIKE %s)"
        params = (tid, f"%{term}%", f"%{term}%")
        results = self.db.execute_query(query, params)
        if not results:
            messagebox.showinfo("结果", "未找到相关课程")
            return
        win = tk.Toplevel(self.root)
        win.title("查询结果")
        for pid, pname, yr, sem, hrs in results:
            text = f"{pid} | {pname} | 年度:{yr} | 学期:{sem} | 学时:{hrs}"
            tk.Label(win, text=text).pack(anchor='w', padx=10, pady=2)


    def project_management(self, tid):
        win = tk.Toplevel(self.root)
        win.title("项目管理")
        win.geometry("1200x600")
        top_frame = tk.Frame(win)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="新增项目承担", command=lambda: self.add_project(tid, win)).grid(row=0, column=0, padx=5)
        tk.Button(top_frame, text="共同承担项目", command=lambda: self.coop_project(tid, win)).grid(row=0, column=1, padx=5)
        tk.Button(top_frame, text="查询项目", command=lambda: self.search_project_window(tid)).grid(row=0, column=2, padx=5)

        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(list_frame)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        entries = self.db.execute_query(
            "SELECT p.project_id, p.project_name, p.project_source, p.project_type, tp.principal_rank, p.total_fund, tp.my_fund, p.start_year, p.end_year " \
            "FROM Teacher_Project tp JOIN Project p ON tp.project_id=p.project_id " \
            "WHERE tp.teacher_id=%s ORDER BY p.start_year DESC", (tid,)
        )
        for idx, (pid, pname, src, ptype, prank, total, mfund, syr, eyr) in enumerate(entries):
            frame_row = tk.Frame(scroll_frame, bd=1, relief="solid")
            frame_row.pack(fill=tk.X, pady=2, padx=2)
            ptype_str = project_type_map.get(ptype, "未知类型")
            info = f"{pid} | {pname} | 项目来源:{src} | 项目类型:{ptype_str} | 年度:{syr}-{eyr} | 排名:{prank} | 总经费:{total} | 承担经费:{mfund}"
            tk.Label(frame_row, text=info).pack(side=tk.LEFT, padx=5)
            tk.Button(frame_row, text="修改", command=lambda e=pid: self.modify_teacher_project(tid, e, pname, src, ptype, syr, eyr, prank, mfund, win)).pack(side=tk.RIGHT, padx=5)
            tk.Button(frame_row, text="删除", command=lambda e=pid: self.delete_teacher_project(tid, e, win)).pack(side=tk.RIGHT)

    def add_project(self, tid, parent):
        win = tk.Toplevel(parent)
        win.title("新增项目承担")
        win.geometry("1000x500")
        labels = ["项目号", "项目名称", "项目来源", "项目类型", "排名", "开始年份", "结束年份", "承担经费"]
        entries = {}
        for i, text in enumerate(labels):
            tk.Label(win, text=f"{text}:").grid(row=i, column=0, padx=10, pady=5, sticky='w')
            if text in ["项目类型"]:
                var = tk.StringVar()
                combo = ttk.Combobox(win, width=100, textvariable=var, values=["1-国家级项目", "2-省部级项目", "3-市厅级项目", "4-企业合作项目", "5-其他类型项目"], state='readonly')
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = combo
            else:
                entry = tk.Entry(win, width=100)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[text] = entry

        def save():
            try:
                pid = entries["项目号"].get().strip()
                pname = entries["项目名称"].get().strip()
                src = entries["项目来源"].get().strip()
                ptype = int(entries["项目类型"].get().split('-')[0])
                prank = int(entries["排名"].get().strip())
                syr = int(entries["开始年份"].get().strip())
                eyr = int(entries["结束年份"].get().strip())
                mfund = entries["承担经费"].get().strip()
                if not all([pid, pname, src, mfund]):
                    messagebox.showerror("错误", "所有字段必须填写")
                    raise ValueError
            except:
                messagebox.showerror("错误", "请检查输入格式")
                return
            try:
                mfund = round(float(mfund), 2)  # 保留两位小数
            except ValueError:
                messagebox.showerror("错误", "承担经费必须为数字")
                return
            # 检查项目号是否已存在
            existing = self.db.execute_query("SELECT project_id FROM Project WHERE project_id=%s", (pid,))
            if existing:
                messagebox.showerror("错误", "项目号已存在，请使用其他项目号")
                return
            # 检查年份格式
            if syr < 1958 or syr > 2100 or eyr < 1958 or eyr > 2100:
                messagebox.showerror("错误", "发表年份必须在1958到2100之间")
                return
            # 检查排名是否合理
            if prank < 1:
                messagebox.showerror("错误", "排名必须大于0")
                return

            # 插入 Project
            # ! 新项目当前总经费为0，直接加上我的承担经费
            res1 = self.db.execute_update(
                "INSERT INTO Project (project_id, project_name, project_source, project_type, start_year, end_year, total_fund) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (pid, pname, src, ptype, syr, eyr, mfund)
            )
            if res1 < 1:
                messagebox.showerror("错误", "项目添加失败，可能项目号已存在")
                return
            # 插入 Teacher_Project
            res2 = self.db.execute_update(
                "INSERT INTO Teacher_Project (teacher_id, project_id, principal_rank, my_fund) " \
                "VALUES (%s, %s, %s, %s)",
                (tid, pid, prank, mfund)
            )
            if res2 > 0:
                messagebox.showinfo("成功", "新项目承担添加成功")
                win.destroy()
                parent.destroy()
                self.project_management(tid)
            else:
                messagebox.showerror("错误", "关联教师项目失败")

        tk.Button(win, text="保存", command=save).grid(row=8, column=0, columnspan=2, pady=20)

    def coop_project(self, tid, parent):
        """共同承担项目：添加当前教师到已有项目中"""
        win = tk.Toplevel(parent)
        win.title("共同承担项目")
        win.geometry("1200x300")

        # 1. 列出已有的项目（排除当前教师已参与的）
        projects = self.db.execute_query(
            "SELECT DISTINCT tp.project_id, p.project_name, p.total_fund "
            "FROM Teacher_Project tp "
            "JOIN Project p ON tp.project_id=p.project_id "
            "WHERE NOT EXISTS ("
            "  SELECT 1 FROM Teacher_Project tp2 "
            "  WHERE tp2.teacher_id=%s AND tp2.project_id=tp.project_id"
            ")",
            (tid,)
        )
        choices = [
            f"{pid}-{pname}" 
            for pid, pname, _ in projects
        ]

        tk.Label(win, text="选择项目:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        var = tk.StringVar()
        combo = ttk.Combobox(win, width=100, textvariable=var, values=choices, state='readonly')
        combo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="排名:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        entry_rank = tk.Entry(win)
        entry_rank.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text="承担经费:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        entry_fund = tk.Entry(win)
        entry_fund.grid(row=2, column=1, padx=10, pady=5)

        def save():
            sel = var.get().strip()
            if not sel:
                messagebox.showerror("错误", "请选择项目")
                return
            pid = sel.split('-',1)[0]
            try:
                prank = int(entry_rank.get().strip())
                myfund = float(entry_fund.get().strip())
            except:
                messagebox.showerror("错误", "排名必须是整数，经费必须是数字")
                return
            # 检查排名唯一
            cnt = self.db.execute_query(
                "SELECT COUNT(*) FROM Teacher_Project WHERE project_id=%s AND principal_rank=%s AND teacher_id<>%s",
                (pid, prank, tid)
            )
            if cnt and cnt[0][0] > 0:
                messagebox.showerror("错误", f"排名 {prank} 已被其他教师使用，请换一个")
                return
            
            # 插入关联
            res = self.db.execute_update(
                "INSERT INTO Teacher_Project (teacher_id,project_id,principal_rank,my_fund) "
                "VALUES (%s,%s,%s,%s)",
                (tid, pid, prank, myfund)
            )
            if res > 0:
                total = self.db.execute_query(
                    "SELECT SUM(my_fund) FROM Teacher_Project WHERE project_id=%s",
                    (pid,)
                )[0][0] or 0.0
                self.db.execute_update(
                    "UPDATE Project SET total_fund=%s WHERE project_id=%s",
                    (total, pid)
                )
                messagebox.showinfo("成功", "共同承担项目添加成功")
                win.destroy()
                parent.destroy()
                self.project_management(tid)
            else:
                messagebox.showerror("错误", "添加失败，可能重复")

        tk.Button(win, text="保存", command=save).grid(row=3, column=0, columnspan=2, pady=20)
    
    def modify_teacher_project(self, tid, pid, pname, src, ptype, start_year, end_year, old_rank, old_fund, parent):
        """修改当前教师在某项目中的全部属性"""
        win = tk.Toplevel(parent)
        win.title("修改项目承担信息")
        win.geometry("600x500")

        # 项目基本信息
        tk.Label(win, text=f"项目号:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        entry_pid = tk.Entry(win)
        entry_pid.insert(0, pid)
        entry_pid.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="项目名称:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        entry_pname = tk.Entry(win)
        entry_pname.insert(0, pname)
        entry_pname.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text="项目来源:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        entry_src = tk.Entry(win)
        entry_src.insert(0, src)
        entry_src.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(win, text="项目类型:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        type_var = tk.StringVar()
        combo_type = ttk.Combobox(win, textvariable=type_var,
                                  values=[f"{k}-{v}" for k, v in project_type_map.items()], state='readonly')
        combo_type.set(f"{ptype}-{project_type_map.get(ptype, '未知类型')}")
        combo_type.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(win, text="开始年份:").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        entry_syr = tk.Entry(win)
        entry_syr.insert(0, str(start_year))
        entry_syr.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(win, text="结束年份:").grid(row=5, column=0, padx=10, pady=5, sticky='w')
        entry_eyr = tk.Entry(win)
        entry_eyr.insert(0, str(end_year))
        entry_eyr.grid(row=5, column=1, padx=10, pady=5)

        # 关联属性
        tk.Label(win, text="作者排名:").grid(row=6, column=0, padx=10, pady=5, sticky='w')
        entry_rank = tk.Entry(win)
        entry_rank.insert(0, str(old_rank))
        entry_rank.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(win, text="承担经费:").grid(row=7, column=0, padx=10, pady=5, sticky='w')
        entry_fund = tk.Entry(win)
        entry_fund.insert(0, str(old_fund))
        entry_fund.grid(row=7, column=1, padx=10, pady=5)

        def save():
            try:
                new_pid = entry_pid.get().strip()
                new_pname = entry_pname.get().strip()
                new_src = entry_src.get().strip()
                new_ptype = int(type_var.get().split('-')[0])
                new_syr = int(entry_syr.get().strip())
                new_eyr = int(entry_eyr.get().strip())
                new_rank = int(entry_rank.get().strip())
                new_fund = round(float(entry_fund.get().strip()), 2)
            except:
                messagebox.showerror("错误", "请检查输入格式，确保所有字段有效")
                return
            # 唯一性校验
            exist = self.db.execute_query("SELECT project_id FROM Project WHERE project_id=%s AND project_id<>%s", (new_pid, pid))
            if exist:
                messagebox.showerror("错误", "项目号已存在，请修改")
                return
            if new_rank < 1:
                messagebox.showerror("错误", "作者排名必须大于0")
                return
            if new_syr < 1958 or new_eyr < new_syr:
                messagebox.showerror("错误", "年份范围不合理")
                return
            # 更新 Project 表
            res1 = self.db.execute_update(
                "UPDATE Project SET project_id=%s, project_name=%s, project_source=%s, project_type=%s, start_year=%s, end_year=%s WHERE project_id=%s",
                (new_pid, new_pname, new_src, new_ptype, new_syr, new_eyr, pid)
            )
            # 更新 Teacher_Project 表
            res2 = self.db.execute_update(
                "UPDATE Teacher_Project SET project_id=%s, principal_rank=%s, my_fund=%s WHERE teacher_id=%s AND project_id=%s",
                (new_pid, new_rank, new_fund, tid, pid)
            )
            if res1 > 0 or res2 > 0:
                # 重新计算并更新总经费
                total = self.db.execute_query(
                    "SELECT SUM(my_fund) FROM Teacher_Project WHERE project_id=%s",
                    (new_pid,)
                )[0][0] or 0.0
                self.db.execute_update(
                    "UPDATE Project SET total_fund=%s WHERE project_id=%s",
                    (total, new_pid)
                )
                messagebox.showinfo("成功", "项目承担信息修改成功")
                win.destroy()
                parent.destroy()
                self.project_management(tid)
            else:
                messagebox.showerror("错误", "修改失败")

        tk.Button(win, text="保存", command=save).grid(row=8, column=0, columnspan=2, pady=20)

    def delete_teacher_project(self, tid, pid, parent):
        if messagebox.askyesno("确认", "确定删除该记录吗?" ):
            # 查询当前承担经费与总经费
            row = self.db.execute_query(
                "SELECT my_fund " \
                "FROM Teacher_Project " \
                "WHERE teacher_id=%s AND project_id=%s",
                (tid, pid)
            )
            if row:
                my_fund = row[0][0]
                total = self.db.execute_query(
                    "SELECT total_fund " \
                    "FROM Project WHERE project_id=%s",
                    (pid,)
                )[0][0] or 0.0
                # 删除关联
                self.db.execute_update(
                    "DELETE FROM Teacher_Project " \
                    "WHERE teacher_id=%s AND project_id=%s",
                    (tid, pid)
                )
                # 仅剩一人时删除项目表
                if abs(total - my_fund) < 1e-6:
                    self.db.execute_update(
                        "DELETE FROM Project " \
                        "WHERE project_id=%s", (pid,)
                    )
                else:
                    new_total = total - my_fund
                    self.db.execute_update(
                        "UPDATE Project SET total_fund=%s " \
                        "WHERE project_id=%s",
                        (new_total, pid)
                    )
            messagebox.showinfo("成功", "删除成功")
            parent.destroy()
            self.project_management(tid)

    def search_project_window(self, tid):
        term = simpledialog.askstring("查询", "请输入项目名称或项目号:")
        if term is None:
            return
        query = "SELECT p.project_id, p.project_name, p.project_source, p.total_fund, CONCAT(p.start_year, '-', p.end_year), tp.principal_rank, tp.my_fund FROM Teacher_Project tp JOIN Project p ON tp.project_id=p.project_id WHERE tp.teacher_id=%s AND (p.project_id LIKE %s OR p.project_name LIKE %s)"
        params = (tid, f"%{term}%", f"%{term}%")
        results = self.db.execute_query(query, params)
        if not results:
            messagebox.showinfo("结果", "未找到相关项目")
            return
        win = tk.Toplevel(self.root)
        win.title("查询结果")
        for pid, pname, src, total, dur, prank, mf in results:
            text = f"{pid} | {pname} | {src} | 年度:{dur} | 排名:{prank} | 承担经费:{mf} | 总经费:{total}"
            tk.Label(win, text=text).pack(anchor='w', padx=10, pady=2)


    def query_stats(self):
        win = tk.Toplevel(self.root)
        win.title("查询统计")
        win.geometry("800x600")
        tk.Label(win, text="教师工号:").grid(row=0, column=0, padx=10, pady=5)
        entry_id = tk.Entry(win)
        entry_id.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(win, text="年份范围(如2022-2023):").grid(row=1, column=0, padx=10, pady=5)
        entry_range = tk.Entry(win)
        entry_range.grid(row=1, column=1, padx=10, pady=5)
        txt = tk.Text(win)
        txt.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        win.grid_rowconfigure(2, weight=1)
        win.grid_columnconfigure(1, weight=1)

        def search():
            tid = entry_id.get().strip()
            yr = entry_range.get().strip()
            if not tid:
                messagebox.showerror("错误", "请输入工号")
                return
            start = end = None
            if yr:
                try:
                    s, e = yr.split('-')
                    start, end = int(s), int(e)
                except:
                    messagebox.showerror("错误", "年份格式错误")
                    return
                # 检查年份在1958到2100之间
            if start is not None and (start < 1958 or start > 2100):
                messagebox.showerror("错误", "开始年份必须在1958到2100之间")
                return
            if end is not None and (end < 1958 or end > 2100):
                messagebox.showerror("错误", "结束年份必须在1958到2100之间")
                return

            txt.delete(1.0, tk.END)
            # 教师基本信息
            info = self.db.execute_query(
                "SELECT name, "
                "CASE gender WHEN 1 THEN '男' WHEN 2 THEN '女' END as gender, "
                "CASE title WHEN 1 THEN '博士后' WHEN 2 THEN '助教' WHEN 3 THEN '讲师' WHEN 4 THEN '副教授' "
                "WHEN 5 THEN '特任教授' WHEN 6 THEN '教授' WHEN 7 THEN '助理研究员' WHEN 8 THEN '特任副研究员' "
                "WHEN 9 THEN '副研究员' WHEN 10 THEN '特任研究员' WHEN 11 THEN '研究员' END as title "
                "FROM Teacher WHERE teacher_id=%s", (tid,)
            )
            if not info:
                messagebox.showerror("错误", "教师不存在")
                return
            name, gender, title = info[0]
            txt.insert(tk.END, f"教师基本信息:\n工号:{tid}\t姓名:{name}\t性别:{gender}\t职称:{title}\n\n")

            # 论文
            txt.insert(tk.END, "论文:\n")
            qp = (
                "SELECT p.paper_name, p.pub_source, p.pub_year, p.paper_type, p.paper_level, "
                "tp.author_rank, tp.is_corresponding "
                "FROM Teacher_Paper tp JOIN Paper p ON tp.paper_id=p.paper_id "
                "WHERE tp.teacher_id=%s"
            )
            params = [tid]
            if start is not None and end is not None:
                qp += " AND p.pub_year BETWEEN %s AND %s"
                params += [start, end]
            qp += " ORDER BY p.pub_year DESC"
            papers = self.db.execute_query(qp, tuple(params))
            if papers:
                for pname, src, pyr, ptype, plevel, rank, corr in papers:
                    type_desc = paper_type_map.get(ptype, '未知类型')
                    level_desc = paper_level_map.get(plevel, '未知级别')
                    txt.insert(tk.END, f"{pname} | {src} | {pyr} | 类型:{type_desc} | 级别:{level_desc} | 排名:{rank} | {'通讯作者' if corr else ''}\n")
            else:
                txt.insert(tk.END, "无论文记录\n")

            # 课程
            txt.insert(tk.END, "\n课程:\n")
            # txt.insert(tk.END, "------------------\n")
            qc = (
                "SELECT c.course_id, c.course_name, tc.year, tc.semester, tc.my_hours "
                "FROM Teacher_Course tc JOIN Course c ON tc.course_id=c.course_id "
                "WHERE tc.teacher_id=%s"
            )
            params = [tid]
            if start is not None and end is not None:
                qc += " AND tc.year BETWEEN %s AND %s"
                params += [start, end]
            qc += " ORDER BY tc.year, tc.semester"
            courses = self.db.execute_query(qc, tuple(params))
            if courses:
                for cid, cname, yr2, sem, hrs in courses:
                    sem_desc = semester_map.get(sem, str(sem))
                    txt.insert(tk.END, f"课程号:{cid}\t课程名{cname}\t学期:{yr2}{sem_desc}\t主讲学时:{hrs}\n")
            else:
                txt.insert(tk.END, "无课程记录\n")

            # 项目
            txt.insert(tk.END, "\n项目:\n")
            qpr = (
                "SELECT p.project_id, p.project_name, p.project_type, p.project_source, "
                "CONCAT(p.start_year, '-', p.end_year), tp.principal_rank, tp.my_fund, p.total_fund "
                "FROM Teacher_Project tp JOIN Project p ON tp.project_id=p.project_id "
                "WHERE tp.teacher_id=%s"
            )
            params = [tid]
            if start is not None and end is not None:
                qpr += " AND NOT(p.end_year < %s OR p.start_year > %s)"
                params += [start, end]
            qpr += " ORDER BY p.start_year DESC"
            projs = self.db.execute_query(qpr, tuple(params))
            if projs:
                for pid, pname, ptype, src, dur, rank, mf, ttlf in projs:
                    type_desc = project_type_map.get(ptype, '未知类型')
                    txt.insert(tk.END, f"{pname} | {src} | 类型:{type_desc} | 年度:{dur} | 排名:{rank} | 总经费:{ttlf} | 承担经费:{mf}\n")
            else:
                txt.insert(tk.END, "无项目记录\n")

        tk.Button(win, text="查询", command=search).grid(row=3, column=0, columnspan=2, pady=10)


    def _export_report(self):
        tid = simpledialog.askstring("输入", "请输入教师工号:")
        yr = simpledialog.askstring("输入", "请输入年份范围(如2022-2023):")
        if not tid or not yr:
            return
        try:
            s, e = yr.split('-')
            start = int(s)
            end = int(e)
        except:
            messagebox.showerror("错误", "年份格式错误")
            return
        # 检查年份在1958到2100之间
        if start < 1958 or start > 2100 or end < 1958 or end > 2100:
            messagebox.showerror("错误", "年份必须在1958到2100之间")
            return
        # 检索数据
        info = self.db.execute_query(
            "SELECT name, CASE gender WHEN 1 THEN '男' WHEN 2 THEN '女' END as gender, CASE title WHEN 1 THEN '博士后' WHEN 2 THEN '助教' WHEN 3 THEN '讲师' WHEN 4 THEN '副教授' WHEN 5 THEN '特任教授' WHEN 6 THEN '教授' WHEN 7 THEN '助理研究员' WHEN 8 THEN '特任副研究员' WHEN 9 THEN '副研究员' WHEN 10 THEN '特任研究员' WHEN 11 THEN '研究员' END as title FROM Teacher WHERE teacher_id=%s", (tid,))
        if not info:
            messagebox.showerror("错误", "教师不存在")
            return
        name, gender, title = info[0]
        papers = self.db.execute_query(
            "SELECT p.paper_name, p.pub_source, p.pub_year, tp.author_rank, tp.is_corresponding FROM Teacher_Paper tp JOIN Paper p ON tp.paper_id=p.paper_id WHERE tp.teacher_id=%s AND p.pub_year BETWEEN %s AND %s ORDER BY p.pub_year DESC", (tid, start, end)
        )
        courses = self.db.execute_query(
            "SELECT c.course_name, tc.year, tc.semester, tc.my_hours FROM Teacher_Course tc JOIN Course c ON tc.course_id=c.course_id WHERE tc.teacher_id=%s AND tc.year BETWEEN %s AND %s ORDER BY tc.year, tc.semester", (tid, start, end)
        )
        projs = self.db.execute_query(
            "SELECT p.project_name, p.project_source, CONCAT(p.start_year, '-', p.end_year), tp.principal_rank, tp.my_fund FROM Teacher_Project tp JOIN Project p ON tp.project_id=p.project_id WHERE tp.teacher_id=%s AND NOT(p.end_year < %s OR p.start_year > %s) ORDER BY p.start_year DESC", (tid, start, end)
        )
        # 生成PDF
        filename = f"报告_{name}_{yr}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        y = height - 40

        c.setFont(chinese_font, 16)
        c.drawString(40, y, f"教师教学科研报告 ({yr})")
        y -= 30
        c.setFont(chinese_font, 12)
        c.drawString(40, y, f"工号: {tid}  姓名: {name}  性别: {gender}  职称: {title}")
        y -= 25
        c.drawString(40, y, "\n论文:")
        y -= 20
        if papers:
            for pname, src, pyr, rank, corr in papers:
                line = f"{pyr} | {pname} | {src} | 排名:{rank} {'通讯作者' if corr else ''}"
                c.drawString(60, y, line)
                y -= 20
                if y < 100:
                    c.showPage()
                    y = height - 40
        else:
            c.drawString(60, y, "无论文记录")
            y -= 20
        c.drawString(40, y, "\n课程:")
        y -= 20
        if courses:
            for cname, yr2, sem, hrs in courses:
                line = f"{yr2}-{sem} | {cname} | 学时:{hrs}"
                c.drawString(60, y, line)
                y -= 20
                if y < 100:
                    c.showPage()
                    y = height - 40
        else:
            c.drawString(60, y, "无课程记录")
            y -= 20
        c.drawString(40, y, "\n项目:")
        y -= 20
        if projs:
            for pname, src, dur, rank, mf in projs:
                line = f"{dur} | {pname} | {src} | 排名:{rank} | 经费:{mf}"
                c.drawString(60, y, line)
                y -= 20
                if y < 100:
                    c.showPage()
                    y = height - 40
        else:
            c.drawString(60, y, "无项目记录")
            y -= 20
        c.save()
        messagebox.showinfo("成功", f"PDF报告已生成: {filename}")

    def export_report(self):
        tid = simpledialog.askstring("输入", "请输入教师工号:")
        yr = simpledialog.askstring("输入", "请输入年份范围(如2022-2023):")
        if not tid or not yr:
            return
        try:
            s, e = yr.split('-')
            start = int(s)
            end = int(e)
        except:
            messagebox.showerror("错误", "年份格式错误")
            return
        # 检查年份在1958到2100之间
        if start < 1958 or start > 2100 or end < 1958 or end > 2100:
            messagebox.showerror("错误", "年份必须在1958到2100之间")
            return

        # 检索数据
        info = self.db.execute_query(
            "SELECT name, CASE gender WHEN 1 THEN '男' WHEN 2 THEN '女' END as gender, CASE title WHEN 1 THEN '博士后' WHEN 2 THEN '助教' WHEN 3 THEN '讲师' WHEN 4 THEN '副教授' WHEN 5 THEN '特任教授' WHEN 6 THEN '教授' WHEN 7 THEN '助理研究员' WHEN 8 THEN '特任副研究员' WHEN 9 THEN '副研究员' WHEN 10 THEN '特任研究员' WHEN 11 THEN '研究员' END as title FROM Teacher WHERE teacher_id=%s", (tid,))
        if not info:
            messagebox.showerror("错误", "教师不存在")
            return
        name, gender, teacher_title = info[0]
        papers = self.db.execute_query(
            "SELECT p.paper_name, p.pub_source, p.pub_year, p.paper_type, p.paper_level, "
            "tp.author_rank, tp.is_corresponding "
            "FROM Teacher_Paper tp JOIN Paper p ON tp.paper_id=p.paper_id "
            "WHERE tp.teacher_id=%s AND p.pub_year BETWEEN %s AND %s "
            "ORDER BY p.pub_year DESC",
            (tid, start, end)
        )
        courses = self.db.execute_query(
            "SELECT c.course_id, c.course_name, tc.year, tc.semester, tc.my_hours "
            "FROM Teacher_Course tc JOIN Course c ON tc.course_id=c.course_id "
            "WHERE tc.teacher_id=%s AND tc.year BETWEEN %s AND %s "
            "ORDER BY tc.year, tc.semester",
            (tid, start, end)
        )
        projs = self.db.execute_query(
            "SELECT p.project_id, p.project_name, p.project_type, p.project_source, "
            "CONCAT(p.start_year, '-', p.end_year), tp.principal_rank, tp.my_fund, p.total_fund "
            "FROM Teacher_Project tp JOIN Project p ON tp.project_id=p.project_id "
            "WHERE tp.teacher_id=%s AND NOT(p.end_year < %s OR p.start_year > %s) "
            "ORDER BY p.start_year DESC",
            (tid, start, end)
        )

        # 生成PDF - 使用Paragraph支持自动换行
        filename = f"报告_{name}_{yr}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        y_position = height - 40

        # 设置样式
        styles = getSampleStyleSheet()

        # 标题样式
        title_style = styles['Title']
        title_style.fontName = chinese_font
        title_style.fontSize = 18
        title_style.leading = 22

        # 教师信息样式
        info_style = styles['Normal']
        info_style.fontName = chinese_font
        info_style.fontSize = 12
        info_style.leading = 15

        # 内容样式
        content_style = styles['BodyText']
        content_style.fontName = chinese_font
        content_style.fontSize = 10
        content_style.leading = 14

        # 绘制标题
        header = Paragraph(f"教师教学科研报告 ({yr})", title_style)
        header.wrap(width - 80, 40)
        header.drawOn(c, 40, y_position)
        y_position -= 40

        # 绘制教师基本信息
        info_text = f"<b>教师基本信息:</b><br/>" \
                    f"工号: {tid} &nbsp; 姓名: {name} &nbsp; 性别: {gender} &nbsp; 职称: {teacher_title}"
        info_para = Paragraph(info_text, info_style)
        info_para.wrap(width - 80, 40)
        info_para.drawOn(c, 40, y_position)
        y_position -= 40

        # 课程部分
        courses_text = "<b>课程:</b><br/>"
        if courses:
            for cid, cname, yr2, sem, hrs in courses:
                sem_desc = semester_map.get(sem, str(sem))
                short_name = cname if len(cname)<=50 else cname[:50]+"..."
                courses_text += (
                    f"• {cid} | {yr2}-{sem_desc} | {short_name} | 学时:{hrs}<br/>"
                )
        else:
            courses_text += "无课程记录<br/>"

        courses_para = Paragraph(courses_text, content_style)
        courses_height = courses_para.wrap(width - 80, height - 100)[1]
        if y_position - courses_height < 50:
            c.showPage()
            y_position = height - 40
        courses_para.drawOn(c, 40, y_position - courses_height)
        y_position -= courses_height + 20

        # 论文部分
        papers_text = "<b>论文:</b><br/>"
        if papers:
            for pname, src, pyr, ptype, plevel, rank, corr in papers:
                corr_str = " (通讯作者)" if corr else ""
                # 类型/级别映射
                type_desc  = paper_type_map.get(ptype, '未知类型')
                level_desc = paper_level_map.get(plevel, '未知级别')
                # 长度截断
                short_name = pname if len(pname)<=100 else pname[:100]+"..."
                papers_text += (
                    f"• {pyr} | {short_name} | {src} | "
                    f"类型:{type_desc} | 级别:{level_desc} | 排名:{rank}{corr_str}<br/>"
                )
        else:
            papers_text += "无论文记录<br/>"

        papers_para = Paragraph(papers_text, content_style)
        papers_height = papers_para.wrap(width - 80, height - 100)[1]
        if y_position - papers_height < 50:  # 检查空间是否足够
            c.showPage()
            y_position = height - 40
        papers_para.drawOn(c, 40, y_position - papers_height)
        y_position -= papers_height + 20

        # 项目部分
        projs_text = "<b>项目:</b><br/>"
        if projs:
            for pid, pname, ptype, src, dur, rank, mf, tf in projs:
                short_name = pname if len(pname)<=80 else pname[:80]+"..."
                type_desc = project_type_map.get(ptype, '未知类型')
                projs_text += (
                    f"• {pid} | {short_name} | 类型:{type_desc} | {src} | "
                    f"年度:{dur} | 排名:{rank} | 承担经费:{mf} | 总经费:{tf}<br/>"
                )
        else:
            projs_text += "无项目记录<br/>"

        projs_para = Paragraph(projs_text, content_style)
        projs_height = projs_para.wrap(width - 80, height - 100)[1]
        if y_position - projs_height < 50:
            c.showPage()
            y_position = height - 40
        projs_para.drawOn(c, 40, y_position - projs_height)

        c.save()
        messagebox.showinfo("成功", f"PDF报告已生成: {filename}")