#importing the libraries
from tkinter import ttk
from tkinter import filedialog
from tkinter.font import BOLD 
from tinytag import TinyTag
from tkinter import *
from pygame import mixer
import os
import time
import random
import pyautogui
import customtkinter
from tkinter import messagebox

#library for album image managing
import eyed3
import io
from PIL import Image,ImageTk 

#sqlite3 for data management
import sqlite3
import threading

#database creation for the first time app opening
try:
	con=sqlite3.connect("Melo_database.db",check_same_thread=False)
	cur=con.cursor()
except Exception as e:
	messagebox.showerror("Error",f"An error occured because {e}")
	os._exit(0)

sql_songs_list1=[]
system_songs=[]
try:
    cur.execute("create table melo_dat(songs_without_path text,songs_with_path text,favourite int default 0,most_played int default 0,current int default 1,playlist1 int default 0,total_playlist int default 1)")
    cur.execute("create table playlists(playlist1 text)")
    cur.execute("create table colors (color int default 1,playlist1 text)")
    cur.execute("insert into colors(color,playlist1) values(1,'white')")
    con.commit()
except Exception as e:
	pass

cur.execute("select * from melo_dat")
for i in cur:
	sql_songs_list1.append(i[1])

mixer.init()

#creating the list of songs
songs_list_without_index=[]
songs_list=[]
list1=""
x=os.path.join(os.path.expandvars("%userprofile%"))
drives = [ chr(x) + ":" for x in range(65,91) if os.path.exists(chr(x) + ":") ]
drives.remove("C:")
drives.append(x)
for i in drives:
	for root, dirs, files in os.walk(i+"\\"):
		for file in files:
			try:
				if (file.endswith('.mp3') or file.endswith('.mpeg') ):
					b=root+"\\"+file
					a=file
					system_songs.append(b)
					if b not in sql_songs_list1:
						cur.execute(f"insert into melo_dat (songs_without_path,songs_with_path) values('{a}','{b}')")
						con.commit()
			except:
				pass

to_delete=[]
for i in sql_songs_list1:
        if i not in system_songs:
                to_delete.append(i)

for i in to_delete:
        cur.execute(f"delete from melo_dat where songs_with_path='{i}'")
        con.commit()

length_of_songsList=len(songs_list)

#creating a main window with title and icon
root=Tk()
root.geometry("1000x600+450+100")
root.resizable(0,0)
root.title("Melo")

#app icon
app_icon = PhotoImage(file = ".\\resources\\icon.png")
root.iconphoto(False, app_icon)
root.config(bg="#1f1d1d")

#defaut variables
starting_time=0
current_song=0
current_index=0
suffle=0
loop=1
repeat_one=0
selected_in_listbox=0
faourite_songs=[]
single=0
a=0
minutes=0
seconds=0
thread=0
fav_heart=[]
wait=0
error_for_timer=0
songs=[]
error=0
playlist_dict=dict()

#timer
def timer():
	global songs_list,current_index,a,minutes,seconds,tag,time1,var,Time_view,wait,thread,error,error_for_timer
	while True:
		try:
			while(a<=int(time1)):
				time.sleep(0.25)
				if seconds==60:
						minutes+=1
						seconds=0
				progress_bar.set(int(a))
				Time_view.config(text=str(minutes)+":"+str(seconds))
				time.sleep(0.25)
				seconds+=1
				time.sleep(0.25)
				while current_song==0:
						root.update()
						pass
				if error_for_timer==1:
					a=0
					Time_view.config(text="--:--")
					progress_bar.set(0)
					mixer.music.stop()
					play.config(image=Photo_pause)
					album_label.config(image=album_image)
					break
				a=a+1
				time.sleep(0.25)
				if wait==1:
					mixer.music.set_pos(a)
				wait=0
		except:
			pass
		next_previous("nex")
		if error==1:
			thread=0
			return

#new implementations
def on_closing():
        global playlist_dict
        try:
            for old,new in playlist_dict.items():
                cur.execute(f"alter table melo_dat rename column {old} to {new}")
                con.commit()
                cur.execute(f"alter table playlists rename column {old} to {new}")
                con.commit()
                cur.execute(f"alter table colors rename column {old} to {new}")
                con.commit()
        except:
            pass		
        try:
                mixer.music.stop()
                mixer.music.unload()
                mixer.quit()
        except:
            try:
                mixer.music.stop()
                mixer.music.unload()
            except:
                pass
        root.destroy()
        os._exit(0)		
root.protocol("WM_DELETE_WINDOW", on_closing)


def timer_settings():
	global songs_list,current_index,a,thread,minutes,seconds,time1
	tag=TinyTag.get(songs_list[current_index])
	time1=tag.duration
	minutes=00
	seconds=00
	a=0
	try:
		progress_bar.configure(to=int(time1))
	except:
		progress_bar.configure(to=1)
	if thread==0:
		thread=1
		t1=threading.Thread(target=timer)
		t1.start()

#function to play the song
def play1():
	global starting_time,songs_list,list_of_tracks,current_song,fav_heart,songs_list_without_index,length_of_songsList
	if starting_time==0:
		if not list_of_tracks.get(0):
			songs_list=[]
			songs_list_without_index=[]
			length_of_songsList=0
			cur.execute("select * from melo_dat")
			for i in cur:
				songs_list_without_index.append(i[0])
				songs_list.append(i[1])
				fav_heart.append(i[2])
			length_of_songsList=len(songs_list)
			for i in range(length_of_songsList):
				a=str(i+1)+". "+songs_list_without_index[i]
				list_of_tracks.insert(i,str(i+1)+". "+songs_list_without_index[i])
		try:
			mixer.music.load(songs_list[0])
			mixer.music.play()	
			if fav_heart[0]==1:
				favourite_heart.config(image=Photo_red_heart)
		except:
			pass
		temp=songs_list[0]
		album_image_process(temp)
		
		play.config(image=Photo_play)
		favourite_heart.config(image=Photo_white_heart)
		starting_time=1
		current_song=1
		title=list_of_tracks.get(0)
		if len(title)>39:
			Track_title.config(anchor="w")
		else:
			Track_title.config(anchor="center")
		Track_title.config(text=title)
		tag=TinyTag.get(songs_list[current_index])
		timer_settings()
		try:
			artist=tag.artist
			if len(artist)>35:
				Artist_name.config(anchor="w")
			Artist_name.config(text="Artist :"+artist)
		except:
			Artist_name.config(anchor="center")
			Artist_name.config(text="Artist : Not available")
		most_played()
	elif current_song==1:
		mixer.music.pause()
		play.config(image=Photo_pause)
		current_song=0	
	else:
		mixer.music.unpause()
		play.config(image=Photo_play)
		current_song=1

#function for nex button
def next_previous(mode):
	global songs_list,current_index,starting_time,current_song,suffle,selected_in_listbox,minutes,seconds,a,thread,time1,error,fav_heart,error_for_timer
	mixer.music.unload()
	try:
		if mode=="nex":
			if (loop==1 and selected_in_listbox==0):
				if (current_index<length_of_songsList-1):
					current_index+=1
				else:
					if loop==1:
						current_index=0
			elif (suffle==1 and selected_in_listbox==0):
				current_index=random.randrange(0,length_of_songsList)
			elif selected_in_listbox==1:
				current_index+=1
				selected_in_listbox=0	

		elif mode=="prev":
			if (loop==1 and selected_in_listbox==0):
				if (current_index>0):
					current_index-=1
				else:
					if loop==1:
						current_index=length_of_songsList-1
			elif (suffle==1 and selected_in_listbox==0):
				current_index=random.randrange(0,length_of_songsList)
			elif selected_in_listbox==1:
				current_index+=1
				selected_in_listbox=0	
				
		favourite_heart.config(image=Photo_white_heart)
		list_of_tracks.activate(current_index)
		mixer.music.load(songs_list[current_index])
		mixer.music.play()	
		if fav_heart[current_index]==1:
			favourite_heart.config(image=Photo_red_heart)
		play.config(image=Photo_play)
		current_song=1
		starting_time=1
		temp=songs_list[current_index]
		album_image_process(temp)
		Text=list_of_tracks.get(current_index)
		data2=Text[0:43]
		if len(data2)>39:
			Track_title.config(anchor="w")
		else:
			Track_title.config(anchor="center")
		Track_title.config(text=data2)
		tag=TinyTag.get(songs_list[current_index])
		timer_settings()
		try:
			artist=tag.artist
			if len(artist)>35:
				Artist_name.config(anchor="w")
			Artist_name.config(text="Artist :"+artist)
		except:
			Artist_name.config(anchor="center")
			Artist_name.config(text="Artist : Not available")
		most_played()
		error=0
		error_for_timer=0
	except:
		Track_title.config(text="Music not supported")
		Artist_name.config(text="")
		error_for_timer=1
		error=1

#function to change track title when a listbox item is clicked
def callback(event):
	global current_song,starting_time,current_index,selected_in_listbox,a,minutes,seconds,tag,time1,var,thread	
	try:
		selection=event.widget.curselection()
		if selection:
			index=selection[0]
			data=event.widget.get(index)
			Track_title.configure(text=data)
			current_index=index-1
			selected_in_listbox=1
			next_previous("nex")
	except:
		pass

#function  for volume controls
def volume_up():
	pyautogui.press('volumeup',3)

def volume_down():
	pyautogui.press('volumedown',3)

#suffle function
def Suffle():
	global suffle,loop,repeat_one
	if repeat_one==0 and loop==1:
		suffle=1
		repeat_one=0
		loop=0
		Music_Suffle.config(image=Photo_suffle)
	
	elif repeat_one==0 and suffle==1:
		repeat_one=1
		loop=0
		suffle=0
		Music_Suffle.config(image=Photo_repeat_one)
	elif loop==0:
		loop=1
		suffle=0
		repeat_one=0
		Music_Suffle.config(image=Photo_loop)
	else:
		pass

#Album art modification functions
def album_image_process(song_name):
    try:	
        song_name=songs_list[current_index]
        song=eyed3.load(song_name)
        img=Image.open(io.BytesIO(song.tag.images[0].image_data))
        image1=img.resize((300,300),Image.ANTIALIAS)
        image1=ImageTk.PhotoImage(image1)
        album_label.configure(image=image1)
        album_label.image=image1
    except:
        i=random.randint(1,7)
        image_except=Image.open(f".\\resources\\{i}.jpg")
        image2=ImageTk.PhotoImage(image_except)
        album_label.configure(image=image2)
        album_label.image=image2
    return

#library songs
def library_songs():
	try:
		global songs_list_without_index,songs_list,length_of_songsList,fav_heart
		list_of_tracks.delete(0,END)
		songs_list=[]
		fav_heart=[]
		songs_list_without_index=[]
		length_of_songsList=0
		cur.execute("select * from melo_dat")
		for i in cur:
			songs_list_without_index.append(i[0])
			songs_list.append(i[1])
			fav_heart.append(i[2])
		length_of_songsList=len(songs_list)
		for i in range(length_of_songsList):
			a=str(i+1)+". "+songs_list_without_index[i]
			list_of_tracks.insert(i,str(i+1)+". "+songs_list_without_index[i])
	except:
		pass
        
def add_favourite():
	global songs_list_without_index,current_index
	y=0
	try:
		a=songs_list_without_index[current_index]
	except:
		a=list_for_most_played_buttons[current_index][1]
	cur.execute(f"select favourite from melo_dat where songs_without_path='{a}'")
	for i in cur:
		y=i[0]
	if y==0:
		cur.execute(f"update melo_dat set favourite=1 where songs_without_path='{a}'")
		favourite_heart.config(image=Photo_red_heart) 
	else:
		cur.execute(f"update melo_dat set favourite=0 where songs_without_path='{a}'")
		favourite_heart.config(image=Photo_white_heart) 
	con.commit()
	root.update()


#adding songs for library favourite
def library_favourite():
	global songs_list_without_index,songs_list,length_of_songsList,fav_heart
	list_of_tracks.delete(0,END)
	songs_list=[]
	songs_list_without_index=[]
	fav_heart=[]
	length_of_songsList=0
	cur.execute("select * from melo_dat where favourite=1")
	for i in cur:
		songs_list_without_index.append(i[0])
		songs_list.append(i[1])
		fav_heart.append(1)
	length_of_songsList=len(songs_list)
	for i in range(length_of_songsList):
		a=str(i+1)+". "+songs_list_without_index[i]
		list_of_tracks.insert(i,str(i+1)+". "+songs_list_without_index[i])

#increamenting most played
def most_played():
	global songs_list,current_index
	a=songs_list[current_index]
	root.update()
	cur.execute(f"update melo_dat set most_played=most_played+1 where songs_with_path='{a}'")
	con.commit()
	root.update()
	return

cur.execute("select max(most_played),songs_with_path,songs_without_path,favourite from melo_dat group by songs_with_path")
list_for_most_played_buttons=[]
for i in cur:
	list_for_most_played_buttons.append(i)
list_for_most_played_buttons=sorted(list_for_most_played_buttons,reverse=True)

#functions for most played list buttons
def most_played_list():
	global songs_list_without_index,songs_list,length_of_songsList,list_for_most_played_buttons,fav_heart
	list_of_tracks.delete(0,END)
	songs_list=[]
	fav_heart=[]
	songs_list_without_index=[]
	length_of_songsList=0
	for i in list_for_most_played_buttons:
		songs_list_without_index.append(i[2])
		songs_list.append(i[1])
		fav_heart.append(i[3])
	length_of_songsList=len(songs_list)
	for i in range(length_of_songsList):
		a=str(i+1)+". "+songs_list_without_index[i]
		list_of_tracks.insert(i,str(i+1)+". "+songs_list_without_index[i])
	return

#common functions of buttons
button_music=0
def buttons_common(index):
    global button_music,starting_time,current_song,current_index,list_for_most_played_buttons,button_music
    current_index=index
    current_song=1
    starting_time=1
    button_music=list_for_most_played_buttons[index][1]
    try:
        mixer.music.load(button_music)
        mixer.music.play()	
    except:
        print("music not supported")
    text=list_for_most_played_buttons[index][2]
    data2=text[0:43]
    if len(data2)>39:
        Track_title.config(anchor="w")
    else:
        Track_title.config(anchor="center")
    Track_title.config(text=data2)
    play.config(image=Photo_play)
    tag=TinyTag.get(button_music)
    artist=tag.artist
    try:
        if len(artist)>35:
            Artist_name.config(anchor="w")
        Artist_name.config(text="Artist :"+artist)
    except:
        Artist_name.config(anchor="center")
        Artist_name.config(text="Artist : Not available")
    timer_settings()

# most_played button album art 
def most_album_art(index):
	try:
		song_name=list_for_most_played_buttons[index][1]
		song=eyed3.load(song_name)
		img=Image.open(io.BytesIO(song.tag.images[0].image_data))
		image1=img.resize((300,300),Image.ANTIALIAS)
		image1=ImageTk.PhotoImage(image1)
		album_label.configure(image=image1)
		album_label.image=image1
	except:
		image3=PhotoImage(file=".\\resources\\music.png")
		album_label.configure(image=image3)
		album_label.image=image3
	
# calling buttons
def button1(index):
	most_album_art(index)
	most_played_list()
	buttons_common(index)
	return

#window for add playlist
def remove(playlist_name,win,lb):
	global songs
	for i in lb.curselection():
		song=songs[i]
		cur.execute(f"update melo_dat set {playlist_name}=0 where songs_without_path='{song}'")
		con.commit()
	root.update()
	win.destroy()

def add(playlist_name,lb,win):
	for i in lb.curselection():
		song=songs[i]
		cur.execute(f"update melo_dat set {playlist_name}=1 where songs_without_path='{song}'")
		con.commit()
	win.destroy()

def search2(ev,entry,lb,playlist_name,comand):
		global songs
		songs=[]
		q=entry.get()
		if comand=="add_songs":
			cur.execute(f"select songs_without_path from melo_dat where songs_without_path LIKE '%{q}%'")
		else:
			cur.execute(f"select songs_without_path from melo_dat where songs_without_path LIKE '%{q}%' AND {playlist_name}=1")
		lb.delete(0,END)
		j=0
		for i in cur:
			lb.insert(j,str(j+1)+". "+i[0])
			songs.append(i[0])
			j+=1

def add_songs_to_playlist(playlist_name,comand):
	global songs
	songs=[]
	win=Toplevel(root)
	win.configure(bg="#272223")
	win.geometry("500x525+500+120")
	win.resizable(0,0)
	icon = PhotoImage(file = ".\\resources\\icon.png")
	win.iconphoto(False,icon)
	entry=customtkinter.CTkEntry(master=win,width=300,bg_color="#272223",fg_color="#272223",placeholder_text="Search",font=("Georgia",11,BOLD))
	entry.place(x=53,y=10)
	entry.bind("<Key>",lambda v: search2(v,entry,lb,playlist_name,comand))
	lb=Listbox(win,width=40,font=("Georgia",12),bg="#343434",fg="white",height=17,border=0,selectbackground="red",selectmode=MULTIPLE)
	lb.place(x=10,y=50)
	if comand=="add_songs":
		cur.execute("select songs_without_path from melo_dat")
	else:
		cur.execute(f"select songs_without_path from melo_dat where {playlist_name}=1")
	z=0
	for i in cur:
		songs.append(i[0])
		lb.insert(z,str(z+1)+". "+i[0])
		z+=1
	if comand=="add_songs":
		btn=customtkinter.CTkButton(win,text="ADD",command=lambda :add(playlist_name,lb,win))
	else:
		btn=customtkinter.CTkButton(win,text="REMOVE",command=lambda : remove(playlist_name,win,lb))	
	btn.place(x=120,y=390)
	win.mainloop()
	
#most played default images
def most_played_images(index):
    try:
        song_name=list_for_most_played_buttons[index][1]
        song=eyed3.load(song_name)
        img=Image.open(io.BytesIO(song.tag.images[0].image_data))
        image1=img.resize((132,123),Image.ANTIALIAS)
        image1=ImageTk.PhotoImage(image1)
        globals()["button_"+str(index+1)].configure(image=image1)
        globals()["button_"+str(index+1)].image=image1
    except:
        image2=PhotoImage(file=".\\resources\\8.png")
        globals()["button_"+str(index+1)].configure(image=image2)
        globals()["button_"+str(index+1)].image=image2

#function of playlist buttons
def add_playlist_to_listbox(name):
	global playlist_dict,songs_list_without_index,songs_list,length_of_songsList,fav_heart
	list_of_tracks.delete(0,END)
	songs_list=[]
	songs_list_without_index=[]
	fav_heart=[]
	length_of_songsList=0
	cur.execute(f"select songs_without_path,songs_with_path,favourite from melo_dat where {name}=1")
	for i in cur:
			songs_list_without_index.append(i[0])
			songs_list.append(i[1])
			fav_heart.append(i[2])
	length_of_songsList=len(songs_list)
	for i in range(length_of_songsList):
		list_of_tracks.insert(i,str(i+1)+". "+songs_list_without_index[i])
	return

#search function
def search(ev):
	global songs_list,songs_list_without_index,length_of_songsList,fav_heart
	songs_list=[]
	fav_heart=[]
	songs_list_without_index=[]
	length_of_songsList=0
	q=Search_box.get()
	cur.execute(f"select songs_with_path,songs_without_path,favourite from melo_dat where songs_without_path LIKE '%{q}%'")
	list_of_tracks.delete(0,END)
	j=0
	for i in cur:
		list_of_tracks.insert(j,str(j+1)+". "+i[1])
		songs_list.append(i[0])
		songs_list_without_index.append(i[1])
		fav_heart.append(i[2])
		j+=1
	length_of_songsList=len(songs_list)


def insert_songs():
	global songs_list,songs_list_without_index,length_of_songsList,fav_heart
	path=filedialog.askdirectory(title="Melo")
	if path=="":
		return	
	songs_list=[]
	fav_heart=[]
	songs_list_without_index=[]
	length_of_songsList=0
	for root, dirs, files in os.walk(path+"\\"):
		for file in files:
			try:
				if (file.endswith('.mp3') or file.endswith('.mpeg') ):
					b=root+"\\"+file
					a=file
					songs_list.append(b)
					songs_list_without_index.append(a)
			except:
				pass
	list_of_tracks.delete(0,END)
	j=0
	for i in songs_list_without_index:
		list_of_tracks.insert(j,str(j+1)+". "+i)
		j+=1
		cur.execute(f"select favourite from melo_dat where songs_without_path='{i}'")
		for l in cur:
				fav_heart.append(l[0])
	length_of_songsList=len(songs_list)

def check(value):
	global a,wait,minutes,seconds
	a=int(value)
	wait=1
	minutes=int(a/60)
	seconds=int(a%60)

playlist_rename=None
def Rename():
	global playlist_rename,playlist_dict
	ac=customtkinter.CTkInputDialog(text="Enter the name:",title="Rename")
	h=ac.get_input()
	if h=="" or h.isspace() or h==None:
		return
	playlist_dict[playlist_rename]=h
	globals()[playlist_rename].config(text=h)
	playlist_dict[playlist_rename]=h

def change_font_color(name):
    colors=["#ff0000","#ff9966","#99ff66","#00ff00","#ffffff","#ffccff","#cc00cc","#ff99ff","#b3ffb3","#e600ac","#cc9900","#4dd2ff"]
    color=random.choice(colors)
    globals()[name].config(fg=color)
    cur.execute(f"update colors set {name}='{color}' where color=1")
    con.commit()

def delete_playlist(name):
    cur.execute("select total_playlist from melo_dat")
    for i in cur:
        if i[0]==1:
            messagebox.showwarning("Info","There should be atleast one playlist")
            return
    cur.execute("update melo_dat set total_playlist=total_playlist-1")
    con.commit()
    cur.execute(f"alter table melo_dat drop column {name}")
    con.commit()
    cur.execute(f"alter table playlists drop column {name}")
    con.commit()
    cur.execute(f"alter table colors drop column {name}")
    con.commit()
    globals()[name].destroy()
	
def do_popup(event,i):
	global playlist_rename
	playlist_rename=i
	try:
		m.tk_popup(event.x_root, event.y_root)
	finally:
		m.grab_release()

def add_playlist():
	cur.execute("select total_playlist from melo_dat")
	for i in cur:
		total=i[0]
		break
	if total>=6:
		messagebox.showwarning("Info","You can create maximum 6 playlists")
		return
	p=customtkinter.CTkInputDialog(text="Enter the name:",title="Rename")
	p=p.get_input()
	if p=="" or p.isspace() or p==None:
		return
	try:
		cur.execute("update melo_dat set total_playlist=total_playlist+1")
		con.commit()
		cur.execute(f"alter table melo_dat add column {p} int default 0")
		con.commit()
		cur.execute(f"alter table playlists add column {p} text")
		con.commit()
		cur.execute(f"alter table colors add column {p} text default 'white'")
		con.commit()
		globals()[p]=Button(adding_playlist_using_1_btn,anchor=W,text=p,fg="white",bd=0,bg="black",font=("Georgia",10,"bold"))
		globals()[p].pack(pady=1,anchor="w",expand=TRUE,fill=X)
		globals()[p].bind("<Button-3>",lambda x:do_popup(x,p))
		globals()[p].bind("<Button-1>",lambda x:add_playlist_to_listbox(p))
	except:
			pass

#options frame
Options=Frame(root,bg="#000000",height=560,width=170)
Options.place(x=0,y=0)
melo_label=customtkinter.CTkLabel(Options,text="Melo",font=("Georgia",45,"bold"),text_color="red")
melo_label.place(x=5,y=5)

#Library
playlist_options_label=Label(Options,text="Library",fg="white",bg="black",font=("Georgia",15,"bold"))
playlist_options_label.place(x=5,y=90)

#library images
songs_image=PhotoImage(file=".\\resources\\songs.png")
fav_image=PhotoImage(file=".\\resources\\fav.png")
most_play_image=PhotoImage(file=".\\resources\\most.png")

#library labels
songs_label=Label(Options,image=songs_image,bg="black")
songs_label.place(x=30,y=135)
fav_label=Label(Options,image=fav_image,bg="black")
fav_label.place(x=30,y=171)
most_play_label=Label(Options,image=most_play_image,bg="black")
most_play_label.place(x=30,y=205)

#library options
songs_button=Button(Options,text="Songs",fg="white",anchor="w",bd=0,bg="black",font=("Georgia",10,"bold"),width=9,command=library_songs)
songs_button.place(x=60,y=135)

Favourite_button=Button(Options,text="Favourite",anchor="w",fg="white",bd=0,bg="black",font=("Georgia",10,"bold"),width=9,command=library_favourite)
Favourite_button.place(x=60,y=171)

most_played_button=Button(Options,text="Most Played",anchor="w",fg="white",bd=0,bg="black",font=("Georgia",10,"bold"),width=9,command=most_played_list)
most_played_button.place(x=55,y=205)

#playlist
Playlist_label=Label(Options,text="Playlist",fg="white",bg="black",font=("Georgia",15,"bold"))
Playlist_label.place(x=5,y=280)

adding_playlist_using_1_btn=Frame(Options,background="black",width=200,height=300)
adding_playlist_using_1_btn.place(x=30,y=330)

#Most_Played frame
Most_played=Frame(root,bg="#1f1d1d")
Most_played.place(x=170,y=0)
Most_played_label=Label(Most_played,text="Most Played",font=("Georgia",11,"bold"),bg="#1f1d1d",fg="white")
Most_played_label.place(x=0,y=0)


#most played items
def most_played_buttons():
	class playlist:
		def __init__(self,i) -> None:
			globals()["button_"+str(i+1)]=Button(Most_played,height=120,width=130,bd=0, background="black",command=lambda :button1(i))
			globals()["button_"+str(i+1)].pack(side=LEFT,padx=12,pady=30)
	for i in range(0,5):
		playlist(i)
		most_played_images(i)
threading.Thread(target=most_played_buttons).start()


#frame for playlist
Playlist=Frame(root,bg="#272223",bd=0,height=400,width=480)
Playlist.place(x=170,y=160)

#frame for music image and name
Music=Frame(root,bg="#444141",height=417,width=350)
Music.place(x=650,y=160)

#album image
album_image=PhotoImage(file=".\\resources\\music.png")

#Frame for music album
album_label=Label(Music,bg="black",height="300",width="300",image=album_image)
album_label.place(x=25,y=20)

#label for title of the music
Track_title=Label(Music,text="Title : title not available",font=("Georgia",10),bg="#444141",fg="white",width=35,anchor="center")
Track_title.place(x=2,y=340)

#labell for artist name
Artist_name=Label(Music,bg="#444141",fg="white",font=("Georgia",10),text="Artist name not available",width=35,anchor="center")
Artist_name.place(x=2,y=364)
	
#To search the songs
Search_box=customtkinter.CTkEntry(Playlist,bg_color="#272223",fg_color="#272223",placeholder_text="Search",font=("Georgia",11,BOLD),width=300,height=15)
Search_box.place(x=12,y=5)
Search_box.bind("<Key>",search)

insert_folder_image=PhotoImage(file=".\\resources\\open_folder.png")
insert_folder_songs=Button(Playlist,image=insert_folder_image,bg="black",bd=0,background="#272223",command=insert_songs)
insert_folder_songs.place(x=415,y=2)

#List of the  songs from system
list_of_tracks=Listbox(Playlist,font=("Georgia",12),bg="#343434",fg="white",width=39,height=14,border=0,selectbackground="red",yscrollcommand=False)
list_of_tracks.place(x=5,y=42)
list_of_tracks.bind("<<ListboxSelect>>",callback)

#bottom frame for controls
Controls=Frame(root,bg="#333333",height=40,width=1000)
Controls.place(x=0,y=560)

#image of play button
Photo_pause=PhotoImage(file=".\\resources\\play.png")
Photo_play=PhotoImage(file=".\\resources\\pause.png")
Photo_next=PhotoImage(file=".\\resources\\next.png")
Photo_previous=PhotoImage(file=".\\resources\\previous.png")

Photo_volume_up=PhotoImage(file=".\\resources\\volume_up.png")
Photo_volume_down=PhotoImage(file=".\\resources\\volume_down.png")

Photo_loop=PhotoImage(file=".\\resources\\loop.png")
Photo_suffle=PhotoImage(file=".\\resources\\suffle.png")
Photo_repeat_one=PhotoImage(file=".\\resources\\repeat_one.png")
Photo_red_heart=PhotoImage(file=".\\resources\\red_heart.png")
Photo_white_heart=PhotoImage(file=".\\resources\\white_heart.png")

#control buttons
play=Button(Controls,bg="#333333",fg="#333333",image=Photo_pause,border=0,activebackground="#293241",command=play1)
play.place(x=160,y=4)
previous=Button(Controls,bg="#333333",fg="#333333",image=Photo_previous,border=0,activebackground="#293241",command=lambda:next_previous("prev"))
previous.place(x=110,y=4)
Next=Button(Controls,bg="#333333",fg="#333333",image=Photo_next,border=0,activebackground="#293241",command=lambda:next_previous("nex"))
Next.place(x=210,y=4)

#volume buttons
Vol_up=Button(Controls,image=Photo_volume_up,bg="#333333",fg="#333333",text="vol UP",border=0,activebackground="#293241",command=volume_up)
Vol_up.place(x=960,y=4)
Vol_down=Button(Controls,image=Photo_volume_down,bg="#333333",fg="#333333",text="V -",border=0,activebackground="#293241",comman=volume_down)
Vol_down.place(x=920,y=4)

#volume percentage label
vol_label=Label(Controls,text="vol",font=("Georgia",12),bg="#343434",fg="white",border=0)
vol_label.place(x=875,y=6)

#label for timer
Time_view=Label(Controls,bg="#333333",fg="white",text="-:-",font=("Georgia",11),border=0,activebackground="#293241")
Time_view.place(x=260,y=6)

progress_bar= customtkinter.CTkSlider(master=Controls, from_=0, to=100, command=check
,border_color="red",height=5,button_hover_color="red",button_color="red",border_width=0,fg_color="grey",progress_color="red",width=340)
progress_bar.place(x=260,y=14)
progress_bar.set(0)

#suffle and loop buttions
Music_Suffle=Button(Controls,image=Photo_loop,bg="#333333",fg="#333333",border=0,activebackground="#293241",comman=Suffle)
Music_Suffle.place(x=60,y=4)

#button to add favourite
favourite_heart=Button(Controls,image=Photo_white_heart,bg="#333333",fg="#333333",text="SUFF",border=0,activebackground="#293241",comman=add_favourite)
favourite_heart.place(x=780,y=6)



m = Menu(root,bg="#f2f2f2", tearoff = 0)
m.add_command(label ="Add songs",command=lambda :add_songs_to_playlist(playlist_rename,"add_songs"))
m.add_command(label ="Remove songs",command=lambda :add_songs_to_playlist(playlist_rename,"remove_songs"))
m.add_command(label ="Delete playlist",command=lambda: delete_playlist(playlist_rename))
m.add_command(label ="Change Font Color",command=lambda :change_font_color(playlist_rename))
m.add_separator()
m.add_command(label ="Rename",command=Rename)

#option to add playlist
add_playlist_image=PhotoImage(file=".\\resources\\plus2.png")
add_playlist_button=Button(Options,image=add_playlist_image,fg="white",bd=0,bg="black",font=("Georgia",10,"bold"),command=add_playlist)
add_playlist_button.place(x=115,y=281)


class plist:
	def __init__(self,name):
		globals()[name].bind("<Button-3>",lambda x:do_popup(x,name))
		globals()[name].bind("<Button-1>",lambda x:add_playlist_to_listbox(name))
def  playlist_allocation():
    cur.execute("select * from colors")
    for i in cur:
        colors_list=i
    c=1
    cur.execute("select name FROM PRAGMA_TABLE_INFO('playlists')")
    for i in cur:
        y=i[0]
        globals()[str(y)]=Button(adding_playlist_using_1_btn,anchor=W,text=i[0],fg=colors_list[c],bd=0,bg="black",font=("Georgia",10,"bold"))
        globals()[str(y)].pack(pady=1,anchor="w",expand=TRUE,fill=X)
        plist(i[0])
        c+=1
    return
threading.Thread(target=playlist_allocation).start()


root.mainloop()