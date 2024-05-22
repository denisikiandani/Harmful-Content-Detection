import pysubs2

# Buat objek SSAFile baru
subs = pysubs2.SSAFile()

list_transcript = [["when I'm back in the White House America's enemies will now once again", 0.9746600389480591, 4], [" and they're going to know it", 0.8480657935142517, 6], [' that if you try to', 0.9774478673934937, 9], [' kill our citizens we will kill you we will kill you', 0.9911298155784607, 13], [' I told them all that we had no problem', 0.9775905609130859, 17], [" you know we had no problem three years ago we had no problem for four years nobody even this is Unthinkable I mean I just watch and see what's happening it's Unthinkable this couldn't have happened", 0.9837308526039124, 28]]
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

#
# import pysubs2
# from pysubs2 import Color, Alignment, SSAStyle
#
# # Buat objek SSAFile baru
# subs = pysubs2.SSAFile()
#
# # Buat style dengan warna merah
# red_style = SSAStyle(
#     primarycolor=Color(255, 0, 0),  # Red
#     alignment=Alignment.MIDDLE_CENTER
# )
#
# # Tambahkan subtitle pertama dengan style merah
# subs.append(pysubs2.SSAEvent(
#     start=pysubs2.make_time(s=0),
#     end=pysubs2.make_time(s=5),
#     text="Subtitle pertama (merah).",
#     style="RedStyle"
# ))
#
# # Buat style dengan warna biru
# blue_style = SSAStyle(
#     primarycolor=Color(0, 0, 255),  # Blue
#     alignment=Alignment.MIDDLE_CENTER
# )
#
# # Tambahkan subtitle kedua dengan style biru
# subs.append(pysubs2.SSAEvent(
#     start=pysubs2.make_time(s=5),
#     end=pysubs2.make_time(s=10),
#     text="Subtitle kedua (biru).",
#     style="BlueStyle"
# ))
#
# # Tambahkan style ke SSAFile
# subs.styles["RedStyle"] = red_style
# subs.styles["BlueStyle"] = blue_style
#
# # Simpan file SRT
# subs.save("my_subtitles.srt")