import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
from scanner import get_local_network, scan
from remote_control import RemoteControl

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("NetControl Pro - إدارة الشبكة")
        self.geometry("1100x700")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NetControl Pro",
                                      font=ctk.CTkFont(size=24, weight="bold", family="Segoe UI"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        self.scan_button = ctk.CTkButton(self.sidebar_frame, text="فحص الشبكة",
                                        font=ctk.CTkFont(family="Segoe UI"),
                                        command=self.start_scan)
        self.scan_button.grid(row=1, column=0, padx=20, pady=10)

        self.manual_button = ctk.CTkButton(self.sidebar_frame, text="إضافة جهاز يدوياً",
                                          font=ctk.CTkFont(family="Segoe UI"),
                                          command=self.manual_connect, fg_color="#4A4A4A", hover_color="#5A5A5A")
        self.manual_button.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="المظهر:", anchor="w", font=ctk.CTkFont(family="Segoe UI"))
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # --- Main Content ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Header with Status
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        self.header_label = ctk.CTkLabel(self.header_frame, text="الأجهزة المتصلة",
                                        font=ctk.CTkFont(size=28, weight="bold", family="Segoe UI"))
        self.header_label.pack(side="left")

        self.status_label = ctk.CTkLabel(self.header_frame, text="جاهز", font=ctk.CTkFont(size=14, family="Segoe UI"), text_color="gray")
        self.status_label.pack(side="right", padx=10)

        # Devices List
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="قائمة الأجهزة المكتشفة", label_font=ctk.CTkFont(family="Segoe UI", size=14))
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.devices = []
        self.device_frames = []

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def start_scan(self):
        self.scan_button.configure(state="disabled", text="جاري الفحص...")
        self.status_label.configure(text="جاري فحص الشبكة...", text_color="#3B8ED0")
        for frame in self.device_frames:
            frame.destroy()
        self.device_frames = []
        self.devices = []

        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        network = get_local_network()
        if network:
            try:
                self.devices = scan(network)
            except ImportError:
                self.after(0, lambda: messagebox.showerror("خطأ", "يجب تثبيت Npcap أو WinPcap لتشغيل فحص الشبكة.\nيرجى تثبيت Npcap من الموقع الرسمي."))
                self.devices = []
            except Exception as e:
                error_msg = str(e)
                if "libpcap" in error_msg or "pcap" in error_msg:
                    error_msg = "يجب تثبيت Npcap أو WinPcap لتشغيل فحص الشبكة."
                self.after(0, lambda msg=error_msg: messagebox.showerror("خطأ في الفحص", f"فشل فحص الشبكة: {msg}"))
                self.devices = []
        else:
            self.after(0, lambda: messagebox.showerror("خطأ", "لم يتم العثور على شبكة محلية نشطة."))
            self.devices = []

        self.after(0, self.update_device_list)

    def update_device_list(self):
        self.scan_button.configure(state="normal", text="فحص الشبكة")
        self.status_label.configure(text=f"تم العثور على {len(self.devices)} جهاز", text_color="gray")

        for i, device in enumerate(self.devices):
            self.add_device_card(device, i)

    def manual_connect(self):
        dialog = ctk.CTkInputDialog(text="أدخل عنوان IP للجهاز:", title="اتصال يدوي", font=ctk.CTkFont(family="Segoe UI"))
        ip = dialog.get_input()
        if ip:
            device = {"ip": ip, "hostname": "جهاز يدوي", "mac": "غير معروف"}
            self.devices.append(device)
            self.add_device_card(device, len(self.device_frames))

    def add_device_card(self, device, index):
        card = ctk.CTkFrame(self.scrollable_frame, height=100)
        card.grid(row=index, column=0, padx=10, pady=10, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Icon or Placeholder
        icon_label = ctk.CTkLabel(card, text="💻", font=ctk.CTkFont(size=40))
        icon_label.grid(row=0, column=0, padx=20, pady=10)

        # Device Info
        info_text = f"الاسم: {device['hostname']}\nIP: {device['ip']}\nMAC: {device['mac']}"
        label = ctk.CTkLabel(card, text=info_text, justify="left", font=ctk.CTkFont(size=13, family="Segoe UI"))
        label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=20)

        btn_font = ctk.CTkFont(family="Segoe UI", size=12)

        msg_btn = ctk.CTkButton(actions_frame, text="رسالة", width=100, font=btn_font,
                                command=lambda: self.open_message_dialog(device))
        msg_btn.grid(row=0, column=0, padx=5, pady=5)

        proc_btn = ctk.CTkButton(actions_frame, text="العمليات", width=100, font=btn_font,
                                command=lambda: self.open_processes_window(device))
        proc_btn.grid(row=0, column=1, padx=5, pady=5)

        restart_btn = ctk.CTkButton(actions_frame, text="إعادة تشغيل", width=100, font=btn_font,
                                   fg_color="#E59400", hover_color="#C68000",
                                   command=lambda: self.confirm_action("إعادة تشغيل", device))
        restart_btn.grid(row=1, column=0, padx=5, pady=5)

        shutdown_btn = ctk.CTkButton(actions_frame, text="إغلاق", width=100, font=btn_font,
                                    fg_color="#D35B58", hover_color="#B34B48",
                                    command=lambda: self.confirm_action("إغلاق كامل", device))
        shutdown_btn.grid(row=1, column=1, padx=5, pady=5)

        self.device_frames.append(card)

    def open_message_dialog(self, device):
        dialog = ctk.CTkInputDialog(text=f"أدخل الرسالة لجهاز {device['ip']}:", title="إرسال رسالة", font=ctk.CTkFont(family="Segoe UI"))
        msg = dialog.get_input()
        if msg:
            success, res = RemoteControl.send_message(device['ip'], msg)
            if success:
                messagebox.showinfo("تم", "تم إرسال الرسالة بنجاح!")
            else:
                messagebox.showerror("خطأ", f"فشل إرسال الرسالة: {res}")

    def confirm_action(self, action, device):
        if messagebox.askyesno("تأكيد", f"هل أنت متأكد أنك تريد {action} للجهاز {device['ip']}؟"):
            restart = True if "إعادة" in action else False
            success, res = RemoteControl.shutdown(device['ip'], restart=restart)
            if success:
                messagebox.showinfo("تم", f"تم إرسال أمر {action} بنجاح!")
            else:
                messagebox.showerror("خطأ", f"فشل تنفيذ الأمر: {res}")

    def open_processes_window(self, device):
        ProcessesWindow(self, device)

class ProcessesWindow(ctk.CTkToplevel):
    def __init__(self, parent, device):
        super().__init__(parent)
        self.device = device
        self.title(f"العمليات - {device['ip']}")
        self.geometry("700x500")
        self.attributes('-topmost', True) # Keep on top

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=f"العمليات النشطة على {device['ip']}",
                                 font=ctk.CTkFont(size=18, weight="bold", family="Segoe UI"))
        self.label.grid(row=0, column=0, pady=20)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="قائمة المهام")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.refresh_btn = ctk.CTkButton(self, text="تحديث", font=ctk.CTkFont(family="Segoe UI"), command=self.load_processes)
        self.refresh_btn.grid(row=2, column=0, pady=20)

        self.load_processes()

    def load_processes(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.refresh_btn.configure(state="disabled", text="جاري التحميل...")
        threading.Thread(target=self.fetch_procs_thread, daemon=True).start()

    def fetch_procs_thread(self):
        success, procs = RemoteControl.get_processes(self.device['ip'])
        self.after(0, lambda: self.display_procs(success, procs))

    def display_procs(self, success, procs):
        self.refresh_btn.configure(state="normal", text="تحديث")
        if success:
            for i, proc in enumerate(procs):
                f = ctk.CTkFrame(self.scrollable_frame)
                f.grid(row=i, column=0, sticky="ew", pady=2, padx=5)
                f.grid_columnconfigure(0, weight=1)

                name_lbl = ctk.CTkLabel(f, text=f"{proc['name']} (PID: {proc['pid']})", font=ctk.CTkFont(size=12))
                name_lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")

                kill_btn = ctk.CTkButton(f, text="إنهاء", width=60, height=25, fg_color="#D35B58", hover_color="#B34B48",
                                        command=lambda p=proc['pid']: self.kill_proc(p))
                kill_btn.grid(row=0, column=1, padx=10, pady=5)
        else:
            ctk.CTkLabel(self.scrollable_frame, text=f"خطأ: {procs}", text_color="red").grid(row=0, column=0)

    def kill_proc(self, pid):
        if messagebox.askyesno("تأكيد", f"إنهاء العملية ذات الرقم {pid}؟"):
            success, res = RemoteControl.kill_process(self.device['ip'], pid)
            if success:
                messagebox.showinfo("تم", "تم إنهاء العملية.")
                self.load_processes()
            else:
                messagebox.showerror("خطأ", f"لا يمكن إنهاء العملية: {res}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
