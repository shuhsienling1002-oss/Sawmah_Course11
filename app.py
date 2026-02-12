import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="Ira to kako a minokay - 我回來了", 
    page_icon="🏠", 
    layout="centered"
)

# --- 1. 資料庫 (第 1 課：Ira to kako a minokay) ---
VOCAB_MAP = {
    "ina": "媽媽", "ira": "有/在/到達", "to": "了(完成貌)", "kako": "我", "a": "連綴詞",
    "minokay": "回家", "kiso": "你", "macahiw": "肚子餓", "o": "是/主格",
    "maan": "什麼", "ko": "主格標記", "kaolahan": "喜歡的/想要的", "iso": "你的",
    "mangalay": "想要", "komaen": "吃", "konga": "地瓜", "hay": "好/是的",
    "i": "在(介係詞)", "parad": "桌子/長凳", "alaen": "拿(祈使/被拿)"
}

VOCABULARY = [
    {"amis": "minokay", "zh": "回家/回來", "emoji": "🏠", "root": "nokay", "root_zh": "回家"},
    {"amis": "macahiw", "zh": "肚子餓了", "emoji": "🤤", "root": "cahiw", "root_zh": "餓"},
    {"amis": "kaolahan", "zh": "所喜愛的", "emoji": "💖", "root": "olah", "root_zh": "喜愛"},
    {"amis": "konga", "zh": "地瓜", "emoji": "🍠", "root": "konga", "root_zh": "地瓜"},
    {"amis": "parad", "zh": "桌子/長凳", "emoji": "🪑", "root": "parad", "root_zh": "平台"},
    {"amis": "ala", "zh": "取得/拿取", "emoji": "🖐️", "root": "ala", "root_zh": "拿"},
]

SENTENCES = [
    {
        "amis": "Ina, ira to kako a minokay.", 
        "zh": "媽媽，我回來了。", 
        "note": """
        <br><b>ira</b>：存在動詞（在此指到達/在現場）。
        <br><b>to</b>：完成貌助詞，表示狀態已改變。
        <br><b>kako</b>：主格代名詞「我」。
        <br><b>a</b>：連綴詞，連接主要動詞與次要動作。
        <br><b>minokay</b>：動詞，由詞根 nokay 加 mi- 綴構成。"""
    },
    {
        "amis": "O maan ko kaolahan iso?", 
        "zh": "你想要/喜歡什麼？", 
        "note": """
        <br><b>O maan</b>：疑問句首，意為「是什麼」。
        <br><b>ko</b>：主格標記，引導全句主語。
        <br><b>kaolahan</b>：由詞根 olah (喜愛) 加上環綴 ka...an 構成的名詞化動詞，指「所喜愛的事物」。
        <br><b>iso</b>：屬格代名詞「你的」。"""
    },
    {
        "amis": "Hay, ira i parad ko konga, alaen.", 
        "zh": "好，地瓜在桌子上，去拿吧。", 
        "note": """
        <br><b>Hay</b>：肯定感嘆詞「是/好」。
        <br><b>i parad</b>：介系詞結構，i (在) + parad (桌子/長凳)。
        <br><b>alaen</b>：詞根 ala (拿) + 受事焦點後綴 -en，在祈使語境下表示「(地瓜)要被拿/去拿吧」。"""
    }
]

STORY_DATA = [
    {"amis": "Ina, ira to kako a minokay.", "zh": "媽媽，我回來了。"},
    {"amis": "A! Ira to kiso a minokay!", "zh": "阿！你回來了！"},
    {"amis": "Macahiw kako.", "zh": "我肚子餓了。"},
    {"amis": "O maan ko kaolahan iso?", "zh": "你想要吃什麼？"},
    {"amis": "Mangalay kako a komaen to konga.", "zh": "我想要吃地瓜。"},
    {"amis": "Hay, ira i parad ko konga, alaen.", "zh": "好，地瓜在桌子上，去拿吧。"}
]

# --- 2. 視覺系統 (CSS 注入) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    .stApp { background-color: #0a0e05; color: #ECF0F1; font-family: 'Noto Sans TC', sans-serif; }
    .header-container { background: rgba(0, 20, 0, 0.8); border: 2px solid #39FF14; box-shadow: 0 0 20px rgba(57, 255, 20, 0.3); border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 30px; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #39FF14; font-size: 40px; text-shadow: 0 0 10px #39FF14; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.05); }
    .stTabs [aria-selected="true"] { border: 1px solid #39FF14; color: #39FF14 !important; font-weight: bold; }
    .stButton>button { border: 1px solid #39FF14 !important; background: transparent !important; color: #39FF14 !important; width: 100%; border-radius: 5px; }
    .stButton>button:hover { background: #39FF14 !important; color: #000 !important; }
    
    .quiz-card { background: rgba(20, 30, 20, 0.9); border: 1px solid #39FF14; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .quiz-tag { background: #39FF14; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; margin-right: 10px; }
    
    .zh-translation-block {
        background: rgba(20, 20, 20, 0.6);
        border-left: 4px solid #AAA;
        padding: 20px;
        margin-top: 0px; 
        border-radius: 5px;
        color: #CCC;
        font-size: 16px;
        line-height: 2.0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 (v9.0) ---
def get_html_card(item, type="word"):
    # 設定：full_amis_block 依然保持 100px padding (防切頭)，下方負邊距拉近
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        body {{ background-color: transparent; color: #ECF0F1; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 1px dashed #39FF14; cursor: pointer; margin: 0 3px; color: #EEE; transition: 0.3s; font-size: 19px; }}
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 60px; background-color: #000; color: #39FF14; text-align: center; border: 1px solid #39FF14; border-radius: 6px; padding: 5px; position: absolute; z-index: 100; bottom: 135%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        .play-btn-inline {{ background: rgba(57, 255, 20, 0.1); border: 1px solid #39FF14; color: #39FF14; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #39FF14; color: #000; transform: scale(1.1); }}
        
        /* 單字卡樣式 */
        .word-card-static {{ background: rgba(20, 30, 20, 0.9); border: 1px solid #39FF14; border-left: 5px solid #39FF14; padding: 15px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; }}
        .wc-root-tag {{ font-size: 12px; background: #39FF14; color: #000; padding: 2px 6px; border-radius: 3px; font-weight: bold; }}
        .wc-amis {{ color: #39FF14; font-size: 24px; font-weight: bold; margin: 5px 0; }}
        .wc-zh {{ color: #FFF; font-size: 16px; font-weight: bold; }}
        .play-btn-large {{ background: transparent; border: 1px solid #39FF14; color: #39FF14; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; }}
        
        /* 阿美語全文區塊樣式 */
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#BBB;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        # 互動課文區塊：產生帶發音與翻譯的單字 Span
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        # 句型解析區塊
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:rgba(57, 255, 20, 0.1); border:1px solid #39FF14; color:#39FF14; padding:5px 12px; border-radius:4px; cursor:pointer;" onclick="speak(`{full_js}`)">▶ 播放整句</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 (Logic Hardened) ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#39FF14'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#39FF14'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    # 安全檢查：如果詞根不夠，補一些假詞根
    if len(other_roots) < 2: other_roots += ["roma", "lalan", "cidal"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#39FF14'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#39FF14'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字 (修正：精準挖空邏輯)
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    # 找出所有在字典裡的字 (忽略標點)
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx] # 例如 "Ina,"
        target_clean = re.sub(r"[^\w']", "", target_raw).lower() # "ina"
        
        # 顯示題目：把那個字挖掉
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        # 選項：必須是乾淨的單字，不帶標點
        correct_ans = target_clean # 正確答案存為 "ina" (乾淨版)
        
        # 干擾項
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans]
        if len(distractors) < 2: distractors += ["kako", "ira"] # Fallback
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#FFF; font-size:18px;'>{q_text}</span><br><span style='color:#BBB; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    
    else:
        # 如果句子太短沒字可挖，回退到聽力題
        questions.append(questions[0]) 

    # 8. 補一題 (隨機)
    questions.append(random.choice(questions[:4])) 

    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 ---
st.markdown("""<div class="header-container"><h1 class="main-title">Ira to kako a minokay</h1><div style="color: #39FF14; letter-spacing: 5px;">第 1 課：我回來了</div><div style="font-size: 12px; margin-top:10px; color:#888;">講師：高生榮 | 教材：高生榮</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🐜 互動課文", "📖 核心單字", "🧬 句型解析", "⚔️ 實戰測驗"])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 上方為阿美語(可點擊查義/發音)，下方為對應中文翻譯")
    
    st.markdown("""<div style="background:rgba(20,20,20,0.6); padding:10px; border-left:4px solid #39FF14; border-radius:5px 5px 0 0;">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字練習")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 句型分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:rgba(57,255,20,0.05); padding:15px; border:1px dashed #39FF14; border-radius: 5px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#FFF; font-size:16px; margin-bottom:10px; border-top:1px solid #333; padding-top:10px;">{s['zh']}</div>
        <div style="color:#CCC; font-size:14px; line-height:1.8; border-top:1px dashed #555; padding-top:5px;"><span style="color:#39FF14; font-family:Orbitron; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#888;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#FFF; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    # 判斷邏輯：統一轉小寫比對 (避免 Ina vs ina 問題)
                    if opt.lower() == q['correct'].lower():
                        st.success("通過 (Access Granted)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:2px solid #39FF14; background:rgba(57,255,20,0.1);"><h2 style="color:#39FF14">MISSION COMPLETE</h2><p>得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("重新啟動系統 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("協作單位：桃園市阿美族三一教育文化協會")


