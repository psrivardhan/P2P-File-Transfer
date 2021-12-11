import curses
from curses import wrapper
import datetime, time


screen = curses.initscr()
screen.keypad(True)
curses.curs_set(0)
curses.noecho()

## Define Colors
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, curses.COLOR_WHITE,-1)
curses.init_pair(2,curses.COLOR_GREEN,-1)
curses.init_pair(3,curses.COLOR_RED,-1)
curses.init_pair(4,curses.COLOR_BLACK,curses.COLOR_WHITE)
# Log text color
curses.init_pair(5,248,-1)   
# For time stamp
curses.init_pair(6,220,-1)
# Newtork log upstream
curses.init_pair(7,195,-1)
# Newtork log upstream
curses.init_pair(8,185,-1)


# Get screen width/height
H,W= screen.getmaxyx()

screen.bkgd(' ',curses.color_pair(1))

log_pad_total = 600
log_pad_siz = H-15
log_pad_loc= 0

#######  Curses Pads ###########
clt_info_bar = curses.newpad(1,40)
title_info_bar = curses.newpad(1,16)
server_info_bar = curses.newpad(1,22)
navbar = curses.newpad(1,max(W,100))

log_pad = curses.newpad(log_pad_total,W)
log_pad.bkgd(' ',curses.color_pair(5))

output_pad = curses.newpad(50,max(W,40))



title_info_bar.addstr(" QuickTransfer ",curses.A_BOLD)


navbar.addstr("R:",curses.color_pair(4))
navbar.addstr(" Register File\t")

navbar.addstr("D:",curses.color_pair(4))
navbar.addstr(" Download File\t")

navbar.addstr("M:",curses.color_pair(4))
navbar.addstr(" My Files\t")

navbar.addstr("Q:",curses.color_pair(4))
navbar.addstr(" Quit")

#################################################################


def tui_handle_resize():
    # Get screen width/height
    global  statbar,navbar,inpbar,clt_info_bar,server_info_bar,H,W,Wb2,title_info_bar
    
    H,W = screen.getmaxyx()
    Wb2 = int(W/2)

    screen.clear()
    screen.refresh()

    statbar = curses.newwin(1,W,H-4,0)
    inpbar  = curses.newwin(1,W,H-3,0)
    
    
    clt_info_bar.refresh(0,0,0,0,0,Wb2-9)
    server_info_bar.refresh(0,0,0,W-22,0,W)
    title_info_bar.refresh(0,0,0,Wb2-8,0,Wb2+8)
    navbar.refresh(0,0,H-1,0,H-1,W-1)
    log_pad.refresh(log_pad_loc,0,2,0,log_pad_siz-1,W-1)
    output_pad.refresh(0,0,H-15,0,H-1,W-1)
    ## Init the Screen

    
    
    

def tui_curses_clr_line():
    pass

def tui_clear_all():
    pass

def tui_refresh_all():
    pass

def tui_reset_bottom():
    inpbar.clear()
    statbar.clear()
    inpbar.refresh()
    statbar.refresh()
    navbar.refresh(0,0,H-1,0,H-1,W-1)

def tui_report_err(msg):
    pass
    
def tui_set_server_status(msg,*argv):
    server_info_bar.clear()
    server_info_bar.addstr("Server: ")

    if len(argv) > 0  :
        server_info_bar.addstr(msg,argv[0])
    else:
        server_info_bar.addstr(msg)
    server_info_bar.refresh(0,0,0,W-22,0,W)

def tui_set_clt_status(msg,*argv):
    clt_info_bar.clear()
    clt_info_bar.addstr("Client IP: ")
    clt_info_bar.addstr(str(msg[0]),curses.A_DIM)
    clt_info_bar.addstr(" Port: ")
    clt_info_bar.addstr(str(msg[1]),curses.A_DIM)
    clt_info_bar.refresh(0,0,0,0,0,Wb2-8)
    title_info_bar.refresh(0,0,0,Wb2-8,0,Wb2+8)
    navbar.refresh(0,0,H-1,0,H-1,W-1)
    

def tui_log(msg,iserror=False,issucc=False):
    # Add time Stamp
    log_pad.addstr(time.strftime('%l:%M:%S %p')+":  ",curses.color_pair(6))
    if iserror:
        log_pad.addstr(msg,curses.color_pair(3))
    elif issucc:
        log_pad.addstr(msg,curses.color_pair(2))
    else:
        log_pad.addstr(msg)

    # Get new yx
    y,x = log_pad.getyx()
    # If it is greater
    global log_pad_loc
    if y - log_pad_loc > log_pad_siz:
        # Move the scr
        log_pad_loc = y -5
    log_pad.refresh(log_pad_loc,0,2,0,log_pad_siz-1,W-1)

def tui_network_log_send(msg):
    log_pad.addstr(time.strftime('%l:%M:%S %p')+":  ",curses.color_pair(6))
    log_pad.addstr(msg,curses.color_pair(7))
    # Get new yx
    y,x = log_pad.getyx()
    # If it is greater
    global log_pad_loc
    if y - log_pad_loc > log_pad_siz:
        # Move the scr
        log_pad_loc = y -5
    log_pad.refresh(log_pad_loc,0,2,0,log_pad_siz-1,W-1)

def tui_network_log_recv(msg):
    log_pad.addstr(time.strftime('%l:%M:%S %p')+":  ",curses.color_pair(6))
    log_pad.addstr(msg,curses.color_pair(8))
    # Get new yx
    y,x = log_pad.getyx()
    # If it is greater
    global log_pad_loc
    if y - log_pad_loc > log_pad_siz:
        # Move the scr
        log_pad_loc = y -10
    log_pad.refresh(log_pad_loc,0,2,0,log_pad_siz-1,W-1)
    
def tui_show_output(msg):
    output_pad.clear()
    output_pad.addstr(msg)
    output_pad.refresh(0,0,H-15,0,H-1,W-1)

def tui_log_scroll_up():
    # Get new yx
    y,x = log_pad.getyx()
    global log_pad_loc
    log_pad_loc = max(log_pad_loc-5,0)
    log_pad.refresh(log_pad_loc,0,2,0,log_pad_siz-1,W-1)

def tui_log_scroll_down():
    # Get new yx
    y,x = log_pad.getyx()
    # If it is greater
    # Move the scr
    global log_pad_loc
    log_pad_loc = min(log_pad_loc+5,y-5)
    log_pad.refresh(log_pad_loc,0,2,0,log_pad_siz-1,W-1)
#################################################################
    
## Divide the Screen

tui_handle_resize()





tui_reset_bottom()
