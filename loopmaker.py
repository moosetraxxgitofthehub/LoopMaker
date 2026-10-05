import logging, os, queue, subprocess, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from processing import make_loop, LoopError, SPEEDS

class App:
    def __init__(self, root):
        self.root = root
        root.title('LoopMaker')
        root.geometry('440x340')
        root.resizable(False, False)
        self.source = None
        self.output = None
        self.busy = False
        self.events = queue.Queue()
        panel = ttk.Frame(root, padding=24)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='LoopMaker', font=('Segoe UI', 22, 'bold')).pack(pady=(0, 16))
        self.choose = ttk.Button(panel, text='CHOOSE VIDEO', command=self.select)
        self.choose.pack()
        self.filename = ttk.Label(panel, text='No video selected', wraplength=380)
        self.filename.pack(pady=10)
        row = ttk.Frame(panel)
        row.pack()
        ttk.Label(row, text='Speed:  ').pack(side='left')
        self.speed = ttk.Combobox(row, values=[f'{s:.1f}x' for s in SPEEDS], state='readonly', width=8)
        self.speed.set('1.0x')
        self.speed.pack(side='left')
        self.make = ttk.Button(panel, text='MAKE LOOP', command=self.start)
        self.make.pack(pady=14)
        self.progress = ttk.Progressbar(panel, mode='indeterminate')
        self.progress.pack(fill='x')
        self.status = ttk.Label(panel, text='Outputs: “LoopMaker Output” beside your video.', wraplength=380)
        self.status.pack(pady=8)
        self.open = ttk.Button(panel, text='OPEN OUTPUT FOLDER', state='disabled', command=self.open_folder)
        self.open.pack()
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)
    def select(self):
        path = filedialog.askopenfilename(title='Choose a video', filetypes=[('Common video files', '*.mp4 *.mov *.webm *.mkv *.avi *.m4v *.mpeg *.mpg *.wmv'), ('All Supported Video Files', '*.*')])
        if path:
            self.source = path
            self.filename.config(text=Path(path).name)
    def start(self):
        if not self.source:
            messagebox.showinfo('LoopMaker', 'Choose a video first.')
            return
        self.busy = True
        self.choose.config(state='disabled')
        self.make.config(state='disabled')
        self.speed.config(state='disabled')
        self.open.config(state='disabled')
        self.status.config(text='Processing…')
        self.progress.start(12)
        source, speed = self.source, float(self.speed.get()[:-1])
        def work():
            try: self.events.put(('ok', make_loop(source, speed)))
            except LoopError as exc: self.events.put(('error', str(exc)))
            except Exception:
                logging.exception('Unexpected processing error')
                self.events.put(('error', 'Something went wrong. Please try another video.'))
        threading.Thread(target=work, daemon=True).start()
    def poll(self):
        try:
            kind, value = self.events.get_nowait()
            self.busy = False
            self.progress.stop()
            self.choose.config(state='normal')
            self.make.config(state='normal')
            self.speed.config(state='readonly')
            if kind == 'ok':
                self.output = value
                self.status.config(text=f'✓ Loop complete: {value.name}')
                self.open.config(state='normal')
            else:
                self.status.config(text='Ready to try again.')
                messagebox.showerror('LoopMaker', value)
        except queue.Empty: pass
        self.root.after(100, self.poll)
    def open_folder(self):
        try:
            if os.name == 'nt': os.startfile(str(self.output.parent))
            else: subprocess.Popen(['xdg-open', str(self.output.parent)])
        except OSError: messagebox.showinfo('Output folder', str(self.output.parent))
    def close(self):
        if self.busy:
            messagebox.showinfo('LoopMaker', 'Please wait for the loop to finish before closing.')
        else: self.root.destroy()

if __name__ == '__main__':
    log_dir = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'LoopMaker'
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=log_dir / 'loopmaker.log', level=logging.ERROR)
    except OSError: logging.basicConfig(level=logging.CRITICAL)
    root = tk.Tk()
    App(root)
    root.mainloop()
