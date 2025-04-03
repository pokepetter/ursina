import tkinter as tk

from .peer import TextPeer
from ..utils import Frame

class Minimap(Frame):
    def __init__(self, master, textw, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.tw = textw
        self.config(highlightthickness=0, bg=self.base.theme.border)
        
        self.cw = tk.Canvas(self, width=100, highlightthickness=0, **self.base.theme.minimap)
        self.cw.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(1, 0))

        """
        self.peer = TextPeer(self.cw, self.tw, font=("Arial", 1, "bold"), state=tk.DISABLED, width=100, highlightthickness=0, bd=0, **self.base.theme.minimap)
        self.peerwindow = self.cw.create_window(0, 0, window=self.peer, anchor="nw", height=self.winfo_screenheight(), tag="peerwindow")
        # Remove any text selection possibility
        self.peer.bindtags((str(self.peer), str(self), "all"))
        
        # Reaching the mouse wheel event of the peer text widget for minimap scrolling
        self.peer.bind("<MouseWheel>", self.scroll_minimap)
        
        #Add a binding to the peer text widget to scroll the main text widget to the clicked position
        self.peer.bind("<Button-1>", self.scroll_to)
        """
        # TODO: SLIDER
        # the current slider using a semi transparent photoimage rendered inside the canvas wont work
        # mainly due to the image not rendering on top of peer text window added to canvas.
        # but also, currently the slider is not necessary and the minimap can be scrolled with mousescroll 

        # TODO:scrolling minimap along with the attached text widget automatically (but figuring out ratios is hard)
        
        """
        self.slider_image = tk.PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAAG4AAABFCAYAAACrMNMOAAAACXBIWXMAAABfAAAAXwEqnu0dAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAMBJREFUeJzt0UENwCAAwMAxLajjhwOkz8M+pMmdgiYda5/5kPPeDuAf46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIuyrgo46KMizIu6gNeAwIJ26ERewAAAABJRU5ErkJggg==")
        self.slider = self.cw.create_image(0, 0, image=self.slider_image, anchor=tk.NW, tag="slider")
        self.cw.tag_raise('slider')
        
        self.y_top_lim = 0
        self._drag_data = {"y": 0, "item": None}
        self.yvalue = 0

        self.cw.tag_bind("slider", "<ButtonPress-1>", self.drag_start)
        self.cw.tag_bind("slider", "<ButtonRelease-1>", self.drag_stop)
        self.cw.tag_bind("slider", "<B1-Motion>", self.drag)
        """

        if textw:
            self.redraw()
            
    """
    def attach(self, textw):
        self.tw = textw

        self.cw.delete(self.peerwindow)
        self.peer = TextPeer(self.cw, self.tw, font=("Arial", 1, "bold"), state=tk.DISABLED, width=100, highlightthickness=0, bd=0, **self.base.theme.minimap)
        self.peerwindow = self.cw.create_window(0, 0, window=self.peer, anchor="nw", height=self.winfo_screenheight())
    """
    
    def redraw(self):
        self.y_bottom_lim = int(self.tw.index(tk.END).split(".")[0]) * 2 + 10
        # self.y_bottom_lim = self.tw.yview()[1] * self.cw.winfo_height()
    
    def drag_start(self, event):
        self._drag_data["item"] = self.cw.find_closest(event.x, event.y)[0]
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        self._drag_data["item"] = None
        self._drag_data["y"] = 0

    def drag(self, event):
        item = self._drag_data["item"]
        if item != 1:
            return

        delta_y = event.y - self._drag_data["y"]
        self.cw.move(item, 0, delta_y)
        self._drag_data["y"] = event.y

        self.yvalue = y = self.cw.coords(item)[1]
        if y <= self.y_top_lim:
            self.cw.move("slider", 0, -(y - self.y_top_lim))
        elif y >= self.y_bottom_lim:
            self.cw.move("slider", 0, -(y - self.y_bottom_lim))

        self.tw.yview(int(y / self.cw.winfo_height() * 350))
        self.tw.master.on_scroll()

    """
    def scroll_to(self, event):
        y = event.y
        print(y/2)
        self.tw.yview(int(y / 2)-3)
        self.tw.master.on_scroll()
        self.yvalue = y
        
    def scroll_minimap(self, event):
        #Scrolling the minimap with the mouse wheel
        self.cw.yview_scroll(-1 * int(event.delta / 120), "units")
        self.yvalue = min(max(self.cw.coords("slider")[1], self.y_top_lim), self.y_bottom_lim)
    """