#!/usr/bin/env python
# coding=utf-8


import os
import sys
import Tkinter as tk
import tkMessageBox
window = tk.Tk()

def alert_btn_clcik():
    tkMessageBox.showinfo(title='提示', message='人生苦短')
    pass

def close_clcik():
    window.destroy()
    pass

def print_selection():
    pass


def setup_window(title="githooks提示"):
    global window
    window.title(title)
    tk_reset_center(rt=window)
    window.wm_attributes("-topmost", True)
    pass

def show_alert(msg="暂无内容"):
    setup_window()

    l=tk.Label(window, text=msg, wraplength=window.winfo_reqwidth())
    l.pack()

    btn = tk.Button(window,text="点击关闭",command=close_clcik)
    btn.pack()

    alert_btn = tk.Button(window,text="点击弹框",command=alert_btn_clcik)
    alert_btn.pack()


    r1 = tk.Radiobutton(window, text='Option A',
                    variable="var", value='A',
                    command=print_selection)
    r1.pack()

    window.mainloop()

    pass


def tk_reset_center(rt):
    rt.update()
    curWidth = rt.winfo_reqwidth() # get current width
    curHeight = rt.winfo_height() # get current height
    scnWidth,scnHeight = rt.maxsize() # get screen width and height
    tmpcnf = '%dx%d+%d+%d'%(curWidth*2,curHeight*1,
    (scnWidth-curWidth)/2,(scnHeight-curHeight)/2)
    rt.geometry(tmpcnf)
    pass

def main():
    text = "我是提示"
    show_alert(text)
    print "执行完毕"
    pass

if __name__ == '__main__':
    main()
    pass

