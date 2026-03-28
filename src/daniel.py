import re
import tiktoken

# 1. THE MASSIVE DICTIONARY (Hierarchical: Longest patterns first)
COMPRESSION_MAP = {
    r"\b(can you|could you|would you|will you|i want you to|i need you to)\b": "",
    r"\b(please|kindly|if you don't mind|if possible|at your convenience)\b": "",
    r"\b(thank you|thanks|i appreciate it|much appreciated)\b": "",
    r"\b(i am|i'm) (looking|trying) to (understand|find|get)\b": "",
    r"\b(as an ai|as a large language model|as a helpful assistant)\b": "",
    r"\b(it would be helpful if you could|it'd be great if you could)\b": "",
    r"\b(feel free to|go ahead and)\b": "",
    r"\b(let's|let us) (begin|start|take a look|examine)\b": "",

    r"\b(provide|give|write|draft) (a|an|the) (detailed|thorough|complete) (explanation|desc|summary) of\b": "explain",
    r"\b(create|make|generate|build|construct) (a|an|the) (list|table|chart) of\b": "list",
    r"\b(write|create|generate|code|program) (the|some|a) (python|java|c\+\+) (script|code|snippet) (to|for)\b": "code:",
    r"\b(summarize|condense|shorten|boil down) (the|this|following) (text|doc|file)\b": "summarize",
    r"\b(solve|calculate|compute|work out) (the|this|following) (math|equation|formula|problem)\b": "solve:",
    r"\b(debug|fix|find the errors in|troubleshoot) (this|the|my) (code|script)\b": "fix:",
    r"\b(compare and contrast|show the differences between)\b": "compare",
    r"\b(translate|convert|change) (this|the) (from|to)\b": "convert",

    r"\b(in addition to|as well as|along with|plus)\b": "&",
    r"\b(leads to|results in|outputs|consequently|so that)\b": "->",
    r"\b(therefore|as a result|which means that|thus)\b": "=>",
    r"\b(is the same as|is equal to|the equivalent of)\b": "=",
    r"\b(approximately|roughly|about|around|nearly)\b": "~",
    r"\b(on the other hand|alternatively|instead of|rather than)\b": "vs",
    r"\b(for example|for instance|such as|e\.g\.)\b": "ex:",
    r"\b(with (regards|respect) to|regarding|about the topic of)\b": "re:",

    r"\b(in order to|for the purpose of|with the intent to)\b": "to",
    r"\b(due to the fact that|because of the fact that|owing to)\b": "because",
    r"\b(at the present time|at this point in time|currently)\b": "now",
    r"\b(a (large|wide) (number|variety|array|range) of)\b": "many",
    r"\b(in the event that|if it should happen that)\b": "if",
    r"\b(it is (important|crucial|vital) to (note|mention))\b": "note:",
    r"\b(basically|essentially|actually|literally|fundamentally)\b": "",
    r"\b(thoroughly|carefully|exhaustively|completely|highly)\b": "",
    r"\b(very|extremely|really|quite|definitely)\b": "",

    r"\b(the following|this|below) (text|code|data|input|context) is\b": "input:",
    r"\b(step-by-step|in a series of steps|sequentially)\b": "steps:",
    r"\b(no more than|not exceeding|at most|a maximum of)\b": "max",
    r"\b(at least|no less than|a minimum of)\b": "min",
    r"\b(in the style of|written like|imitate)\b": "style:",
}

TYPO_SHORTHAND_MAP = {
    # --- 1. POLITENESS MANGLED ---
    r"\bpl[eaz]{1,4}s?e?\b": "",               # please, plz, plez, pleese, plse
    r"\bth[axnk]{1,4}s?\b": "",                # thanks, thx, thnx, tnk, thankyou
    r"\b(sry|sorr?y|soary)\b": "",             # sorry, sry, sorrey
    r"\b(knly|kindl[yie]{1,3})\b": "",         # kindly, knly, kindli
    
    # --- 2. COMMON INSTRUCTIONAL TYPOS ---
    r"\b(summariz[e|ation]|sumary|summry|sumerize)\b": "summarize",
    r"\b(expl[ai]{1,2}n[ation]{0,4}|expln)\b": "explain",
    r"\b(descr[ibe|ption]{1,5}|desc)\b": "describe",
    r"\b(generat[e|ion]{1,3}|gen|genrate)\b": "generate",
    r"\b(calculat[e|ion]{1,3}|calc)\b": "calculate",
    r"\b(analys[is|ize]|analize|analys)\b": "analyze",
    r"\b(diff|diff[erence]{1,5}|difrence)\b": "diff",
    
    # --- 3. CHAT SLANG & SHORTENINGS ---
    r"\b(u|ur|u're)\b": "you",                  # Standardizes for later rules
    r"\b(r|are)\b": "are",
    r"\b(b/c|bc|bcs|bcause|cause|coz)\b": "because",
    r"\b(w/|wth)\b": "with",
    r"\b(w/o)\b": "without",
    r"\b(info|informat[ion]{1,3})\b": "info",
    r"\b(msg|mess[age]{1,3})\b": "msg",
    r"\b(img|im[age]{1,3})\b": "img",
    r"\b(approx|approx[imately]{1,8})\b": "~",
    
    # --- 4. ACCIDENTAL REPEATS ---
    # This catches "the the" or "and and"
    r"\b(\w+)\s+\1\b": r"\1", 
    
    # --- 5. AI-SPECIFIC MANGLES ---
    r"\bas\s+an?\s+ai\b": "",                  # "as an ai", "as a ai"
    r"\blanguag\s+modl\b": "",                 # common misspellings of "language model"
}

# Add this to your existing map
COMPRESSION_MAP.update(TYPO_SHORTHAND_MAP)

def regex_condenser(raw_text, model="gpt-4"):
    # Initialize Tokenizer (Local)
    encoding = tiktoken.encoding_for_model(model)
    start_tokens = len(encoding.encode(raw_text))
    
    # Process Map
    text = raw_text
    for pattern, replacement in COMPRESSION_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Final Cleanup: Remove double spaces and strip edges
    text = " ".join(text.split()).strip()
    
    end_tokens = len(encoding.encode(text))
    
    return {
        "original": raw_text,
        "condensed": text,
        "savings": start_tokens - end_tokens,
        "percent": round(((start_tokens - end_tokens) / start_tokens) * 100, 1) if start_tokens > 0 else 0
    }

# --- TEST ---
prompt = "You are an experienced career coach and former hiring manager in the tech industry. I am a recent graduate with a degree in computer science, and I am trying to decide between pursuing a career in software engineering or data analysis. I enjoy problem-solving and building things, but I also like working with data and identifying patterns and insights. I have intermediate skills in Python, basic knowledge of SQL, and some experience with web development including HTML, CSS, and JavaScript. I have completed two internships, one focused on frontend development and another involving data cleaning and visualization. I value work-life balance, strong long-term salary growth, and opportunities to work remotely. Please compare software engineering and data analysis across factors such as salary, job demand, daily responsibilities, required skills, and long-term career growth. Based on my background and preferences, recommend which path would be a better fit for me and explain your reasoning. Then provide a detailed six-month plan outlining what I should learn, what types of projects I should build, and how I should approach applying for jobs. Finally, suggest two or three specific portfolio project ideas that would help me stand out to employers in your recommended path, and present your response in a clear and practical way.---"
data = regex_condenser(prompt)

print(f"OUT: {data['condensed']}")
print(f"SAVED: {data['savings']} tokens ({data['percent']}%)")