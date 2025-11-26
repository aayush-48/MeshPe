import re


def extract_amount(text):
    nums = re.findall(r"\d+", text)
    return int(nums[0]) if nums else None


def extract_receiver(text):
    words = text.split()

    # Pattern 1: "... to <receiver ...>"
    if "to" in words:
        i = words.index("to")
        return " ".join(words[i + 1:]).strip()

    # Pattern 2: "... for <receiver ...>"
    if "for" in words:
        i = words.index("for")
        return " ".join(words[i + 1:]).strip()

    # Pattern 3: "pay simran 100 rupees" or "send ravi 200"
    # Take words after "pay"/"send" up until a numeric token appears.
    # Pattern 3: "pay simran 100 rupees" or "send ravi 200"
    # Take words after "pay"/"send" up until a numeric token appears.
    for trigger in ["pay", "send", "transfer", "transwar"]:
        if trigger in words:
            i = words.index(trigger)
            tail = words[i + 1 :]
            if not tail:
                continue

            receiver_tokens = []
            for w in tail:
                # stop when we hit a pure number (amount) or currency word
                if re.fullmatch(r"\d+", w) or w.lower() in {"rs", "inr", "rupees", "rupay"}:
                    break
                receiver_tokens.append(w)

            receiver = " ".join(receiver_tokens).strip()
            if receiver:
                return receiver

    return None


def extract_action(text):
    if "pay" in text:
        return "pay"
    if "send" in text:
        return "send"
    if "transfer" in text or "transwar" in text:
        return "transfer"
    return None
