from collections import Counter


def check_inclusion(s, t):
    len_s, len_t = len(s), len(t)

    # Agar s uzunligi t dan katta bo'lsa, False qaytaramiz
    if len_s > len_t:
        return False

    # s va birinchi oynaning harflari sanog'ini hisoblash
    s_count = Counter(s)
    window_count = Counter(t[:len_s])
    print(s_count)
    # Birinchi oynani tekshirish
    if s_count == window_count:
        return True

    # Oynani chapdan o'ngga siljitish
    for i in range(len_s, len_t):
        # Yangi harfni oynaga qo'shish
        window_count[t[i]] += 1
        # Eski harfni o'chirish
        window_count[t[i - len_s]] -= 1
        if window_count[t[i - len_s]] == 0:
            del window_count[t[i - len_s]]

        # Har bir oynani tekshirish
        if s_count == window_count:
            return True

    return False


# Misollar
s = "ab"
t = "eidbaooo"
print(check_inclusion(s, t))  # True

s = "ab"
t = "eidboaoo"
print(check_inclusion(s, t))  # False