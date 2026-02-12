import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="Ira to kako - 我回來了", 
    page_icon="🏠", 
    layout="centered"
)

# --- 1. 資料庫 (居家生活 第 1 課) ---
VOCAB_MAP = {
    "ira": "有/存在", "to": "了", "kako": "我", "minokay": "回家", 
    "o": "噢(感嘆)", "kiso": "你", "pahanhan": "休息", "ho": "先/還", 
    "awaay": "沒有/不在", "ko": "主格標記", "tao": "人/別人", 
    "i": "在", "loma'": "家", "papotal": "外面", "ci": "人名標記", 
    "ama": "爸爸"
}

VOCABULARY = [
    {"amis": "minokay", "zh": "回家", "emoji": "🏠", "root": "nokay", "root_zh": "歸"},
    {"amis": "pahanhan", "zh": "休息/呼吸", "emoji": "🛋️", "root": "hanhan", "root_zh": "氣息"},
    {"amis": "awaay", "zh": "沒有/不在", "emoji": "🈳", "root": "awa", "root_zh": "無"},
    {"amis": "papotal", "zh": "外面/庭院", "emoji": "🌳", "root": "potal", "root_zh": "外"},
    {"amis": "tao", "zh": "人/別人", "emoji": "👥", "root": "tao", "root_zh": "他人"},
    {"amis": "ira", "zh": "有/存在", "emoji": "✅", "root": "ira", "root_zh": "有"},
    {"amis": "loma'", "zh": "家", "emoji": "🏡", "root": "loma'", "root_zh": "家"},
]

SENTENCES = [
    {
        "amis": "Ira to kako minokay.", 
        "zh": "我回來了。", 
        "note": """
        <br><b>Ira</b>：有/存在 (這裡指「出現」)。
        <br><b>結構</b>：Ira + 主詞 + 動作。
        <br><b>語感</b>：這是一種「宣告」。不只是說「我回家了」，而是強調「我的人已經出現在這裡了」。"""
    },
    {
        "amis": "O, minokay to kiso!", 
        "zh": "噢，你回來啦！", 
        "note": """
        <br><b>O</b>：感嘆詞，表示驚訝或確認。
        <br><b>to</b>：了 (狀態改變)。
        <br><b>情境</b>：家人確認對方歸來的自然反應。"""
    },
    {
        "amis": "Pahanhan ho.", 
        "zh": "先休息一下吧。", 
        "note": """
        <br><b>Pahanhan</b>：休息 (原意與 <i>hanhan</i> 呼吸有關，指喘口氣)。
        <br><b>ho</b>：先/暫且 (祈使語氣)。
        <br><b>省略</b>：省略了主詞 <i>kiso</i>，直接建議對方休息。"""
    },
    {
        "amis": "Awaay ko tao i loma'?", 
        "zh": "家裡沒人嗎？", 
        "note": """
        <br><b>Awaay</b>：沒有/不在 (Ira 的相反詞)。
        <br><b>tao</b>：別人/人 (這裡指家裡的其他人)。
        <br><b>句型</b>：Awaay ko... (沒有...)。"""
    },
    {
        "amis": "Ira, i papotal ci Ama.", 
        "zh": "有，爸爸在外面。", 
        "note": """
        <br><b>papotal</b>：外面/庭院。
        <br><b>Ci vs Ko</b>：
        <br>🔸 <b>Ko</b>：用於普通名詞 (如 <i>ko tao</i>)。
        <br>🔹 <b>Ci</b>：專用於人名或親屬稱謂 (如 <i>ci Ama</i>)。"""
    }
]

STORY_DATA = [
    {"amis": "Ira to kako minokay.", "zh": "我回來了。"},
    {"amis": "O, minokay to kiso!", "zh": "噢，你回來啦！"},
    {"amis": "Pahanhan ho.", "zh": "先休息一下吧。"},
    {"amis": "Awaay ko tao i loma'?", "zh": "家裡沒人嗎？"},
    {"amis": "Ira, i papotal ci Ama.", "zh": "有，爸爸在外面。"}
]

# --- 2. 視覺系統 (CSS 注入 - 溫馨暖橘主題) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
.stApp { background-color: #FFF8E1; color: #5D4037; font-family: 'Noto Sans TC', sans-serif; }
.stTabs [data-baseweb="tab"] { color: #8D6E63 !important; font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-size: 18px; font-weight: 700; }
.stTabs [aria-selected="true"] { border-bottom: 4px solid #E65100 !important; color: #E65100 !important; }
.stButton>button { border: 2px solid #FF9800 !important; background: #FFFFFF !important; color: #E65100 !important; font-family: 'Nunito', 'Noto Sans TC', sans-serif !important; font-size: 18px !important; font-weight: 700 !important; width: 100%; border-radius: 12px; }
.stButton>button:hover { background: #FF9800 !important; color: #FFFFFF !important; }
.quiz-card { background: #FFFFFF; border: 2px solid #FFCC80; padding: 25px; border-radius: 12px; margin-bottom: 20px; }
.quiz-tag { background: #E65100; color: #FFF; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 14px; margin-right: 10px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }
.zh-translation-block { background: #FFF3E0; border-left: 5px solid #FF9800; padding: 20px; color: #5D4037; font-size: 16px; line-height: 2.0; font-family: 'Noto Sans TC', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 ---
def get_html_card(item, type="word"):
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
        body {{ background-color: transparent; color: #5D4037; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 2px solid #FF9800; cursor: pointer; margin: 0 3px; color: #5D4037; transition: 0.3s; font-size: 19px; font-weight: 600; }}
        .interactive-word:hover {{ color: #E65100; border-bottom-color: #E65100; }}
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #E65100; color: #FFF; text-align: center; border-radius: 8px; padding: 8px; position: absolute; z-index: 100; bottom: 145%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-weight: 700; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        .play-btn-inline {{ background: #FF9800; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #E65100; transform: scale(1.1); }}
        .word-card-static {{ background: #FFFFFF; border: 1px solid #FFE0B2; border-left: 6px solid #FF9800; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; box-shadow: 0 3px 6px rgba(0,0,0,0.05); }}
        .wc-root-tag {{ font-size: 12px; background: #FFF3E0; color: #E65100; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }}
        .wc-amis {{ color: #E65100; font-size: 26px; font-weight: 900; margin: 2px 0; font-family: 'Nunito', sans-serif; }}
        .wc-zh {{ color: #5D4037; font-size: 16px; font-weight: 500; }}
        .play-btn-large {{ background: #FFF3E0; border: 2px solid #FF9800; color: #E65100; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #E65100; color: #FFF; }}
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
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#757575;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
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
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#E65100; border:none; color:#FFF; padding:6px 15px; border-radius:8px; cursor:pointer; font-family:Nunito; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
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
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#E65100'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#E65100'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["nokay", "hanhan", "awa"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#E65100'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#E65100'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2]
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#E65100; font-size:18px;'>{q_text}</span><br><span style='color:#5D4037; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    questions.append(random.choice(questions[:4])) 
    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (使用 components.html 隔離渲染標題) ---
# 主題：溫馨暖橘 (Warm Home) - 居家、舒適、木質調
header_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@900&family=Noto+Sans+TC:wght@700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Noto Sans TC', sans-serif; text-align: center; }
        .container {
            background: linear-gradient(180deg, #E65100 0%, #8D6E63 100%);
            border-bottom: 6px solid #5D4037;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            color: #FFFFFF; /* 強制白色 */
        }
        h1 {
            font-family: 'Nunito', sans-serif;
            color: #FFFFFF !important; /* 強制白色 */
            font-size: 48px;
            margin: 0 0 10px 0;
            text-shadow: 3px 3px 0 #000000;
            letter-spacing: 2px;
        }
        .subtitle {
            color: #FFE0B2; /* 亮米黃 */
            border: 1px solid #FFE0B2;
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            padding: 5px 20px;
            display: inline-block;
            font-weight: bold;
            font-size: 18px;
        }
        .footer {
            margin-top: 10px;
            font-size: 12px;
            color: #FFCC80;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ira to kako</h1>
        <div class="subtitle">第 1 課：我回來了</div>
        <div class="footer">Code-CRF v6.5 | Theme: Warm Home (Cozy)</div>
    </div>
</body>
</html>
"""

components.html(header_html, height=220)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 互動課文", 
    "🛋️ 核心單字", 
    "🧬 句型解析", 
    "⚔️ 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    st.markdown("""<div style="background:#FFFFFF; padding:10px; border: 2px solid #FFCC80; border-radius:12px;">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與詞根")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:15px; border:1px dashed #E65100; border-radius: 12px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#BF360C; font-size:16px; margin-bottom:10px; border-top:1px solid #FFCC80; padding-top:10px;">{s['zh']}</div>
        <div style="color:#E65100; font-size:14px; line-height:1.8; border-top:1px dashed #FFCC80; padding-top:5px;"><span style="color:#BF360C; font-family:Nunito; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#5D4037;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#E65100; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ 正確 (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ 錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:4px solid #E65100; border-radius:15px; background:#FFFFFF;"><h2 style="color:#BF360C; font-family:Nunito;">MISSION COMPLETE</h2><p style="font-size:20px; color:#E65100;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v6.5 | Architecture: Chief Architect")
