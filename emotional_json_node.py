from __future__ import annotations
import json, re

AU_CATALOGUE = {
    "AU1":("inner_brow_raise","inner brow raised"),
    "AU2":("outer_brow_raise","outer brow raised, arched eyebrows"),
    "AU4":("brow_lower","furrowed brow, knitted brows"),
    "AU5":("upper_lid_raise","wide eyes, upper eyelids raised"),
    "AU6":("cheek_raise","raised cheeks, smiling eyes"),
    "AU7":("lid_tighten","tightened eyelids, intense gaze"),
    "AU9":("nose_wrinkle","nose wrinkled, sneer"),
    "AU12":("lip_corner_pull","lip corners pulled back, smile"),
    "AU14":("dimpler","dimples, corner lip indent"),
    "AU15":("lip_corner_depress","lip corners pulled down, downturned mouth"),
    "AU17":("chin_raise","chin raised"),
    "AU20":("lip_stretch","lips stretched back, fear grimace"),
    "AU23":("lip_tighten","lips tightened, pressed"),
    "AU24":("lip_press","lips pressed together"),
    "AU25":("lips_part","lips parted, mouth slightly open"),
    "AU26":("jaw_drop","jaw dropped, mouth open"),
    "AU27":("mouth_stretch","mouth wide open"),
    "AU43":("eye_closure_soft","eyes slightly closed, heavy eyelids"),
}

EMOTION_AU_PROFILES = {
    "neutral":{},
    "happiness":{"AU6":0.75,"AU12":1.0,"AU25":0.5},
    "joy":{"AU1":0.25,"AU5":0.25,"AU6":1.0,"AU12":1.0,"AU25":0.75,"AU26":0.5},
    "sadness":{"AU1":0.75,"AU4":0.5,"AU15":0.75,"AU17":0.5,"AU43":0.5},
    "grief":{"AU1":1.0,"AU4":0.75,"AU15":1.0,"AU17":0.75,"AU25":0.5,"AU43":0.75},
    "anger":{"AU4":1.0,"AU5":0.75,"AU7":0.75,"AU23":0.75,"AU24":0.5,"AU25":0.5},
    "rage":{"AU4":1.0,"AU5":1.0,"AU7":1.0,"AU9":0.5,"AU23":1.0,"AU24":0.75,"AU25":0.75,"AU26":0.5},
    "fear":{"AU1":0.75,"AU2":0.75,"AU4":0.5,"AU5":1.0,"AU7":0.5,"AU20":0.75,"AU25":0.5,"AU26":0.75},
    "terror":{"AU1":1.0,"AU2":1.0,"AU4":0.75,"AU5":1.0,"AU7":0.75,"AU20":1.0,"AU25":0.75,"AU26":1.0,"AU27":0.5},
    "disgust":{"AU9":1.0,"AU15":0.75,"AU25":0.5},
    "surprise":{"AU1":0.75,"AU2":1.0,"AU5":1.0,"AU25":0.5,"AU26":0.75,"AU27":0.5},
    "shock":{"AU1":1.0,"AU2":1.0,"AU5":1.0,"AU25":0.75,"AU26":1.0,"AU27":0.75},
    "contempt":{"AU12":0.5,"AU14":0.75},
    "awe":{"AU1":0.75,"AU2":0.75,"AU5":1.0,"AU25":0.5,"AU26":0.75},
    "anxiety":{"AU1":0.5,"AU4":0.75,"AU7":0.5,"AU23":0.75},
    "pain":{"AU4":1.0,"AU7":0.75,"AU9":0.75,"AU25":0.75,"AU43":0.5},
    "agony":{"AU4":1.0,"AU7":1.0,"AU9":1.0,"AU25":1.0,"AU26":0.5,"AU43":0.75},
    "love":{"AU1":0.5,"AU6":0.75,"AU12":0.75,"AU43":0.5},
    "tenderness":{"AU1":0.25,"AU6":0.5,"AU12":0.5,"AU43":0.75},
    "shame":{"AU4":0.5,"AU15":0.5,"AU17":0.75,"AU43":1.0},
    "pride":{"AU2":0.5,"AU5":0.25,"AU12":0.75},
    "curiosity":{"AU1":0.5,"AU2":0.25,"AU4":0.25,"AU5":0.5},
    "boredom":{"AU15":0.5,"AU17":0.5,"AU43":0.75},
    "sleepy":{"AU43":1.0,"AU17":0.5,"AU15":0.25},
    "excitement":{"AU1":0.5,"AU2":0.5,"AU5":0.75,"AU6":0.75,"AU12":1.0,"AU25":0.75,"AU26":0.5},
    "determination":{"AU4":0.5,"AU7":0.5,"AU23":0.75,"AU24":0.5},
    "stoic":{"AU7":0.25,"AU23":0.25},
    "serenity":{"AU6":0.25,"AU12":0.25,"AU43":0.5},
    "melancholy":{"AU1":0.5,"AU4":0.25,"AU15":0.5,"AU43":0.75},
}

AU_TOKEN_MAP = {
    "AU1":{"low":["subtle inner brow raise"],"mid":["inner brows raised"],"high":["deeply raised inner brows, anguished"]},
    "AU2":{"low":["slightly arched brows"],"mid":["arched eyebrows"],"high":["dramatically arched brows"]},
    "AU4":{"low":["mild brow furrow"],"mid":["furrowed brow"],"high":["deeply furrowed brow, scowling"]},
    "AU5":{"low":["slightly widened eyes"],"mid":["wide eyes"],"high":["eyes wide open, startled gaze"]},
    "AU6":{"low":["slight cheek lift"],"mid":["raised cheeks, smiling eyes"],"high":["Duchenne smile, eyes crinkled with joy"]},
    "AU7":{"low":["slightly tightened eyelids"],"mid":["intense gaze"],"high":["piercing stare, laser focus in eyes"]},
    "AU9":{"low":["subtle nose wrinkle"],"mid":["wrinkled nose"],"high":["deeply wrinkled nose, strong sneer"]},
    "AU12":{"low":["faint smile"],"mid":["smile, lip corners back"],"high":["broad smile, beaming grin"]},
    "AU14":{"low":["faint dimple"],"mid":["dimples visible"],"high":["deep dimples"]},
    "AU15":{"low":["slight lip corner droop"],"mid":["downturned mouth"],"high":["strongly downturned mouth, pronounced frown"]},
    "AU17":{"low":["slight chin raise"],"mid":["chin raised"],"high":["chin strongly raised"]},
    "AU20":{"low":["lips slightly stretched"],"mid":["lips stretched back, tension grimace"],"high":["extreme lip stretch, fear grimace"]},
    "AU23":{"low":["lips slightly tightened"],"mid":["lips tightened, resolute expression"],"high":["lips firmly pressed, tight-lipped"]},
    "AU24":{"low":["lips lightly pressed"],"mid":["lips pressed together"],"high":["lips firmly clamped"]},
    "AU25":{"low":["lips barely parted"],"mid":["lips parted, mouth slightly open"],"high":["lips clearly parted, open mouth"]},
    "AU26":{"low":["jaw slightly dropped"],"mid":["jaw dropped, mouth open"],"high":["jaw fully dropped, gaping mouth"]},
    "AU27":{"low":["mouth partially open"],"mid":["mouth wide open"],"high":["mouth stretched wide, agape"]},
    "AU43":{"low":["eyes gently closing"],"mid":["heavy eyelids, soft gaze"],"high":["drowsy eyes, nearly closed eyes"]},
}

LIGHTING_TOKENS = {
    "golden hour":"golden hour lighting, warm amber sunlight, soft backlight, lens flare, long shadows",
    "studio":"studio lighting, softbox illumination, catchlights in eyes, clean neutral background",
    "dramatic":"dramatic chiaroscuro lighting, high contrast, deep shadows, Rembrandt lighting",
    "neon":"neon lighting, cyberpunk glow, electric blue and magenta rim light, volumetric light",
    "natural":"natural diffused daylight, soft fill light, gentle shadows, outdoor ambient light",
    "candlelight":"warm candlelight, flickering amber glow, intimate low-key atmosphere, vignette edges",
    "moonlight":"cool blue moonlight, night scene, silver rim light, deep atmospheric shadows",
    "cinematic":"cinematic three-point lighting, motivated light sources, film-quality illumination",
    "sunset":"sunset lighting, warm red-orange hues, long silhouette shadows, golden sky",
    "horror":"low-key horror lighting, under-lighting, harsh upward shadows, sinister atmosphere",
}

CAMERA_TOKENS = {
    "extreme close-up":"extreme close-up shot, face fills entire frame, pores visible, macro detail",
    "close-up":"close-up portrait, face prominent, shoulders cropped, tight framing",
    "portrait":"portrait shot, shoulders and chest visible, medium close-up, eye-level angle",
    "medium":"medium shot, waist-up framing, conversational distance",
    "full body":"full body shot, head to toe, establishing character pose",
    "wide":"wide angle shot, environmental context visible, 24mm lens",
    "bokeh":"shallow depth of field, bokeh background, 85mm portrait lens, subject isolation",
    "cinematic":"cinematic widescreen framing, anamorphic lens, 2.39:1 aspect, letterbox",
    "dutch angle":"dutch angle, tilted camera, dynamic tension, disorienting composition",
}

ACTION_TOKENS = {
    "crying":"tears streaming down face, red eyes, glistening cheeks, emotional breakdown",
    "laughing":"laughing, open mouth, eyes clenched with laughter, joyful expression",
    "running":"running, dynamic motion blur, legs in stride, athletic movement",
    "standing":"standing, upright posture, grounded pose",
    "sitting":"sitting, seated position, relaxed posture",
    "fighting":"fighting stance, raised fists, combat ready, tense muscles",
    "embracing":"embracing, arms wrapped around, tender hug, close contact",
    "screaming":"mouth wide open in a scream, extreme tension, raw emotion",
    "kneeling":"kneeling, one or both knees on ground",
    "collapsed":"collapsed on ground, slumped posture, defeated body language",
    "sleeping":"sleeping, eyes closed, peaceful repose",
    "smiling":"gentle smile, relaxed pleasant expression",
    "reaching":"reaching forward, outstretched arm, grasping gesture",
    "walking":"walking, casual stride, mid-step pose",
}

CHARACTER_TOKENS = {
    "warrior":"warrior character, battle armor, scars, fierce expression",
    "mage":"mage, flowing robes, arcane symbols, mystical aura, wise expression",
    "knight":"knight, plate armor, heraldry, noble bearing, medieval attire",
    "villain":"villain character, dark clothing, menacing demeanor",
    "hero":"hero character, determined expression, heroic posture",
    "soldier":"soldier, military uniform, tactical gear, stern expression",
    "angel":"angel, luminous wings, radiant halo, ethereal glow, divine expression",
    "demon":"demon, dark wings, glowing eyes, infernal markings",
    "vampire":"vampire, pallid skin, fangs visible, dark aristocratic clothing",
    "royalty":"royal character, crown, regal attire, commanding presence",
    "ghost":"ghost, translucent form, ethereal glow, spectral wisps",
    "detective":"detective, trench coat, sharp analytical gaze, noir atmosphere",
}

BASE_NEGATIVE = (
    "deformed, disfigured, bad anatomy, extra limbs, missing limbs, "
    "fused fingers, extra fingers, poorly drawn face, cloned face, "
    "mutilated, bad proportions, malformed, ugly, blurry, low quality, "
    "pixelated, watermark, signature, text, username, out of frame, "
    "cropped, worst quality, low resolution, jpeg artifacts, flat shading, cartoon"
)

EMOTION_NEGATIVES = {
    "happiness":"sad expression, tears, frown, downturned mouth",
    "joy":"sad expression, frown, crying",
    "sadness":"happy expression, smile, joyful",
    "grief":"smile, happy expression, bright colors",
    "anger":"smiling, happy expression, calm demeanor",
    "rage":"calm, serene, smiling, peaceful",
    "fear":"confident, calm, relaxed expression",
    "terror":"calm, smiling, relaxed, neutral",
    "disgust":"pleasant expression, smile, welcoming",
    "surprise":"calm, unsurprised, expected expression",
    "awe":"bored, unimpressed, dismissive",
    "anxiety":"calm, relaxed, peaceful, serene",
    "pain":"smiling, happy, comfortable expression",
    "love":"cold, distant, hostile expression",
    "pride":"ashamed, defeated, downcast",
    "excitement":"bored, tired, uninterested",
    "serenity":"tense, stressed, anxious",
    "stoic":"emotional, expressive, exaggerated expression",
}

QUALITY_TOKENS = (
    "masterpiece, best quality, ultra-detailed, 8k uhd, "
    "photorealistic, RAW photo, intricate details, "
    "professional photography, film grain"
)

EMOTION_SYNONYMS = {
    "happiness":["happy","happiness","cheerful","pleased","content","delighted","glad"],
    "joy":["joy","joyful","elated","jubilant","exuberant","blissful"],
    "sadness":["sad","sadness","unhappy","sorrowful","downcast","dejected"],
    "grief":["grief","grieving","devastated","bereaved","mourning","heartbroken"],
    "anger":["angry","anger","irritated","annoyed","furious","irate","mad"],
    "rage":["rage","raging","livid","enraged","wrathful","seething"],
    "fear":["fear","afraid","scared","frightened","fearful","apprehensive"],
    "terror":["terror","terrified","horrified","petrified","panic"],
    "disgust":["disgust","disgusted","repulsed","revolted","nauseated"],
    "surprise":["surprise","surprised","astonished","startled"],
    "shock":["shock","shocked","stunned","dumbfounded"],
    "contempt":["contempt","contemptuous","dismissive","scornful"],
    "awe":["awe","awed","reverent","overwhelmed","breathless"],
    "anxiety":["anxiety","anxious","nervous","uneasy","tense","stressed"],
    "pain":["pain","pained","hurt","aching","suffering"],
    "agony":["agony","agonized","torment","excruciating"],
    "love":["love","loving","affectionate","adoring","enamored"],
    "tenderness":["tender","tenderness","gentle","nurturing","caring"],
    "shame":["shame","ashamed","humiliated","disgraced","mortified"],
    "pride":["pride","proud","dignified","triumphant","accomplished"],
    "curiosity":["curiosity","curious","inquisitive","intrigued"],
    "boredom":["boredom","bored","uninterested","listless","apathetic"],
    "sleepy":["sleepy","tired","exhausted","drowsy","weary","fatigued"],
    "excitement":["excitement","excited","thrilled","eager","enthusiastic"],
    "determination":["determination","determined","resolute","steadfast"],
    "stoic":["stoic","stoical","impassive","expressionless","stone-faced"],
    "serenity":["serenity","serene","peaceful","tranquil","calm","placid"],
    "melancholy":["melancholy","melancholic","pensive","brooding"],
    "neutral":["neutral","blank","expressionless","deadpan"],
}

def _tier(v):
    return "low" if v<=0.40 else ("mid" if v<=0.69 else "high")

def _detect_emotion(text):
    t = text.lower()
    for em, syns in sorted(EMOTION_SYNONYMS.items(), key=lambda kv: max(len(s) for s in kv[1]), reverse=True):
        for s in syns:
            if s in t:
                return em
    return "neutral"

def _detect_field(text, lookup):
    t = text.lower()
    for key in sorted(lookup.keys(), key=len, reverse=True):
        if key in t:
            return key
    return None

def _parse(raw):
    raw = raw.strip()
    r = {k:None for k in ["emotion","action","lighting","camera","character","subject","style","mood","setting"]}
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            for k in r:
                if k in data and isinstance(data[k], str):
                    r[k] = data[k].strip().lower()
            return r
        except json.JSONDecodeError:
            pass
    r["emotion"]   = _detect_emotion(raw)
    r["action"]    = _detect_field(raw, ACTION_TOKENS)
    r["lighting"]  = _detect_field(raw, LIGHTING_TOKENS)
    r["camera"]    = _detect_field(raw, CAMERA_TOKENS)
    r["character"] = _detect_field(raw, CHARACTER_TOKENS)
    quoted = re.findall(r'"([^"]+)"', raw)
    if quoted:
        r["subject"] = quoted[0]
    return r

def _au_tokens(au_profile):
    tokens = []
    for au, intensity in sorted(au_profile.items()):
        if au not in AU_TOKEN_MAP:
            continue
        opts = AU_TOKEN_MAP[au].get(_tier(intensity), [])
        if opts:
            tokens.append(opts[0])
    return tokens

def _format_au(au_profile):
    if not au_profile:
        return "AU_PROFILE: neutral (no AUs activated)"
    parts = []
    for au, v in sorted(au_profile.items()):
        _, desc = AU_CATALOGUE.get(au, ("?","?"))
        parts.append(f"{au}({v:.2f}\u00b7{_tier(v)}\u00b7{desc})")
    return "AU_PROFILE: " + " | ".join(parts)

def _expression_tags(emotion, au_profile):
    tags = [emotion.replace("_"," ")]
    for au, v in sorted(au_profile.items()):
        short, _ = AU_CATALOGUE.get(au, ("?","?"))
        tags.append(f"{short}:{v:.1f}")
    return ", ".join(tags)

def _positive(parsed, au_toks, quality_prefix, style_suffix, intensity, add_quality):
    parts = []
    if add_quality:
        parts.append(quality_prefix)
    if parsed.get("subject"):
        parts.append(parsed["subject"])
    elif parsed.get("character") and parsed["character"] in CHARACTER_TOKENS:
        parts.append(CHARACTER_TOKENS[parsed["character"]])
    if parsed.get("action") and parsed["action"] in ACTION_TOKENS:
        parts.append(ACTION_TOKENS[parsed["action"]])
    if au_toks:
        parts.append(f"({', '.join(au_toks)}:{intensity:.1f})")
    if parsed.get("lighting") and parsed["lighting"] in LIGHTING_TOKENS:
        parts.append(LIGHTING_TOKENS[parsed["lighting"]])
    if parsed.get("camera") and parsed["camera"] in CAMERA_TOKENS:
        parts.append(CAMERA_TOKENS[parsed["camera"]])
    if parsed.get("setting"):
        parts.append(parsed["setting"])
    if parsed.get("mood"):
        parts.append(parsed["mood"])
    if style_suffix.strip():
        parts.append(style_suffix.strip())
    return ", ".join(filter(None, parts))

def _negative(emotion, extra):
    parts = [BASE_NEGATIVE]
    eneg = EMOTION_NEGATIVES.get(emotion, "")
    if eneg:
        parts.append(eneg)
    if extra.strip():
        parts.append(extra.strip())
    return ", ".join(parts)


class EmotionalJSONToDiffusionPrompt:
    CATEGORY    = "Prompt/Emotional"
    FUNCTION    = "process"
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {
                    "multiline": True,
                    "default": '{\n  "emotion": "sadness",\n  "action": "crying",\n  "lighting": "candlelight",\n  "camera": "close-up",\n  "character": "soldier",\n  "subject": "a weathered soldier",\n  "style": "cinematic oil painting",\n  "mood": "somber, atmospheric",\n  "setting": "collapsed trench at dusk"\n}',
                }),
            },
            "optional": {
                "emotion_override":     (list(EMOTION_AU_PROFILES.keys()), {"default":"neutral"}),
                "lighting_override":    (["none"]+list(LIGHTING_TOKENS.keys()), {"default":"none"}),
                "camera_override":      (["none"]+list(CAMERA_TOKENS.keys()), {"default":"none"}),
                "expression_intensity": ("FLOAT", {"default":1.0,"min":0.1,"max":1.5,"step":0.05}),
                "quality_prefix":       ("STRING", {"multiline":False,"default":QUALITY_TOKENS}),
                "style_suffix":         ("STRING", {"multiline":False,"default":""}),
                "extra_negative":       ("STRING", {"multiline":True,"default":""}),
                "add_quality_tokens":   ("BOOLEAN", {"default":True}),
                "debug_mode":           ("BOOLEAN", {"default":False}),
            },
        }

    RETURN_TYPES  = ("STRING","STRING","STRING","STRING")
    RETURN_NAMES  = ("positive_prompt","negative_prompt","expression_tags","au_profile")

    def process(self, input_text, emotion_override="neutral", lighting_override="none",
                camera_override="none", expression_intensity=1.0, quality_prefix=QUALITY_TOKENS,
                style_suffix="", extra_negative="", add_quality_tokens=True, debug_mode=False):
        parsed = _parse(input_text)
        if emotion_override and emotion_override not in ("neutral","none"):
            parsed["emotion"] = emotion_override
        if lighting_override and lighting_override != "none":
            parsed["lighting"] = lighting_override
        if camera_override and camera_override != "none":
            parsed["camera"] = camera_override
        emotion = parsed.get("emotion") or "neutral"
        if emotion not in EMOTION_AU_PROFILES:
            emotion = _detect_emotion(emotion)
        parsed["emotion"] = emotion
        base_au = dict(EMOTION_AU_PROFILES.get(emotion, {}))
        au_scaled = {au: min(1.0, round(v*expression_intensity,4)) for au,v in base_au.items()}
        au_toks = _au_tokens(au_scaled)
        pos = _positive(parsed, au_toks, quality_prefix, style_suffix, expression_intensity, add_quality_tokens)
        neg = _negative(emotion, extra_negative)
        tags = _expression_tags(emotion, au_scaled)
        au_str = _format_au(au_scaled)
        if debug_mode:
            print(f"\nDEBUG: emotion={emotion} | action={parsed.get('action')} | lighting={parsed.get('lighting')} | camera={parsed.get('camera')}\nAU tokens: {au_toks}\n")
        return (pos, neg, tags, au_str)


NODE_CLASS_MAPPINGS = {"EmotionalJSONToDiffusionPrompt": EmotionalJSONToDiffusionPrompt}
NODE_DISPLAY_NAME_MAPPINGS = {"EmotionalJSONToDiffusionPrompt": "🎭 Emotional → Diffusion Prompt"}
