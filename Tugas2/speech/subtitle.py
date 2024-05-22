import pysubs2

# Buat objek SSAFile baru
subs = pysubs2.SSAFile()

list_transcript = [[
                       "she know that I I just wanted to cheer you see we you and I are the same I can't say the things that I truly feel just stop it and you're wrong we're nothing alike",
                       0.8770774006843567, 13], [" it's really embarrassed me", 0.9449164867401123, 17], [
                       ' have you considered my feelings at all everyone just hurt this I seriously hate pushy people like you',
                       0.9591031670570374, 25],
                   [" what if I told you in person just leave me alone didn't you hear me", 0.8906494379043579, 31],
                   [' but I hate you', 0.813417911529541, 33], [' I see', 0.6545330286026001, 45],
                   [' you hate me that much okay well then', 0.8414788246154785, 54], [' hey', 0.3442528545856476, 57]]

# # Tambahkan subtitle pertama
# subs.append(pysubs2.SSAEvent(
#     start=pysubs2.make_time(s=0),
#     end=pysubs2.make_time(s=5),
#     text="Subtitle pertama."
# ))
#
# # Tambahkan subtitle kedua
# subs.append(pysubs2.SSAEvent(
#     start=pysubs2.make_time(s=5),
#     end=pysubs2.make_time(s=10),
#     text="Subtitle kedua."
# ))


# Looping Save Transkrip
detik_sebelumnya = 0

for transkrip in list_transcript:
    subs.append(pysubs2.SSAEvent(
        start=pysubs2.make_time(s=detik_sebelumnya),
        end=pysubs2.make_time(s=transkrip[2]),
        text=transkrip[0]
    ))
    detik_sebelumnya = transkrip[2]

# Simpan file SRT
subs.save("Anime.srt")

import pysubs2
from pysubs2 import Color, Alignment, SSAStyle

# Buat objek SSAFile baru
subs = pysubs2.SSAFile()

# Buat style dengan warna merah
red_style = SSAStyle(
    primarycolor=Color(255, 0, 0),  # Red
    alignment=Alignment.MIDDLE_CENTER
)

# Tambahkan subtitle pertama dengan style merah
subs.append(pysubs2.SSAEvent(
    start=pysubs2.make_time(s=0),
    end=pysubs2.make_time(s=5),
    text="Subtitle pertama (merah).",
    style="RedStyle"
))

# Buat style dengan warna biru
blue_style = SSAStyle(
    primarycolor=Color(0, 0, 255),  # Blue
    alignment=Alignment.MIDDLE_CENTER
)

# Tambahkan subtitle kedua dengan style biru
subs.append(pysubs2.SSAEvent(
    start=pysubs2.make_time(s=5),
    end=pysubs2.make_time(s=10),
    text="Subtitle kedua (biru).",
    style="BlueStyle"
))

# Tambahkan style ke SSAFile
subs.styles["RedStyle"] = red_style
subs.styles["BlueStyle"] = blue_style

# Simpan file SRT
subs.save("my_subtitles.srt")