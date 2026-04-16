import json, os, random, webbrowser, re
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle

# --- CONFIG & BUILT-IN DATA ---
DB = "us_gaap_data.json"
DEV_PASS = "sharpayvargas1" 
L, Q = [], []
THEME = "night" 

# Your 10-year expertise goes here as the "Factory Reset" data
DEFAULT_STANDARDS = [
    ["ASC 606 - Revenue", "1. Identify the contract. 2. Performance obligations. 3. Transaction price. 4. Allocate price. 5. Recognize revenue."],
    ["ASC 842 - Leases", "Requires recognition of ROU assets and lease liabilities on the balance sheet for most leases."],
    ["Inventory NRV", "Inventory must be measured at the lower of cost or net realizable value (NRV)."]
]

DEFAULT_QUIZ = [
    {"q": "How many steps in ASC 606?", "c": ["3", "5", "7"], "a": "5", "e": "ASC 606 follows a 5-step framework.", "r": "ASC 606"},
    {"q": "What asset is recorded under ASC 842?", "c": ["Fixed Asset", "ROU Asset", "Intangible"], "a": "ROU Asset", "e": "Lessees record a Right-of-Use asset.", "r": "ASC 842"}
]

def get_db_path():
    # Fix for Android: Ensures file is saved in the app's private folder
    if os.environ.get('ANDROID_ARGUMENT'):
        return os.path.join(App.get_running_app().user_data_dir, DB)
    return DB

def get_colors():
    if THEME == "night":
        return {"bg": (0.05, 0.07, 0.12, 1), "card": (0.1, 0.15, 0.25, 0.7), "text": (0.9, 0.95, 1, 1), "accent": (0, 0.8, 0.9, 1), "gold": (1, 0.84, 0, 1), "success": (0.2, 0.9, 0.5, 1), "danger": (1, 0.3, 0.3, 1), "border": (0, 0.8, 0.9, 0.4)}
    return {"bg": (0.95, 0.97, 0.98, 1), "card": (1, 1, 1, 1), "text": (0.1, 0.12, 0.15, 1), "accent": (0.1, 0.4, 0.7, 1), "gold": (0.7, 0.45, 0, 1), "success": (0.05, 0.5, 0.25, 1), "danger": (0.8, 0.1, 0.1, 1), "border": (0.1, 0.4, 0.7, 0.2)}

def save():
    try:
        with open(get_db_path(), "w") as f: json.dump({"l": L, "q": Q}, f)
    except Exception as e: print(f"Save Error: {e}")

def load():
    global L, Q
    path = get_db_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                d = json.load(f)
                L[:] = d.get("l", [])
                Q[:] = d.get("q", [])
                if L or Q: return # If file has data, use it
        except Exception as e: print(f"Load Error: {e}")
    # Fallback to sample data if file is missing or empty
    L[:] = list(DEFAULT_STANDARDS)
    Q[:] = list(DEFAULT_QUIZ)

# --- UI CLASSES ---

class GlassButton(Button):
    def __init__(self, btn_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""; self.background_down = ""; self.background_color = (0, 0, 0, 0)
        self.markup = True; self.size_hint = (0.85, None); self.height = '56dp'
        self.pos_hint = {'center_x': 0.5}; self.base_clr = btn_color
        with self.canvas.before:
            self.bg_color = Color(); self.bg_rect = RoundedRectangle(radius=[12,])
            self.border_color = Color(); self.border_line = Line(width=1.1, radius=[12,])
            self.accent_color = Color(); self.accent_line = Line(width=1.5)
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._update_canvas)

    def _update_canvas(self, *args):
        c = get_colors(); base = self.base_clr if self.base_clr else c["card"]
        self.bg_color.rgba = base if self.state == 'normal' else [x*0.8 for x in base[:3]] + [1]
        self.bg_rect.pos = self.pos; self.bg_rect.size = self.size
        self.border_color.rgba = c["border"]; self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 12)
        self.accent_color.rgba = c["accent"] if self.state == 'normal' else c["gold"]
        self.accent_line.points = [self.x + 20, self.y + 2, self.right - 20, self.y + 2]

class StyledScreen(Screen):
    def on_enter(self): Window.clearcolor = get_colors()["bg"]
    def show_status(self, text, is_err=False):
        if hasattr(self, 'status_lbl'):
            c = get_colors(); self.status_lbl.text = text; self.status_lbl.color = c["danger"] if is_err else c["success"]
            Clock.schedule_once(lambda dt: setattr(self.status_lbl, 'text', ""), 4)

class AppLogo(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height='110dp', **kwargs)
        self.click_count = 0; self.refresh()
    def refresh(self):
        self.clear_widgets(); c = get_colors()
        title = Button(text="[b]US GAAP & TAXATION[/b]", font_size='22sp', markup=True, color=c["gold"], background_color=(0,0,0,0), size_hint_y=None, height='45dp')
        title.bind(on_press=self.secret_click); self.add_widget(title)
        self.add_widget(Label(text="E X P E R T   S T U D Y   S Y S T E M", font_size='11sp', color=c["accent"], size_hint_y=None, height='20dp'))
    def secret_click(self, x):
        self.click_count += 1
        if self.click_count >= 10: self.click_count = 0; App.get_running_app().root.current = 'admin'

class QuizScreen(StyledScreen):
    timer_event = None
    def on_enter(self):
        super().on_enter()
        if not Q: self.manager.current = 'menu'
        else:
            self.p = random.sample(Q, min(len(Q), 20)); self.i, self.s = 0, 0; self.next()
    def next(self):
        self.stop_timer(); self.layout.clear_widgets(); c = get_colors(); q = self.p[self.i]; self.t_left = 15 
        exit_layer = AnchorLayout(anchor_x='right', anchor_y='top', size_hint_y=None, height='40dp', padding=[10, 10])
        self.x_btn = Button(text="[b]X[/b]", markup=True, size_hint=(None, None), size=('40dp', '40dp'), background_color=(0,0,0,0), color=c["danger"], font_size='24sp')
        self.x_btn.bind(on_press=self.quit_quiz); exit_layer.add_widget(self.x_btn); self.layout.add_widget(exit_layer)
        self.scroll = ScrollView(size_hint=(1, 1)); self.content_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=[20, 10]); self.content_box.bind(minimum_height=self.content_box.setter('height'))
        self.timer_lbl = Label(text=f"TIME: {self.t_left}s", size_hint_y=None, height='30dp', color=c["gold"], bold=True); self.content_box.add_widget(self.timer_lbl)
        self.content_box.add_widget(Label(text=f"QUESTION {self.i+1}/{len(self.p)}", size_hint_y=None, height='30dp', color=c["accent"]))
        self.q_lbl = Label(text=q['q'], size_hint_y=None, height='100dp', halign='center', text_size=(Window.width-80, None), color=c["text"], font_size='18sp'); self.content_box.add_widget(self.q_lbl)
        self.opt_container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None); self.opt_container.bind(minimum_height=self.opt_container.setter('height'))
        opts = list(q['c']); random.shuffle(opts)
        for opt in opts:
            btn = GlassButton(text=opt.strip(), color=c["text"]); btn.bind(on_press=self.check); self.opt_container.add_widget(btn)
        self.content_box.add_widget(self.opt_container); self.result_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, opacity=0); self.result_box.bind(minimum_height=self.result_box.setter('height')); self.content_box.add_widget(self.result_box); self.scroll.add_widget(self.content_box); self.layout.add_widget(self.scroll); self.timer_event = Clock.schedule_interval(self.tick, 1)
    def tick(self, dt):
        self.t_left -= 1; self.timer_lbl.text = f"TIME: {self.t_left}s"
        if self.t_left <= 0: self.stop_timer(); self.check(None)
    def stop_timer(self):
        if self.timer_event: Clock.unschedule(self.timer_event); self.timer_event = None
    def check(self, b):
        self.stop_timer()
        if self.result_box.opacity == 1: return
        c = get_colors(); q = self.p[self.i]; is_cor = b and b.text.strip() == q['a'].strip(); hex_success, hex_danger, hex_neutral = ("00ff88", "ff5555", "e6f2ff") if THEME == "night" else ("058041", "b30000", "1a1f26")
        if is_cor: self.s += 1
        for btn in self.opt_container.children:
            btn.disabled = True; btn_txt = btn.text.strip()
            if btn_txt == q['a'].strip(): btn.text = f"[b][color={hex_success}]{btn_txt}[/color][/b]"
            elif b and btn == b and not is_cor: btn.text = f"[b][color={hex_danger}]{btn_txt}[/color][/b]"
            else: btn.text = f"[color={hex_neutral}]{btn_txt}[/color]"
        self.result_box.opacity = 1; status_text = "CORRECT" if is_cor else ("TIME'S UP!" if b is None else "WRONG")
        self.result_box.add_widget(Label(text=status_text, color=(c["success"] if is_cor else c["danger"]), bold=True, size_hint_y=None, height='40dp'))
        exp_lbl = Label(text=f"EXPLANATION:\n{q['e']}", italic=True, color=c["text"], halign='center', size_hint_y=None, text_size=(Window.width-100, None)); exp_lbl.bind(texture_size=lambda s, v: setattr(s, 'height', v[1] + 20)); self.result_box.add_widget(exp_lbl)
        ref_id = q.get('r', "")
        if ref_id:
            rev_text_color = (1,1,1,1) if THEME == "night" else (0,0,0,1)
            link_btn = GlassButton(text=f"REVIEW: {ref_id}", btn_color=c["gold"], color=rev_text_color)
            link_btn.bind(on_press=lambda x: self.go_to_kb(ref_id)); self.result_box.add_widget(link_btn)
        self.result_box.add_widget(GlassButton(text="CONTINUE", color=c["text"], on_press=lambda x: self.step()))
    def quit_quiz(self, x): self.stop_timer(); self.manager.current = 'menu'
    def step(self): self.i += 1; self.next() if self.i < len(self.p) else self.end_score()
    def end_score(self):
        self.layout.clear_widgets(); c = get_colors(); self.layout.add_widget(Label(text=f"SCORE: {int(self.s/len(self.p)*100)}%", font_size='32sp', color=c["gold"], bold=True)); self.layout.add_widget(GlassButton(text="FINISH", color=c["text"], on_press=lambda x: setattr(self.manager, 'current', 'menu')))
    def go_to_kb(self, ref):
        kb_screen = self.manager.get_screen('kb')
        match = next((item for item in L if ref.lower() in item[0].lower()), None)
        if match: kb_screen.view(match[0], match[1]); self.manager.current = 'kb'
    def __init__(self, **kw): super().__init__(**kw); self.layout = BoxLayout(orientation='vertical'); self.add_widget(self.layout)

class KB(StyledScreen):
    is_direct, target_t, target_c, filter_text = False, "", "", ""
    def on_enter(self):
        super().on_enter(); c = get_colors(); self.layout.clear_widgets()
        if not self.is_direct:
            self.layout.add_widget(AppLogo())
            self.search_ti = TextInput(text=self.filter_text, hint_text="Search Standards...", size_hint=(0.85, None), height='48dp', pos_hint={'center_x': 0.5}, background_color=c["card"], foreground_color=c["text"], hint_text_color=c["accent"], multiline=False); self.search_ti.bind(text=self.update_filter); self.layout.add_widget(self.search_ti)
            sc = ScrollView(size_hint_x=0.85, pos_hint={'center_x': 0.5}); b = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10); b.bind(minimum_height=b.setter('height'))
            for t, content in sorted(L):
                if self.filter_text.lower() in t.lower():
                    btn = GlassButton(text=t, color=c["text"]); btn.bind(on_press=lambda x, tt=t, cc=content: self.view(tt, cc)); b.add_widget(btn)
            sc.add_widget(b); self.layout.add_widget(sc); self.layout.add_widget(Widget()); self.layout.add_widget(GlassButton(text="MENU", color=c["text"], on_press=lambda x: setattr(self.manager, 'current', 'menu')))
        else:
            self.layout.add_widget(Label(text=self.target_t.upper(), size_hint_y=None, height='80dp', bold=True, color=c["gold"], halign='center', font_size='18sp', text_size=(Window.width-60, None)))
            card_anchor = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=1); content_scroll = ScrollView(size_hint=(0.95, 0.85)); text_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=(40, 10)); text_container.bind(minimum_height=text_container.setter('height'))
            parts = re.split(r'(\d\.\s)', self.target_c); combined_lines = []; temp_line = ""
            for p in parts:
                if re.match(r'\d\.\s', p):
                    if temp_line: combined_lines.append(temp_line.strip())
                    temp_line = p
                else: temp_line += p
            combined_lines.append(temp_line.strip())
            for line in combined_lines:
                if not line: continue
                lbl = Label(text=line, size_hint_y=None, color=c["text"], font_size='15sp', line_height=1.4, halign='justify', valign='top'); lbl.bind(texture_size=lambda s, v: setattr(s, 'height', v[1])); lbl.bind(width=lambda s, v: setattr(s, 'text_size', (v, None))); text_container.add_widget(lbl)
            content_scroll.add_widget(text_container); card_anchor.add_widget(content_scroll); self.layout.add_widget(card_anchor); self.layout.add_widget(Widget(size_hint_y=None, height='10dp')); self.layout.add_widget(GlassButton(text="BACK", color=c["text"], on_press=lambda x: self.back_kb())); self.layout.add_widget(Widget(size_hint_y=None, height='15dp'))
    def update_filter(self, instance, value): self.filter_text = value; self.on_enter()
    def view(self, t, content): self.is_direct = True; self.target_t = t; self.target_c = content; self.on_enter()
    def back_kb(self): self.is_direct = False; self.on_enter()
    def __init__(self, **kw): super().__init__(**kw); self.layout = BoxLayout(orientation='vertical', padding=20, spacing=5); self.add_widget(self.layout)

class Menu(StyledScreen):
    def on_enter(self):
        super().on_enter(); self.main_box.clear_widgets(); c = get_colors()
        mode_row = AnchorLayout(anchor_x='right', anchor_y='top', size_hint_y=None, height='50dp', padding=[25, 15]); self.mode_lbl = Label(text="NIGHT" if THEME == "night" else "DAY", font_size='10sp', color=c["accent"], bold=True); mode_row.add_widget(self.mode_lbl); self.main_box.add_widget(mode_row); self.main_box.add_widget(AppLogo())
        menu_items = [("KNOWLEDGE BASE", 'kb', None), ("MANAGE STANDARDS", 'ml', None), ("PRACTICE QUIZ", 'pq', (0.1, 0.4, 0.8, 1)), ("MANAGE QUIZ", 'mq', (0.1, 0.4, 0.8, 1))]
        for t, s, clr in menu_items:
            b = GlassButton(text=t, btn_color=clr, color=c["text"]); b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc)); self.main_box.add_widget(b); self.main_box.add_widget(Widget(size_hint_y=None, height='12dp'))
        self.main_box.add_widget(Widget()); f = Button(text="By [b][color=64a5ff]Rachel Vargas, CPA[/color][/b]", markup=True, background_color=(0,0,0,0), size_hint_y=None, height='40dp', font_size='11sp', color=c["text"]); f.bind(on_press=lambda x: webbrowser.open("https://www.linkedin.com/in/rachel-vargas-cpa")); self.main_box.add_widget(f)
    def on_touch_down(self, touch):
        if hasattr(self, 'mode_lbl') and self.mode_lbl.collide_point(*touch.pos):
            global THEME; THEME = "day" if THEME == "night" else "night"; self.on_enter(); return True
        return super().on_touch_down(touch)
    def __init__(self, **kw): super().__init__(**kw); self.main_box = BoxLayout(orientation='vertical'); self.add_widget(self.main_box)

class ManageL(StyledScreen):
    mode = "add"
    def on_enter(self): super().on_enter(); self.draw()
    def draw(self):
        self.layout.clear_widgets(); self.layout.add_widget(AppLogo()); c = get_colors(); self.status_lbl = Label(text="", size_hint_y=None, height='30dp', bold=True, markup=True); self.layout.add_widget(self.status_lbl); tabs = BoxLayout(size_hint=(0.85, None), height='48dp', spacing=10, pos_hint={'center_x': 0.5}); b1 = Button(text="IMPORT", background_color=(0,0,0,0), color=(c["accent"] if self.mode == 'add' else c["text"])); b2 = Button(text="REPO", background_color=(0,0,0,0), color=(c["accent"] if self.mode == 'list' else c["text"])); b1.bind(on_press=lambda x: self.set_m("add")); b2.bind(on_press=lambda x: self.set_m("list")); tabs.add_widget(b1); tabs.add_widget(b2); self.layout.add_widget(tabs)
        if self.mode == "add":
            self.ti = TextInput(hint_text="Standard Ref - Desc | Full Content...", size_hint=(0.85, 0.4), pos_hint={'center_x': 0.5}, background_color=c["card"], foreground_color=c["text"]); self.layout.add_widget(self.ti); self.layout.add_widget(GlassButton(text="SAVE STANDARDS", btn_color=c["success"], color=(1,1,1,1), on_press=self.bulk))
        else:
            sc = ScrollView(size_hint_x=0.85, pos_hint={'center_x': 0.5}); bl = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8); bl.bind(minimum_height=bl.setter('height'))
            for i in L: bl.add_widget(GlassButton(text=f"DEL: {i[0]}", btn_color=c["danger"], color=(1,1,1,1), on_press=lambda x, t=i[0]: self.rem(t)))
            sc.add_widget(bl); self.layout.add_widget(sc)
        self.layout.add_widget(Widget()); self.layout.add_widget(GlassButton(text="BACK", color=c["text"], on_press=lambda x: setattr(self.manager, 'current', 'menu')))
    def set_m(self, m): self.mode = m; self.draw()
    def bulk(self, x):
        global L; count = 0
        for ln in self.ti.text.strip().split('\n'):
            if "|" in ln: p = [i.strip() for i in ln.split('|')]; L.append([p[0], p[1]]); count += 1
        save(); self.ti.text = ""; self.show_status(f"SAVED {count}")
    def rem(self, t): global L; L[:] = [i for i in L if i[0] != t]; save(); self.draw()
    def __init__(self, **kw): super().__init__(**kw); self.layout = BoxLayout(orientation='vertical', padding=25, spacing=10); self.add_widget(self.layout)

class ManageQ(StyledScreen):
    mode = "add"
    def on_enter(self): super().on_enter(); self.draw()
    def draw(self):
        self.layout.clear_widgets(); self.layout.add_widget(AppLogo()); c = get_colors(); self.status_lbl = Label(text="", size_hint_y=None, height='30dp', bold=True, markup=True); self.layout.add_widget(self.status_lbl); tabs = BoxLayout(size_hint=(0.85, None), height='48dp', spacing=10, pos_hint={'center_x': 0.5}); b1 = Button(text="IMPORT", background_color=(0,0,0,0), color=(c["accent"] if self.mode == 'add' else c["text"])); b2 = Button(text="LIST", background_color=(0,0,0,0), color=(c["accent"] if self.mode == 'list' else c["text"])); b1.bind(on_press=lambda x: self.set_m("add")); b2.bind(on_press=lambda x: self.set_m("list")); tabs.add_widget(b1); tabs.add_widget(b2); self.layout.add_widget(tabs)
        if self.mode == "add":
            self.ti = TextInput(hint_text="Q | Opt1,Opt2 | Ans | Exp | RefTitle", size_hint=(0.85, 0.4), pos_hint={'center_x': 0.5}, background_color=c["card"], foreground_color=c["text"]); self.layout.add_widget(self.ti); self.layout.add_widget(GlassButton(text="SAVE QUIZ", btn_color=c["success"], color=(1,1,1,1), on_press=self.bulk))
        else:
            sc = ScrollView(size_hint_x=0.85, pos_hint={'center_x': 0.5}); bl = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8); bl.bind(minimum_height=bl.setter('height'))
            for idx, q in enumerate(Q): bl.add_widget(GlassButton(text=f"REM: {q['q'][:30]}", btn_color=c["danger"], color=(1,1,1,1), on_press=lambda x, i=idx: self.rem(i)))
            sc.add_widget(bl); self.layout.add_widget(sc)
        self.layout.add_widget(Widget()); self.layout.add_widget(GlassButton(text="BACK", color=c["text"], on_press=lambda x: setattr(self.manager, 'current', 'menu')))
    def set_m(self, m): self.mode = m; self.draw()
    def bulk(self, x):
        global Q; count = 0
        for ln in self.ti.text.strip().split('\n'):
            p = [i.strip() for i in ln.split('|')]
            if len(p) >= 5: Q.append({"q":p[0], "c":p[1].split(','), "a":p[2], "e":p[3], "r":p[4]}); count += 1
        save(); self.ti.text = ""; self.show_status(f"IMPORTED {count}")
    def rem(self, i): global Q; Q.pop(i); save(); self.draw()
    def __init__(self, **kw): super().__init__(**kw); self.layout = BoxLayout(orientation='vertical', padding=25, spacing=10); self.add_widget(self.layout)

class AdminScreen(StyledScreen):
    unlocked = False
    def on_enter(self): super().on_enter(); self.draw()
    def draw(self):
        self.layout.clear_widgets(); self.layout.add_widget(AppLogo()); c = get_colors(); self.status_lbl = Label(text="", size_hint_y=None, height='30dp', bold=True, markup=True); self.layout.add_widget(self.status_lbl)
        if not self.unlocked:
            self.pw = TextInput(hint_text="Password...", password=True, multiline=False, size_hint=(0.85, None), height='54dp', pos_hint={'center_x': 0.5}, background_color=c["card"], foreground_color=c["text"]); self.layout.add_widget(self.pw); self.layout.add_widget(GlassButton(text="UNLOCK", color=c["text"], on_press=self.check_pw))
        else:
            self.layout.add_widget(Label(text=f"Standards: {len(L)} | Quiz Items: {len(Q)}", color=c["gold"])); self.layout.add_widget(GlassButton(text="GET STANDARDS", btn_color=(0, 0.6, 0.7, 1), on_press=self.copy_standards)); self.layout.add_widget(GlassButton(text="GET QUIZ", btn_color=(0.1, 0.4, 0.8, 1), on_press=self.copy_quiz)); self.layout.add_widget(GlassButton(text="WIPE ALL", btn_color=c["danger"], color=(1,1,1,1), on_press=self.wipe_all))
        self.layout.add_widget(Widget()); self.layout.add_widget(GlassButton(text="BACK", color=c["text"], on_press=self.go_back))
    def check_pw(self, x):
        if self.pw.text == DEV_PASS: self.unlocked = True; self.draw()
    def copy_standards(self, x): data = "\n".join([f"{i[0]} | {i[1]}" for i in L]); Clipboard.copy(data); self.show_status("Copied!")
    def copy_quiz(self, x): data = "\n".join([f"{q['q']} | {','.join(q['c'])} | {q['a']} | {q['e']} | {q.get('r','')}" for q in Q]); Clipboard.copy(data); self.show_status("Copied!")
    def wipe_all(self, x): global L, Q; L.clear(); Q.clear(); save(); self.unlocked = False; self.manager.current = 'menu'
    def go_back(self, x): self.unlocked = False; self.manager.current = 'menu'
    def __init__(self, **kw): super().__init__(**kw); self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10); self.add_widget(self.layout)

class MainApp(App):
    def build(self):
        load(); sm = ScreenManager(); sm.add_widget(Menu(name='menu')); sm.add_widget(KB(name='kb')); sm.add_widget(ManageL(name='ml')); sm.add_widget(ManageQ(name='mq')); sm.add_widget(QuizScreen(name='pq')); sm.add_widget(AdminScreen(name='admin')); return sm 

if __name__ == "__main__":
    MainApp().run()
