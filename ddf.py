#!/usr/bin/python
# vim: fileencoding=utf-8 
#
#	ddf is clone of DF of FD clone.
#
#
#簡単な使い方説明
#  j, k, 矢印上, 矢印下: カーソル移動（j,k使用推奨）
#  Space: ファイルの選択/選択解除
#  BackSpace, b: いっこ上のディレクトリに移動
#  Enter,h: いま選んでいるディレクトリに入る。ファイルならなにもしない（いまんとこ）
#  g: ディレクトリ移動(change directory, Go)
#     ※ コピー、移動、削除はファイルを選択してから！
#  c: 選択中のファイルを指定ディレクトリにコピー
#  m: 選択中のファイルを指定ディレクトリに移動
#  D: 選択中のファイル削除（rmするので元に戻せません。気をつけてね）
#  x: コマンド実行。選択中のファイルがあればすべてを引数につけて実行。
#
#  r: カーソル位置のファイルリネーム（これは選択系じゃないよ）
#  a: すべて選択状態にする
#  ESC: すべての選択状態解除
#
#  q: もうやめたい
#
#
#
#TODO:
#	* もふとん！
#	* 設定ファイル
#	* フォルダをみるPermissionがないときの処理?
#	* BSで戻ったときpositionを元に戻す?
#	* 隠しファイルの表示/非表示
#	* DFみたいな検索機能
#

import curses
import locale
import os
import shutil

maxcy=maxcx=1

class File:
	def __init__(self, f):
		self.fname=f
		self.base, self.ext = os.path.splitext(f)
		self.isDir=os.path.isdir(f)
		self.size=os.path.getsize(f)
		self.isSelect=False
		
	def select(self):
		if self.isSelect==False:
			self.isSelect=True
		else:
			self.isSelect=False
		
class FileList:
	def __init__(self):
		self.files=[]
		
	def add(self, fname):
		f=File(fname)
		self.files.append(f)
		
	def opendir(self, path):
		self.files=[]
		flist=os.listdir(path)
		flist.sort()
		for i in flist:
			self.add(i)
		return len(self.files)

	def selectALL(self):
		for i in self.files:
			i.isSelect=True
	
	def unselectALL(self):
		for i in self.files:
			i.isSelect=False
			
	def toggleSelect(self):
		for i in self.files:
			i.select()
	
def inputtext(scr, text=''):
	curses.echo()
	curses.nocbreak()
	scr.addstr(maxcy-1, 0, text)
	ret = scr.getstr(maxcy-1, len(text), 80)
	curses.noecho()
	curses.cbreak()
	return ret

def inputpath(scr, text=''):
	ret='.'
	path = os.path.expanduser(inputtext(scr, text))
	if os.path.exists(path): ret=path
	return ret

def copyFiles(scr, flist):
	dst=inputpath(scr, 'CopyTo?')
	if os.path.exists(dst):
		for i in flist.files:
			if i.isSelect==True:
				#os.system('cp "'+i.fname+'" "'+dst+'"')
				shutil.copy(i.fname, dst)

def moveFiles(scr, flist):
	dst=inputpath(scr, 'MoveTo?')
	if os.path.exists(dst):
		for i in flist.files:
			if i.isSelect==True:
				#os.system('mv "'+i.fname+'" "'+dst+'"')
				shutil.move(i.fname, dst)
				try:
					shutil.move(i.fname, dst)
				except shutil.Error:
					return 'File Move Error: already exists.'

def deleteFiles(scr, flist):
	for i in flist.files:
		if i.isSelect==True:
			os.remove(i.fname)

def renameFile(scr, f):
	new=inputtext(scr, 'NewFileName:')
	os.rename(f, new)

def runcommand(scr):
	cmd=inputtext(scr, 'Run:')
	os.system(cmd)
	#os.system(cmd+' &')
	
def runcommand2(scr, flist):
	opt=''
	cmd=inputtext(scr, 'Run:')
	for i in flist.files:
		if i.isSelect:
			# for os.system, contain blank and quotes.
			opt+=' "'+i.fname+'"'
	os.system(cmd+opt)
	
def main(scr):
	global maxcy,maxcx
	maxcy, maxcx = scr.getmaxyx()	# get terminal width,height
	cx=cy=0	# cursor position.
	cy=1
	offset=0
	index=0
	flist=FileList()
	# 起動時にhomeになるように
	os.chdir(os.path.expanduser('~/'))
	itemnum=flist.opendir(os.getcwd())
	#curses.curs_set(2)
	
	while True:
		scr.clear()
		scr.move(0,0)
		scr.addstr(os.getcwd()+'  index:'+str(index))
		scr.move(1,0)
		cnt=0
		for i in flist.files[offset:offset+(maxcy-2)]:
			sele=' '
			if i.isSelect==True: sele='*'
			dire=''
			if i.isDir==True: dire='/'
			more=''
			if len(i.fname)>maxcx-6: more='..'
			if (cnt+offset)==index:
				scr.addstr(sele+i.fname[0:maxcx-6]+more+dire+" \n", curses.A_STANDOUT)
			else:
				scr.addstr(sele+i.fname[0:maxcx-6]+more+dire+" \n", curses.A_NORMAL)
			cnt+=1
		scr.refresh()
		scr.move(cy, cx)
	
		###############################
		# input check ここから
		################################
		c = scr.getch()
		if c==ord('q'): break
		
		if c==ord(' '):
			flist.files[index].select()
			# いっこ下げる処理、というか
			cy+=1
			index+=1
			if index>itemnum-1: index=itemnum-1
			if cy>itemnum: cy=itemnum
			if cy==maxcy-1:
				cy=maxcy-2
				offset+=1
				if offset>itemnum-(maxcy-2): offset=itemnum-(maxcy-2)
				
		if c==10 or c==ord('h'):	## ENTER キー
			if flist.files[index].isDir==True:
				os.chdir(flist.files[index].fname)
				offset=index=0
				cy=1
				itemnum=flist.opendir(os.getcwd())
			else:
				# ファイルを開く処理など
				#os.system('gedit '+flist.files[index].fname)
				pass
				
		if c==ord('b') or c==curses.KEY_BACKSPACE:
			os.chdir('../')
			offset=index=0
			cy=1
			itemnum=flist.opendir(os.getcwd())
			
		if c==27:	## ESCAPE キー
			flist.unselectALL()
			
		# rename
		if c==ord('r'):
			renameFile(scr, flist.files[index].fname)
			offset=index=0
			cy=0
			itemnum=flist.opendir(os.getcwd())

		# run command(後ろに選択されているファイルを渡す)
		if c==ord('x'):
			runcommand2(scr, flist)
			
		if c==ord('a'):
			flist.selectALL()
			
		#if c==ord('A'):
		#	flist.unselectALL()
		
		if c==ord('c'):
			copyFiles(scr, flist)
			
		if c==ord('m'):
			moveFiles(scr, flist)
			offset=index=0
			cy=1
			itemnum=flist.opendir(os.getcwd())
			
		if c==ord('D'):
			deleteFiles(scr, flist)
			offset=index=0
			cy=1
			itemnum=flist.opendir(os.getcwd())
			
		if c==ord('g'):
			os.chdir(inputpath(scr, 'GoTo:'))
			offset=index=0
			cy=1
			itemnum=flist.opendir(os.getcwd())
			
		if c==ord('j') or c==curses.KEY_DOWN:
			cy+=1
			index+=1
			if index>itemnum-1: index=itemnum-1
			if cy>itemnum: cy=itemnum
			if cy==maxcy-1:
				cy=maxcy-2
				offset+=1
				if offset>itemnum-(maxcy-2): offset=itemnum-(maxcy-2)
		if c==ord('k') or c==curses.KEY_UP:
			cy-=1
			index-=1
			if index<0: index=0
			if cy==0:
				cy=1
				offset-=1
				if offset<0: offset=0
		####################################
		# input check おわり
		####################################

locale.setlocale(locale.LC_ALL, "")
curses.wrapper(main)

