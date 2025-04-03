import tkinter as tk
from tkinter import ttk


class Style(ttk.Style):
    _instance = 0
    def __init__(self, master, config, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.base = master
        self.config = config
        self.theme = config.theme
        
        self.gen_fileicons()
        self.config_treeview()
        self.config_tree_scrollbar()
        
        Style._instance += 1
    
    def config_tree_scrollbar(self):
        self.element_create(f"TreeScrollbar{Style._instance}.trough", "from", "clam")
        self.element_create(f"TreeScrollbar{Style._instance}.thumb", "from", "clam")

        self.layout(f"TreeScrollbar{Style._instance}", [
            (f"TreeScrollbar{Style._instance}.trough", {
                'sticky': 'ns',
                'children': [
                    (f"TreeScrollbar{Style._instance}.thumb", {
                        'unit': '1',
                        'sticky': 'nsew'
                    })
                ]
            })
        ])

        
        bg, highlight = self.theme.scrollbar.values()
        self.configure(f"TreeScrollbar{Style._instance}", gripcount=0, background=bg, troughcolor=bg, bordercolor=bg, lightcolor=bg, darkcolor=bg, arrowsize=14)
        self.map(f"TreeScrollbar{Style._instance}", background=[('pressed', highlight), ('!disabled', self.theme.border)])
        
        self.element_create(f"EditorScrollbar{Style._instance}.trough", "from", "clam")
        self.element_create(f"EditorScrollbar{Style._instance}.thumb", "from", "clam")

        self.layout(f"EditorScrollbar{Style._instance}", [
            (f"EditorScrollbar{Style._instance}.trough", {
                'sticky': 'nsew',
                'children': [
                    (f"EditorScrollbar{Style._instance}.thumb", {
                        'sticky': 'nsew'
                    })
                ]
            })
            
        ])
        self.configure(f"EditorScrollbar{Style._instance}", gripcount=0, background=bg, troughcolor=bg, bordercolor=bg, lightcolor=bg, darkcolor=bg)
        self.map(f"EditorScrollbar{Style._instance}", background=[('pressed', highlight), ('!disabled', self.theme.border)])

    def config_treeview(self):
        ## TREENODE CHEVRONS -----
        self.img_tree_close = tk.PhotoImage("img_tree_close", data="""
                iVBORw0KGgoAAAANSUhEUgAAAAsAAAALCAYAAACprHcmAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d
                2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAALBJREFUGJVjYIACExMTfxMTk8WhoaHMDDgAE4zx69ev4////ze4d+
                /ecgcHBxZsihmROXp6emKsrKx7GRgYrvPy8kYdOHDgD07FhDQwoSu+dOnSq9+/fzszMDBofv78eY2npyc7TsUwDez
                s7JEMDAweL1++XAgTx+oRPT09sZ8/fy5nZGTcLiYmFk+Mm6/x8vJGI7sZV2hgKERRTEghigfZ2NgsGRkZLygpKWGE
                LwwAAECxSWJ5KCTqAAAAAElFTkSuQmCC""")
        self.img_tree_open = tk.PhotoImage("img_tree_open", data="""
                iVBORw0KGgoAAAANSUhEUgAAAAsAAAALCAYAAACprHcmAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d
                2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAALxJREFUGJW10D0KwkAQBeA3wd2EiJ23ELbZYJMTKGJhIZ7G81irCB
                4g5TaBNJ7Bzh92Y/GsItsogvjK4Zs3MMC/IkVRjNu2beq6vr1Dxpi+1nqUkFxrrQ/GmP4HeCC5TgAsATyUUseyLAc
                xtNbmSqkdSfHer6QbisiWZJZl2aSqqou1NgewB9Dz3k+bprlK3NItpGm6CCFsYggASYedc3eScxF5hBBOIpLGEABe
                zdGFIcm9iMycc+cvv/pjnkvzViGP6ap9AAAAAElFTkSuQmCC""")
        self.img_tree_empty = tk.PhotoImage("img_tree_empty", data="""
                iVBORw0KGgoAAAANSUhEUgAAAAsAAAALCAYAAACprHcmAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d
                2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAA5JREFUGJVjYBgFIwgAAAHvAAGLZFZqAAAAAElFTkSuQmCC""")

        self.element_create(
            f"Treeitem{Style._instance}.nindicator", 'image',  self.img_tree_close,
            ('user1', '!user2', self.img_tree_open), ('user2', self.img_tree_empty), 
            sticky='w', width=20)

        self.configure(f"Treeview{Style._instance}", font=self.config.uifont, rowheight=25, **self.theme.tree)  
        self.map(f"Treeview{Style._instance}", background=[('selected', self.theme.tree["activebackground"])])

        self.layout(f"Treeview{Style._instance}", [('Treeview.treearea', {'sticky': 'nswe'})])
        self.layout(f"Treeview{Style._instance}.Item", [
            (f"Treeview{Style._instance}.padding", {
                'sticky': 'nswe',
                'children': [
                    (f"Treeview{Style._instance}.nindicator", {
                        'side': 'left', 'sticky': ''
                    }),
                    (f"Treeview{Style._instance}.image", {
                        'side': 'left', 'sticky': ''
                    }),
                    (f"Treeview{Style._instance}.text", {
                        'side': 'left', 'sticky': ''
                    })
                ]
            })
        ])
    
    def gen_fileicons(self):
        self.document_icn = tk.PhotoImage("document", data="""
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAJ2AAACdgBx6C5rQA
        AABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADlSURBVDiNpZGxTgJBFEXPW9aGCRTYWht+wyVEEuq1md
        7Exm/A2NjxFUvBD1CQ7JZWlOhXQCNsoYnPajZk3Zks4VaTmfvOO8nAhRF3SJfa2X2XLwi39ZIi74XtzoOA0eIwUZVVQ+cDu
        AHmuTWz+mNUbdGo57HcKiTAc5KVb15AKIU1G4Ux6GMd0grgICIyBX26yw737j5uMZsm2VEBVBUAIeqfbeDLP4PcGmkqujgb
        LyDJjsuLDAJJWwFyax6ainV1L8BX9KX6BZHfr7ZDp93KYBCb9f6nfFUYhoZV+by+MutzLIP5A16TRi/mS3m5AAAAAElFTkS
        uQmCC
        """)

        self.folder_icn = tk.PhotoImage("foldericon", data="""
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAMCAYAAABr5z2BAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB
        3d3cuaW5rc2NhcGUub3Jnm+48GgAAAJBJREFUKJHdzTEKwkAUhOF/loCFRbAVr+IhLAWLCPaW3sFGPIOm1Bt4hxSSEwRs7Z
        UdayErmnROO++bp93htJK0BUa8pxEq1ovZhQ/R/ni+G/LWEjW2y4Stx4NnmUU7l9R6YTxBbFLfb49sGlL4m9ieh84aAA17D
        sCfDLiHdwDqrlpwDTHGAqiA+IONQIW0fAFkySdEGFdeCgAAAABJRU5ErkJggg==""")
