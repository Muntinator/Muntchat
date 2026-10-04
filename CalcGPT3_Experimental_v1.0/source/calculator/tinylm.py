# Generated TinyLM for TI-Nspire CX II. Inference only; no training dependency.
# CalcGPT 3 runtime, format 13 data. Pure TI Python; no Ndless, no libraries.
from math import exp, tanh
from random import random
from ti_system import get_key, get_time_ms, recall_list, store_list
from ti_draw import *

VERSION="3.1"
FORMAT=13

# ---------------------------------------------------------------- data loading
# Weights are stored as packed signed bytes: two values per TI list element,
# chunked at 800 elements per named list. Nothing ever rebuilds the whole model.
def load_chunks(prefix,count):
    result=[]
    for part in range(int(count)):
        result.extend(recall_list(prefix+str(part)))
    return result

def load_tensor(prefix,count):
    result=[]
    for part in range(int(count)):
        result.append(recall_list(prefix+str(part)))
    return result

def qvalue(tensor,index):
    """Decode one signed value. Used only for rare unaligned/odd tail elements."""
    packed=index//2; part=packed//800
    value=int(tensor[part][packed-part*800])
    if index%2==0: return value//256-128
    return value%256-128

try:
    INFO=recall_list("tdinfo")
    if int(INFO[0])!=FORMAT: raise ValueError
    E=int(INFO[1]); H=int(INFO[2]); TRAINED_EPOCHS=int(INFO[3]); N=int(INFO[4])
    LENS=[int(x) for x in recall_list("tdlens")]
    S=recall_list("tdscale")
    QPARTS=[int(x) for x in recall_list("tdqp")]
    Q=[None,None,None,None,None,None,None]
    chars=[int(x) for x in load_chunks("tdvc",INFO[5])]
    VOCAB=[]; word=""
    for value in chars:
        if value==0: VOCAB.append(word); word=""
        else: word+=chr(value)
    assoc=load_chunks("tda",INFO[6])
except Exception:
    print("CalcGPT 3 model data is not installed in this problem.")
    print("If you are upgrading from an older release, press ESC, delete the old")
    print("tinydata program, paste the generated tinydata programs (tinydata,")
    print("tinydata2, ... in order), run them once, then run tinylm again.")
    raise SystemExit

# ---------------------------------------------------------------- model tables
LOOKUP={}
for i in range(N): LOOKUP[VOCAB[i]]=i
FIRST_WORD=6
while FIRST_WORD<N and VOCAB[FIRST_WORD][:1]=="<": FIRST_WORD+=1
PRONOUN_IDS={}
for word in ("i","you","he","she","we","they","me","him","her","us","them"):
    if word in LOOKUP: PRONOUN_IDS[LOOKUP[word]]=1
PROFANITY_IDS={}
for token in range(N):
    word=VOCAB[token].lower()
    blocked=(word in ("hell","damn","ass") or word[:4] in ("fuck","shit") or
             word[:5] in ("bitch",) or word[:7] in ("bastard",))
    if blocked: PROFANITY_IDS[token]=1
GENDER_IDS={}
for word in ("man","woman","men","women","boy","girl","boys","girls",
             "male","female","husband","wife","he","she","him","her","his","hers"):
    if word in LOOKUP: GENDER_IDS[LOOKUP[word]]=1
CONTINUATION_IDS={}
for word in ("a","an","the","this","that","these","those","my","your","our",
             "his","her","their","some","any","very","too","and","or","but",
             "to","of","in","on","at","from","with","for","by","about"):
    if word in LOOKUP: CONTINUATION_IDS[LOOKUP[word]]=1
PUNCT_IDS={}
for word in (".","!","?",",",";",":"):
    if word in LOOKUP: PUNCT_IDS[LOOKUP[word]]=1
ASSOCIATIONS={}
pos=0
while pos<len(assoc):
    prompt=assoc[pos]*256+assoc[pos+1]; count=assoc[pos+2]; pos+=3
    mapping={}
    for i in range(count):
        token=assoc[pos]*256+assoc[pos+1]; weight=1.8*assoc[pos+2]/255.0; pos+=3
        mapping[token]=weight
    ASSOCIATIONS[prompt]=mapping

# ------------------------------------------------------- dialogue conditioning
intent=(117, 73, 42, 24, 0, 119, 11, 235, 7, 2, 1, 145, 210, 16, 16, 12, 2, 22, 210, 26, 13, 6, 1, 61, 199, 23, 19, 13, 0, 211, 200, 17, 24, 14, 1, 99, 206, 33, 10, 6, 1, 171, 197, 28, 18, 12, 1, 120, 199, 31, 15, 10, 2, 59, 192, 17, 30, 16, 1, 43, 192, 32, 19, 12, 0, 29, 37, 193, 19, 6, 1, 186, 199, 1, 11, 45, 0, 248, 183, 29, 24, 19, 2, 55, 181, 26, 28, 20, 0, 153, 179, 26, 25, 24, 2, 9, 187, 35, 19, 14, 2, 19, 182, 33, 26, 13, 2, 3, 184, 35, 29, 7, 0, 240, 181, 32, 29, 12, 1, 115, 177, 29, 29, 20, 0, 82, 48, 196, 7, 3, 0, 41, 31, 184, 36, 4, 1, 98, 186, 39, 19, 11, 0, 193, 181, 34, 23, 16, 2, 25, 180, 34, 32, 9, 0, 205, 177, 31, 28, 19, 2, 102, 172, 28, 28, 28, 1, 112, 177, 34, 23, 21, 1, 59, 177, 34, 29, 16, 0, 138, 183, 40, 20, 12, 1, 166, 178, 36, 23, 19, 0, 139, 48, 190, 14, 3, 2, 124, 185, 44, 15, 11, 0, 131, 176, 35, 29, 15, 1, 178, 176, 22, 36, 21, 1, 173, 180, 40, 23, 12, 0, 213, 176, 36, 27, 17, 0, 230, 175, 36, 27, 17, 2, 83, 171, 30, 34, 20, 1, 254, 184, 47, 16, 8, 0, 115, 42, 179, 28, 6, 1, 152, 169, 22, 33, 30, 1, 63, 176, 40, 21, 18, 1, 8, 184, 49, 15, 7, 1, 42, 172, 31, 38, 13, 0, 128, 174, 40, 20, 21, 0, 77, 166, 30, 27, 32, 2, 125, 170, 24, 37, 24, 2, 119, 175, 42, 23, 15, 1, 198, 176, 23, 43, 14, 0, 223, 171, 26, 38, 20, 0, 74, 38, 23, 169, 25, 0, 25, 42, 173, 28, 11, 2, 63, 168, 30, 38, 20, 0, 204, 175, 45, 26, 8, 0, 129, 164, 34, 31, 27, 0, 42, 164, 31, 34, 27, 2, 7, 167, 38, 34, 16, 1, 114, 168, 39, 31, 17, 1, 87, 178, 49, 19, 9, 0, 151, 170, 41, 23, 20, 0, 51, 164, 31, 35, 25, 2, 61, 172, 44, 25, 13, 1, 79, 170, 42, 37, 6, 0, 250, 166, 38, 24, 28, 0, 137, 180, 52, 17, 6, 1, 239, 175, 48, 26, 5, 1, 133, 173, 22, 46, 14, 1, 57, 160, 30, 33, 32, 1, 17, 178, 51, 18, 9, 1, 247, 171, 45, 23, 16, 1, 150, 40, 37, 166, 12, 1, 38, 165, 39, 40, 11, 2, 88, 169, 45, 25, 15, 1, 21, 166, 42, 21, 26, 1, 13, 164, 40, 38, 13, 0, 207, 171, 47, 26, 11, 2, 4, 166, 30, 43, 16, 1, 118, 164, 34, 41, 16, 1, 65, 172, 49, 23, 12, 0, 170, 163, 35, 40, 18, 1, 192, 167, 23, 46, 19, 1, 29, 161, 40, 38, 16, 1, 15, 163, 33, 42, 18, 1, 14, 168, 47, 23, 18, 0, 154, 161, 40, 26, 28, 0, 64, 175, 54, 19, 7, 0, 52, 160, 30, 26, 39, 2, 79, 165, 45, 33, 12, 1, 252, 160, 31, 40, 24, 1, 170, 171, 51, 23, 10, 1, 167, 162, 42, 38, 13, 1, 149, 170, 50, 29, 6, 0, 93, 157, 36, 37, 26, 2, 98, 168, 49, 29, 9, 0, 220, 47, 166, 27, 15, 0, 78, 173, 54, 19, 8, 2, 82, 164, 30, 46, 16, 1, 193, 166, 48, 33, 9, 1, 130, 163, 45, 32, 14, 1, 107, 162, 44, 30, 19, 0, 54, 155, 36, 37, 26, 2, 126, 154, 36, 28, 37, 2, 123, 170, 53, 10, 22, 2, 108, 163, 46, 29, 16, 2, 37, 162, 45, 36, 12, 1, 141, 60, 177, 14, 3, 1, 117, 156, 39, 27, 33, 1, 82, 166, 49, 30, 9, 2, 104, 166, 50, 24, 14, 2, 50, 159, 43, 36, 17, 1, 243, 152, 36, 34, 33, 1, 222, 165, 29, 49, 11, 1, 221, 161, 32, 45, 17, 0, 39, 154, 38, 33, 30, 2, 38, 155, 36, 40, 24, 1, 214, 154, 38, 23, 39, 1, 78, 172, 57, 16, 10, 1, 5, 164, 49, 24, 18, 2, 99, 163, 49, 26, 17, 1, 241, 166, 52, 17, 20, 0, 187, 155, 41, 26, 33, 2, 81, 167, 54, 20, 14, 2, 62, 167, 54, 22, 11, 0, 102, 159, 28, 46, 22, 0, 37, 158, 32, 45, 20, 0, 105, 152, 29, 40, 34, 0, 92, 37, 160, 48, 9)
INTENT_PRIORS=[intent[i]/32.0 for i in range(4)]
INTENT_WORDS={}; pos=4
while pos+5<len(intent):
    token=intent[pos]*256+intent[pos+1]
    INTENT_WORDS[token]=(intent[pos+2],intent[pos+3],intent[pos+4],intent[pos+5]); pos+=6

def classify_intent(prompt_ids):
    scores=list(INTENT_PRIORS); seen={}
    for token in prompt_ids:
        if token in seen: continue
        seen[token]=1; evidence=INTENT_WORDS.get(token)
        if evidence:
            for act in range(4): scores[act]+=evidence[act]/255.0
    best=0
    for act in range(1,4):
        if scores[act]>scores[best]: best=act
    ordered=sorted(scores,reverse=True)
    confidence=int(100*(ordered[0]-ordered[1])/max(0.01,ordered[0]))
    return best,min(100,confidence)

emotion=(211, 2, 1, 0, 33, 3, 5, 0, 189, 245, 5, 0, 0, 3, 1, 1, 2, 15, 241, 1, 1, 1, 5, 2, 2, 1, 109, 241, 4, 1, 1, 6, 1, 1, 2, 23, 241, 1, 1, 1, 7, 1, 1, 1, 179, 240, 3, 1, 1, 6, 2, 3, 2, 11, 239, 1, 1, 1, 6, 6, 1, 1, 151, 239, 3, 1, 1, 7, 3, 2, 1, 147, 239, 3, 1, 2, 8, 2, 2, 2, 127, 235, 2, 2, 2, 5, 6, 5, 1, 83, 239, 1, 1, 1, 10, 2, 2, 1, 150, 238, 3, 1, 1, 10, 1, 2, 0, 253, 233, 6, 4, 1, 6, 5, 1, 0, 119, 237, 1, 0, 0, 10, 1, 5, 1, 251, 235, 3, 1, 1, 9, 2, 3, 0, 160, 236, 3, 1, 1, 10, 2, 2, 0, 116, 238, 1, 0, 0, 12, 3, 1, 2, 10, 233, 8, 3, 1, 5, 4, 2, 0, 246, 237, 2, 0, 0, 12, 3, 0, 2, 115, 231, 3, 1, 3, 7, 4, 6, 2, 92, 232, 2, 2, 2, 8, 3, 8, 2, 40, 235, 2, 1, 1, 11, 4, 1, 2, 31, 234, 3, 1, 1, 10, 4, 1, 1, 195, 236, 2, 2, 1, 12, 1, 1, 0, 252, 237, 2, 1, 1, 13, 2, 2, 0, 191, 236, 1, 0, 2, 12, 2, 2, 1, 210, 235, 1, 2, 1, 12, 2, 2, 1, 35, 234, 1, 1, 1, 11, 5, 3, 0, 195, 234, 3, 0, 0, 11, 2, 3, 1, 211, 233, 1, 1, 2, 11, 3, 4, 1, 157, 236, 1, 1, 1, 14, 1, 2, 1, 90, 234, 4, 1, 1, 12, 3, 1, 1, 27, 231, 5, 1, 1, 9, 1, 7, 1, 18, 235, 2, 1, 1, 13, 2, 2, 0, 89, 236, 1, 1, 1, 14, 1, 1, 1, 181, 233, 1, 3, 2, 12, 1, 3, 0, 255, 235, 1, 1, 1, 14, 3, 2, 0, 177, 235, 1, 1, 0, 14, 1, 3, 1, 87, 233, 4, 1, 1, 13, 1, 2, 1, 4, 233, 3, 1, 0, 13, 3, 1, 2, 30, 231, 1, 1, 1, 12, 8, 1, 2, 21, 230, 1, 1, 1, 11, 9, 1, 1, 161, 233, 2, 1, 1, 14, 2, 3, 1, 145, 230, 3, 2, 3, 11, 5, 1, 1, 140, 234, 2, 1, 1, 15, 1, 2, 1, 123, 235, 1, 1, 1, 16, 2, 1, 1, 245, 229, 11, 2, 1, 7, 4, 2, 1, 194, 231, 3, 1, 1, 13, 6, 1, 1, 103, 231, 4, 2, 1, 13, 2, 2, 0, 243, 230, 4, 1, 1, 12, 3, 4, 0, 216, 233, 2, 1, 1, 15, 1, 1, 2, 114, 232, 3, 1, 1, 15, 1, 1, 2, 77, 229, 4, 1, 1, 12, 4, 3, 2, 14, 232, 2, 1, 1, 15, 3, 1, 1, 207, 232, 1, 1, 1, 15, 2, 2, 1, 174, 227, 2, 1, 3, 10, 10, 2, 1, 41, 229, 4, 2, 1, 12, 3, 3, 0, 74, 233, 1, 0, 0, 16, 2, 1, 1, 238, 231, 2, 1, 1, 15, 2, 3, 1, 177, 232, 4, 1, 1, 16, 1, 1, 0, 215, 230, 5, 0, 0, 14, 3, 2, 0, 113, 232, 2, 1, 0, 16, 2, 2, 2, 69, 230, 1, 1, 3, 15, 1, 3, 2, 46, 230, 1, 1, 1, 15, 3, 3, 2, 39, 226, 8, 4, 3, 11, 1, 1, 1, 202, 230, 1, 1, 1, 15, 2, 5, 1, 165, 228, 4, 2, 1, 13, 4, 4, 0, 144, 233, 1, 0, 1, 18, 1, 2, 1, 156, 227, 4, 2, 1, 13, 4, 5, 1, 114, 228, 1, 1, 1, 14, 2, 6, 0, 225, 230, 3, 2, 0, 16, 3, 1, 0, 111, 230, 3, 1, 0, 16, 3, 2, 2, 70, 226, 3, 3, 1, 13, 4, 5, 2, 54, 227, 6, 1, 1, 14, 3, 3, 1, 164, 225, 8, 2, 2, 12, 1, 5, 1, 143, 225, 4, 2, 1, 12, 3, 8, 1, 133, 230, 2, 2, 2, 17, 2, 1, 1, 129, 229, 3, 1, 1, 16, 2, 3, 1, 125, 232, 2, 1, 1, 19, 1, 1, 0, 247, 230, 1, 1, 1, 17, 2, 4, 0, 185, 232, 1, 1, 0, 19, 1, 1, 0, 174, 229, 2, 1, 0, 16, 2, 5, 2, 95, 227, 1, 1, 1, 15, 7, 2, 2, 8, 228, 3, 1, 1, 16, 1, 5, 1, 229, 230, 2, 1, 1, 18, 1, 2, 1, 71, 224, 7, 2, 1, 12, 4, 4, 1, 38, 227, 4, 1, 1, 15, 3, 5, 1, 2, 231, 1, 2, 1, 19, 1, 1, 0, 139, 228, 3, 1, 1, 16, 1, 6, 2, 99, 225, 1, 1, 3, 14, 8, 3, 2, 88, 223, 2, 4, 1, 12, 7, 5, 2, 71, 229, 1, 1, 1, 18, 1, 3, 1, 205, 225, 3, 2, 1, 14, 7, 2, 1, 192, 225, 6, 2, 1, 14, 3, 5, 1, 171, 223, 5, 2, 1, 12, 3, 10, 1, 154, 224, 3, 1, 1, 13, 9, 5, 1, 122, 229, 3, 1, 1, 18, 1, 2, 1, 111, 228, 2, 2, 1, 17, 2, 3, 1, 94, 225, 3, 2, 1, 14, 5, 5, 0, 238, 227, 2, 1, 0, 16, 3, 5, 0, 222, 227, 2, 2, 1, 16, 2, 4, 0, 206, 225, 5, 1, 1, 14, 3, 5, 2, 38, 226, 5, 3, 1, 16, 2, 1, 1, 234, 227, 1, 1, 2, 17, 2, 4, 1, 216, 229, 1, 1, 1, 19, 1, 2, 1, 204, 227, 1, 1, 1, 17, 5, 3, 1, 44, 227, 4, 1, 1, 17, 4, 2, 1, 30, 226, 5, 1, 1, 16, 2, 4, 1, 28, 228, 3, 1, 0, 18, 2, 2, 0, 117, 227, 0, 0, 0, 17, 10, 1, 0, 100, 229, 2, 1, 0, 19, 2, 2, 0, 25, 228, 2, 1, 0, 18, 2, 4, 2, 118, 226, 2, 1, 1, 18, 4, 2, 1, 198, 228, 2, 2, 1, 20, 2, 1, 1, 128, 224, 3, 1, 2, 16, 5, 5, 1, 79, 228, 1, 2, 1, 20, 2, 3, 1, 33, 227, 3, 1, 1, 19, 2, 2, 0, 150, 227, 2, 1, 0, 19, 1, 4, 0, 115, 228, 1, 1, 0, 20, 1, 4, 2, 82, 221, 4, 1, 1, 14, 8, 6, 1, 249, 224, 1, 1, 1, 17, 7, 2, 1, 36, 226, 4, 1, 1, 19, 2, 3, 0, 220, 226, 3, 1, 0, 19, 3, 2, 2, 87, 224, 2, 2, 1, 18, 2, 4, 2, 66, 223, 6, 2, 1, 17, 2, 2, 2, 55, 223, 3, 3, 1, 17, 5, 4, 2, 26, 226, 1, 1, 1, 20, 1, 6, 1, 246, 226, 2, 1, 1, 20, 2, 2, 1, 228, 223, 6, 1, 2, 17, 4, 1)
EMOTION_PRIORS=[emotion[i]/128.0 for i in range(7)]
EMOTION_WORDS={}; pos=7
while pos+8<len(emotion):
    token=emotion[pos]*256+emotion[pos+1]
    EMOTION_WORDS[token]=tuple(emotion[pos+2:pos+9]); pos+=9

def classify_emotion(prompt,prompt_ids):
    """Combine learned word evidence with information lost by lowercasing."""
    scores=list(EMOTION_PRIORS); seen={}
    for token in prompt_ids:
        if token in seen: continue
        seen[token]=1; evidence=EMOTION_WORDS.get(token)
        if evidence:
            for tone in range(7): scores[tone]+=evidence[tone]/255.0
    letters=0; capitals=0
    for ch in prompt:
        if "a"<=ch.lower()<="z":
            letters+=1
            if "A"<=ch<="Z": capitals+=1
    bangs=prompt.count("!"); questions=prompt.count("?")
    lower=prompt.lower(); plain=""
    for ch in lower: plain+=ch if "a"<=ch<="z" else " "
    hesitation_words=plain.split()
    hesitant=(not prompt.strip() or "..." in prompt or "uh" in hesitation_words or
              "um" in hesitation_words or "hmm" in hesitation_words)
    loud=letters>=3 and capitals*100>=65*letters
    if loud and bangs>=2:
        beginning=lower.strip()
        surprised=(questions or beginning.startswith("what") or
                   beginning.startswith("why") or beginning.startswith("how"))
        if surprised: scores[6]+=6.0
        else: scores[1]+=6.0
    elif bangs>=2:
        scores[4]+=1.5; scores[6]+=1.5; scores[1]+=0.8
    if questions>=2: scores[6]+=4.0
    if hesitant: scores[3]+=4.2; scores[5]+=2.8
    best=0
    for tone in range(1,7):
        if scores[tone]>scores[best]: best=tone
    ordered=sorted(scores,reverse=True)
    confidence=int(100*(ordered[0]-ordered[1])/max(0.01,ordered[0]))
    return best,min(100,confidence)

# ------------------------------------------------------------- inference core
def sigmoid(x):
    if x>12: return 0.999994
    if x<-12: return 0.000006
    return 1.0/(1.0+exp(-x))

BI_DQ=[]; BH_DQ=[]; BO_DQ=[]

def prepare():
    """Dequantize the small bias vectors once so the hot loops never decode them."""
    global BI_DQ,BH_DQ,BO_DQ
    bi=Q[3]; bh=Q[4]; bo=Q[6]
    BI_DQ=[qvalue(bi,g)*S[3] for g in range(3*H)]
    BH_DQ=[qvalue(bh,g)*S[4] for g in range(3*H)]
    BO_DQ=[qvalue(bo,t)*S[6] for t in range(N)]

def dot_row(tensor,x,start,length):
    """Dot product of one quantized row with x, decoding two values per list read.

    Values are packed two-per-element and a row is mostly even-aligned, so the
    inner loop reads each packed element once instead of calling qvalue per
    weight. This is the single largest speed win on the calculator."""
    q=start>>1
    part=q//800
    off=q-part*800
    chunk=tensor[part]
    total=0.0; i=0; last=length-1
    while i<last:
        if off>=800:
            while off>=800:
                part+=1; off-=800
            chunk=tensor[part]
        v=int(chunk[off]); off+=1
        total+=((v>>8)-128)*x[i]+((v&255)-128)*x[i+1]
        i+=2
    if i==last:
        total+=qvalue(tensor,start+i)*x[i]
    return total

def step(token,h):
    emb=Q[0]; wi=Q[1]; wh=Q[2]
    s0=S[0]; s1=S[1]; s2=S[2]
    x=[0.0]*E
    start=token*E
    q=start>>1; part=q//800; off=q-part*800; chunk=emb[part]
    i=0; last=E-1
    while i<last:
        if off>=800:
            while off>=800:
                part+=1; off-=800
            chunk=emb[part]
        v=int(chunk[off]); off+=1
        x[i]=((v>>8)-128)*s0
        x[i+1]=((v&255)-128)*s0
        i+=2
    if i==last:
        x[i]=qvalue(emb,start+i)*s0
    gates=[0.0]*(3*H)
    for g in range(2*H):
        gates[g]=sigmoid(s1*dot_row(wi,x,g*E,E)+s2*dot_row(wh,h,g*H,H)+BI_DQ[g]+BH_DQ[g])
    new=[0.0]*H
    base=2*H
    for j in range(H):
        g=base+j
        candidate=tanh(s1*dot_row(wi,x,g*E,E)+BI_DQ[g]+gates[j]*(s2*dot_row(wh,h,g*H,H)+BH_DQ[g]))
        z=gates[H+j]
        new[j]=(1.0-z)*candidate+z*h[j]
    return new

def logits(h):
    wo=Q[5]; result=[0.0]*N; s5=S[5]
    for token in range(N):
        start=token*H
        q=start>>1; part=q//800; off=q-part*800; chunk=wo[part]
        total=0.0; i=0; last=H-1
        while i<last:
            if off>=800:
                while off>=800:
                    part+=1; off-=800
                chunk=wo[part]
            v=int(chunk[off]); off+=1
            total+=((v>>8)-128)*h[i]+((v&255)-128)*h[i+1]
            i+=2
        if i==last:
            total+=qvalue(wo,start+i)*h[i]
        result[token]=s5*total+BO_DQ[token]
    return result

def ensure_model(messages,scroll):
    if Q[0] is not None: return scroll
    scroll=draw(messages,"",scroll,"Loading model...",True)
    for tensor in range(7):
        Q[tensor]=load_tensor("tdq"+str(tensor)+"x",QPARTS[tensor])
    prepare()
    return scroll

# ------------------------------------------------------------------ text tools
def tokenize(text):
    out=[]; word=""
    for ch in text.lower():
        if ("a"<=ch<="z") or ("0"<=ch<="9") or ch=="'": word+=ch
        else:
            if word: out.append(LOOKUP.get(word,1)); word=""
            if ch in ".,!?;:": out.append(LOOKUP.get(ch,1))
    if word: out.append(LOOKUP.get(word,1))
    return out

# --------------------------------------------------------------- decoder knobs
MAX_TOKENS=42
TEMPS=(0.25,0.42,0.60,0.80)
TEMP_INDEX=1
LENGTHS=(0.7,1.0,1.3)
LENGTH_INDEX=1
TEMP=TEMPS[TEMP_INDEX]
LENGTH_SCALE=LENGTHS[LENGTH_INDEX]
CONTEXT_WEIGHT=0.5
CONTEXT_LIMIT=16
PROMPT_LIMIT=18
BIGRAM_BASE=32768

def choose(scores,used,recent7,last,last2,seen3,bias,confidence,position,forbidden):
    best=[]
    temp=TEMP
    boost=(2.0+2.0*confidence)*max(0.25,1.0-position/20.0)
    punct=bool(last>=0)
    trigram=bool(last2>=0)
    for token in range(FIRST_WORD,N):
        if token in forbidden: continue
        if token in PUNCT_IDS and punct:
            if last in CONTINUATION_IDS: continue
            if last2>=0 and VOCAB[last2]=="a" and VOCAB[last]=="little": continue
        score=scores[token]/temp
        repeats=used.get(token,0)
        if token in recent7: score-=2.4
        score-=1.15*repeats
        if token==last: score-=6.0
        # Do not repeat an exact three-token sequence: this is the cheapest
        # effective cure for "it is it is" loops without flattening the reply.
        if trigram and ((last2*N+last)*N+token) in seen3: score-=7.0
        if token in PRONOUN_IDS:
            score-=1.4*repeats
            if repeats>=2: score-=8.0
            if last in PRONOUN_IDS: score-=2.8
        weight=bias.get(token)
        if weight: score+=boost*weight
        pos=0
        while pos<len(best) and score<best[pos][0]: pos+=1
        if pos<12:
            best.insert(pos,(score,token))
            if len(best)>12: best.pop()
    high=best[0][0]; weights=[]; total=0.0
    for score,token in best:
        weight=exp(score-high); weights.append(weight); total+=weight
    target=random()*total; running=0.0
    for i in range(len(best)):
        running+=weights[i]
        if running>=target: return best[i][1]
    return best[-1][1]

def render(tokens):
    text=""; capitalize=True
    allowed={"s":("it","that","what","he","she","there","here","who"),
             "m":("i",),"re":("you","we","they"),
             "ve":("i","you","we","they"),
             "ll":("i","you","he","she","we","they","it"),
             "d":("i","you","he","she","we","they"),
             "t":("don","can","isn","aren","wasn","weren","won","wouldn","couldn","shouldn")}
    def numeric(word):
        if not word: return False
        for ch in word:
            if not ("0"<=ch<="9"): return False
        return True
    for index in range(len(tokens)):
        word=VOCAB[tokens[index]]
        if word in ".,!?;:":
            decimal=(word=="." and index>0 and index+1<len(tokens) and
                     numeric(VOCAB[tokens[index-1]]) and
                     numeric(VOCAB[tokens[index+1]]))
            text=text.rstrip()+word
            if not decimal and word in ".!?": capitalize=True
            text+=" "
        else:
            previous=VOCAB[tokens[index-1]] if index>0 else ""
            if word in allowed and previous in allowed[word]:
                text=text.rstrip()+"'"+word+" "; capitalize=False; continue
            if word=="i" or word[:2]=="i'": word="I"+word[1:]
            elif capitalize and word:
                word=word[0].upper()+word[1:]
            text+=word+" "; capitalize=False
    return text.strip()

# ------------------------------------------------------------ understanding
STOP_WORDS=("the","a","an","is","are","was","were","what","why",
            "how","do","does","did","can","could","would","should",
            "i","you","it","this","that","to","of","and","or",
            "thanks","thank","please")
WEAK_OUTPUT=("i","you","he","she","we","they","me","him","her","us",
             "them","the","a","an","is","are","was","were","be","been",
             "to","of","and","or","but","do","does","did")

def build_stop():
    stop={}
    for word in STOP_WORDS:
        if word in LOOKUP: stop[LOOKUP[word]]=1
    for mark in (".",",","!","?",";",":"):
        if mark in LOOKUP: stop[LOOKUP[mark]]=1
    weak={}
    for word in WEAK_OUTPUT:
        if word in LOOKUP: weak[LOOKUP[word]]=1
    return stop,weak

STOP,WEAK=build_stop()

def understand(prompt_ids,context_ids):
    """Map prompt (and recent conversation) tokens to likely response content.

    The rolling context is a *feature-level* mechanism: the previous turn's
    content words contribute associations at reduced weight so short follow-ups
    such as "what about Germany?" stay on topic without perturbing the GRU with
    out-of-distribution history."""
    content=[token for token in prompt_ids if token not in STOP and token>=1]
    known=[token for token in content if token!=1]
    coverage=(len(known)/len(content)) if content else 0.0
    unique={}
    for token in known: unique[token]=1.0
    for index in range(len(prompt_ids)-1):
        left=prompt_ids[index]; right=prompt_ids[index+1]
        if left!=1 and right!=1 and left not in PUNCT_IDS and right not in PUNCT_IDS:
            key=BIGRAM_BASE+((left*257+right*17)%BIGRAM_BASE)
            unique[key]=1.0
    context=[token for token in context_ids if token not in STOP and token!=1]
    for token in context:
        if unique.get(token,0.0)<CONTEXT_WEIGHT: unique[token]=CONTEXT_WEIGHT
    for index in range(len(context_ids)-1):
        left=context_ids[index]; right=context_ids[index+1]
        if left!=1 and right!=1 and left not in PUNCT_IDS and right not in PUNCT_IDS:
            key=BIGRAM_BASE+((left*257+right*17)%BIGRAM_BASE)
            if unique.get(key,0.0)<CONTEXT_WEIGHT: unique[key]=CONTEXT_WEIGHT
    if not unique: return {},0.0
    bias={}; associated=0.0; strength=0.0; total_weight=0.0
    for prompt_token,feature_weight in unique.items():
        total_weight+=feature_weight
        related=ASSOCIATIONS.get(prompt_token)
        if not related: continue
        associated+=feature_weight
        strongest=0.0
        for token,weight in related.items():
            if token not in WEAK:
                bias[token]=bias.get(token,0.0)+weight*feature_weight
            if weight>strongest: strongest=weight
        strength+=feature_weight*strongest/1.8
    association_coverage=associated/max(0.001,total_weight)
    average_strength=strength/max(0.001,associated)
    confidence=coverage*(0.60*association_coverage+0.40*average_strength)
    if not known: confidence*=0.5
    return bias,min(1.0,confidence)

# ------------------------------------------------------------------- renderer
BG=(255,255,255); PANEL=(235,240,247); USER=(25,95,190); USER_BG=(235,244,255)
ACCENT=(0,130,115); TEXT=(20,35,58); MUTED=(92,108,130)
def color(c): set_color(c[0],c[1],c[2])

def wrap(text,width=35):
    rows=[]; line=""
    for word in text.split(" "):
        trial=word if not line else line+" "+word
        if len(trial)>width:
            if line: rows.append(line)
            line=word
        else: line=trial
    if line: rows.append(line)
    return rows or [""]

def rows_for(messages,partial="",thinking=False):
    rows=[]
    for role,text in messages:
        lines=wrap(text,30 if role=="user" else 35)
        for i,line in enumerate(lines): rows.append((role,("YOU  " if role=="user" and i==0 else "LM   " if i==0 else "     ")+line))
        rows.append(("gap",""))
    if thinking:
        if partial:
            lines=wrap(partial)
            for i,line in enumerate(lines):
                rows.append(("bot",("LM   " if i==0 else "     ")+line))
        else:
            rows.append(("bot","LM   Thinking"+"."*((get_time_ms()//350)%4)))
    return rows

def draw(messages,entry,scroll,partial="",thinking=False):
    color(BG); fill_rect(0,0,318,212)
    color(PANEL); fill_rect(0,0,318,25); fill_rect(0,158,318,54)
    color(ACCENT); fill_rect(0,24,318,2)
    color(TEXT); draw_text(9,17,"CalcGPT")
    # Raised 1.5x-height sequel mark, one character-space after CalcGPT.
    color((235,105,35))
    fill_rect(67,3,9,2); fill_rect(74,5,2,5)
    fill_rect(67,9,9,2); fill_rect(74,11,2,5)
    fill_rect(67,15,9,2)
    status="E"+str(TRAINED_EPOCHS)+" T"+str(TEMP)
    if LAST_INTENT>=0:
        status+=" "+("I","Q","D","C")[LAST_ACT]+("N","A","G","F","H","S","U")[LAST_EMOTION]+str(LAST_INTENT)+"%"
    color(MUTED); draw_text(196,17,status)
    rows=rows_for(messages,partial,thinking); visible=9
    maximum=max(0,len(rows)-visible); scroll=min(maximum,max(0,scroll))
    y=39
    for role,line in rows[scroll:scroll+visible]:
        if role=="user":
            color(USER_BG); fill_rect(14,y-11,290,13)
        color(USER if role=="user" else ACCENT if role=="bot" else MUTED)
        draw_text(19 if role=="user" else 7,y,line[:43]); y+=13
    color(MUTED); draw_text(7,170,"UP/DN L/R  ^N new ^R redo ^T temp")
    color((245,248,252)); fill_rect(5,176,308,34)
    color(ACCENT); draw_line(5,176,313,176); draw_line(5,210,313,210)
    color(TEXT)
    if NOTICE:
        draw_text(10,199,NOTICE)
    elif thinking:
        draw_text(10,199,"Thinking...")
    else:
        typed=[entry[i:i+33] for i in range(0,len(entry),33)] or [""]
        typed=typed[-2:]
        if len(typed)==1:
            draw_text(10,199,"> "+typed[0]+"_")
        else:
            draw_text(10,190,"> "+typed[0])
            draw_text(10,204,"  "+typed[1]+"_")
    paint_buffer(); return scroll

# --------------------------------------------------------------- candidate QA
def candidate_score(tokens,bias,prompt_ids):
    score=0.0; counts={}; seen3={}
    prev=-1; prev2=-1
    for token in tokens:
        score+=2.2*bias.get(token,0.0)
        counts[token]=counts.get(token,0)+1
        if counts[token]>1: score-=0.8*(counts[token]-1)
        if token in prompt_ids: score+=0.08
        if prev2>=0:
            key=(prev2*N+prev)*N+token
            if key in seen3: score-=1.2
            seen3[key]=1
        prev2=prev; prev=token
    if tokens and VOCAB[tokens[-1]] in ".!?'": score+=1.0
    if tokens and tokens[-1] in CONTINUATION_IDS: score-=5.0
    return score

def acceptable(tokens,bias):
    """Absolute quality gate so a good first candidate can skip the second pass."""
    if not tokens: return False
    if VOCAB[tokens[-1]] not in ".!?": return False
    if tokens[-1] in CONTINUATION_IDS: return False
    counts={}; content=0; relevant=0; repeated=0; distinct=0
    for token in tokens:
        if token in PUNCT_IDS: continue
        content+=1
        previous=counts.get(token,0)
        counts[token]=previous+1
        if previous==0: distinct+=1
        else: repeated+=1
        if token in bias: relevant+=1
    if content<3 or distinct<2: return False
    if repeated*100>40*max(1,content): return False
    if bias and relevant*100<20*content: return False
    return True

def sample_candidate(initial,bias,confidence,minimum,maximum,forbidden):
    h=list(initial); made=[]; used={}; recent7={}; ring=[]; seen3={}
    last=-1; last2=-1
    for index in range(maximum):
        token=choose(logits(h),used,recent7,last,last2,seen3,bias,confidence,index,forbidden)
        made.append(token)
        used[token]=used.get(token,0)+1
        ring.append(token); recent7[token]=recent7.get(token,0)+1
        if len(ring)>7:
            old=ring.pop(0); recent7[old]-=1
            if recent7[old]<=0: del recent7[old]
        if last2>=0: seen3[(last2*N+last)*N+token]=1
        last2=last; last=token; h=step(token,h)
        if index>=minimum and VOCAB[token] in ".!?" and random()<0.72: break
    while made and made[-1] in CONTINUATION_IDS: made.pop()
    if len(made)>=2 and VOCAB[made[-2]]=="a" and VOCAB[made[-1]]=="little":
        made=made[:-2]
    return made

def previous_user_ids(messages):
    """Rolling context: the previous user prompts, bounded in size."""
    ids=[]; seen=0
    for index in range(len(messages)-1,-1,-1):
        role,text=messages[index]
        if role!="user": continue
        seen+=1
        if seen==1: continue
        ids=tokenize(text)[:12]+ids
        if len(ids)>=CONTEXT_LIMIT: break
    return ids[:CONTEXT_LIMIT]

def generate(prompt,messages,scroll):
    global LAST_INTENT,LAST_ACT,LAST_EMOTION
    scroll=ensure_model(messages,scroll)
    h=[0.0]*H
    prompt_ids=tokenize(prompt)[:PROMPT_LIMIT]
    context_ids=previous_user_ids(messages)
    LAST_ACT,act_confidence=classify_intent(prompt_ids)
    LAST_EMOTION,emotion_confidence=classify_emotion(prompt,prompt_ids)
    bias,confidence=understand(prompt_ids,context_ids)
    LAST_INTENT=max(act_confidence,emotion_confidence)
    meaningful=0
    for token in prompt_ids:
        if token not in PUNCT_IDS and token!=1: meaningful+=1
    minimum=4+min(4,meaningful//3)
    maximum=min(MAX_TOKENS,9+meaningful+int(5*confidence))
    if confidence<0.20: maximum=min(maximum,10+meaningful)
    if LAST_ACT==1: maximum=min(MAX_TOKENS,maximum+4)
    elif LAST_ACT==2: maximum=max(minimum+2,maximum-2)
    elif LAST_ACT==3: maximum=max(minimum+2,maximum-3)
    if LAST_EMOTION in (1,2,6): maximum=max(minimum+2,maximum-3)
    maximum=int(maximum*LENGTH_SCALE)
    if maximum<minimum: maximum=minimum
    forbidden={}
    for token in PROFANITY_IDS: forbidden[token]=1
    gender_topic=False
    for token in prompt_ids:
        if token in GENDER_IDS: gender_topic=True
    if not gender_topic:
        for token in GENDER_IDS: forbidden[token]=1
    # Match the explicitly conditioned dialogue structure used during training.
    act_token=LOOKUP.get(("<act_info>","<act_question>","<act_directive>","<act_commitment>")[LAST_ACT],1)
    emotion_token=LOOKUP.get(("<emo_calm>","<emo_anger>","<emo_disgust>","<emo_fear>","<emo_happy>","<emo_sad>","<emo_surprise>")[LAST_EMOTION],1)
    for token in ([2,4]+prompt_ids+[act_token,emotion_token,5]): h=step(token,h)
    scroll=draw(messages,"",scroll,"",True)
    first=sample_candidate(h,bias,confidence,minimum,maximum,forbidden)
    if acceptable(first,bias):
        made=first
    else:
        scroll=draw(messages,"",scroll,"",True)
        second=sample_candidate(h,bias,confidence,minimum,maximum,forbidden)
        made=first if candidate_score(first,bias,prompt_ids)>=candidate_score(second,bias,prompt_ids) else second
    result=render(made)
    if result and result[-1] not in ".!?": result+="."
    if not result: result="..."
    return result,scroll

def sentence_case(text):
    out=""; capitalize=True; word=""
    for index in range(len(text)):
        ch=text[index]
        if "a"<=ch.lower()<="z":
            letter=ch.upper() if capitalize else ch
            out+=letter; word+=letter; capitalize=False
        else:
            if word=="i": out=out[:-1]+"I"
            word=""; out+=ch
            decimal=(ch=="." and index>0 and index+1<len(text) and
                     "0"<=text[index-1]<="9" and "0"<=text[index+1]<="9")
            if ch in ".!?" and not decimal: capitalize=True
    if word=="i": out=out[:-1]+"I"
    return out

def needs_capital(entry):
    index=len(entry)-1
    while index>=0 and entry[index]==" ": index-=1
    return index<0 or entry[index] in ".!?"

# ---------------------------------------------------------------- application
# Controls are plain functions of the module state so they can be tested on the
# desktop harness before they ever run on hardware.
def respond(prompt,base):
    """Generate a reply, restoring the pre-prompt conversation on regeneration."""
    global messages,RESTORE,LAST_PROMPT,scroll,NOTICE
    RESTORE=list(base); LAST_PROMPT=prompt
    messages=list(base); messages.append(("user",prompt))
    scroll=max(0,len(rows_for(messages,"",True))-3)
    draw(messages,"",scroll,"",True)
    try:
        response,scroll=generate(prompt,messages,scroll)
    except Exception:
        response="(model error)"; NOTICE="Model error - reinstall tinydata?"
    messages.append(("bot",response))
    if len(messages)>20: messages=messages[-20:]

def regenerate():
    global messages,entry,scroll,NOTICE
    if not LAST_PROMPT:
        NOTICE="Nothing to redo"
        return
    messages=list(RESTORE); entry=""
    respond(LAST_PROMPT,RESTORE)

def clear_conversation():
    global messages,entry,scroll,RESTORE,LAST_PROMPT,NOTICE
    messages=[]; entry=""; scroll=0; RESTORE=[]; LAST_PROMPT=""
    NOTICE="Conversation cleared"

def cycle_temp():
    global TEMP_INDEX,TEMP,NOTICE
    TEMP_INDEX=(TEMP_INDEX+1)%len(TEMPS); TEMP=TEMPS[TEMP_INDEX]
    NOTICE="Temperature "+str(TEMP)

def cycle_length():
    global LENGTH_INDEX,LENGTH_SCALE,NOTICE
    LENGTH_INDEX=(LENGTH_INDEX+1)%len(LENGTHS); LENGTH_SCALE=LENGTHS[LENGTH_INDEX]
    NOTICE="Length x"+str(LENGTH_SCALE)

messages=[]; entry=""; scroll=0; shift_once=False; caps=False; LAST_INTENT=-1; LAST_ACT=0; LAST_EMOTION=0; NOTICE=""; PRINT_LATEST=False
RESTORE=[]; LAST_PROMPT=""
try:
    entry="".join(chr(int(value)) for value in recall_list("tdpaste"))[:120]
    store_list("tdpaste",[])
except Exception:
    entry=""

PASTE_KEYS=("tab","paste","ctrl-v","ctrl+v","command-v","command+v","cmd-v","cmd+v")

use_buffer(); draw(messages,entry,scroll)
while True:
    key=get_key(1)
    if key not in PASTE_KEYS:
        NOTICE=""
    if key=="esc": break
    elif key in ("up","up_arrow"): scroll=max(0,scroll-1)
    elif key in ("down","down_arrow"): scroll+=1
    elif key in ("left","left_arrow"): scroll=max(0,scroll-9)
    elif key in ("right","right_arrow"): scroll+=9
    elif key in ("del","backspace","delete"): entry=entry[:-1]
    elif key in ("shift","shift_left","shift_right"):
        shift_once=not shift_once
    elif key in ("caps","capslock","alpha_lock"):
        caps=not caps
    elif key=="var" and len(entry)<120:
        entry+="?"
    elif key=="trig" and len(entry)<120:
        entry+="!"
    elif key in PASTE_KEYS:
        NOTICE="ESC, run tinydata, paste, rerun"
    elif key in ("ctrl","command","cmd"):
        # Some TI environments report a modifier and its following key as two
        # separate events rather than one combined event.
        second=get_key(1)
        low=second.lower() if isinstance(second,str) else ""
        if low=="v": NOTICE="ESC, run tinydata, paste, rerun"
        elif low=="n": clear_conversation()
        elif low=="r": regenerate()
        elif low=="t": cycle_temp()
        elif low=="l": cycle_length()
        elif second=="1" and len(entry)<120: entry+="!"
        elif second in ("/","?") and len(entry)<120: entry+="?"
    elif key=="menu" and messages:
        PRINT_LATEST=True; NOTICE="ESC to view latest in Shell"
    elif key in ("enter","return","\n"):
        prompt=entry.strip(); entry=""
        respond(prompt,messages)
    elif key in ("space"," ") and len(entry)<120:
        entry=sentence_case(entry+" ")
    elif key in ("question","questionmark","question_mark"): entry+="?"
    elif key in ("exclamation","exclamationmark","exclamation_mark"): entry+="!"
    elif len(key)==1 and len(entry)<120:
        if shift_once and key=="1": entry+="!"
        elif shift_once and key=="/": entry+="?"
        elif "a"<=key.lower()<="z":
            letter=key.lower()
            if caps or shift_once or key!=key.lower() or needs_capital(entry): letter=letter.upper()
            entry+=letter
        elif "0"<=key<="9" or key in "'\".,!?;:" : entry+=key
        shift_once=False
    scroll=draw(messages,entry,scroll)

if PRINT_LATEST and messages:
    print("\nLATEST CALCGPT RESPONSE:\n")
    print(messages[-1][1])
