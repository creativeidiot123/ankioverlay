_B8='operation_did_execute'
_B7='_anki_overlay_instance'
_B6='reviewer_did_answer_card'
_B5='answered_card'
_B4='screenRemoved'
_B3='screenAdded'
_B2='applicationStateChanged'
_B1='- Remove Selected'
_B0='FocusPolicy'
_A_='WindowDoesNotAcceptFocus'
_Az='FramelessWindowHint'
_Ay='WindowStaysOnTopHint'
_Ax='CursorShape'
_Aw='english_example_3'
_Av='german_example_3'
_Au='english_example_2'
_At='german_example_2'
_As='<num_slash>'
_Ar='<num_dot>'
_Aq='<num_minus>'
_Ap='<num_plus>'
_Ao='<num_star>'
_An='Answer the card'
_Am='focus_dim_message'
_Al='focus_dim_show_message'
_Ak='setPosition'
_Aj='setVolume'
_Ai='arming'
_Ah='ignored: nothing to undo'
_Ag='card_id'
_Af='cubic'
_Ae='linear'
_Ad='ignore'
_Ac='english_example_1'
_Ab='german_example_1'
_Aa='english_word'
_AZ='german_word'
_AY='PAY ATTENTION'
_AX='focus_dim_replay_counts_as_activity'
_AW='name'
_AV='shake_glow'
_AU='force'
_AT='visibility'
_AS='style'
_AR='content'
_AQ='answer'
_AP='correct'
_AO='AlignmentFlag'
_AN='quad'
_AM='focus_dim_ramp_sec'
_AL='debug_status'
_AK='key_toggle'
_AJ='key_undo'
_AI='key_replay'
_AH='Select Deck...'
_AG='toggle'
_AF='compact'
_AE='partial'
_AD='focus_dim_question_only'
_AC='key_easy'
_AB='key_good'
_AA='key_hard'
_A9='key_again'
_A8='pos_y'
_A7='pos_x'
_A6='height'
_A5='width'
_A4='command'
_A3='warning'
_A2='none'
_A1='replay'
_A0='durations_v2'
_z='focus_dim_partial_reset_sec'
_y='focus_dim_warning_font_px'
_x='focus_dim_safe_feather'
_w='focus_dim_safe_padding'
_v='focus_dim_max_opacity'
_u='focus_dim_punish_opacity'
_t='focus_dim_warning_opacity'
_s='focus_dim_timing_model'
_r='question'
_q='focus_dim_warning_style'
_p='font_size_translation'
_o='font_size_word'
_n='key_flip'
_m='deck_themes'
_l='deck_maps'
_k='focus_dim_warning_subtext'
_j='focus_dim_warning_text'
_i='font_size_example'
_h='reviewer'
_g='punish'
_f='full'
_e='flip_only'
_d='focus_dim_lockdown_sec'
_c='focus_dim_punish_sec'
_b='focus_dim_warning_sec'
_a='grade_from_question_mode'
_Z='review'
_Y='deck'
_X='lockdown'
_W='focus_dim_replay_reset_mode'
_V='mode'
_U='reveal_then_grade'
_T='focus_dim_curve'
_S='focus_dim_enabled'
_R='deck_id'
_Q='easy'
_P='good'
_O='hard'
_N='again'
_M='idle'
_L='focus_dim_idle_sec'
_K='opacity'
_J='color_sent'
_I='color_pitch'
_H='color_word'
_G='flip'
_F='undo'
_E=1.
_D=.0
_C=False
_B=True
_A=None
import atexit,copy,html,json,math,os,shutil,time,traceback
from dataclasses import dataclass,field
from enum import Enum
from aqt import gui_hooks,mw
from aqt.qt import*
from aqt.utils import tooltip
try:from PyQt6.QtMultimedia import QAudioOutput,QMediaPlayer;QMediaContent=_A
except Exception:
	try:from aqt.qt import QAudioOutput,QMediaPlayer
	except Exception:QAudioOutput=_A;QMediaPlayer=_A
	try:from aqt.qt import QMediaContent
	except Exception:QMediaContent=_A
try:from pynput import keyboard;HAS_PYNPUT=_B
except Exception:keyboard=_A;HAS_PYNPUT=_C
DEFAULT_CONFIG={_l:[],_m:[],_A5:389,_A6:368,_K:16,_A7:1504,_A8:649,_H:'#ff79c6',_I:'#50fa7b',_J:'#bd93f9',_A9:'p',_AA:'[',_AB:']',_AC:'9',_n:'o',_AI:'/',_AJ:'l',_AK:'<ctrl>+9',_AL:_C,_a:_e,_o:42,_p:26,_i:18,_S:_B,_L:28.,_AM:5.,_b:5.,_c:5.,_d:5.,_s:_A0,_t:45,_u:75,_v:100,_T:_AN,_AD:_C,_w:16,_x:20,_j:_AY,_k:_An,_q:'pulse',_y:30,_W:_AE,_z:2.5,_AX:_B,_Al:_B,_Am:_AY}
HOTKEY_KEYS=[_AK,_n,_AI,_AJ,_A9,_AA,_AB,_AC]
HOTKEY_LABELS={_AK:'Toggle',_n:'Flip',_AI:'Replay',_AJ:'Undo',_A9:'Again',_AA:'Hard',_AB:'Good',_AC:'Easy'}
GRADE_HOTKEY_KEYS=_A9,_AA,_AB,_AC
NUMPAD_TOKEN_TO_VK={'<num0>':'<96>','<num1>':'<97>','<num2>':'<98>','<num3>':'<99>','<num4>':'<100>','<num5>':'<101>','<num6>':'<102>','<num7>':'<103>','<num8>':'<104>','<num9>':'<105>',_Ao:'<106>',_Ap:'<107>',_Aq:'<109>',_Ar:'<110>',_As:'<111>'}
NUMPAD_VK_BY_PRIMARY_KEY={'0':'<96>','1':'<97>','2':'<98>','3':'<99>','4':'<100>','5':'<101>','6':'<102>','7':'<103>','8':'<104>','9':'<105>','*':'<106>','-':'<109>','.':'<110>','/':'<111>'}
DECK_MAP_FIELDS=[('German Word',_AZ),('English Word',_Aa),('German Ex 1',_Ab),('English Ex 1',_Ac),('German Ex 2',_At),('English Ex 2',_Au),('German Ex 3',_Av),('English Ex 3',_Aw)]
LEGACY_FIELD_MAP={_AZ:'word',_Aa:'definition',_Ab:'sentence',_Ac:'image'}
THEME_MODE_VALUES='',_f,_AF
LEFT_MOUSE_BUTTON=Qt.MouseButton.LeftButton if hasattr(Qt,'MouseButton')else Qt.LeftButton
RESIZE_CURSOR=Qt.CursorShape.SizeFDiagCursor if hasattr(Qt,_Ax)else Qt.SizeFDiagCursor
DRAG_CURSOR=Qt.CursorShape.SizeAllCursor if hasattr(Qt,_Ax)else Qt.SizeAllCursor
ALIGN_CENTER=Qt.AlignmentFlag.AlignCenter if hasattr(Qt,_AO)else Qt.AlignCenter
PENDING_TIMEOUT_SEC=4.2
QUEUED_TRANSITION_MAX_AGE_SEC=4.5
TRANSITION_WATCHDOG_MS=120
FOCUS_DIM_TICK_MS=125
FOCUS_DIM_IDLE_TICK_MS=250
FOCUS_DIM_CLEAR_SEC=.15
FOCUS_DIM_RISE_SEC=4.
PAY_ATTENTION_INTERVAL_MS=3000
PAY_ATTENTION_SOUND_FILE='pay_attention.mp3'
GRADE_SOUND_FILES={_AP:'_tinder_correct.mp3','wrong':'_tinder_wrong.mp3'}
GRADE_SOUND_BY_COMMAND={_N:'wrong',_O:_AP,_P:_AP,_Q:_AP}
GRADE_SOUND_COMMAND_BY_EASE={1:_N,2:_O,3:_P,4:_Q}
COMMAND_DEBOUNCE_SEC={_G:.18,_N:.18,_O:.18,_P:.18,_Q:.18,_F:.18,_A1:.08,_AG:.2}
def _log(message):print(f"[Anki Overlay] {message}")
def _now():return time.monotonic()
def _clamp_float(value,default,minimum,maximum):
	try:numeric=float(value)
	except Exception:return float(default)
	return max(float(minimum),min(float(maximum),numeric))
def _normalize_opacity(value,default=-1):
	try:numeric=int(value)
	except Exception:return default
	return numeric if-1<=numeric<=100 else default
def _normalize_font_size(value,default,minimum=10,maximum=120):
	try:numeric=int(value)
	except Exception:return default
	return max(minimum,min(maximum,numeric))
def _normalize_hex_color(value,default):
	raw=str(value or'').strip()
	if len(raw)==7 and raw.startswith('#'):
		try:int(raw[1:],16);return f"#{raw[1:].lower()}"
		except Exception:pass
	return default
def _normalize_optional_hex_color(value):return''if not str(value or'').strip()else _normalize_hex_color(value,'')
def _normalize_hotkey(value):
	combo=str(value or'').strip().lower()
	if not combo:return''
	for(token,vk)in NUMPAD_TOKEN_TO_VK.items():combo=combo.replace(token,vk)
	return'<107>'if combo=='+'else combo
def _hotkey_registration_variants(combo):
	normalized=_normalize_hotkey(combo)
	if not normalized:return[]
	parts=normalized.split('+');variants=[normalized]
	if parts:
		numpad_vk=NUMPAD_VK_BY_PRIMARY_KEY.get(parts[-1])
		if numpad_vk:
			variant='+'.join(parts[:-1]+[numpad_vk])
			if variant not in variants:variants.append(variant)
	return variants
def _normalize_grade_from_question_mode(value,default=_e):mode=str(value or'').strip().lower();return mode if mode in{_Ad,_e,_U}else default
def _normalize_focus_curve(value,default=_AN):curve=str(value or'').strip().lower();return curve if curve in{_Ae,_AN,_Af}else default
def _normalize_replay_reset_mode(value,default=_AE):mode=str(value or'').strip().lower();return mode if mode in{_A2,_AE,_f}else default
def _curve_value(progress,curve):
	value=max(_D,min(_E,float(progress)))
	if curve==_Ae:return value
	if curve==_Af:return value*value*value
	return value*value
def _qt_window_flag(name):
	if hasattr(Qt,'WindowType')and hasattr(Qt.WindowType,name):return getattr(Qt.WindowType,name)
	return getattr(Qt,name,0)
def _event_global_point(event):
	if hasattr(event,'globalPosition'):return event.globalPosition().toPoint()
	if hasattr(event,'globalPos'):return event.globalPos()
	return QPoint()
def _qt_text_draw_flags(vertical_flag):
	word_wrap=int(Qt.TextFlag.TextWordWrap)if hasattr(Qt,'TextFlag')else int(Qt.TextWordWrap)
	if hasattr(Qt,_AO):return word_wrap|int(Qt.AlignmentFlag.AlignHCenter)|int(vertical_flag)
	return word_wrap|int(Qt.AlignHCenter)|int(vertical_flag)
def _no_brush():return Qt.BrushStyle.NoBrush if hasattr(Qt,'BrushStyle')else Qt.NoBrush
class ReviewUiState(Enum):IDLE=_M;QUESTION=_r;ANSWER=_AQ;TRANSITIONING='transitioning'
@dataclass
class TransitionState:
	command:str='';card_id:int|_A=_A;started_at:float=_D;source_state:str=ReviewUiState.IDLE.value;reveal_request:dict|_A=_A;queued_command:str='';queued_card_id:int|_A=_A;queued_at:float=_D
	def clear_pending(self,clear_reveal=_C):
		self.command='';self.card_id=_A;self.started_at=_D;self.source_state=ReviewUiState.IDLE.value
		if clear_reveal:self.reveal_request=_A
	def clear_queue(self):self.queued_command='';self.queued_card_id=_A;self.queued_at=_D
@dataclass
class FocusDimState:
	enabled:bool=_C;idle_started_at:float=_D;last_activity_at:float=_D;phase:str=_M;target_opacity:float=_D;current_opacity:float=_D;last_tick_at:float=_D;last_idle_elapsed:float=_D;stage_progress:float=_D;last_ramp_progress:float=_D;last_activity_source:str='';last_card_id:int|_A=_A;last_side:str|_A=_A;fail_open_active:bool=_C
	def reset(self,clear_identity=_B):
		self.idle_started_at=_D;self.last_activity_at=_D;self.phase=_M;self.target_opacity=_D;self.current_opacity=_D;self.last_tick_at=_D;self.last_idle_elapsed=_D;self.stage_progress=_D;self.last_ramp_progress=_D;self.last_activity_source=''
		if clear_identity:self.last_card_id=_A;self.last_side=_A
@dataclass
class RefreshState:
	pending:bool=_C;requested_at:float=_D;delay_ms:int|_A=_A;flags:dict=field(default_factory=lambda:{_AR:_C,_AS:_C,_AT:_C,_AU:_C});expected_card_id:int|_A=_A;expected_reviewer_state:str|_A=_A
	def clear(self):self.pending=_C;self.requested_at=_D;self.delay_ms=_A;self.flags={_AR:_C,_AS:_C,_AT:_C,_AU:_C};self.expected_card_id=_A;self.expected_reviewer_state=_A
class MainWindowEventFilter(QObject):
	WATCHED_TYPES={QEvent.Type.Show,QEvent.Type.Hide,QEvent.Type.WindowStateChange,QEvent.Type.ActivationChange,QEvent.Type.Move,QEvent.Type.Resize}
	def __init__(self,controller,parent=_A):super().__init__(parent);self._controller=controller
	def eventFilter(self,obj,event):
		if event.type()in self.WATCHED_TYPES:self._controller.request_overlay_visibility_reconcile('main_window_event')
		return _C
class HotkeyRecorder(QPushButton):
	def __init__(self,current_key,parent=_A):super().__init__(current_key or'None',parent);self.current_key=current_key or'';self.recording=_C;self.setFixedWidth(150);self.setCheckable(_B);self.clicked.connect(self.toggle_recording)
	def toggle_recording(self):
		self.recording=self.isChecked();self.setText('... ? ...'if self.recording else self.current_key or'None')
		if self.recording:self.setFocus()
	def keyPressEvent(self,event):
		A='<enter>'
		if not self.recording:return super().keyPressEvent(event)
		key=event.key();modifiers=event.modifiers()
		if key in[Qt.Key.Key_Control,Qt.Key.Key_Shift,Qt.Key.Key_Alt,Qt.Key.Key_Meta]:return
		parts=[]
		for(flag,label)in((Qt.KeyboardModifier.ControlModifier,'<ctrl>'),(Qt.KeyboardModifier.ShiftModifier,'<shift>'),(Qt.KeyboardModifier.AltModifier,'<alt>'),(Qt.KeyboardModifier.MetaModifier,'<meta>')):
			if modifiers&flag:parts.append(label)
		key_str=QKeySequence(key).toString().lower();mapping={'backspace':'<backspace>','del':'<delete>','ins':'<insert>','return':A,'enter':A,'capslock':'<caps_lock>'};keypad_mapping={'0':'<num0>','1':'<num1>','2':'<num2>','3':'<num3>','4':'<num4>','5':'<num5>','6':'<num6>','7':'<num7>','8':'<num8>','9':'<num9>','*':_Ao,'+':_Ap,'-':_Aq,'.':_Ar,'/':_As};parts.append(keypad_mapping.get(key_str,mapping.get(key_str,key_str))if modifiers&Qt.KeyboardModifier.KeypadModifier else mapping.get(key_str,key_str));self.current_key='+'.join(parts);self.recording=_C;self.setChecked(_C);self.setText(self.current_key or'None')
class OverlayAlarmLayer(QWidget):
	def __init__(self,parent=_A):super().__init__(parent);self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,_B);self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,_B);self._intensity=_D;self._phase=_M;self._stage_progress=_D;self._anim_time=_D;self._pop_until=_D;self.hide()
	def set_state(self,intensity,phase,stage_progress,anim_time):
		intensity=max(_D,min(_E,float(intensity)));phase=str(phase or _M);stage_progress=max(_D,min(_E,float(stage_progress)));changed=abs(self._intensity-intensity)>.03 or self._phase!=phase or abs(self._stage_progress-stage_progress)>.05
		if phase==_X and self._phase!=_X:self._pop_until=float(anim_time)+.22
		self._intensity=intensity;self._phase=phase;self._stage_progress=stage_progress;self._anim_time=float(anim_time)
		if self._intensity<=.01:self.hide();return
		if not self.isVisible():self.show();changed=_B
		if changed:self.update()
	def paintEvent(self,event):
		super().paintEvent(event)
		if self._intensity<=.01:return
		painter=QPainter(self)
		try:
			try:painter.setRenderHint(QPainter.RenderHint.Antialiasing,_B)
			except Exception:painter.setRenderHint(QPainter.Antialiasing,_B)
			pop_scale=_E+.02*((self._pop_until-self._anim_time)/.22)if self._anim_time<self._pop_until else _E;base=QColor(255,215,90,255)if self._phase==_A3 else QColor(255,130,65,255)if self._phase==_g else QColor(255,78,72,255);rect=self.rect().adjusted(6,6,-6,-6)
			if pop_scale>_E:grow=int((pop_scale-_E)*12e1);rect=rect.adjusted(-grow,-grow,grow,grow)
			painter.setBrush(_no_brush());glow_alpha=max(0,min(255,int(70*self._intensity)));glow_pen=QPen(QColor(base.red(),base.green(),base.blue(),glow_alpha));glow_pen.setWidthF(3.2);painter.setPen(glow_pen);painter.drawRoundedRect(rect.adjusted(-4,-4,4,4),20,20)
			border=QPen(QColor(255,255,255,max(40,min(255,int(145*self._intensity)))));border.setWidthF(2.+self._intensity);painter.setPen(border);painter.drawRoundedRect(rect,18,18)
		except Exception:traceback.print_exc()
class FocusDimOverlay(QWidget):
	def __init__(self,screen):super().__init__(_A);self._screen=screen;self._opacity_percent=_D;self._phase=_M;self._stage_progress=_D;self._warning_text='';self._warning_subtext='';self._show_message=_C;self._warning_style=_AV;self._warning_font_px=30;self._safe_rect_global=QRect();self._safe_feather=20;self._anim_time=_D;self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,_B);self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,_B);flags=_qt_window_flag(_Ay)|_qt_window_flag(_Az)|_qt_window_flag('Tool');flags|=_qt_window_flag('WindowTransparentForInput')|_qt_window_flag(_A_);self.setWindowFlags(flags);no_focus=Qt.FocusPolicy.NoFocus if hasattr(Qt,_B0)else Qt.NoFocus;self.setFocusPolicy(no_focus);self.sync_geometry();self.hide()
	def sync_geometry(self):
		if self._screen:self.setGeometry(self._screen.geometry())
	def clear_dim(self):self._opacity_percent=_D;self._show_message=_C;self._safe_rect_global=QRect();self.hide();self.update()
	def apply_dim(self,opacity_percent,phase,stage_progress,warning_text,warning_subtext,show_message,warning_style,warning_font_px,safe_rect_global,safe_feather,anim_time):
		opacity_percent=max(_D,min(1e2,float(opacity_percent)));phase=str(phase or _M);stage_progress=max(_D,min(_E,float(stage_progress)));warning_text=str(warning_text or'');warning_subtext=str(warning_subtext or'');show_message=bool(show_message);warning_style=str(warning_style or _AV).strip().lower();warning_font_px=max(14,min(84,int(warning_font_px)));safe_rect_global=QRect(safe_rect_global)if isinstance(safe_rect_global,QRect)else QRect();safe_feather=max(0,int(safe_feather));changed=abs(self._opacity_percent-opacity_percent)>.9 or self._phase!=phase or abs(self._stage_progress-stage_progress)>.05 or self._warning_text!=warning_text or self._warning_subtext!=warning_subtext or self._show_message!=show_message or self._warning_style!=warning_style or self._warning_font_px!=warning_font_px or self._safe_rect_global!=safe_rect_global or self._safe_feather!=safe_feather
		self._opacity_percent=opacity_percent;self._phase=phase;self._stage_progress=stage_progress;self._warning_text=warning_text;self._warning_subtext=warning_subtext;self._show_message=show_message;self._warning_style=warning_style;self._warning_font_px=warning_font_px;self._safe_rect_global=safe_rect_global;self._safe_feather=safe_feather;self._anim_time=float(anim_time)
		if self._opacity_percent<=.01 and not self._show_message:self.hide();return
		before_geo=self.geometry();self.sync_geometry();changed=changed or before_geo!=self.geometry()
		if not self.isVisible():self.show();self.raise_();changed=_B
		if changed:self.update()
	def _safe_rect_local(self):
		if self._safe_rect_global.isNull()or not self._safe_rect_global.isValid():return QRect()
		local=QRect(self._safe_rect_global);geo=self.geometry();local.translate(-geo.x(),-geo.y());local=local.intersected(self.rect());return local if local.width()>=8 and local.height()>=8 else QRect()
	def _draw_safe_feather(self,painter,safe_rect,outer_alpha,inner_alpha):
		if self._safe_feather<=0:return
		rings=[];max_dist=max(1,self._safe_feather)
		for ratio in(.35,.7,_E):
			dist=max(1,int(max_dist*ratio))
			if dist not in rings:rings.append(dist)
		for dist in rings:t=min(_E,dist/max(_E,float(max_dist)));alpha=int(inner_alpha+(outer_alpha-inner_alpha)*t);painter.setPen(QPen(QColor(0,0,0,max(0,min(255,alpha))),max(1,int(max_dist/3))));painter.setBrush(_no_brush());ring=safe_rect.adjusted(-dist,-dist,dist,dist);painter.drawRoundedRect(ring,max(8.,14.+dist*.18),max(8.,14.+dist*.18))
	def _draw_warning_text(self,painter):
		if not self._show_message:return
		headline=self._warning_text or _AY;subtext=self._warning_subtext or _An
		if self._phase==_X and int(self._anim_time*2.8)%2==1:headline,subtext=subtext.upper(),headline
		scale=_E
		if self._phase==_A3:scale=1.02+.03*self._stage_progress
		elif self._phase==_g:scale=1.05+.04*self._stage_progress
		elif self._phase==_X:scale=1.08+.04*self._stage_progress
		font_px=max(16,int(self._warning_font_px*scale));title_font=QFont();title_font.setBold(_B);title_font.setPixelSize(font_px);sub_font=QFont();sub_font.setBold(_B);sub_font.setPixelSize(max(13,int(font_px*.45)));area=self.rect().adjusted(int(self.width()*.1),int(self.height()*.18),-int(self.width()*.1),-int(self.height()*.18));title_rect=QRect(area);title_rect.setHeight(int(area.height()*.62));title_flags=_qt_text_draw_flags(Qt.AlignmentFlag.AlignBottom if hasattr(Qt,_AO)else Qt.AlignBottom);sub_flags=_qt_text_draw_flags(Qt.AlignmentFlag.AlignTop if hasattr(Qt,_AO)else Qt.AlignTop);shadow_alpha=120 if self._phase==_X else 95 if self._phase==_g else 72;painter.setFont(title_font);painter.setPen(QColor(255,76,76,shadow_alpha));painter.drawText(title_rect.translated(2,2),title_flags,headline);painter.setPen(QColor(255,255,255,245));painter.drawText(title_rect,title_flags,headline);painter.setFont(sub_font);sub_rect=QRect(area);sub_rect.setTop(title_rect.bottom()+6);painter.setPen(QColor(255,220,220,190));painter.drawText(sub_rect,sub_flags,subtext)
	def paintEvent(self,event):
		super().paintEvent(event)
		if self._opacity_percent<=.01 and not self._show_message:return
		painter=QPainter(self)
		try:
			try:painter.setRenderHint(QPainter.RenderHint.Antialiasing,_B);painter.setRenderHint(QPainter.RenderHint.TextAntialiasing,_B)
			except Exception:painter.setRenderHint(QPainter.Antialiasing,_B);painter.setRenderHint(QPainter.TextAntialiasing,_B)
			base_alpha=max(0,min(255,int(self._opacity_percent/1e2*255.)));painter.fillRect(self.rect(),QColor(0,0,0,base_alpha));safe_rect=self._safe_rect_local()
			if safe_rect.isValid():factor=.08 if self._phase==_X else .05 if self._phase==_g else .03 if self._phase==_A3 else _D;inner_alpha=int(base_alpha*factor);painter.fillRect(safe_rect,QColor(0,0,0,inner_alpha));self._draw_safe_feather(painter,safe_rect,base_alpha,inner_alpha)
			self._draw_warning_text(painter)
		except Exception:traceback.print_exc();self.clear_dim();_controller.focus_dim_fail_open('overlay paintEvent')
class Overlay(QWidget):
	def __init__(self):
		super().__init__();flags=_qt_window_flag(_Ay)|_qt_window_flag(_Az)|_qt_window_flag('Tool');flags|=_qt_window_flag(_A_);self.setWindowFlags(flags);self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,_B)
		if hasattr(Qt.WidgetAttribute,'WA_ShowWithoutActivating'):self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating,_B)
		if hasattr(Qt.WidgetAttribute,'WA_X11DoNotAcceptFocus'):self.setAttribute(Qt.WidgetAttribute.WA_X11DoNotAcceptFocus,_B)
		no_focus=Qt.FocusPolicy.NoFocus if hasattr(Qt,_B0)else Qt.NoFocus;self.setFocusPolicy(no_focus);self._dragging=_C;self._drag_offset=QPoint();self._resizing=_C;self._resize_start_pos=QPoint();self._resize_start_size=QSize();self._resize_margin=6;self.main_layout=QVBoxLayout(self);self.main_layout.setContentsMargins(0,0,0,0);self.web_text=QTextBrowser();self.web_text.setOpenExternalLinks(_C);self.web_text.setOpenLinks(_C);self.web_text.setReadOnly(_B);self.web_text.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu);self.web_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,_B);self.web_text.setFocusPolicy(no_focus);self.web_text.setFrameShape(QFrame.Shape.NoFrame if hasattr(QFrame,'Shape')else QFrame.NoFrame);self.web_text.setStyleSheet('background: transparent; border: 0;');self.main_layout.addWidget(self.web_text);self.alarm_layer=OverlayAlarmLayer(self);self.drag_handle=QLabel('Drag',self);self.drag_handle.setAlignment(ALIGN_CENTER);self.drag_handle.setFixedSize(56,18);self.drag_handle.setCursor(DRAG_CURSOR);self.drag_handle.setStyleSheet('background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: rgba(255,255,255,0.85); font-size: 10px; font-weight: 600;');self.drag_handle.installEventFilter(self);self.resize_handle=QWidget(self);self.resize_handle.setFixedSize(16,16);self.resize_handle.setCursor(RESIZE_CURSOR);self.resize_handle.setStyleSheet('background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25); border-radius: 4px;');self.resize_handle.installEventFilter(self);self.apply_prefs();self._position_overlay_controls();self.show()
	def apply_prefs(self):conf=get_config();self.fixed_width=conf[_A5];self.max_def_height=conf[_A6];self.move(conf[_A7],conf[_A8]);self.update_geometry()
	def update_geometry(self):self.web_text.setFixedHeight(self.max_def_height);self.setFixedSize(self.fixed_width,self.max_def_height);self._position_overlay_controls()
	def _position_overlay_controls(self):self.alarm_layer.setGeometry(self.rect());self.alarm_layer.raise_();self.drag_handle.move(self._resize_margin,self._resize_margin);self.drag_handle.raise_();self.resize_handle.move(self.width()-self.resize_handle.width()-self._resize_margin,self.height()-self.resize_handle.height()-self._resize_margin);self.resize_handle.raise_()
	def _save_window_geometry(self):
		conf=get_config()
		for(key,value)in((_A7,self.x()),(_A8,self.y()),(_A5,self.width()),(_A6,self.height())):conf[key]=value
		save_config(conf)
	def eventFilter(self,obj,event):
		if obj==self.resize_handle:
			if event.type()==QEvent.Type.MouseButtonPress and event.button()==LEFT_MOUSE_BUTTON:self._resizing=_B;self._resize_start_pos=_event_global_point(event);self._resize_start_size=self.size();self.resize_handle.grabMouse();return _B
			if event.type()==QEvent.Type.MouseMove and self._resizing:delta=_event_global_point(event)-self._resize_start_pos;self.fixed_width=max(200,min(2500,self._resize_start_size.width()+delta.x()));self.max_def_height=max(100,min(2000,self._resize_start_size.height()+delta.y()));self.update_geometry();return _B
			if event.type()==QEvent.Type.MouseButtonRelease and self._resizing:self._resizing=_C;self.resize_handle.releaseMouse();self._save_window_geometry();return _B
		if obj==self.drag_handle:
			if event.type()==QEvent.Type.MouseButtonPress and event.button()==LEFT_MOUSE_BUTTON:self._dragging=_B;self._drag_offset=_event_global_point(event)-self.frameGeometry().topLeft();self.drag_handle.grabMouse();return _B
			if event.type()==QEvent.Type.MouseMove and self._dragging:self.move(_event_global_point(event)-self._drag_offset);return _B
			if event.type()==QEvent.Type.MouseButtonRelease and self._dragging:self._dragging=_C;self.drag_handle.releaseMouse();self._save_window_geometry();return _B
		return super().eventFilter(obj,event)
	def resizeEvent(self,event):super().resizeEvent(event);self._position_overlay_controls()
	def set_content(self,html_body,style_options):alpha=style_options[_K]/1e2;style=f"""
        <style>
        html, body {{ background: transparent !important; margin: 0; padding: 0; color: white; font-family: "Segoe UI Variable", "Segoe UI", "Noto Sans", "Helvetica Neue", Arial, sans-serif; height: 100%; width: 100%; overflow: hidden; }}
        .box {{ background: rgba(12,12,12,{alpha}); border: 2px solid rgba(255,255,255,0.15); border-radius: 18px; height: 100%; box-sizing: border-box; }}
        .content-area {{ width: 100%; height: 100%; padding: 18px 20px; box-sizing: border-box; overflow-y: auto; }}
        .content-area.compact {{ padding: 12px 14px; }}
        .content-shell {{ min-height: 100%; display: flex; align-items: center; justify-content: center; }}
        .content-stack {{ width: 100%; max-width: 640px; margin: 0 auto; text-align: center; }}
        .main-word {{ font-size: {style_options[_o]}px; font-weight: 700; color: {style_options[_H]}; line-height: 1.08; letter-spacing: 0.01em; margin: 0 0 12px; text-align: center; }}
        .content-area.compact .main-word {{ margin-bottom: 8px; }}
        .answer-word {{ font-size: {style_options[_p]}px; font-weight: 600; color: {style_options[_I]}; line-height: 1.24; letter-spacing: 0.015em; margin: 0 0 18px; text-align: center; }}
        .content-area.compact .answer-word {{ margin-bottom: 12px; }}
        .main-word, .answer-word, .example-de, .example-en {{ background: transparent; border: 0; outline: none; box-shadow: none; text-shadow: none; -webkit-text-stroke: 0; }}
        .example-pair {{ max-width: 580px; margin: 14px auto 0; padding: 0; border: none; border-radius: 0; background: transparent; text-align: left; }}
        .content-area.compact .example-pair {{ margin-top: 8px; padding: 0; }}
        .example-de {{ font-size: {style_options[_i]}px; color: white; line-height: 1.45; margin-bottom: 6px; font-weight: 600; }}
        .example-en {{ font-size: {style_options[_i]}px; color: {style_options[_J]}; line-height: 1.45; opacity: 0.95; }}
        .status-line {{ font-size: 0.8em; opacity: 0.75; margin-top: 12px; text-align: left; }}
        hr {{ border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 8px 0; width: 100%; }}
        </style>
        """;content_class='content-area compact'if style_options.get(_V)==_AF else'content-area';self.update_geometry();media_dir=mw.col.media.dir()+os.path.sep;base_url=QUrl.fromLocalFile(media_dir);self.web_text.document().setBaseUrl(base_url);self.web_text.setHtml(f"<html><head><base href='{base_url.toString()}'>{style}</head><body><div class='box'><div class='{content_class}'><div class='content-shell'><div class='content-stack'>{html_body}</div></div></div></div></body></html>")
	def set_focus_alarm_intensity(self,intensity,phase=_M,stage_progress=_D,anim_time=_D):self.alarm_layer.set_state(intensity,phase,stage_progress,anim_time)
class ConfigDialog(QDialog):
	def __init__(self):super().__init__(mw);self.setWindowTitle('Overlay Preferences');self.resize(900,600);self.conf=get_config();self.all_decks=self._all_deck_names();self.init_ui()
	def _all_deck_names(self):
		try:items=mw.col.decks.all_names_and_ids()
		except Exception:return[]
		names=[]
		for item in items or[]:
			if isinstance(item,dict):name=item.get(_AW,'')
			else:name=getattr(item,_AW,'')
			name=str(name or'').strip()
			if name:names.append(name)
		return sorted(names)
	def init_ui(self):layout=QVBoxLayout(self);tabs=QTabWidget();self._build_mapping_tab(tabs);self._build_visuals_tab(tabs);self._build_theme_tab(tabs);self._build_hotkeys_tab(tabs);layout.addWidget(tabs);button=QPushButton('Save & Apply Settings');button.clicked.connect(self.save_all);layout.addWidget(button)
	def _build_mapping_tab(self,tabs):
		widget=QWidget();outer=QVBoxLayout(widget);self.table=QTableWidget(0,len(DECK_MAP_FIELDS)+1);self.table.setHorizontalHeaderLabels(['Deck']+[label for(label,_)in DECK_MAP_FIELDS]);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
		for mapping in self.conf.get(_l,[]):self._add_row(mapping)
		buttons=QHBoxLayout();add_button=QPushButton('+ Add Mapping');add_button.clicked.connect(lambda:self._add_row({}));remove_button=QPushButton(_B1);remove_button.clicked.connect(lambda:self.table.removeRow(self.table.currentRow()));buttons.addWidget(add_button);buttons.addWidget(remove_button);outer.addWidget(self.table);outer.addLayout(buttons);tabs.addTab(widget,'Decks Mapping')
	def _build_visuals_tab(self,tabs):
		widget=QWidget();form=QFormLayout(widget);self.w=self._spin_box(200,2500,self.conf[_A5]);self.h=self._spin_box(100,2000,self.conf[_A6]);self.op=self._slider(self.conf[_K]);self.c_w=QLineEdit(self.conf[_H]);self.c_p=QLineEdit(self.conf[_I]);self.c_s=QLineEdit(self.conf[_J]);self.fs_word=self._spin_box(20,160,_normalize_font_size(self.conf.get(_o,42),42,20,160));self.fs_translation=self._spin_box(12,120,_normalize_font_size(self.conf.get(_p,26),26,12,120));self.fs_example=self._spin_box(10,96,_normalize_font_size(self.conf.get(_i,18),18,10,96));self.grade_mode=QComboBox()
		for(text,value)in(('Use Grade Keys To Flip (Recommended)',_e),('Ignore Grade Keys On Question',_Ad),('Reveal Then Auto-Grade',_U)):self.grade_mode.addItem(text,value)
		index=self.grade_mode.findData(_normalize_grade_from_question_mode(self.conf.get(_a,_e)));self.grade_mode.setCurrentIndex(index if index>=0 else 0);self.fd_enable=QCheckBox();self.fd_enable.setChecked(bool(self.conf.get(_S,_C)));self.fd_idle_sec=self._float_box(.5,6e2,self.conf.get(_L),DEFAULT_CONFIG[_L]);self.fd_warning_sec=self._float_box(.1,6e2,self.conf.get(_b),DEFAULT_CONFIG[_b]);self.fd_punish_sec=self._float_box(.1,6e2,self.conf.get(_c),DEFAULT_CONFIG[_c]);self.fd_lockdown_sec=self._float_box(.1,6e2,self.conf.get(_d),DEFAULT_CONFIG[_d]);self.fd_warning_opacity=self._slider(int(_clamp_float(self.conf.get(_t),DEFAULT_CONFIG[_t],0,100)));self.fd_punish_opacity=self._slider(int(_clamp_float(self.conf.get(_u),DEFAULT_CONFIG[_u],0,100)));self.fd_max_opacity=self._slider(int(_clamp_float(self.conf.get(_v),DEFAULT_CONFIG[_v],0,100)));self.fd_curve=QComboBox()
		for(text,value)in(('Quadratic (Default)',_AN),('Linear',_Ae),('Cubic',_Af)):self.fd_curve.addItem(text,value)
		curve_index=self.fd_curve.findData(_normalize_focus_curve(self.conf.get(_T,DEFAULT_CONFIG[_T])));self.fd_curve.setCurrentIndex(curve_index if curve_index>=0 else 0);self.fd_question_only=QCheckBox();self.fd_question_only.setChecked(bool(self.conf.get(_AD,_C)));self.fd_safe_padding=self._spin_box(0,140,int(_clamp_float(self.conf.get(_w),DEFAULT_CONFIG[_w],0,140)));self.fd_safe_feather=self._spin_box(0,180,int(_clamp_float(self.conf.get(_x),DEFAULT_CONFIG[_x],0,180)));self.fd_warning_text=QLineEdit(str(self.conf.get(_j,DEFAULT_CONFIG[_j])or DEFAULT_CONFIG[_j]));self.fd_warning_subtext=QLineEdit(str(self.conf.get(_k,DEFAULT_CONFIG[_k])or DEFAULT_CONFIG[_k]));self.fd_warning_style=QComboBox()
		for(text,value)in(('Shake + Glow',_AV),('Pulse','pulse')):self.fd_warning_style.addItem(text,value)
		style_index=self.fd_warning_style.findData(str(self.conf.get(_q,DEFAULT_CONFIG[_q])).strip().lower());self.fd_warning_style.setCurrentIndex(style_index if style_index>=0 else 0);self.fd_warning_font_px=self._spin_box(14,84,int(_clamp_float(self.conf.get(_y),DEFAULT_CONFIG[_y],14,84)));self.fd_replay_reset_mode=QComboBox()
		for(text,value)in(('Partial Relief (Recommended)',_AE),('Full Reset',_f),('No Relief',_A2)):self.fd_replay_reset_mode.addItem(text,value)
		replay_index=self.fd_replay_reset_mode.findData(_normalize_replay_reset_mode(self.conf.get(_W,DEFAULT_CONFIG[_W])));self.fd_replay_reset_mode.setCurrentIndex(replay_index if replay_index>=0 else 0);self.fd_partial_reset_sec=self._float_box(.2,3e1,self.conf.get(_z),DEFAULT_CONFIG[_z])
		for(label,widget_value)in(('Width:',self.w),('Answer Box Height:',self.h),('Opacity %:',self.op),('Word Color:',self.c_w),('Translation Color:',self.c_p),('Example Color:',self.c_s),('Word Font Size:',self.fs_word),('Translation Font Size:',self.fs_translation),('Example Font Size:',self.fs_example),('Question-Side Grade Keys:',self.grade_mode),('Focus Dim Enabled:',self.fd_enable),('Idle Grace (sec):',self.fd_idle_sec),('Warning Duration (sec):',self.fd_warning_sec),('Punish Duration (sec):',self.fd_punish_sec),('Lockdown Duration (sec):',self.fd_lockdown_sec),('Warning Opacity:',self.fd_warning_opacity),('Punish Opacity:',self.fd_punish_opacity),('Focus Dim Max Opacity:',self.fd_max_opacity),('Punish Curve:',self.fd_curve),('Focus Dim Question Only:',self.fd_question_only),('Safe Zone Padding:',self.fd_safe_padding),('Safe Zone Feather:',self.fd_safe_feather),('Warning Text:',self.fd_warning_text),('Warning Subtext:',self.fd_warning_subtext),('Warning Style:',self.fd_warning_style),('Warning Font (px):',self.fd_warning_font_px),('Replay Reset Mode:',self.fd_replay_reset_mode),('Partial Reset Relief (sec):',self.fd_partial_reset_sec)):form.addRow(label,widget_value)
		note=QLabel('Text mode: mapped note fields are rendered as plain text (HTML is escaped).');note.setWordWrap(_B);form.addRow('',note);tabs.addTab(widget,'Visuals')
	def _build_theme_tab(self,tabs):
		widget=QWidget();outer=QVBoxLayout(widget);self.theme_table=QTableWidget(0,6);self.theme_table.setHorizontalHeaderLabels(['Deck','Word Color','Translation Color','Example Color','Opacity','Mode']);self.theme_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
		for theme in self.conf.get(_m,[]):self._add_theme_row(theme)
		buttons=QHBoxLayout();add_button=QPushButton('+ Add Theme');add_button.clicked.connect(lambda:self._add_theme_row({}));remove_button=QPushButton(_B1);remove_button.clicked.connect(lambda:self.theme_table.removeRow(self.theme_table.currentRow()));buttons.addWidget(add_button);buttons.addWidget(remove_button);outer.addWidget(self.theme_table);outer.addLayout(buttons);tabs.addTab(widget,'Per-Deck Theme')
	def _build_hotkeys_tab(self,tabs):
		widget=QWidget();form=QFormLayout(widget);self.hk_widgets={}
		for key in HOTKEY_KEYS:recorder=HotkeyRecorder(self.conf.get(key,''));self.hk_widgets[key]=recorder;form.addRow(key.replace('key_','').title()+':',recorder)
		tabs.addTab(widget,'Hotkeys')
	def _spin_box(self,minimum,maximum,value):box=QSpinBox();box.setRange(minimum,maximum);box.setValue(value);return box
	def _float_box(self,minimum,maximum,value,default):box=QDoubleSpinBox();box.setRange(minimum,maximum);box.setDecimals(1);box.setSingleStep(.1);box.setValue(_clamp_float(value,default,minimum,maximum));return box
	def _slider(self,value):slider=QSlider(Qt.Orientation.Horizontal);slider.setRange(0,100);slider.setValue(value);return slider
	def _add_row(self,data):
		row=self.table.rowCount();self.table.insertRow(row);deck_cb=QComboBox();deck_cb.addItems([_AH]+self.all_decks);combos=[QComboBox()for _ in DECK_MAP_FIELDS]
		def update_fields():
			fields=self._get_fields(deck_cb.currentText())if deck_cb.currentText()!=_AH else[]
			for combo in combos:
				current=combo.currentText();combo.clear();combo.addItems(['']+fields)
				if current in fields:combo.setCurrentText(current)
		deck_cb.currentIndexChanged.connect(update_fields);self.table.setCellWidget(row,0,deck_cb)
		for(index,combo)in enumerate(combos,start=1):self.table.setCellWidget(row,index,combo)
		deck_name=data.get(_Y,'')
		if data.get(_R)is not _A:deck_name=_controller.deck_name_from_id(data[_R])or deck_name
		if deck_name:
			deck_cb.setCurrentText(deck_name);update_fields()
			for(index,(_,field_key))in enumerate(DECK_MAP_FIELDS):
				if data.get(field_key):combos[index].setCurrentText(data[field_key])
	def _add_theme_row(self,data):
		A='Default';normalized=_controller.normalize_deck_theme_entry(data)or _controller.normalize_deck_theme_entry({});row=self.theme_table.rowCount();self.theme_table.insertRow(row);deck_cb=QComboBox();deck_cb.addItems([_AH]+self.all_decks);deck_name=normalized.get(_Y,'')
		if normalized.get(_R)is not _A:deck_name=_controller.deck_name_from_id(normalized[_R])or deck_name
		if deck_name:deck_cb.setCurrentText(deck_name)
		opacity_spin=QSpinBox();opacity_spin.setRange(-1,100);opacity_spin.setSpecialValueText(A);opacity_spin.setValue(_normalize_opacity(normalized.get(_K,-1)));mode_cb=QComboBox();mode_cb.addItems([A,_f,_AF])
		if normalized.get(_V)in(_f,_AF):mode_cb.setCurrentText(normalized[_V])
		for(column,widget_value)in enumerate([deck_cb,QLineEdit(normalized.get(_H,'')),QLineEdit(normalized.get(_I,'')),QLineEdit(normalized.get(_J,'')),opacity_spin,mode_cb]):self.theme_table.setCellWidget(row,column,widget_value)
	def _deck_ids_for_name(self,deck_name):
		root_name=str(deck_name or'').strip()
		if not root_name:return[]
		deck_ids=[]
		try:all_names=self._all_deck_names()
		except Exception:return[]
		for name in all_names:
			if name!=root_name and not name.startswith(root_name+'::'):continue
			try:did=int(mw.col.decks.id(name))
			except Exception:continue
			if did not in deck_ids:deck_ids.append(did)
		return deck_ids
	def _get_fields(self,deck_name):
		try:
			deck_ids=self._deck_ids_for_name(deck_name)
			if not deck_ids:return[]
			if len(deck_ids)==1:mids=mw.col.db.list('select distinct n.mid from cards c join notes n on c.nid = n.id where c.did = ?',deck_ids[0])
			else:
				placeholders=','.join('?'for _ in deck_ids);sql=f'select distinct n.mid from cards c join notes n on c.nid = n.id where c.did in ({placeholders})'
				mids=mw.col.db.list(sql,*deck_ids)
			shared=_A
			for mid in mids:
				model=mw.col.models.get(mid)
				if not model:continue
				field_names={fld[_AW]for fld in model.get('flds',[])};shared=field_names if shared is _A else shared.intersection(field_names)
			return sorted(shared or[])
		except Exception:return[]
	def save_all(self):
		final=get_config();final[_l]=[]
		for row in range(self.table.rowCount()):
			deck_cb=self.table.cellWidget(row,0)
			deck_name=(deck_cb.currentText().strip()if deck_cb else'')
			if not deck_name or deck_name==_AH:continue
			try:deck_id=int(mw.col.decks.id(deck_name))
			except Exception:deck_id=_A
			mapping={_R:deck_id,_Y:deck_name};has_mapped_field=_C
			for(column,(_,field_key))in enumerate(DECK_MAP_FIELDS,start=1):
				field_combo=self.table.cellWidget(row,column);selected=field_combo.currentText().strip()if field_combo and hasattr(field_combo,'currentText')else''
				if selected:mapping[field_key]=selected;has_mapped_field=_B
			if has_mapped_field:final[_l].append(mapping)
		final[_m]=[]
		for row in range(self.theme_table.rowCount()):
			deck_cb=self.theme_table.cellWidget(row,0)
			if not deck_cb or deck_cb.currentText()==_AH:continue
			deck_name=deck_cb.currentText()
			try:deck_id=int(mw.col.decks.id(deck_name))
			except Exception:deck_id=_A
			mode=self.theme_table.cellWidget(row,5).currentText().strip().lower();final[_m].append({_R:deck_id,_Y:deck_name,_H:_normalize_optional_hex_color(self.theme_table.cellWidget(row,1).text().strip()),_I:_normalize_optional_hex_color(self.theme_table.cellWidget(row,2).text().strip()),_J:_normalize_optional_hex_color(self.theme_table.cellWidget(row,3).text().strip()),_K:self.theme_table.cellWidget(row,4).value(),_V:''if mode=='default'else mode})
		warning_opacity=int(self.fd_warning_opacity.value());punish_opacity=max(warning_opacity,int(self.fd_punish_opacity.value()));max_opacity=max(punish_opacity,int(self.fd_max_opacity.value()));final.update({_A5:self.w.value(),_A6:self.h.value(),_K:self.op.value(),_H:_normalize_hex_color(self.c_w.text(),DEFAULT_CONFIG[_H]),_I:_normalize_hex_color(self.c_p.text(),DEFAULT_CONFIG[_I]),_J:_normalize_hex_color(self.c_s.text(),DEFAULT_CONFIG[_J]),_o:self.fs_word.value(),_p:self.fs_translation.value(),_i:self.fs_example.value(),_a:_normalize_grade_from_question_mode(self.grade_mode.currentData(),_e),_S:self.fd_enable.isChecked(),_L:float(self.fd_idle_sec.value()),_b:float(self.fd_warning_sec.value()),_c:float(self.fd_punish_sec.value()),_d:float(self.fd_lockdown_sec.value()),_s:_A0,_t:warning_opacity,_u:punish_opacity,_v:max_opacity,_T:_normalize_focus_curve(self.fd_curve.currentData(),DEFAULT_CONFIG[_T]),_AD:self.fd_question_only.isChecked(),_w:self.fd_safe_padding.value(),_x:self.fd_safe_feather.value(),_j:self.fd_warning_text.text(),_k:self.fd_warning_subtext.text(),_q:self.fd_warning_style.currentData(),_y:self.fd_warning_font_px.value(),_W:_normalize_replay_reset_mode(self.fd_replay_reset_mode.currentData(),DEFAULT_CONFIG[_W]),_z:self.fd_partial_reset_sec.value(),_AM:max(.1,float(self.fd_warning_sec.value())),_AX:self.fd_replay_reset_mode.currentData()!=_A2,_Al:_B,_Am:self.fd_warning_text.text(),_A7:final.get(_A7,50),_A8:final.get(_A8,50)})
		for(key,recorder)in self.hk_widgets.items():final[key]=_normalize_hotkey(recorder.current_key)
		flip_combo=_normalize_hotkey(final.get(_n,''))
		if flip_combo and any(flip_combo==_normalize_hotkey(final.get(key,''))for key in GRADE_HOTKEY_KEYS)and _normalize_grade_from_question_mode(final.get(_a))==_Ad:final[_a]=_e
		issues=_controller.validate_hotkeys(final)
		if issues:tooltip(f"Fix hotkeys before saving: {'; '.join(issues[:3])}",period=5000);return
		save_config(final);tooltip('Saved!',period=1500)
		try:
			addon_key=_controller.addon_config_key();persisted=mw.addonManager.getConfig(addon_key)
			persisted_maps=persisted.get(_l,[])if isinstance(persisted,dict)else[]
			meta_count='n/a'
			try:
				meta_getter=getattr(mw.addonManager,'addonMeta',_A)
				if meta_getter:
					meta_cfg=(meta_getter(addon_key)or{}).get('config')
					if isinstance(meta_cfg,dict):meta_count=len(meta_cfg.get(_l,[])or[])
			except Exception as meta_exc:_log(f"Post-save addonMeta read failed: {meta_exc}")
			_log(f"Saved deck_maps count: ui={len(final.get(_l,[]))}, persisted={len(persisted_maps)}, meta={meta_count}, key={addon_key}")
			if len(persisted_maps)!=len(final.get(_l,[])):_log(f"Persisted deck_maps payload: {persisted_maps}")
		except Exception as exc:_log(f"Post-save deck_maps verification failed: {exc}")
		if _controller.overlay:_controller.overlay.apply_prefs();_controller.reconcile_overlay_visibility('config_saved',force_show=not _controller.overlay_user_hidden)
		_controller.start_global_listener(show_feedback=_B,toggle_only=not _controller.runtime_enabled);_controller.refresh_focus_dim_controller(force_rebuild=_B);_controller.update_overlay();self.accept()
class OverlayController:
	def __init__(self):self.config_cache=_A;self.overlay=_A;self.init_overlay_timer=_A;self.transition_watchdog_timer=_A;self.overlay_refresh_timer=_A;self.focus_dim_timer=_A;self.current_listener=_A;self.main_window_event_filter=_A;self.focus_dim_overlays=[];self.app_state_hooks_connected=_C;self.focus_dim_screen_hooks_connected=_C;self.listener_hotkey_signature=_A;self.listener_toggle_only=_A;self.missing_pynput_warned=_C;self.addon_active=_C;self.runtime_enabled=_B;self.overlay_user_hidden=_C;self.overlay_auto_hidden_by_window=_C;self.overlay_last_screen_key=_A;self.overlay_last_visibility_signature=_A;self.overlay_visibility_reconcile_pending=_C;self.overlay_visibility_reconcile_force_show=_C;self.overlay_visibility_reconcile_reason='';self.last_overlay_render_key=_A;self.last_overlay_style_key=_A;self.review_state=ReviewUiState.IDLE;self.last_card_id=_A;self.last_hotkey_captured='';self.last_command_attempted='';self.last_command_result='';self.pending=TransitionState();self.last_command_time={};self.last_external_overlay_refresh_at=_D;self.transition_watchdog_last_snapshot=_A;self.focus=FocusDimState();self.refresh=RefreshState();self.grade_sound_players={};self.grade_sound_outputs={};self.grade_sound_initialized=_C;self.grade_sound_last_command='';self.grade_sound_last_source='';self.grade_sound_last_played_at=_D;self.pay_attention_player=_A;self.pay_attention_audio_output=_A;self.pay_attention_timer=_A;self.pay_attention_sound_path='';self.pay_attention_active=_C;self.pay_attention_warning_issued=_C;self.debug_refresh_requests=0;self.debug_refresh_runs=0;self.debug_force_refresh_runs=0;self.debug_visibility_reconciles=0;self.debug_watchdog_ticks=0;self.debug_watchdog_state_changes=0;self.debug_last_counter_log_at=_D
	def maybe_log_debug_counters(self):
		conf=self.get_config_view()
		if not conf or not conf.get(_AL):return
		now=_now()
		if now-self.debug_last_counter_log_at<5.:return
		self.debug_last_counter_log_at=now;_log('refresh_req={0}, refresh_run={1}, force_refresh={2}, reconcile={3}, watchdog={4}, watchdog_changes={5}'.format(self.debug_refresh_requests,self.debug_refresh_runs,self.debug_force_refresh_runs,self.debug_visibility_reconciles,self.debug_watchdog_ticks,self.debug_watchdog_state_changes))
	def default_config(self):return copy.deepcopy(DEFAULT_CONFIG)
	def addon_config_key(self):
		try:
			key=mw.addonManager.addonFromModule(__name__)
			return key or __name__
		except Exception as exc:_log(f"addonFromModule failed; falling back to __name__: {exc}");return __name__
	def read_meta_config(self,addon_key):
		try:
			meta_getter=getattr(mw.addonManager,'addonMeta',_A)
			if not meta_getter:return _A
			meta=meta_getter(addon_key)or{}
			config=meta.get('config')
			return config if isinstance(config,dict)else _A
		except Exception as exc:_log(f"addonMeta config read failed: {exc}");return _A
	def normalize_deck_mapping_entry(self,mapping):
		if not isinstance(mapping,dict):return
		deck_id=mapping.get(_R)
		try:deck_id=int(deck_id)if deck_id is not _A else _A
		except Exception:deck_id=_A
		normalized={_R:deck_id,_Y:mapping.get(_Y,'')};has_mapped_field=_C
		for(_,field_key)in DECK_MAP_FIELDS:
			value=mapping.get(field_key,'')
			if not value and LEGACY_FIELD_MAP.get(field_key):value=mapping.get(LEGACY_FIELD_MAP[field_key],'')
			value=str(value or'').strip()
			if value:normalized[field_key]=value;has_mapped_field=_B
		return normalized if has_mapped_field else _A
	def normalize_deck_maps(self,deck_maps):return[mapped for mapped in(self.normalize_deck_mapping_entry(entry)for entry in deck_maps or[])if mapped]if isinstance(deck_maps,list)else[]
	def normalize_deck_theme_entry(self,theme):
		if not isinstance(theme,dict):return
		mode=str(theme.get(_V,'')).strip().lower()
		if mode not in THEME_MODE_VALUES:mode=''
		deck_id=theme.get(_R)
		try:deck_id=int(deck_id)if deck_id is not _A else _A
		except Exception:deck_id=_A
		return{_R:deck_id,_Y:theme.get(_Y,''),_H:_normalize_optional_hex_color(theme.get(_H,'')),_I:_normalize_optional_hex_color(theme.get(_I,'')),_J:_normalize_optional_hex_color(theme.get(_J,'')),_K:_normalize_opacity(theme.get(_K,-1)),_V:mode}
	def normalize_deck_themes(self,deck_themes):return[mapped for mapped in(self.normalize_deck_theme_entry(entry)for entry in deck_themes or[])if mapped]if isinstance(deck_themes,list)else[]
	def normalize_focus_dim_timing_values(self,conf,raw=_A):
		raw_is_dict=isinstance(raw,dict);mode=str(conf.get(_s,DEFAULT_CONFIG[_s])or'').strip().lower();idle_sec=_clamp_float(conf.get(_L),DEFAULT_CONFIG[_L],.5,36e2);warning_sec=_clamp_float(conf.get(_b),DEFAULT_CONFIG[_b],.1,36e2);punish_sec=_clamp_float(conf.get(_c),DEFAULT_CONFIG[_c],.1,36e2);lockdown_sec=_clamp_float(conf.get(_d),DEFAULT_CONFIG[_d],.1,36e2)
		if raw_is_dict and _s not in raw:legacy_warning_start=warning_sec;legacy_punish_start=max(legacy_warning_start+.1,punish_sec);legacy_lockdown_start=max(legacy_punish_start+.1,lockdown_sec);idle_sec=_clamp_float(raw.get(_L,legacy_warning_start),DEFAULT_CONFIG[_L],.5,36e2);warning_sec=max(.1,legacy_punish_start-legacy_warning_start);punish_sec=max(.1,legacy_lockdown_start-legacy_punish_start);lockdown_sec=_clamp_float(raw.get(_AM,punish_sec),punish_sec,.1,36e2);mode=_A0
		elif mode!=_A0:mode=_A0
		conf.update({_L:idle_sec,_b:warning_sec,_c:punish_sec,_d:lockdown_sec,_AM:warning_sec,_s:mode or _A0})
	def _normalized_config(self,conf,raw=_A):
		normalized=self.default_config()
		if isinstance(conf,dict):normalized.update(conf)
		normalized[_l]=self.normalize_deck_maps(normalized.get(_l));normalized[_m]=self.normalize_deck_themes(normalized.get(_m));normalized[_H]=_normalize_hex_color(normalized.get(_H),DEFAULT_CONFIG[_H]);normalized[_I]=_normalize_hex_color(normalized.get(_I),DEFAULT_CONFIG[_I]);normalized[_J]=_normalize_hex_color(normalized.get(_J),DEFAULT_CONFIG[_J]);normalized[_a]=_normalize_grade_from_question_mode(normalized.get(_a),DEFAULT_CONFIG[_a]);normalized[_T]=_normalize_focus_curve(normalized.get(_T),DEFAULT_CONFIG[_T]);normalized[_W]=_normalize_replay_reset_mode(normalized.get(_W),DEFAULT_CONFIG[_W]);self.normalize_focus_dim_timing_values(normalized,raw if isinstance(raw,dict)else _A);return normalized
	def get_config(self):
		if self.config_cache is _A:
			addon_key=self.addon_config_key();raw=mw.addonManager.getConfig(addon_key);_log(f"Loading config with key: {addon_key}")
			meta_cfg=self.read_meta_config(addon_key)
			if(not isinstance(raw,dict)or not raw)and isinstance(meta_cfg,dict)and meta_cfg:_log(f"Using addonMeta fallback config for key: {addon_key}");raw=meta_cfg
			if addon_key!=__name__ and(not isinstance(raw,dict)or not raw):
				try:
					legacy=mw.addonManager.getConfig(__name__)
					if isinstance(legacy,dict)and legacy:_log(f"Migrating config from legacy key {__name__} -> {addon_key}");raw=legacy;mw.addonManager.writeConfig(addon_key,legacy)
				except Exception as exc:_log(f"Legacy config migration check failed: {exc}")
			self.config_cache=self._normalized_config(raw,raw)
			try:_log(f"Loaded deck_maps count: {len(self.config_cache.get(_l,[]))}")
			except Exception:pass
		return copy.deepcopy(self.config_cache)
	def get_config_view(self):
		if self.config_cache is _A:self.get_config()
		return self.config_cache
	def save_config(self,conf):
		addon_key=self.addon_config_key();self.config_cache=self._normalized_config(conf)
		try:serialized=json.dumps(self.config_cache);_log(f"Saving config with key: {addon_key}, bytes={len(serialized)}, deck_maps={len(self.config_cache.get(_l,[])or[])}")
		except Exception as exc:_log(f"Config JSON serialization failed before write: {exc}")
		mw.addonManager.writeConfig(addon_key,self.config_cache)
	def compute_hotkey_signature(self,conf):return tuple((key,_normalize_hotkey(conf.get(key,'')))for key in HOTKEY_KEYS)
	def validate_hotkey_combo(self,combo):
		if not combo:return _C
		if not HAS_PYNPUT:return _B
		try:keyboard.HotKey.parse(combo);return _B
		except Exception:return _C
	def validate_hotkeys(self,conf):
		seen={};issues=[];shared_flip_grades=[];shared_issue=_C
		for key in HOTKEY_KEYS:
			label=HOTKEY_LABELS[key];combo=_normalize_hotkey(conf.get(key,''))
			if not combo:issues.append(f"{label} is empty");continue
			if not self.validate_hotkey_combo(combo):issues.append(f"{label} is invalid ({combo})");continue
			variants=_hotkey_registration_variants(combo)
			if not variants:issues.append(f"{label} is invalid ({combo})");continue
			duplicate=_C
			for variant in variants:
				other=seen.get(variant)
				if other is _A:continue
				allow=key==_n and other in GRADE_HOTKEY_KEYS or other==_n and key in GRADE_HOTKEY_KEYS
				if allow:
					grade_key=key if key in GRADE_HOTKEY_KEYS else other
					if grade_key not in shared_flip_grades:shared_flip_grades.append(grade_key)
					if len(shared_flip_grades)>1 and not shared_issue:issues.append(f"Flip can share with only one grade key (currently {', '.join(HOTKEY_LABELS[g]for g in shared_flip_grades)})");shared_issue=_B
					continue
				issues.append(f"{label} duplicates {HOTKEY_LABELS[other]} ({combo})");duplicate=_B;break
			if duplicate:continue
			for variant in variants:seen[variant]=key
		return issues
	def deck_name_from_id(self,deck_id):
		try:deck=mw.col.decks.get(int(deck_id));return deck.get(_AW,'')if deck else''
		except Exception:return''
	def card_deck_candidates(self,card):
		deck_ids=[];deck_names=[]
		for deck_id in(getattr(card,'odid',_A),getattr(card,'did',_A)):
			if deck_id in(_A,0):continue
			try:numeric_id=int(deck_id)
			except Exception:continue
			if numeric_id not in deck_ids:deck_ids.append(numeric_id)
			try:
				deck=mw.col.decks.get(numeric_id)or{};deck_name=deck.get(_AW,'')
				if deck_name and deck_name not in deck_names:deck_names.append(deck_name)
			except Exception:pass
		return deck_ids,deck_names
	def deck_parent_candidates(self,deck_names):
		parent_ids=[];parent_names=[]
		for deck_name in deck_names:
			parts=str(deck_name or'').split('::')
			while len(parts)>1:
				parts=parts[:-1];parent_name='::'.join(parts)
				if not parent_name:continue
				if parent_name not in parent_names:parent_names.append(parent_name)
				try:parent_id=int(mw.col.decks.id(parent_name))
				except Exception:continue
				if parent_id not in parent_ids:parent_ids.append(parent_id)
		return parent_ids,parent_names
	def deck_entry_matches(self,entry,deck_ids,deck_names):
		mapped_id=entry.get(_R)
		if mapped_id is not _A:
			try:
				if int(mapped_id)in deck_ids:return _B
			except Exception:pass
		mapped_name=str(entry.get(_Y,'')or'')
		return bool(mapped_name)and mapped_name in deck_names
	def deck_map_for_card(self,conf,card):
		deck_ids,deck_names=self.card_deck_candidates(card)
		for mapping in conf.get(_l,[]):
			if self.deck_entry_matches(mapping,deck_ids,deck_names):return mapping
		parent_ids,parent_names=self.deck_parent_candidates(deck_names)
		for mapping in conf.get(_l,[]):
			if self.deck_entry_matches(mapping,parent_ids,parent_names):return mapping
	def deck_theme_for_card(self,conf,card):
		deck_ids,deck_names=self.card_deck_candidates(card)
		for theme in conf.get(_m,[]):
			if self.deck_entry_matches(theme,deck_ids,deck_names):return theme
		parent_ids,parent_names=self.deck_parent_candidates(deck_names)
		for theme in conf.get(_m,[]):
			if self.deck_entry_matches(theme,parent_ids,parent_names):return theme
	def effective_style(self,conf,deck_theme):
		style={_H:_normalize_hex_color(conf.get(_H),DEFAULT_CONFIG[_H]),_I:_normalize_hex_color(conf.get(_I),DEFAULT_CONFIG[_I]),_J:_normalize_hex_color(conf.get(_J),DEFAULT_CONFIG[_J]),_K:_normalize_opacity(conf.get(_K,90),default=90),_o:_normalize_font_size(conf.get(_o,42),42,20,160),_p:_normalize_font_size(conf.get(_p,26),26,12,120),_i:_normalize_font_size(conf.get(_i,18),18,10,96),_V:_f}
		if not deck_theme:return style
		for key in(_H,_I,_J):
			value=_normalize_optional_hex_color(deck_theme.get(key,''))
			if value:style[key]=value
		theme_opacity=_normalize_opacity(deck_theme.get(_K,-1))
		if theme_opacity>=0:style[_K]=theme_opacity
		if str(deck_theme.get(_V,'')).strip().lower()in(_f,_AF):style[_V]=str(deck_theme[_V]).strip().lower()
		return style
	def safe_text_field(self,note,field_name):
		if not field_name or field_name not in note:return''
		return html.escape(note[field_name]or'',quote=_C).replace('\n','<br>')
	def build_example_pair(self,german_text,english_text):
		if not german_text and not english_text:return''
		parts=["<div class='example-pair'>"]
		if german_text:parts.append(f"<div class='example-de'>{german_text}</div>")
		if english_text:parts.append(f"<div class='example-en'>{english_text}</div>")
		parts.append('</div>');return''.join(parts)
	def is_main_window_minimized(self):
		try:
			if not mw.isVisible():return _B
			return bool(int(mw.windowState())&int(_qt_window_flag('WindowMinimized')))
		except Exception:return _C
	def ensure_overlay_within_visible_screen(self):
		if not self.overlay:return
		app=QApplication.instance();screens=app.screens()if app else[]
		if not screens:return
		frame=self.overlay.frameGeometry();target_screen=next((screen for screen in screens if screen.availableGeometry().intersects(frame)),_A)
		if target_screen is _A:
			try:target_screen=app.screenAt(mw.frameGeometry().center())if hasattr(app,'screenAt')else _A
			except Exception:target_screen=_A
		target_screen=target_screen or app.primaryScreen()or screens[0];available=target_screen.availableGeometry();width=max(1,self.overlay.width());height=max(1,self.overlay.height());current=self.overlay.pos();next_x=min(max(current.x(),available.x()),available.x()+max(0,available.width()-width));next_y=min(max(current.y(),available.y()),available.y()+max(0,available.height()-height))
		if next_x!=current.x()or next_y!=current.y():
			self.overlay.move(next_x,next_y)
			try:self.overlay._save_window_geometry()
			except Exception:pass
	def overlay_screen_key(self):
		app=QApplication.instance();screens=app.screens()if app else[]
		if not screens:return
		target_screen=_A
		if self.overlay:frame=self.overlay.frameGeometry();target_screen=next((screen for screen in screens if screen.availableGeometry().intersects(frame)),_A)
		if target_screen is _A:
			try:target_screen=app.screenAt(mw.frameGeometry().center())if hasattr(app,'screenAt')else _A
			except Exception:target_screen=_A
		target_screen=target_screen or app.primaryScreen()or screens[0];available=target_screen.availableGeometry()
		try:name=target_screen.name()
		except Exception:name=''
		return name,available.x(),available.y(),available.width(),available.height()
	def request_overlay_visibility_reconcile(self,reason='',force_show=_C):
		if not self.addon_active:return
		if reason:self.overlay_visibility_reconcile_reason=reason
		if force_show:self.overlay_visibility_reconcile_force_show=_B
		if self.overlay_visibility_reconcile_pending:return
		self.overlay_visibility_reconcile_pending=_B
		def run():self.overlay_visibility_reconcile_pending=_C;reason_value=self.overlay_visibility_reconcile_reason;force_show_value=self.overlay_visibility_reconcile_force_show;self.overlay_visibility_reconcile_reason='';self.overlay_visibility_reconcile_force_show=_C;self.reconcile_overlay_visibility(reason_value,force_show_value)
		QTimer.singleShot(0,run)
	def reconcile_overlay_visibility(self,reason='',force_show=_C):
		self.debug_visibility_reconciles+=1
		if not self.overlay:return
		was_visible=self.overlay.isVisible();auto_hidden_was=self.overlay_auto_hidden_by_window;minimized=self.is_main_window_minimized()
		if not self.runtime_enabled:
			self.overlay_auto_hidden_by_window=_C
			if was_visible:self.overlay.hide()
			self.reset_focus_dim_state(clear_overlay=_B);self.overlay_last_visibility_signature='disabled',;return
		if force_show:self.overlay_user_hidden=_C
		if minimized:
			if was_visible and not self.overlay_user_hidden:self.overlay_auto_hidden_by_window=_B
			self.overlay.hide();self.reset_focus_dim_state(clear_overlay=_B);self.overlay_last_visibility_signature='minimized',self.overlay_user_hidden,self.overlay_auto_hidden_by_window;return
		if self.overlay_user_hidden:
			self.overlay_auto_hidden_by_window=_C
			if was_visible:self.overlay.hide()
			self.reset_focus_dim_state(clear_overlay=_B);self.overlay_last_visibility_signature='user_hidden',self.overlay_user_hidden;return
		screen_key=self.overlay_screen_key()
		if not was_visible or screen_key!=self.overlay_last_screen_key or force_show:self.ensure_overlay_within_visible_screen()
		if self.overlay_auto_hidden_by_window or force_show or not was_visible:
			self.overlay.show()
			if not was_visible or auto_hidden_was:self.overlay.raise_()
			self.overlay_auto_hidden_by_window=_C;self.request_overlay_refresh(0,visibility=_B,style=_B)
		if self.focus.enabled:self.focus_dim_tick()
		self.overlay_last_screen_key=screen_key;self.overlay_last_visibility_signature=self.overlay.isVisible(),self.overlay_user_hidden,self.overlay_auto_hidden_by_window,minimized
	def ensure_app_state_hooks(self):
		if self.app_state_hooks_connected:return
		app=QApplication.instance()
		if not app:return
		if hasattr(app,_B2):app.applicationStateChanged.connect(self.on_application_state_changed)
		self.main_window_event_filter=MainWindowEventFilter(self,mw)
		try:mw.installEventFilter(self.main_window_event_filter)
		except Exception:pass
		self.app_state_hooks_connected=_B
	def disconnect_app_state_hooks(self):
		if not self.app_state_hooks_connected:return
		app=QApplication.instance()
		if app and hasattr(app,_B2):
			try:app.applicationStateChanged.disconnect(self.on_application_state_changed)
			except Exception:pass
		if self.main_window_event_filter is not _A:
			try:mw.removeEventFilter(self.main_window_event_filter)
			except Exception:pass
		self.main_window_event_filter=_A;self.app_state_hooks_connected=_C
	def on_application_state_changed(self,*_args):
		if self.addon_active:self.request_overlay_visibility_reconcile('app_state')
	def set_runtime_enabled(self,enabled,reason=_AG):
		enabled=bool(enabled)
		if self.runtime_enabled==enabled:return
		self.runtime_enabled=enabled
		if not enabled:
			self.pending.clear_pending(clear_reveal=_B);self.pending.clear_queue();self.review_state=self.derive_review_state();self.transition_watchdog_last_snapshot=_A;self.last_overlay_render_key=_A;self.last_overlay_style_key=_A;self.clear_overlay_refresh_queue(stop_timer=_B);self.stop_transition_watchdog();self.stop_focus_dim_timer();self.set_pay_attention_active(_C);self.clear_pay_attention_audio(full_release=_C);self.stop_grade_sound_playback();self.overlay_user_hidden=_B;self.reconcile_overlay_visibility(f"{reason}:disabled");self.start_global_listener(toggle_only=_B)
			try:tooltip('Overlay add-on disabled',period=1200)
			except Exception:pass
			return
		self.overlay_user_hidden=_C;self.start_global_listener(toggle_only=_C);self.refresh_focus_dim_controller(force_rebuild=_B);self.reconcile_overlay_visibility(f"{reason}:enabled",force_show=_B);self.request_overlay_refresh(0,content=_B,style=_B,force=_B)
		try:tooltip('Overlay add-on enabled',period=1200)
		except Exception:pass
	def toggle_overlay(self):self.set_runtime_enabled(not self.runtime_enabled,reason='manual_toggle')
	def derive_review_state(self):
		try:
			if mw.state!=_Z or not getattr(mw,_h,_A)or not mw.reviewer.card:return ReviewUiState.IDLE
			return ReviewUiState.QUESTION if mw.reviewer.state==_r else ReviewUiState.ANSWER if mw.reviewer.state==_AQ else ReviewUiState.IDLE
		except Exception:return ReviewUiState.IDLE
	def current_card_id(self):
		try:
			if mw.state==_Z and getattr(mw,_h,_A)and mw.reviewer.card:return mw.reviewer.card.id
		except Exception:pass
	def sync_review_state(self):
		A='ok: question->answer (state sync)';derived=self.derive_review_state();self.last_card_id=self.current_card_id()
		if self.pending.command and derived in(ReviewUiState.QUESTION,ReviewUiState.ANSWER):
			if self.pending.command==_G and self.pending.source_state==ReviewUiState.QUESTION.value and derived==ReviewUiState.ANSWER:self.record_command_result(_G,A);self.end_transition();self.review_state=derived;return
			if self.pending.command in(_N,_O,_P,_Q)and self.pending.source_state==ReviewUiState.ANSWER.value and derived==ReviewUiState.QUESTION:self.record_command_result(self.pending.command,'ok: answer->next-question (state sync)');self.end_transition();self.review_state=derived;return
			if self.pending.command==_F:
				if self.pending.source_state==ReviewUiState.ANSWER.value and derived==ReviewUiState.QUESTION:self.record_command_result(_F,'ok: answer->question (state sync)');self.end_transition();self.review_state=derived;return
				if self.pending.source_state==ReviewUiState.QUESTION.value and derived==ReviewUiState.ANSWER:self.record_command_result(_F,A);self.end_transition();self.review_state=derived;return
				if self.pending.source_state==ReviewUiState.QUESTION.value and derived==ReviewUiState.QUESTION and self.pending.card_id and self.last_card_id and self.last_card_id!=self.pending.card_id:self.record_command_result(_F,'ok: question->previous (state sync)');self.end_transition();self.review_state=derived;return
			if self.pending.command==_U and derived==ReviewUiState.ANSWER and self.pending.reveal_request:
				expected_card=self.pending.reveal_request.get(_Ag)
				if expected_card is _A or expected_card==self.last_card_id:self.handle_pending_reveal_then_grade(self.last_card_id);self.review_state=self.derive_review_state()if not self.pending.command else ReviewUiState.TRANSITIONING;return
		if derived==ReviewUiState.IDLE and self.pending.command:command=self.pending.reveal_request.get(_A4)if self.pending.command==_U and self.pending.reveal_request else self.pending.command;self.record_command_result(command,'cancelled: reviewer left review');self.end_transition(clear_reveal=_B,allow_queued=_C)
		if self.pending.command and derived!=ReviewUiState.IDLE and self.pending.started_at and _now()-self.pending.started_at>PENDING_TIMEOUT_SEC:command=self.pending.reveal_request.get(_A4)if self.pending.command==_U and self.pending.reveal_request else self.pending.command;self.record_command_result(command,'error: transition timeout');_log(f"Transition timeout for '{self.pending.command}', clearing pending state.");self.end_transition(clear_reveal=_B,allow_queued=_C);self.review_state=derived;return
		self.review_state=ReviewUiState.TRANSITIONING if self.pending.command and derived!=ReviewUiState.IDLE else derived
	def begin_transition(self,command,card_id=_A,source_state=_A):self.pending.command=command;self.pending.card_id=self.current_card_id()if card_id is _A else card_id;self.pending.started_at=_now();self.pending.source_state=source_state or self.derive_review_state().value;self.review_state=ReviewUiState.TRANSITIONING;self.transition_watchdog_last_snapshot=_A;self.ensure_transition_watchdog()
	def end_transition(self,clear_reveal=_C,allow_queued=_B):
		self.pending.clear_pending(clear_reveal=clear_reveal);self.review_state=self.derive_review_state();self.transition_watchdog_last_snapshot=_A;self.stop_transition_watchdog()
		if allow_queued:self.dispatch_queued_transition_command()
		else:self.pending.clear_queue()
	def record_command_result(self,command,result):self.last_command_attempted=command;self.last_command_result=result;_log(f"{command}: {result}")
	def is_undo_available(self):
		try:
			action=getattr(getattr(mw,'form',_A),'actionUndo',_A)
			if action is not _A and hasattr(action,'isEnabled'):return bool(action.isEnabled())
		except Exception:pass
		try:
			status=mw.col.undo_status()if getattr(mw,'col',_A)and hasattr(mw.col,'undo_status')else _A
			if status is _A:return _C
			if hasattr(status,'can_undo'):return bool(status.can_undo)
			if hasattr(status,_F):return bool(status.undo)
			if isinstance(status,(tuple,list))and status and isinstance(status[0],bool):return status[0]
		except Exception:pass
		return _B
	def is_debounced(self,command):
		now=_now();window=COMMAND_DEBOUNCE_SEC.get(command,.15);last=self.last_command_time.get(command,_D)
		if now-last<window:return _B
		self.last_command_time[command]=now;return _C
	def queue_transition_command(self,command):
		if command not in{_G,_N,_O,_P,_Q,_F,_A1}:return _C
		self.pending.queued_command=command;self.pending.queued_card_id=self.current_card_id();self.pending.queued_at=_now();return _B
	def dispatch_queued_transition_command(self):
		command,queued_at,queued_card_id=self.pending.queued_command,self.pending.queued_at,self.pending.queued_card_id;self.pending.clear_queue()
		if not command:return
		if queued_at<=_D or _now()-queued_at>QUEUED_TRANSITION_MAX_AGE_SEC:_log(f"Dropped stale queued command '{command}' after transition.");return
		current_card_id=self.current_card_id()
		if queued_card_id is not _A and current_card_id is _A:_log(f"Dropped queued command '{command}' because no active review card was available.");return
		if queued_card_id is not _A and current_card_id is not _A and current_card_id!=queued_card_id:_log(f"Dropped queued command '{command}' because card context changed ({queued_card_id} -> {current_card_id}).");return
		current_state=self.derive_review_state()
		if command==_G and current_state!=ReviewUiState.QUESTION:_log('Dropped queued flip because reviewer is not on question side.');return
		if command in{_N,_O,_P,_Q}and current_state!=ReviewUiState.ANSWER:_log(f"Dropped queued grade '{command}' because reviewer is not on answer side.");return
		QTimer.singleShot(0,lambda:self.addon_active and self.dispatch_command(command,skip_debounce=_B))
	def dispatch_command(self,command,skip_debounce=_C):
		B='pending';A='ignored: debounced'
		if not self.addon_active:self.record_command_result(command,'ignored: addon inactive');return
		self.sync_review_state()
		if command==_AG:
			if self.is_debounced(command):self.record_command_result(command,A);return
			self.toggle_overlay();self.record_command_result(command,'ok');return
		if not self.runtime_enabled:self.record_command_result(command,'ignored: addon toggled off');return
		if self.review_state==ReviewUiState.IDLE:self.record_command_result(command,'ignored: not in review');return
		if self.review_state==ReviewUiState.TRANSITIONING:
			if self.queue_transition_command(command):self.record_command_result(command,f"queued: transitioning ({self.pending.command or B})")
			else:self.record_command_result(command,f"ignored: transitioning ({self.pending.command or B})")
			return
		if not skip_debounce and self.is_debounced(command):self.record_command_result(command,A);return
		if command==_A1:
			try:mw.reviewer.replayAudio()
			except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());return
			self.record_command_result(command,'ok');self.mark_review_activity(command,_B);return
		if command==_F:
			if not self.is_undo_available():self.record_command_result(command,_Ah);return
			try:mw.onUndo()
			except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());return
			self.record_command_result(command,'requested');self.mark_review_activity(_F,_B);self.schedule_external_overlay_refresh('undo_command');return
		if command==_G:
			if self.review_state!=ReviewUiState.QUESTION:self.record_command_result(command,'ignored: already on answer');return
			try:self.begin_transition(_G,self.current_card_id(),self.review_state.value);mw.reviewer._showAnswer()
			except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());self.end_transition(clear_reveal=_B);return
			self.record_command_result(command,'requested: question->answer');self.mark_review_activity(_G,_B);self.schedule_transition_followups();return
		if command in(_N,_O,_P,_Q):
			ease_map={_N:1,_O:2,_P:3,_Q:4};card_id=self.current_card_id()
			if self.review_state==ReviewUiState.QUESTION:
				mode=_normalize_grade_from_question_mode(self.get_config().get(_a,_e))
				if mode==_U:
					self.pending.reveal_request={_A4:command,'ease':ease_map[command],_Ag:card_id}
					try:self.begin_transition(_U,card_id,self.review_state.value);mw.reviewer._showAnswer()
					except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());self.end_transition(clear_reveal=_B);return
					self.record_command_result(command,'requested: reveal_then_grade');self.schedule_transition_followups()
				elif mode==_e:
					try:self.begin_transition(_G,card_id,self.review_state.value);mw.reviewer._showAnswer()
					except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());self.end_transition(clear_reveal=_B);return
					self.record_command_result(command,'requested: flip_only(question->answer)');self.mark_review_activity(_G,_B);self.schedule_transition_followups()
				else:self.record_command_result(command,'ignored: grading on question side')
				return
			if self.review_state!=ReviewUiState.ANSWER:self.record_command_result(command,f"ignored: invalid state {self.review_state.value}");return
			try:self.begin_transition(command,card_id,self.review_state.value);mw.reviewer._answerCard(ease_map[command])
			except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());self.end_transition(clear_reveal=_B);return
			self.record_command_result(command,f"requested: answered {command}");self.mark_review_activity(command,_B);self.play_grade_sound_after_answer_if_needed(command);self.schedule_transition_followups();return
		self.record_command_result(command,'ignored: unknown command')
	def finalize_pending_on_question(self,card_id):
		if not self.pending.command:return
		if self.pending.command in(_N,_O,_P,_Q):
			if self.pending.source_state!=ReviewUiState.ANSWER.value:self.record_command_result(self.pending.command,f"ignored: unexpected source state {self.pending.source_state}")
			else:self.record_command_result(self.pending.command,'ok')
			self.end_transition();return
		if self.pending.command==_F:
			if self.pending.source_state not in(ReviewUiState.QUESTION.value,ReviewUiState.ANSWER.value):self.record_command_result(_F,f"ignored: unexpected source state {self.pending.source_state}");self.end_transition();return
			if self.pending.source_state==ReviewUiState.QUESTION.value and self.pending.card_id is not _A and card_id==self.pending.card_id:self.record_command_result(_F,_Ah);self.end_transition();return
			self.record_command_result(_F,'ok');self.end_transition();return
		if self.pending.command==_U:requested=self.pending.reveal_request[_A4]if self.pending.reveal_request else _U;self.record_command_result(requested,'cancelled: returned to question');self.pending.reveal_request=_A;self.end_transition();return
		if self.pending.command==_G:
			if self.pending.card_id==card_id:self.record_command_result(_G,'ignored: still on question')
			self.end_transition()
	def handle_pending_reveal_then_grade(self,card_id):
		request=self.pending.reveal_request;self.pending.reveal_request=_A
		if not request:self.end_transition();return
		if request.get(_Ag)!=card_id:self.record_command_result(request.get(_A4,_U),'ignored: card changed before grade');self.end_transition();return
		command=request.get(_A4)
		try:self.begin_transition(command,card_id,ReviewUiState.ANSWER.value);mw.reviewer._answerCard(request.get('ease'));self.record_command_result(command,'requested: reveal_then_grade->answered');self.mark_review_activity(command,_B);self.play_grade_sound_after_answer_if_needed(command)
		except Exception as exc:self.record_command_result(command,f"error: {exc}");_log(traceback.format_exc());self.end_transition()
	def transition_snapshot(self):return self.current_card_id(),self.derive_review_state().value,self.pending.command,self.pending.card_id
	def ensure_transition_watchdog(self):
		if self.transition_watchdog_timer is _A:self.transition_watchdog_timer=QTimer(mw);self.transition_watchdog_timer.setInterval(TRANSITION_WATCHDOG_MS);self.transition_watchdog_timer.timeout.connect(self.transition_watchdog_tick)
		if self.pending.command and not self.transition_watchdog_timer.isActive():self.transition_watchdog_timer.start()
	def stop_transition_watchdog(self):
		if self.transition_watchdog_timer and self.transition_watchdog_timer.isActive():self.transition_watchdog_timer.stop()
	def transition_watchdog_tick(self):
		self.debug_watchdog_ticks+=1
		if not self.addon_active or not self.pending.command:self.stop_transition_watchdog();self.maybe_log_debug_counters();return
		snapshot=self.transition_snapshot()
		if snapshot!=self.transition_watchdog_last_snapshot:self.transition_watchdog_last_snapshot=snapshot;self.debug_watchdog_state_changes+=1;self.sync_review_state();self.request_overlay_refresh(0,content=_B,style=_B)
		elif self.pending.started_at and _now()-self.pending.started_at>PENDING_TIMEOUT_SEC:self.sync_review_state()
		if not self.pending.command:self.stop_transition_watchdog()
		self.maybe_log_debug_counters()
	def run_overlay_refresh_request(self):
		self.debug_refresh_runs+=1;flags=dict(self.refresh.flags);expected_card_id=self.refresh.expected_card_id;expected_state=self.refresh.expected_reviewer_state;self.refresh.clear()
		if not self.overlay:self.maybe_log_debug_counters();return
		if expected_card_id is not _A and self.current_card_id()!=expected_card_id:self.maybe_log_debug_counters();return
		if expected_state is not _A:
			try:
				if mw.state!=_Z or not getattr(mw,_h,_A)or mw.reviewer.state!=expected_state:self.maybe_log_debug_counters();return
			except Exception:self.maybe_log_debug_counters();return
		self.force_refresh_data(content=flags.get(_AR,_B),style=flags.get(_AS,_B),visibility=flags.get(_AT,_C),force=flags.get(_AU,_C));self.maybe_log_debug_counters()
	def request_overlay_refresh(self,delay_ms=0,*,content=_B,style=_B,visibility=_C,force=_C,expected_card_id=_A,expected_reviewer_state=_A):
		self.debug_refresh_requests+=1
		if self.overlay_refresh_timer is _A:self.overlay_refresh_timer=QTimer(mw);self.overlay_refresh_timer.setSingleShot(_B);self.overlay_refresh_timer.timeout.connect(self.run_overlay_refresh_request)
		self.refresh.flags[_AR]|=bool(content);self.refresh.flags[_AS]|=bool(style);self.refresh.flags[_AT]|=bool(visibility);self.refresh.flags[_AU]|=bool(force)
		if expected_card_id is not _A:self.refresh.expected_card_id=expected_card_id
		if expected_reviewer_state is not _A:self.refresh.expected_reviewer_state=expected_reviewer_state
		delay=max(0,int(delay_ms))
		if not self.refresh.pending:self.refresh.pending=_B;self.refresh.requested_at=_now();self.refresh.delay_ms=delay;self.overlay_refresh_timer.start(delay);return
		if self.overlay_refresh_timer.isActive():
			remaining=self.overlay_refresh_timer.remainingTime()
			if remaining<0 or delay<remaining:self.refresh.delay_ms=delay;self.overlay_refresh_timer.start(delay)
			return
		self.refresh.delay_ms=delay;self.overlay_refresh_timer.start(delay)
	def clear_overlay_refresh_queue(self,stop_timer=_C):
		if stop_timer and self.overlay_refresh_timer and self.overlay_refresh_timer.isActive():self.overlay_refresh_timer.stop()
		self.refresh.clear()
	def schedule_overlay_refresh(self,delay_ms=0,expected_card_id=_A,expected_reviewer_state=_A):self.request_overlay_refresh(delay_ms,content=_B,style=_B,expected_card_id=expected_card_id,expected_reviewer_state=expected_reviewer_state)
	def schedule_transition_followups(self):
		for delay in(0,120,320):self.request_overlay_refresh(delay,content=_B,style=_B,force=delay==0)
	def schedule_external_overlay_refresh(self,reason='external'):
		if not self.addon_active or not self.runtime_enabled or not self.overlay:return
		try:
			if mw.state!=_Z:return
		except Exception:return
		now=_now()
		if now-self.last_external_overlay_refresh_at<.06:return
		self.last_external_overlay_refresh_at=now;self.request_overlay_refresh(0,content=_B,style=_B);self.request_overlay_refresh(180,content=_B,style=_B)
	def compute_overlay_render_key(self):
		conf=self.get_config_view();card_id=self.current_card_id();derived_state=self.derive_review_state().value;active_deck_id=_A;mapped_fields_signature=_A;theme_signature=_A
		try:
			if mw.state==_Z and getattr(mw,_h,_A)and mw.reviewer.card:
				card=mw.reviewer.card;deck_ids,_=self.card_deck_candidates(card);active_deck_id=deck_ids[0]if deck_ids else getattr(card,'did',_A);deck_cfg=self.deck_map_for_card(conf,card)if conf else _A;deck_theme=self.deck_theme_for_card(conf,card)if conf else _A
				if deck_cfg:mapped_fields_signature=tuple(deck_cfg.get(field_key,'')for(_,field_key)in DECK_MAP_FIELDS)
				if conf:theme_signature=tuple(self.effective_style(conf,deck_theme).get(key)for key in(_H,_I,_J,_K,_o,_p,_i,_V))
		except Exception:pass
		return card_id,derived_state,self.runtime_enabled,self.overlay_user_hidden,bool(conf.get(_AL,_C))if conf else _C,active_deck_id,mapped_fields_signature,theme_signature
	def compute_overlay_style_key(self):conf=self.get_config_view();return bool(conf.get(_S,_C))if conf else _C,self.focus.phase,round(float(self.focus.target_opacity),3),round(float(self.focus.current_opacity),3),self.overlay_auto_hidden_by_window
	def refresh_overlay_content(self):
		if not self.overlay or not self.runtime_enabled:return _C
		self.sync_review_state();conf=self.get_config_view()
		if mw.state!=_Z or not getattr(mw,_h,_A)or not mw.reviewer.card:self.overlay.set_content("<div class='main-word' style='opacity:0.3;'>Standby</div>",self.effective_style(conf,_A));return _B
		card=mw.reviewer.card;note=card.note();deck_cfg=self.deck_map_for_card(conf,card);style_options=self.effective_style(conf,self.deck_theme_for_card(conf,card))
		if not deck_cfg:self.overlay.set_content("<div class='main-word' style='opacity:0.3;'>Deck Not Mapped</div>",style_options);return _B
		is_answer=mw.reviewer.state==_AQ;german_word=self.safe_text_field(note,deck_cfg.get(_AZ));english_word=self.safe_text_field(note,deck_cfg.get(_Aa))if is_answer else'';german_ex_1=self.safe_text_field(note,deck_cfg.get(_Ab));english_ex_1=self.safe_text_field(note,deck_cfg.get(_Ac))if is_answer else'';german_ex_2=self.safe_text_field(note,deck_cfg.get(_At))if is_answer else'';english_ex_2=self.safe_text_field(note,deck_cfg.get(_Au))if is_answer else'';german_ex_3=self.safe_text_field(note,deck_cfg.get(_Av))if is_answer else'';english_ex_3=self.safe_text_field(note,deck_cfg.get(_Aw))if is_answer else'';html_body=f"<div class='main-word'>{german_word or'No German Word'}</div>"+(f"<div class='answer-word'>{english_word or''}</div>{self.build_example_pair(german_ex_1,english_ex_1)}{self.build_example_pair(german_ex_2,english_ex_2)}{self.build_example_pair(german_ex_3,english_ex_3)}"if is_answer else self.build_example_pair(german_ex_1,''))
		if conf.get(_AL):dim_visible=any(dim.isVisible()for dim in self.focus_dim_overlays);html_body+=f"<hr><div class='status-line'>state={self.review_state.value} | last={html.escape(str(self.last_command_attempted))} | result={html.escape(str(self.last_command_result))}<br>dim_enabled={str(bool(conf.get(_S,_C))).lower()} | dim_phase={self.focus.phase} | idle_elapsed={self.focus.last_idle_elapsed:.2f}s | stage={self.focus.stage_progress:.2f} | dim_opacity={self.focus.current_opacity:.1f} | dim_shown={str(dim_visible).lower()} | dim_source={html.escape(str(self.focus.last_activity_source))}</div>"
		self.overlay.set_content(html_body,style_options);return _B
	def refresh_overlay_visuals(self):
		conf=self.get_config_view()
		if not self.runtime_enabled or not conf.get(_S,_C):
			self.set_pay_attention_active(_C)
			if self.overlay and self.overlay.isVisible():self.overlay.set_focus_alarm_intensity(_D,_M,_D,_now())
			return _B
		self.apply_focus_dim_visuals(conf);return _B
	def force_refresh_data(self,*,content=_B,style=_B,visibility=_C,force=_C):
		self.debug_force_refresh_runs+=1
		if not self.runtime_enabled or not content and not style and not visibility:return
		render_key=self.compute_overlay_render_key()if content else self.last_overlay_render_key;style_key=self.compute_overlay_style_key()if style or visibility else self.last_overlay_style_key;refresh_content=bool(content);refresh_style=bool(style or visibility)
		if not force:
			if refresh_content and render_key==self.last_overlay_render_key:refresh_content=_C
			if refresh_style and style_key==self.last_overlay_style_key:refresh_style=_C
			if not refresh_content and not refresh_style:self.maybe_log_debug_counters();return
		content_ok=_B
		if refresh_content:
			content_ok=self.refresh_overlay_content()
			if content_ok:self.last_overlay_render_key=render_key
		if refresh_style:
			style_ok=self.refresh_overlay_visuals()
			if style_ok:self.last_overlay_style_key=style_key
		if refresh_content and not content_ok and refresh_style:self.refresh_overlay_visuals()
		self.maybe_log_debug_counters()
	def update_overlay(self):
		if self.runtime_enabled:self.request_overlay_refresh(0,content=_B,style=_B)
	def stop_global_listener(self):
		if self.current_listener:
			try:self.current_listener.stop()
			except Exception as exc:_log(f"Listener stop failed: {exc}")
		self.current_listener=_A;self.listener_hotkey_signature=_A;self.listener_toggle_only=_A
	def start_global_listener(self,show_feedback=_C,toggle_only=_C):
		if not self.addon_active:_log('Listener start skipped: add-on is inactive.');return
		if not HAS_PYNPUT:
			if show_feedback or not self.missing_pynput_warned:tooltip('Overlay hotkeys unavailable: install pynput in Anki Python env.',period=4000)
			self.missing_pynput_warned=_B;_log('pynput is unavailable; hotkey listener not started.');return
		conf=self.get_config();signature=self.compute_hotkey_signature(conf);requested_toggle_only=bool(toggle_only)
		if self.current_listener and signature==self.listener_hotkey_signature and requested_toggle_only==self.listener_toggle_only:return
		self.stop_global_listener();toggle_combo=_normalize_hotkey(conf.get(_AK,''))
		if requested_toggle_only:
			if not toggle_combo or not self.validate_hotkey_combo(toggle_combo):
				if show_feedback:tooltip('Toggle hotkey is invalid; cannot keep listener while disabled.',period=4500)
				_log('Toggle-only listener not started because toggle hotkey is invalid.');return
		else:
			invalid=self.validate_hotkeys(conf)
			if invalid:tooltip(f"Overlay hotkey config issue: {'; '.join(invalid[:3])}",period=4500);_log(f"Invalid hotkey config: {'; '.join(invalid)}");return
		def enqueue(command_name):
			def runner():
				if not self.addon_active:return
				self.last_hotkey_captured=command_name;mw.taskman.run_on_main(lambda:self.dispatch_command(command_name))
			return runner
		def enqueue_flip_or_grade(grade_command):
			def runner():
				if not self.addon_active:return
				def dispatch():self.sync_review_state();command_name=_G if self.review_state==ReviewUiState.QUESTION else grade_command;self.last_hotkey_captured=command_name;self.dispatch_command(command_name)
				mw.taskman.run_on_main(dispatch)
			return runner
		hotkeys={};sources={};collisions=[]
		def register(combo,callback,command_name):
			if not combo:return
			for variant in _hotkey_registration_variants(combo):
				existing=sources.get(variant)
				if existing is not _A and existing!=command_name:collisions.append(f"{variant}: {existing} vs {command_name}");_log(f"Hotkey collision at runtime ({collisions[-1]}); listener startup aborted.");return
			for variant in _hotkey_registration_variants(combo):hotkeys[variant]=callback;sources[variant]=command_name
		register(toggle_combo,enqueue(_AG),_AG)
		if not requested_toggle_only:
			for(key,command)in((_AI,_A1),(_AJ,_F)):register(_normalize_hotkey(conf.get(key)),enqueue(command),command)
			flip_combo=_normalize_hotkey(conf.get(_n));grade_keys=[(_A9,_N),(_AA,_O),(_AB,_P),(_AC,_Q)];shared_grade=next((grade for(key,grade)in grade_keys if _normalize_hotkey(conf.get(key))==flip_combo),_A)if flip_combo else _A
			if flip_combo:register(flip_combo,enqueue_flip_or_grade(shared_grade)if shared_grade else enqueue(_G),f"flip_or_{shared_grade}"if shared_grade else _G)
			for(key,grade)in grade_keys:
				combo=_normalize_hotkey(conf.get(key))
				if combo and not(combo==flip_combo and shared_grade==grade):register(combo,enqueue(grade),grade)
		if collisions:tooltip('Overlay hotkey runtime collision. Review bindings in settings.',period=5000);return
		if not hotkeys:_log('No valid hotkeys found; listener was not started.');return
		try:self.current_listener=keyboard.GlobalHotKeys(hotkeys);self.current_listener.daemon=_B;self.current_listener.start();self.listener_hotkey_signature=signature;self.listener_toggle_only=requested_toggle_only
		except Exception as exc:self.current_listener=_A;self.listener_hotkey_signature=_A;self.listener_toggle_only=_A;tooltip('Overlay hotkeys failed to start. Check add-on console.',period=4500);_log(f"Hotkey listener startup failed: {exc}");_log(traceback.format_exc())
	def reset_focus_dim_state(self,clear_overlay=_C):
		self.focus.reset(clear_identity=_B);self.set_pay_attention_active(_C)
		if clear_overlay:
			for dim in self.focus_dim_overlays:
				try:dim.clear_dim()
				except Exception:pass
			if self.overlay:
				try:self.overlay.set_focus_alarm_intensity(_D,_M,_D,_now())
				except Exception:pass
	def focus_dim_fail_open(self,reason,exc=_A):
		if self.focus.fail_open_active:return
		self.focus.fail_open_active=_B
		try:
			_log(f"Focus-dim fail-open ({reason})"+(f": {exc}"if exc is not _A else''));self.focus.enabled=_C;self.focus.phase=_M;self.focus.target_opacity=_D
			try:
				conf=self.get_config()
				if conf.get(_S,_C):conf[_S]=_C;self.save_config(conf)
			except Exception:pass
			self.stop_focus_dim_timer();self.set_pay_attention_active(_C)
			for dim in self.focus_dim_overlays:
				try:dim.clear_dim()
				except Exception:pass
			if self.overlay:
				try:self.overlay.set_focus_alarm_intensity(_D,_M,_D,_now())
				except Exception:pass
			try:tooltip('Focus dim disabled after runtime error. Open settings to re-enable.',period=5000)
			except Exception:pass
		finally:self.focus.fail_open_active=_C
	def clear_focus_dim_overlays(self):
		for dim in self.focus_dim_overlays:
			try:dim.hide();dim.deleteLater()
			except Exception:pass
		self.focus_dim_overlays=[]
	def rebuild_focus_dim_overlays(self):
		self.clear_focus_dim_overlays();app=QApplication.instance()
		if app:self.focus_dim_overlays=[FocusDimOverlay(screen)for screen in app.screens()]
	def on_screen_layout_changed(self,*_args):
		if self.overlay:
			self.ensure_overlay_within_visible_screen()
			if self.overlay.isVisible():self.overlay.raise_()
		if self.focus.enabled:self.rebuild_focus_dim_overlays();self.focus_dim_tick()
	def ensure_focus_dim_screen_hooks(self):
		if self.focus_dim_screen_hooks_connected:return
		app=QApplication.instance()
		if not app:return
		if hasattr(app,_B3):app.screenAdded.connect(self.on_screen_layout_changed)
		if hasattr(app,_B4):app.screenRemoved.connect(self.on_screen_layout_changed)
		self.focus_dim_screen_hooks_connected=_B
	def disconnect_focus_dim_screen_hooks(self):
		if not self.focus_dim_screen_hooks_connected:return
		app=QApplication.instance()
		if app:
			if hasattr(app,_B3):
				try:app.screenAdded.disconnect(self.on_screen_layout_changed)
				except Exception:pass
			if hasattr(app,_B4):
				try:app.screenRemoved.disconnect(self.on_screen_layout_changed)
				except Exception:pass
		self.focus_dim_screen_hooks_connected=_C
	def ensure_focus_dim_timer(self):
		if self.focus_dim_timer is _A:self.focus_dim_timer=QTimer(mw);self.focus_dim_timer.setInterval(FOCUS_DIM_TICK_MS);self.focus_dim_timer.timeout.connect(self.focus_dim_tick)
		if not self.focus_dim_timer.isActive():self.focus_dim_timer.start()
	def update_focus_dim_timer_interval(self,interval_ms):
		if self.focus_dim_timer and self.focus_dim_timer.interval()!=interval_ms:self.focus_dim_timer.setInterval(interval_ms)
	def stop_focus_dim_timer(self):
		if self.focus_dim_timer and self.focus_dim_timer.isActive():self.focus_dim_timer.stop()
	def is_review_active_for_dim(self,conf):
		try:
			if mw.state!=_Z or not getattr(mw,_h,_A)or not mw.reviewer.card:return _C
			if self.review_state==ReviewUiState.TRANSITIONING:return _B if not conf.get(_AD)else getattr(mw.reviewer,'state','')==_r or self.pending.source_state==ReviewUiState.QUESTION.value
			return _C if conf.get(_AD)and mw.reviewer.state!=_r else _B
		except Exception:return _C
	def advance_focus_dim_opacity(self,now):
		if self.focus.last_tick_at<=_D:self.focus.last_tick_at=now
		delta=max(_D,now-self.focus.last_tick_at);self.focus.last_tick_at=now;target=max(_D,min(1e2,self.focus.target_opacity))
		if target>self.focus.current_opacity:self.focus.current_opacity=min(target,self.focus.current_opacity+1e2/max(.05,FOCUS_DIM_RISE_SEC)*delta)
		elif target<self.focus.current_opacity:
			self.focus.current_opacity=max(target,self.focus.current_opacity-1e2/max(.05,FOCUS_DIM_CLEAR_SEC)*delta)
			if self.focus.current_opacity<.05:self.focus.current_opacity=_D
	def compute_focus_dim_stage(self,conf,idle_elapsed):
		idle_sec=_clamp_float(conf.get(_L),DEFAULT_CONFIG[_L],.5,36e2);warning_sec=_clamp_float(conf.get(_b),DEFAULT_CONFIG[_b],.1,36e2);punish_sec=_clamp_float(conf.get(_c),DEFAULT_CONFIG[_c],.1,36e2);lockdown_sec=_clamp_float(conf.get(_d),DEFAULT_CONFIG[_d],.1,36e2);warning_opacity=_clamp_float(conf.get(_t),DEFAULT_CONFIG[_t],_D,1e2);punish_opacity=_clamp_float(conf.get(_u),DEFAULT_CONFIG[_u],warning_opacity,1e2);max_opacity=_clamp_float(conf.get(_v),DEFAULT_CONFIG[_v],punish_opacity,1e2);curve=_normalize_focus_curve(conf.get(_T,DEFAULT_CONFIG[_T]),DEFAULT_CONFIG[_T]);elapsed=max(_D,float(idle_elapsed))
		if elapsed<idle_sec:return _Ai,min(_E,elapsed/max(.001,idle_sec)),_D
		after_idle=elapsed-idle_sec
		if after_idle<warning_sec:progress=min(_E,after_idle/max(.001,warning_sec));start=max(6.,warning_opacity*.35);return _A3,progress,start+(warning_opacity-start)*_curve_value(progress,curve)
		after_warning=after_idle-warning_sec
		if after_warning<punish_sec:progress=min(_E,after_warning/max(.001,punish_sec));return _g,progress,warning_opacity+(punish_opacity-warning_opacity)*_curve_value(progress,curve)
		after_punish=after_warning-punish_sec;progress=min(_E,after_punish/max(.001,lockdown_sec));return _X,progress,punish_opacity+(max_opacity-punish_opacity)*_curve_value(progress,curve)
	def current_overlay_global_rect(self):
		if not self.overlay:return QRect()
		try:return self.overlay.frameGeometry()if self.overlay.isVisible()else QRect()
		except Exception:return QRect()
	def focus_alarm_intensity(self):
		if self.focus.phase==_A3:return .28+.3*self.focus.stage_progress
		if self.focus.phase==_g:return .58+.32*self.focus.stage_progress
		return .92 if self.focus.phase==_X else _D
	def apply_partial_focus_reset(self,conf,now):
		relief_sec=_clamp_float(conf.get(_z),DEFAULT_CONFIG[_z],.2,3e1);idle_sec=_clamp_float(conf.get(_L),DEFAULT_CONFIG[_L],.5,36e2);self.focus.last_activity_at=now if self.focus.last_activity_at<=_D else max(min(now,self.focus.last_activity_at+relief_sec),now-idle_sec);self.focus.idle_started_at=self.focus.last_activity_at
		if self.focus.phase==_X:self.focus.phase=_g
		elif self.focus.phase==_g:self.focus.phase=_A3
		self.focus.stage_progress=_D;self.focus.last_ramp_progress=_D
	def sync_focus_dim_baseline_for_card(self):
		try:
			if mw.state!=_Z or not getattr(mw,_h,_A)or not mw.reviewer.card:self.focus.last_card_id=_A;self.focus.last_side=_A;return
			card_id=mw.reviewer.card.id;side=getattr(mw.reviewer,'state','')
		except Exception:return
		card_changed=card_id!=self.focus.last_card_id;entered_question=side==_r and side!=self.focus.last_side
		if not card_changed and not entered_question:self.focus.last_card_id=card_id;self.focus.last_side=side;return
		now=_now();self.focus.last_activity_at=now;self.focus.idle_started_at=now;self.focus.phase=_Ai;self.focus.target_opacity=_D;self.focus.stage_progress=_D;self.focus.last_ramp_progress=_D;self.focus.last_idle_elapsed=_D;self.focus.last_activity_source='card_sync';self.focus.last_card_id=card_id;self.focus.last_side=side
	def apply_focus_dim_visuals(self,conf):
		try:
			self.set_pay_attention_active(self.focus.phase in(_g,_X))
			if not self.focus_dim_overlays:return
			safe_rect=self.current_overlay_global_rect();padding=int(_clamp_float(conf.get(_w),DEFAULT_CONFIG[_w],0,140))
			if safe_rect.isValid()and padding>0:safe_rect=safe_rect.adjusted(-padding,-padding,padding,padding)
			anim_time=_now()
			for dim in self.focus_dim_overlays:dim.apply_dim(self.focus.current_opacity,self.focus.phase,self.focus.stage_progress,str(conf.get(_j,DEFAULT_CONFIG[_j])or DEFAULT_CONFIG[_j]),str(conf.get(_k,DEFAULT_CONFIG[_k])or DEFAULT_CONFIG[_k]),self.focus.phase in(_g,_X),str(conf.get(_q,DEFAULT_CONFIG[_q])or DEFAULT_CONFIG[_q]),int(_clamp_float(conf.get(_y),DEFAULT_CONFIG[_y],14,84)),safe_rect,int(_clamp_float(conf.get(_x),DEFAULT_CONFIG[_x],0,180)),anim_time)
			if self.overlay and self.overlay.isVisible():
				self.overlay.set_focus_alarm_intensity(self.focus_alarm_intensity(),self.focus.phase,self.focus.stage_progress,anim_time)
				if self.focus.current_opacity>_D:self.overlay.raise_()
		except Exception as exc:traceback.print_exc();self.focus_dim_fail_open('focus visuals',exc)
	def focus_dim_tick(self):
		try:
			conf=self.get_config_view();self.focus.enabled=bool(conf.get(_S,_C))and self.runtime_enabled
			if not self.focus.enabled:self.stop_focus_dim_timer();self.reset_focus_dim_state(clear_overlay=_B);return
			self.ensure_focus_dim_screen_hooks()
			if not self.focus_dim_overlays:self.rebuild_focus_dim_overlays()
			self.sync_review_state();self.sync_focus_dim_baseline_for_card();now=_now()
			if self.focus.last_activity_at<=_D:self.focus.last_activity_at=now
			if not self.is_review_active_for_dim(conf):
				self.focus.phase=_M;self.focus.target_opacity=_D;self.focus.idle_started_at=_D;self.focus.last_idle_elapsed=_D;self.focus.stage_progress=_D;self.focus.last_ramp_progress=_D;self.advance_focus_dim_opacity(now);self.request_overlay_refresh(0,content=_C,style=_B)
				try:
					if mw.state!=_Z or not getattr(mw,_h,_A)or not mw.reviewer.card:self.stop_focus_dim_timer()
				except Exception:self.stop_focus_dim_timer()
				return
			idle_elapsed=max(_D,now-self.focus.last_activity_at);self.focus.last_idle_elapsed=idle_elapsed;self.focus.phase,self.focus.stage_progress,self.focus.target_opacity=self.compute_focus_dim_stage(conf,idle_elapsed);self.focus.last_ramp_progress=self.focus.stage_progress;idle_sec=_clamp_float(conf.get(_L),DEFAULT_CONFIG[_L],.5,36e2);self.update_focus_dim_timer_interval(FOCUS_DIM_IDLE_TICK_MS if self.focus.current_opacity<=_D and self.focus.phase==_Ai and idle_elapsed+FOCUS_DIM_IDLE_TICK_MS/1e3<idle_sec else FOCUS_DIM_TICK_MS);self.advance_focus_dim_opacity(now);self.request_overlay_refresh(0,content=_C,style=_B)
		except Exception as exc:traceback.print_exc();self.focus_dim_fail_open('focus tick',exc)
	def refresh_focus_dim_controller(self,force_rebuild=_C):
		conf=self.get_config_view();self.focus.enabled=bool(conf.get(_S,_C))and self.runtime_enabled
		if not self.focus.enabled:self.stop_focus_dim_timer();self.reset_focus_dim_state(clear_overlay=_B);return
		self.ensure_focus_dim_screen_hooks()
		if force_rebuild or not self.focus_dim_overlays:self.rebuild_focus_dim_overlays()
		now=_now()
		if self.focus.last_activity_at<=_D:self.focus.last_activity_at=now
		if self.focus.idle_started_at<=_D:self.focus.idle_started_at=self.focus.last_activity_at
		self.ensure_focus_dim_timer();self.focus_dim_tick()
	def mark_review_activity(self,command,accepted):
		if not accepted or not self.runtime_enabled:return
		conf=self.get_config_view()
		if not conf.get(_S,_C):return
		try:
			if mw.state!=_Z or not getattr(mw,_h,_A)or not mw.reviewer.card:return
		except Exception:return
		reset_mode=_f if command in{_N,_O,_P,_Q,_F,_B5}else _AE if command==_G else _normalize_replay_reset_mode(conf.get(_W),DEFAULT_CONFIG[_W])if command==_A1 else _A2
		if command==_A1 and not conf.get(_AX,_B):reset_mode=_A2
		if reset_mode==_A2:return
		now=_now()
		if reset_mode==_f:self.focus.last_activity_at=now;self.focus.idle_started_at=now;self.focus.phase=_Ai;self.focus.target_opacity=_D;self.focus.stage_progress=_D;self.focus.last_ramp_progress=_D;self.focus.last_activity_source=f"{command}:full"
		else:self.apply_partial_focus_reset(conf,now);self.focus.last_activity_source=f"{command}:partial"
		self.ensure_focus_dim_timer();self.focus_dim_tick()
	def stop_grade_sound_playback(self):
		for player in self.grade_sound_players.values():
			try:player.stop()
			except Exception:pass
	def clear_grade_sounds(self):
		self.stop_grade_sound_playback()
		for player in self.grade_sound_players.values():
			try:player.deleteLater()
			except Exception:pass
		for output in self.grade_sound_outputs.values():
			try:output.deleteLater()
			except Exception:pass
		self.grade_sound_players={};self.grade_sound_outputs={};self.grade_sound_initialized=_C
	def copy_grade_sound_files_to_media_if_missing(self,media_dir):
		addon_dir=os.path.dirname(__file__)
		for filename in set(GRADE_SOUND_FILES.values())|{PAY_ATTENTION_SOUND_FILE}:
			source_path=os.path.join(addon_dir,filename);destination_path=os.path.join(media_dir,filename)
			if os.path.exists(destination_path):continue
			if not os.path.exists(source_path):_log(f"Bundled sound file missing in add-on folder: {source_path}");continue
			if os.path.normcase(os.path.abspath(source_path))==os.path.normcase(os.path.abspath(destination_path)):continue
			try:shutil.copy2(source_path,destination_path);_log(f"Copied bundled sound to collection media: {destination_path}")
			except Exception as exc:_log(f"Failed to copy bundled sound '{filename}' to media: {exc}")
	def create_media_player(self,path):
		if QMediaPlayer is _A:return _A,_A
		url=QUrl.fromLocalFile(path);player=output=_A
		try:
			player=QMediaPlayer(mw)
			if QAudioOutput is not _A and hasattr(player,'setAudioOutput'):output=QAudioOutput(mw);output.setVolume(_E);player.setAudioOutput(output)
			elif hasattr(player,_Aj):player.setVolume(100)
			if hasattr(player,'setSource'):player.setSource(url)
			elif hasattr(player,'setMedia'):
				try:player.setMedia(url)
				except Exception:
					if QMediaContent is _A:raise
					player.setMedia(QMediaContent(url))
		except Exception as exc:
			_log(f"Media player init failed for '{path}': {exc}")
			if player is not _A:
				try:player.deleteLater()
				except Exception:pass
			if output is not _A:
				try:output.deleteLater()
				except Exception:pass
			return _A,_A
		return player,output
	def prime_grade_sound_players(self):
		for(key,player)in self.grade_sound_players.items():
			output=self.grade_sound_outputs.get(key);restore_output=output.volume()if output is not _A else _A;restore_player=player.volume()if output is _A and hasattr(player,'volume')and hasattr(player,_Aj)else _A
			try:
				if output is not _A:output.setVolume(_D)
				elif restore_player is not _A:player.setVolume(0)
				player.play()
				if hasattr(player,'pause'):player.pause()
				if hasattr(player,_Ak):player.setPosition(0)
				player.stop()
			except Exception:pass
			finally:
				try:
					if output is not _A and restore_output is not _A:output.setVolume(restore_output)
					elif restore_player is not _A and hasattr(player,_Aj):player.setVolume(restore_player)
				except Exception:pass
	def init_grade_sounds(self):
		self.clear_grade_sounds()
		if QMediaPlayer is _A:_log('QtMultimedia unavailable; grade sounds disabled.');return
		try:media_dir=mw.col.media.dir()
		except Exception as exc:_log(f"Could not resolve media dir for grade sounds: {exc}");return
		self.copy_grade_sound_files_to_media_if_missing(media_dir)
		for(sound_key,filename)in GRADE_SOUND_FILES.items():
			path=os.path.join(media_dir,filename)
			if not os.path.exists(path):_log(f"Grade sound file missing: {path}");continue
			player,output=self.create_media_player(path)
			if player:
				self.grade_sound_players[sound_key]=player
				if output is not _A:self.grade_sound_outputs[sound_key]=output
		self.grade_sound_initialized=bool(self.grade_sound_players)
		if self.grade_sound_initialized:QTimer.singleShot(0,self.prime_grade_sound_players)
		else:_log('No grade sounds loaded; answer SFX disabled.')
	def play_grade_sound(self,command,source='hotkey'):
		if not self.runtime_enabled:return
		player=self.grade_sound_players.get(GRADE_SOUND_BY_COMMAND.get(command))
		if not player:return
		now=_now()
		if source=='hook'and self.grade_sound_last_source=='hotkey'and self.grade_sound_last_command==command and now-self.grade_sound_last_played_at<.45:return
		try:
			player.stop()
			if hasattr(player,_Ak):player.setPosition(0)
			player.play();self.grade_sound_last_command=command;self.grade_sound_last_source=source;self.grade_sound_last_played_at=now
		except Exception as exc:_log(f"Grade sound playback failed ({command}): {exc}")
	def play_grade_sound_after_answer_if_needed(self,command):
		if not hasattr(gui_hooks,_B6):self.play_grade_sound(command,source='answer_fallback')
	def stop_pay_attention_timer(self):
		if self.pay_attention_timer and self.pay_attention_timer.isActive():self.pay_attention_timer.stop()
	def clear_pay_attention_audio(self,full_release=_C):
		self.pay_attention_active=_C;self.stop_pay_attention_timer()
		if self.pay_attention_player:
			try:self.pay_attention_player.stop()
			except Exception:pass
		if not full_release:return
		for attr in('pay_attention_timer','pay_attention_player','pay_attention_audio_output'):
			obj=getattr(self,attr)
			if obj is not _A:
				try:obj.stop()if hasattr(obj,'stop')else _A
				except Exception:pass
				try:obj.deleteLater()
				except Exception:pass
				setattr(self,attr,_A)
		self.pay_attention_sound_path='';self.pay_attention_warning_issued=_C
	def warn_pay_attention_unavailable(self,reason):
		if self.pay_attention_warning_issued:return
		self.pay_attention_warning_issued=_B;_log(f"Pay-attention audio unavailable: {reason}")
		try:tooltip('Focus-dim warning sound is unavailable. Check pay_attention.mp3 and QtMultimedia.',period=5500)
		except Exception:pass
	def resolve_pay_attention_sound_path(self):
		if self.pay_attention_sound_path and os.path.exists(self.pay_attention_sound_path):return self.pay_attention_sound_path
		candidates=[]
		try:media_dir=mw.col.media.dir()if getattr(mw,'col',_A)else''
		except Exception:media_dir=''
		if media_dir:candidates.append(os.path.join(media_dir,PAY_ATTENTION_SOUND_FILE))
		candidates.append(os.path.join(os.path.dirname(__file__),PAY_ATTENTION_SOUND_FILE))
		for path in candidates:
			if path and os.path.exists(path):self.pay_attention_sound_path=path;return path
		self.pay_attention_sound_path=candidates[0]if candidates else'';return''
	def ensure_pay_attention_player(self):
		if self.pay_attention_player is not _A:return _B
		if QMediaPlayer is _A:self.warn_pay_attention_unavailable('QtMultimedia not available');return _C
		sound_path=self.resolve_pay_attention_sound_path()
		if not sound_path or not os.path.exists(sound_path):self.warn_pay_attention_unavailable('pay_attention.mp3 not found in collection media or add-on folder');return _C
		player,output=self.create_media_player(sound_path)
		if not player:self.warn_pay_attention_unavailable('player init failed');return _C
		self.pay_attention_player=player;self.pay_attention_audio_output=output;return _B
	def play_pay_attention_sound(self):
		if not self.pay_attention_active or not self.ensure_pay_attention_player():return
		try:
			self.pay_attention_player.stop()
			if hasattr(self.pay_attention_player,_Ak):self.pay_attention_player.setPosition(0)
			self.pay_attention_player.play()
		except Exception as exc:_log(f"Pay-attention playback failed: {exc}");self.set_pay_attention_active(_C)
	def on_pay_attention_timer(self):
		if not self.pay_attention_active:self.stop_pay_attention_timer();return
		self.play_pay_attention_sound()
	def ensure_pay_attention_timer(self):
		if self.pay_attention_timer is _A:self.pay_attention_timer=QTimer(mw);self.pay_attention_timer.setInterval(PAY_ATTENTION_INTERVAL_MS);self.pay_attention_timer.timeout.connect(self.on_pay_attention_timer)
		return self.pay_attention_timer
	def set_pay_attention_active(self,active):
		enable=bool(active)and self.runtime_enabled
		if not enable:
			self.pay_attention_active=_C;self.stop_pay_attention_timer()
			if self.pay_attention_player:
				try:self.pay_attention_player.stop()
				except Exception:pass
			return
		was_active=self.pay_attention_active;self.pay_attention_active=_B
		if not self.ensure_pay_attention_player():self.pay_attention_active=_C;self.stop_pay_attention_timer();return
		timer=self.ensure_pay_attention_timer()
		if not timer.isActive():timer.start()
		if not was_active:self.play_pay_attention_sound()
	def init_overlay_once(self):
		self.init_overlay_timer=_A;self.last_overlay_render_key=_A;self.last_overlay_style_key=_A;self.ensure_app_state_hooks();existing=getattr(mw,_B7,_A)
		if existing is not _A:self.overlay=existing;self.start_global_listener(toggle_only=not self.runtime_enabled);self.refresh_focus_dim_controller(force_rebuild=_B);self.reconcile_overlay_visibility('init_existing',force_show=_B);self.sync_initial_review_state();return
		self.overlay=Overlay();mw._anki_overlay_instance=self.overlay;self.start_global_listener(toggle_only=not self.runtime_enabled);self.refresh_focus_dim_controller(force_rebuild=_B);self.reconcile_overlay_visibility('init_new',force_show=_B);self.sync_initial_review_state()
	def sync_initial_review_state(self):
		try:
			if mw.state==_Z and getattr(mw,_h,_A)and mw.reviewer.card:
				if mw.reviewer.state==_r:self.on_show_question(mw.reviewer.card);return
				if mw.reviewer.state==_AQ:self.on_show_answer(mw.reviewer.card);return
		except Exception:pass
		self.request_overlay_refresh(0,content=_B,style=_B,force=_B)
	def ensure_settings_action(self):
		A='Overlay Settings';action=getattr(mw,'_anki_overlay_settings_action',_A)
		if action is not _A:return
		for existing in mw.form.menuTools.actions():
			if existing.text()==A:mw._anki_overlay_settings_action=existing;return
		action=QAction(A,mw);action.triggered.connect(lambda:ConfigDialog().exec());mw.form.menuTools.addAction(action);mw._anki_overlay_settings_action=action
	def on_show_question(self,card):card_id=getattr(card,'id',_A);self.review_state=ReviewUiState.QUESTION;self.last_card_id=card_id;self.finalize_pending_on_question(card_id);self.reconcile_overlay_visibility('show_question');self.update_overlay();self.schedule_overlay_refresh(90,expected_card_id=card_id,expected_reviewer_state=_r);self.schedule_overlay_refresh(220,expected_card_id=card_id,expected_reviewer_state=_r)
	def on_show_answer(self,card):
		card_id=getattr(card,'id',_A);self.review_state=ReviewUiState.ANSWER;self.last_card_id=card_id;self.reconcile_overlay_visibility('show_answer')
		if self.pending.command==_G:self.record_command_result(_G,'ok: question->answer');self.end_transition()
		elif self.pending.command==_U:self.handle_pending_reveal_then_grade(card_id)
		elif self.pending.command==_F:
			if self.pending.source_state not in(ReviewUiState.QUESTION.value,ReviewUiState.ANSWER.value):self.record_command_result(_F,f"ignored: unexpected source state {self.pending.source_state}");self.end_transition()
			elif self.pending.source_state==ReviewUiState.ANSWER.value and self.pending.card_id is not _A and card_id==self.pending.card_id:self.record_command_result(_F,_Ah);self.end_transition()
			else:self.record_command_result(_F,'ok');self.end_transition()
		elif self.pending.command in(_N,_O,_P,_Q):self.record_command_result(self.pending.command,'pending: waiting for question')
		self.update_overlay();self.schedule_overlay_refresh(90,expected_card_id=card_id,expected_reviewer_state=_AQ)
	def on_reviewer_answered_card(self,*args):
		if not self.runtime_enabled:return
		ease=next((value for value in reversed(args)if isinstance(value,int)and 1<=value<=4),_A);command=GRADE_SOUND_COMMAND_BY_EASE.get(ease)
		if command:self.mark_review_activity(_B5,_B);self.play_grade_sound(command,source='hook')
	def reset_runtime_state(self):self.review_state=ReviewUiState.IDLE;self.last_card_id=_A;self.last_hotkey_captured='';self.last_command_attempted='';self.last_command_result='';self.pending=TransitionState();self.last_command_time={};self.focus=FocusDimState();self.transition_watchdog_last_snapshot=_A;self.overlay_user_hidden=_C;self.overlay_auto_hidden_by_window=_C;self.overlay_last_screen_key=_A;self.overlay_last_visibility_signature=_A;self.overlay_visibility_reconcile_pending=_C;self.overlay_visibility_reconcile_force_show=_C;self.overlay_visibility_reconcile_reason='';self.last_overlay_render_key=_A;self.last_overlay_style_key=_A;self.last_external_overlay_refresh_at=_D;self.grade_sound_last_command='';self.grade_sound_last_source='';self.grade_sound_last_played_at=_D;self.pay_attention_active=_C;self.pay_attention_warning_issued=_C;self.debug_refresh_requests=0;self.debug_refresh_runs=0;self.debug_force_refresh_runs=0;self.debug_visibility_reconciles=0;self.debug_watchdog_ticks=0;self.debug_watchdog_state_changes=0;self.debug_last_counter_log_at=_D;self.clear_overlay_refresh_queue(stop_timer=_C)
	def on_profile_close(self,*_args):
		self.addon_active=_C;self.runtime_enabled=_B;self.stop_global_listener();self.stop_transition_watchdog();self.stop_focus_dim_timer();self.disconnect_app_state_hooks();self.disconnect_focus_dim_screen_hooks()
		for attr in('init_overlay_timer','focus_dim_timer','transition_watchdog_timer','overlay_refresh_timer'):
			timer=getattr(self,attr)
			if timer is not _A:
				try:timer.stop();timer.deleteLater()
				except Exception:pass
				setattr(self,attr,_A)
		self.clear_grade_sounds();self.clear_pay_attention_audio(full_release=_B);self.clear_focus_dim_overlays()
		if self.overlay:
			try:self.overlay.hide();self.overlay.deleteLater()
			except Exception:pass
			self.overlay=_A
		if hasattr(mw,_B7):mw._anki_overlay_instance=_A
		self.reset_runtime_state()
	def on_profile_open(self):
		self.addon_active=_B;self.runtime_enabled=_B;self.reset_runtime_state();self.ensure_app_state_hooks()
		if self.init_overlay_timer:
			try:self.init_overlay_timer.stop();self.init_overlay_timer.deleteLater()
			except Exception:pass
		self.init_overlay_timer=QTimer(mw);self.init_overlay_timer.setSingleShot(_B);self.init_overlay_timer.timeout.connect(self.init_overlay_once);self.init_overlay_timer.start(1000);self.ensure_settings_action();self.init_grade_sounds();self.refresh_focus_dim_controller(force_rebuild=_B)
	def atexit_cleanup(self):
		self.addon_active=_C
		for action in(self.stop_transition_watchdog,self.stop_global_listener,self.stop_focus_dim_timer,self.disconnect_app_state_hooks,self.clear_grade_sounds,lambda:self.clear_pay_attention_audio(full_release=_B),lambda:self.clear_overlay_refresh_queue(stop_timer=_B)):
			try:action()
			except Exception:pass
_controller=OverlayController()
def get_config():return _controller.get_config()
def _get_config_view():return _controller.get_config_view()
def save_config(conf):return _controller.save_config(conf)
def update_overlay():return _controller.update_overlay()
def _init_overlay_once():return _controller.init_overlay_once()
def _ensure_settings_action():return _controller.ensure_settings_action()
def _on_show_question(card):return _controller.on_show_question(card)
def _on_show_answer(card):return _controller.on_show_answer(card)
def _on_reviewer_answered_card(*args):return _controller.on_reviewer_answered_card(*args)
def _on_undo_state_did_change(*_args):return _controller.schedule_external_overlay_refresh('undo_state')
def _on_operation_did_execute(*_args):return _controller.schedule_external_overlay_refresh(_B8)
def _on_profile_close(*args):return _controller.on_profile_close(*args)
def on_profile_open():return _controller.on_profile_open()
def _atexit_cleanup():return _controller.atexit_cleanup()
if not getattr(mw,'_anki_overlay_hooks_registered',_C):
	gui_hooks.profile_did_open.append(on_profile_open);gui_hooks.reviewer_did_show_question.append(_on_show_question);gui_hooks.reviewer_did_show_answer.append(_on_show_answer)
	if hasattr(gui_hooks,'undo_state_did_change'):gui_hooks.undo_state_did_change.append(_on_undo_state_did_change)
	if hasattr(gui_hooks,_B8):gui_hooks.operation_did_execute.append(_on_operation_did_execute)
	if hasattr(gui_hooks,_B6):gui_hooks.reviewer_did_answer_card.append(_on_reviewer_answered_card)
	if hasattr(gui_hooks,'profile_will_close'):gui_hooks.profile_will_close.append(_on_profile_close)
	if hasattr(gui_hooks,'main_window_will_close'):gui_hooks.main_window_will_close.append(_on_profile_close)
	mw._anki_overlay_hooks_registered=_B
if not getattr(mw,'_anki_overlay_atexit_registered',_C):atexit.register(_atexit_cleanup);mw._anki_overlay_atexit_registered=_B
