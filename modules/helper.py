from datetime import datetime

def ChangeMonth(date):
    if date.find("Jan")!=-1:
        if date.find("January")!=-1:
            date = date.replace("January","Jan")
        elif date.find("Januari")!=-1:
            date = date.replace("Januari","Jan")
        else :
            date = date.replace("Janu","Jan")
    elif date.find("Feb")!=-1:
        if date.find("February")!=-1:
            date = date.replace("February","Feb")
        else :
            date = date.replace("Februari","Feb")
    elif date.find("Mar")!=-1:
        if date.find("March")!=-1:
            date = date.replace("March","Mar")
        else :
            date = date.replace("Maret","Mar")        
    elif date.find("Apr")!=-1:
        date = date.replace("April","Apr")
    elif date.find("Mei")!=-1:
        date = date.replace("Mei","May")
    elif date.find("Jun")!=-1:
        if date.find("June")!=-1:
            date = date.replace("June","Jun")
        else :
            date = date.replace("Juni","Jun")
    elif date.find("Jul")!=-1:
        if date.find("July")!=-1:
            date = date.replace("July","Jul")
        else :
            date = date.replace("Juli","Jul")        
    elif date.find("Agu")!=-1:
        if date.find("Agustus")!=-1:
            date = date.replace("Agustus","Aug")
        elif date.find("August")!=-1:
            date = date.replace("August","Aug")
        else :
            date = date.replace("Agu","Aug")
    elif date.find("Agt")!=-1:
        date = date.replace("Agt","Aug")
    elif date.find("Ags")!=-1:
        date = date.replace("Ags","Aug")
    elif date.find("Agst")!=-1:
        date = date.replace("Agst","Aug")
    elif date.find("Sep")!=-1:
        date = date.replace("September","Sep")
    elif date.find("Okt")!=-1:
        if date.find("Oktober")!=-1:
            date = date.replace("Oktober","Oct")
        elif date.find("October")!=-1:
            date = date.replace("October","Oct")
        else :
            date = date.replace("Okt","Oct")
    elif date.find("Nov")!=-1:
        date = date.replace("November","Nov")
    elif date.find("Nopember")!=-1:
        date = date.replace("Nopember","Nov")
    elif date.find("Des")!=-1:
        if date.find("Desember")!=-1:
            date = date.replace("Desember","Dec")
        elif date.find("December")!=-1:
            date = date.replace("December","Dec")
        else :
            date = date.replace("Des","Dec")

    return date

def related_links():
    related_links = [
    "Baca Juga",
    "Baca Juga:",
    "baca juga",
    "baca juga :"
    "Berita terkait",
    "Baca:",
    "Baca :",
    "Artikel Terkait",
    "Artikel Lainnya",
    "Berita Lainnya",
    "Read Also",
    "Read More",
    "baca berita selanjutnya",
    "lihat juga",
    "Posting Terkait",
    "READ",
    "Artikel menarik lainnya",
    "Baca juga:",
    "Baca juga: ",
    "Baca selengkapnya di sini",
    "Cek berita, artikel, dan konten",
    "Baca selengkapnya",
    "Baca artikel lain terkait",
    "Baca berita lain"
    ]
    return related_links